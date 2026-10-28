"""
Vision extraction module — sends the invoice/receipt image directly to a
Groq vision-language model and gets back structured JSON. This replaces
the old two-step pipeline (Tesseract OCR -> text-only LLM) with a single
multimodal call: the model reads the image itself (its own OCR) and
extracts fields in the same pass.
"""
import os
import json
import base64
import mimetypes

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Current Groq vision model (as of Oct 2026). Supports image input,
# JSON mode, up to 3 images/request, 20MB size limit.
# See: https://console.groq.com/docs/vision
MODEL_NAME = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """You are an invoice/receipt data extraction engine.
You will be given an image of an invoice or receipt. Read the text in
the image yourself (perform OCR) and extract the following fields.

Respond with ONLY a valid JSON object, no markdown fences, no commentary:

{
  "vendor": string or null,
  "date": string or null,
  "items": [
    {"description": string, "quantity": number or null, "price": number or null}
  ],
  "total": number or null,
  "currency": string or null
}

If a field cannot be determined, use null. Do not invent data that is not
present in the image."""


def _encode_image(image_path: str) -> str:
    """Base64-encode a local image file as a data: URL for the API."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/png"

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{b64}"


def extract_invoice_fields(image_path: str) -> dict:
    """
    Send an invoice/receipt image to the vision LLM and parse the
    structured JSON response. Returns a dict with the extracted fields,
    or an {"error": ...} dict if parsing failed.
    """
    data_url = _encode_image(image_path)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    # Defensive cleanup in case the model wraps output in markdown fences
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM output as JSON", "raw_output": content}
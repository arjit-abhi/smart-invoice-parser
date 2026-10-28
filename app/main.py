"""
Smart Invoice Parser — FastAPI app.

Pipeline: upload image -> vision LLM (reads + structures in one call, via
Groq's qwen/qwen3.8-27b) -> append to CSV -> return JSON to caller.

Run with:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs to try it in the browser.
"""
import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.vision_extract import extract_invoice_fields
from app.export import append_invoice_to_csv, OUTPUT_PATH

app = FastAPI(title="Smart Invoice Parser")

# Allow the frontend (served separately, e.g. from a different port or
# opened as a local file) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Smart Invoice Parser is running.",
        "try": "POST an image to /parse-invoice, or open /docs",
    }


@app.post("/parse-invoice")
async def parse_invoice(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    suffix = os.path.splitext(file.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        structured = extract_invoice_fields(tmp_path)

        if "error" not in structured:
            append_invoice_to_csv(file.filename, structured)

        return {
            "filename": file.filename,
            "extracted": structured,
        }
    finally:
        os.remove(tmp_path)


@app.get("/download-csv")
def download_csv():
    if not os.path.isfile(OUTPUT_PATH):
        raise HTTPException(status_code=404, detail="No invoices parsed yet.")
    return FileResponse(OUTPUT_PATH, filename="invoices.csv", media_type="text/csv")
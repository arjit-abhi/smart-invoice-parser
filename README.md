# Smart Invoice Parser

Smart Invoice Parser extracts structured data from invoice and receipt images
using a Groq vision-language model, then appends successful results to a CSV
file. The project includes a FastAPI backend and a standalone browser frontend.

**Pipeline:** invoice image → Groq vision model → structured JSON → CSV export

The model reads the image directly, so Tesseract and a separate OCR step are
not required.

## Requirements

- Python
- A Groq API key

## Setup

1. Create and activate a virtual environment, then install the dependencies:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   On macOS or Linux, activate the environment with:

   ```bash
   source venv/bin/activate
   ```

2. Set the Groq API key in a `.env` file at the project root:

   ```text
   GROQ_API_KEY=your_groq_api_key
   ```

   Get an API key from [Groq Console](https://console.groq.com/keys). Keep the
   key private and do not commit `.env` to source control.

## Run the application

Start the backend from the project root:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. The frontend is intentionally
separate from the backend: open `frontend/index.html` in a browser while the
backend is running. It sends uploads to the local API at
`http://127.0.0.1:8000`.

You can also use the interactive API documentation at
`http://127.0.0.1:8000/docs`.

## Using the frontend

1. Start the backend as described above.
2. Open `frontend/index.html` in your browser.
3. Choose, drag and drop, or paste an invoice image, then select **Extract data**.
4. Review the extracted vendor, date, items, currency, and total. Use the
   download link to get the CSV of successfully parsed invoices.

The frontend previews the selected image, displays errors from the API, and
keeps up to ten parsed results in the current browser session. The parsed
history is not persistent; the CSV is stored by the backend.

## API

- `GET /` — health/message endpoint.
- `POST /parse-invoice` — accepts an image in a multipart form field named
  `file`. Returns the filename and extracted invoice fields as JSON.
- `GET /download-csv` — downloads the accumulated invoice CSV. Returns 404
  until the CSV exists.

Successful extractions are appended to `app/outputs/invoices.csv`. Results
containing an extraction error are returned to the caller but are not added to
the CSV.

## Project structure

```text
smart-invoice-parser/
├── app/
│   ├── __init__.py          # Marks app as a Python package
│   ├── main.py              # FastAPI app and API endpoints
│   ├── vision_extract.py    # Groq vision request and JSON extraction
│   ├── export.py            # CSV writer
│   └── outputs/
│       ├── .gitkeep         # Keeps the output directory in source control
│       └── invoices.csv     # Generated records (ignored by Git)
├── frontend/
│   └── index.html           # Standalone HTML, CSS, and JavaScript frontend
├── sample_invoices/         # Place invoice images here for testing
├── .gitignore               # Excludes local secrets, environments, and generated data
├── .env                     # Local Groq API key (do not commit)
├── .vscode/
│   └── settings.json        # VS Code environment-file setting
├── requirements.txt         # Python dependencies
└── README.md
```

"""
Export module — writes a structured invoice dict to a CSV row.
"""
import csv
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "outputs", "invoices.csv")

FIELDS = ["filename", "vendor", "date", "total", "currency", "items_json"]


def append_invoice_to_csv(filename: str, data: dict, path: str = OUTPUT_PATH) -> str:
    """
    Append one parsed invoice's data as a row to the CSV file.
    Creates the file with a header if it doesn't exist yet.
    """
    import json

    file_exists = os.path.isfile(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "filename": filename,
            "vendor": data.get("vendor"),
            "date": data.get("date"),
            "total": data.get("total"),
            "currency": data.get("currency"),
            "items_json": json.dumps(data.get("items", [])),
        })

    return path

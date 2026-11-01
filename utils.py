"""Helper functions: file types, turning extracted JSON into tables, saving Excel."""
import io
import mimetypes

import pandas as pd

SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def get_mime_type(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def to_number(value):
    """Convert things like '1,200.50' or '$45' to a float. Returns None if impossible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").replace("$", "").replace("₹", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def build_tables(results: list[tuple[str, dict]]):
    """results = [(filename, extracted_dict), ...] -> (summary_df, items_df)."""
    summary_rows, item_rows = [], []

    for filename, data in results:
        items = data.get("line_items") or []
        total = to_number(data.get("total"))
        summary_rows.append(
            {
                "file": filename,
                "vendor_name": data.get("vendor_name"),
                "invoice_number": data.get("invoice_number"),
                "invoice_date": data.get("invoice_date"),
                "due_date": data.get("due_date"),
                "currency": data.get("currency"),
                "subtotal": to_number(data.get("subtotal")),
                "tax": to_number(data.get("tax")),
                "total": total,
                # Simple sanity check: do the line items add up to the subtotal/total?
                "items_sum": round(
                    sum(to_number(i.get("amount")) or 0 for i in items), 2
                ),
            }
        )
        for item in items:
            item_rows.append(
                {
                    "file": filename,
                    "invoice_number": data.get("invoice_number"),
                    "description": item.get("description"),
                    "quantity": to_number(item.get("quantity")),
                    "unit_price": to_number(item.get("unit_price")),
                    "amount": to_number(item.get("amount")),
                }
            )

    return pd.DataFrame(summary_rows), pd.DataFrame(item_rows)


def to_excel_bytes(summary_df: pd.DataFrame, items_df: pd.DataFrame) -> bytes:
    """Write both tables to one Excel file (two sheets) and return the bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Invoices", index=False)
        items_df.to_excel(writer, sheet_name="Line Items", index=False)
    return buffer.getvalue()

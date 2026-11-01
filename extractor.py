"""Sends an invoice (PDF or image) to Gemini and gets back structured JSON."""
import json
import os

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash"

PROMPT = """You are an invoice data extraction system.
Read the attached invoice and return ONLY valid JSON in exactly this shape:

{
  "vendor_name": string or null,
  "invoice_number": string or null,
  "invoice_date": "YYYY-MM-DD" or null,
  "due_date": "YYYY-MM-DD" or null,
  "currency": string or null,
  "subtotal": number or null,
  "tax": number or null,
  "total": number or null,
  "line_items": [
    {"description": string, "quantity": number, "unit_price": number, "amount": number}
  ]
}

Rules:
- Use null when a field is not on the invoice. Never guess or invent values.
- Numbers must be plain numbers (no currency symbols or commas).
- Return JSON only, with no extra text.
"""


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Copy .env.example to .env and add your key."
        )
    return genai.Client(api_key=api_key)


def _clean_json(text: str) -> dict:
    """Parse JSON even if the model wrapped it in ```json fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text)


def extract_invoice(file_bytes: bytes, mime_type: str) -> dict:
    """Extract structured invoice data from a PDF or image."""
    client = get_client()
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    return _clean_json(response.text)

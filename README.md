# 🧾 Invoice Reader

Extracts vendor, dates, totals and line items from invoices (PDF or image) into a clean Excel file using AI.

> Built with Python, Streamlit and the Gemini API (free tier works).

## The problem
Small businesses waste hours typing invoice details into spreadsheets. This tool reads the invoice for you and exports structured data in seconds.

## Demo
<!-- Add a screenshot or GIF here: ![demo](screenshots/demo.gif) -->

## Features
- Upload one or many invoices (PDF, PNG, JPG, WEBP)
- AI extracts vendor, invoice number, dates, tax, total and every line item
- Results shown in tables, with a sanity-check column (`items_sum`)
- One-click Excel download (two sheets: Invoices, Line Items)

## How it works
```
Upload file -> Gemini reads it -> returns JSON -> pandas tables -> Excel
```

## Run it locally
```bash
git clone https://github.com/YOUR-USERNAME/invoice-reader.git
cd invoice-reader
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your free key from aistudio.google.com/apikey
streamlit run app.py
```
Try it with the files in `sample_invoices/` (fake data).

## Project structure
```
invoice-reader/
├── app.py            # Streamlit UI
├── extractor.py      # AI extraction (prompt + API call)
├── utils.py          # file types, tables, Excel export
├── sample_invoices/  # fake invoices for testing
└── output/           # example result
```

## Limitations and future improvements
- AI can make mistakes, so always verify totals (see `items_sum` vs `subtotal`)
- Add automatic validation (flag invoices where totals don't add up)
- Support Google Sheets export and email-inbox ingestion
- Add Docker and deploy on Streamlit Community Cloud

## Tech
Python · Streamlit · Gemini API (google-genai) · pandas · openpyxl

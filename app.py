"""Invoice Reader: upload invoices (PDF/image) -> extract data with AI -> download Excel."""
import os

import streamlit as st
from dotenv import load_dotenv

from extractor import extract_invoice
from utils import SUPPORTED, build_tables, get_mime_type, to_excel_bytes

load_dotenv()

st.set_page_config(page_title="Invoice Reader", page_icon="🧾", layout="wide")
st.title("🧾 Invoice Reader")
st.caption("Upload invoices and get clean, structured data in Excel. Powered by Gemini.")

if not os.getenv("GEMINI_API_KEY"):
    st.error("No API key found. Copy `.env.example` to `.env` and add your GEMINI_API_KEY.")
    st.stop()

files = st.file_uploader(
    "Upload one or more invoices",
    type=[ext.strip(".") for ext in SUPPORTED],
    accept_multiple_files=True,
)

if files and st.button("Extract data", type="primary"):
    results, errors = [], []
    progress = st.progress(0.0, text="Starting...")

    for i, f in enumerate(files, start=1):
        progress.progress((i - 1) / len(files), text=f"Reading {f.name}...")
        try:
            data = extract_invoice(f.getvalue(), get_mime_type(f.name))
            results.append((f.name, data))
        except Exception as e:  # show the error but keep going with other files
            errors.append((f.name, str(e)))

    progress.progress(1.0, text="Done")
    st.session_state["results"] = results
    st.session_state["errors"] = errors

# Show results (kept in session so the page doesn't lose them on rerun)
results = st.session_state.get("results", [])
errors = st.session_state.get("errors", [])

for name, msg in errors:
    st.warning(f"Could not process **{name}**: {msg}")

if results:
    summary_df, items_df = build_tables(results)

    st.subheader("Invoice summary")
    st.dataframe(summary_df, use_container_width=True)

    st.subheader("Line items")
    st.dataframe(items_df, use_container_width=True)

    st.download_button(
        "⬇️ Download Excel",
        data=to_excel_bytes(summary_df, items_df),
        file_name="invoices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.info("Always double-check totals. AI extraction is fast but not perfect.")

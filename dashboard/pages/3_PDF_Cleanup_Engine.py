import sys
from pathlib import Path
from io import BytesIO
import zipfile
import re

import pandas as pd
import streamlit as st

# --------------------------------------------------
# Streamlit Cloud import-path fix
# --------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


st.set_page_config(
    page_title="PDF Cleanup Engine | Clean0ps",
    page_icon="📄",
    layout="wide",
)

st.title("📄 PDF Cleanup Engine")

st.markdown(
    """
Upload a PDF file to extract text, clean spacing issues, detect pages needing review,
extract tables when available, and export structured CSV/Excel files.

This works best with **text-based PDFs**. Scanned/image-only PDFs need OCR, which is a separate upgrade.
"""
)


def clean_pdf_text(text: str) -> str:
    if not text:
        return ""

    cleaned = text.replace("\x00", " ")
    cleaned = cleaned.replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    lines = [line.strip() for line in cleaned.splitlines()]
    return "\n".join(lines).strip()


def classify_page(raw_text: str, cleaned_text: str, table_count: int) -> str:
    if not raw_text and table_count == 0:
        return "Empty or scanned page"
    if len(cleaned_text) < 25 and table_count == 0:
        return "Low text extraction"
    if table_count > 0 and len(cleaned_text) < 25:
        return "Table-heavy page"
    return "OK"


def extract_pdf(uploaded_file):
    page_records = []
    table_records = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned_text = clean_pdf_text(raw_text)

            tables = page.extract_tables() or []
            table_count = len(tables)

            page_records.append(
                {
                    "page_number": page_number,
                    "raw_character_count": len(raw_text),
                    "cleaned_character_count": len(cleaned_text),
                    "table_count": table_count,
                    "review_status": classify_page(raw_text, cleaned_text, table_count),
                    "cleaned_text": cleaned_text,
                }
            )

            for table_number, table in enumerate(tables, start=1):
                if not table:
                    continue

                rows = [
                    row for row in table
                    if row and any(str(cell).strip() for cell in row if cell is not None)
                ]

                if not rows:
                    continue

                max_cols = max(len(row) for row in rows)

                for row_number, row in enumerate(rows, start=1):
                    row = list(row) + [""] * (max_cols - len(row))

                    record = {
                        "page_number": page_number,
                        "table_number": table_number,
                        "row_number": row_number,
                    }

                    for col_number, cell in enumerate(row, start=1):
                        value = "" if cell is None else str(cell).strip()
                        value = re.sub(r"[ \t]+", " ", value)
                        record[f"column_{col_number}"] = value

                    table_records.append(record)

    pages_df = pd.DataFrame(page_records)
    tables_df = pd.DataFrame(table_records)

    return pages_df, tables_df


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_excel_report(pages_df: pd.DataFrame, tables_df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pages_df.to_excel(writer, index=False, sheet_name="pdf_pages")

        if not tables_df.empty:
            tables_df.to_excel(writer, index=False, sheet_name="extracted_tables")

        summary_df = pd.DataFrame(
            [
                {"metric": "pages_processed", "value": len(pages_df)},
                {
                    "metric": "pages_needing_review",
                    "value": int((pages_df["review_status"] != "OK").sum())
                    if not pages_df.empty else 0,
                },
                {
                    "metric": "tables_extracted",
                    "value": int(
                        tables_df[["page_number", "table_number"]]
                        .drop_duplicates()
                        .shape[0]
                    )
                    if not tables_df.empty else 0,
                },
            ]
        )

        summary_df.to_excel(writer, index=False, sheet_name="summary")

    return output.getvalue()


def build_zip_package(pages_df: pd.DataFrame, tables_df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("cleaned_pdf_pages.csv", to_csv_bytes(pages_df))

        review_df = pages_df[pages_df["review_status"] != "OK"].copy()
        zf.writestr("pages_needing_review.csv", to_csv_bytes(review_df))

        if not tables_df.empty:
            zf.writestr("extracted_pdf_tables.csv", to_csv_bytes(tables_df))

        zf.writestr("pdf_cleanup_report.xlsx", build_excel_report(pages_df, tables_df))

    return output.getvalue()


if pdfplumber is None:
    st.error(
        "PDF support is not installed yet. Add pdfplumber to requirements.txt and redeploy."
    )
    st.stop()


uploaded_pdf = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"],
    accept_multiple_files=False,
)

if uploaded_pdf is None:
    st.info("Drag a PDF file here to start.")
    st.stop()


file_name = uploaded_pdf.name.lower()

if not file_name.endswith(".pdf"):
    st.error("This page only accepts PDF files.")
    st.stop()


with st.spinner("Extracting and cleaning PDF content..."):
    try:
        pages_df, tables_df = extract_pdf(uploaded_pdf)
    except Exception as error:
        st.error("PDF extraction failed.")
        st.exception(error)
        st.stop()


st.success("PDF cleaned and extracted successfully.")

total_pages = len(pages_df)
review_pages = int((pages_df["review_status"] != "OK").sum()) if not pages_df.empty else 0
tables_extracted = (
    int(tables_df[["page_number", "table_number"]].drop_duplicates().shape[0])
    if not tables_df.empty
    else 0
)

col1, col2, col3 = st.columns(3)
col1.metric("Pages Processed", total_pages)
col2.metric("Pages Needing Review", review_pages)
col3.metric("Tables Extracted", tables_extracted)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Cleaned Text", "Extracted Tables", "Review Issues", "Downloads"]
)

with tab1:
    st.subheader("Cleaned PDF Text")
    st.dataframe(pages_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Extracted Tables")

    if tables_df.empty:
        st.warning("No structured tables were detected in this PDF.")
    else:
        st.dataframe(tables_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Pages Needing Review")
    review_df = pages_df[pages_df["review_status"] != "OK"].copy()

    if review_df.empty:
        st.success("No page-level extraction issues detected.")
    else:
        st.dataframe(review_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Download Cleaned PDF Outputs")

    st.download_button(
        "Download cleaned PDF text CSV",
        data=to_csv_bytes(pages_df),
        file_name="cleaned_pdf_pages.csv",
        mime="text/csv",
    )

    if not tables_df.empty:
        st.download_button(
            "Download extracted PDF tables CSV",
            data=to_csv_bytes(tables_df),
            file_name="extracted_pdf_tables.csv",
            mime="text/csv",
        )

    st.download_button(
        "Download PDF cleanup Excel report",
        data=build_excel_report(pages_df, tables_df),
        file_name="pdf_cleanup_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.download_button(
        "Download full PDF cleanup package ZIP",
        data=build_zip_package(pages_df, tables_df),
        file_name="pdf_cleanup_package.zip",
        mime="application/zip",
    )

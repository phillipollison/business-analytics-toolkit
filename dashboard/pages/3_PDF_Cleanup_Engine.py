# --------------------------------------------------
# Clean0ps PDF Cleanup Engine
# --------------------------------------------------
# Purpose:
#   This page lets users upload text-based PDF files, extract text and tables,
#   clean messy extracted content, review page-level quality issues, and export
#   structured outputs.
#
# Current scope:
#   - Works best with text-based PDFs
#   - Extracts text using pdfplumber
#   - Extracts tables when table structure is detectable
#   - Exports cleaned text, extracted tables, review reports, and Excel files
#
# Future OCR upgrade:
#   Scanned/image-only PDFs need OCR support through tools such as Tesseract,
#   AWS Textract, Google Document AI, or Azure Document Intelligence.
# --------------------------------------------------

import sys
from pathlib import Path
from io import BytesIO
import zipfile
import re

import pandas as pd
import streamlit as st

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


def clean_pdf_text(text: str) -> str:
    """
    Clean extracted PDF text.

    This function is intentionally conservative.
    It cleans spacing and obvious extraction clutter without changing meaning.
    """
    if not text:
        return ""

    cleaned = text.replace("\x00", " ")
    cleaned = cleaned.replace("\r", "\n")

    # Normalize repeated spaces and tabs.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Remove excessive blank lines.
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Strip each line.
    lines = [line.strip() for line in cleaned.splitlines()]

    # Drop fully empty leading/trailing lines.
    cleaned = "\n".join(lines).strip()

    return cleaned


def classify_page_issue(raw_text: str, cleaned_text: str, table_count: int) -> str:
    """
    Create a simple review status for each PDF page.
    """
    if not raw_text and table_count == 0:
        return "Empty or scanned page"
    if raw_text and len(cleaned_text) < 25 and table_count == 0:
        return "Low text extraction"
    if table_count > 0 and len(cleaned_text) < 25:
        return "Table-heavy page"
    return "OK"


def extract_pdf(file) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract page text and tables from a PDF.

    Returns:
        pages_df:
            One row per page with raw/cleaned text and review status.

        tables_df:
            One combined table dataset with page number and table number.
    """
    if pdfplumber is None:
        raise RuntimeError(
            "pdfplumber is not installed. Add pdfplumber to requirements.txt and reinstall dependencies."
        )

    page_records = []
    table_records = []

    with pdfplumber.open(file) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned_text = clean_pdf_text(raw_text)

            tables = page.extract_tables() or []
            table_count = len(tables)

            issue_status = classify_page_issue(raw_text, cleaned_text, table_count)

            page_records.append(
                {
                    "page_number": page_index,
                    "raw_character_count": len(raw_text),
                    "cleaned_character_count": len(cleaned_text),
                    "table_count": table_count,
                    "review_status": issue_status,
                    "cleaned_text": cleaned_text,
                }
            )

            for table_index, table in enumerate(tables, start=1):
                if not table:
                    continue

                # Keep rows with at least one non-empty value.
                filtered_rows = [
                    row for row in table
                    if row and any(str(cell).strip() for cell in row if cell is not None)
                ]

                if not filtered_rows:
                    continue

                max_cols = max(len(row) for row in filtered_rows)
                normalized_rows = [
                    list(row) + [""] * (max_cols - len(row))
                    for row in filtered_rows
                ]

                for row_number, row in enumerate(normalized_rows, start=1):
                    record = {
                        "page_number": page_index,
                        "table_number": table_index,
                        "row_number": row_number,
                    }

                    for col_index, cell in enumerate(row, start=1):
                        value = "" if cell is None else str(cell).strip()
                        value = re.sub(r"[ \t]+", " ", value)
                        record[f"column_{col_index}"] = value

                    table_records.append(record)

    pages_df = pd.DataFrame(page_records)
    tables_df = pd.DataFrame(table_records)

    return pages_df, tables_df


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_excel_export(pages_df: pd.DataFrame, tables_df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pages_df.to_excel(writer, index=False, sheet_name="pdf_pages")

        if not tables_df.empty:
            tables_df.to_excel(writer, index=False, sheet_name="extracted_tables")

        summary = pd.DataFrame(
            [
                {"metric": "pages_processed", "value": len(pages_df)},
                {
                    "metric": "pages_needing_review",
                    "value": int((pages_df["review_status"] != "OK").sum()) if not pages_df.empty else 0,
                },
                {
                    "metric": "tables_extracted",
                    "value": int(tables_df[["page_number", "table_number"]].drop_duplicates().shape[0])
                    if not tables_df.empty else 0,
                },
            ]
        )

        summary.to_excel(writer, index=False, sheet_name="summary")

    return output.getvalue()


def build_zip_export(pages_df: pd.DataFrame, tables_df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("cleaned_pdf_pages.csv", dataframe_to_csv_bytes(pages_df))

        review_df = pages_df[pages_df["review_status"] != "OK"].copy()
        zf.writestr("pages_needing_review.csv", dataframe_to_csv_bytes(review_df))

        if not tables_df.empty:
            zf.writestr("extracted_pdf_tables.csv", dataframe_to_csv_bytes(tables_df))

        zf.writestr("pdf_cleanup_report.xlsx", build_excel_export(pages_df, tables_df))

    return output.getvalue()


st.title("📄 PDF Cleanup Engine")

st.markdown(
    """
Clean messy PDF content by extracting page text, detecting review issues, pulling available tables,
and exporting structured files.

This first version works best with **text-based PDFs**. Scanned/image-only PDFs will need OCR later,
because apparently PDFs decided to be both documents and pictures just to annoy everyone.
"""
)

uploaded_pdf = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"],
    help="Best results come from text-based PDFs. Scanned PDFs may return little or no text.",
)

if uploaded_pdf is None:
    st.info("Upload a PDF to start cleaning and extracting content.")
    st.stop()

if pdfplumber is None:
    st.error("pdfplumber is missing. Add pdfplumber to requirements.txt and redeploy.")
    st.stop()

with st.spinner("Extracting and cleaning PDF content..."):
    try:
        pages_df, tables_df = extract_pdf(uploaded_pdf)
    except Exception as error:
        st.error("PDF extraction failed.")
        st.exception(error)
        st.stop()

st.success("PDF extraction complete.")

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
    [
        "Cleaned Page Text",
        "Extracted Tables",
        "Review Issues",
        "Exports",
    ]
)

with tab1:
    st.subheader("Cleaned Page Text")
    st.dataframe(
        pages_df[
            [
                "page_number",
                "raw_character_count",
                "cleaned_character_count",
                "table_count",
                "review_status",
                "cleaned_text",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

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

        st.markdown(
            """
Common reasons a page needs review:

- The page is scanned or image-only
- The page has very little extractable text
- The page is mostly table content
- The PDF structure made extraction unreliable
"""
        )

with tab4:
    st.subheader("Download Cleaned Outputs")

    st.download_button(
        "Download cleaned page text CSV",
        data=dataframe_to_csv_bytes(pages_df),
        file_name="cleaned_pdf_pages.csv",
        mime="text/csv",
    )

    if not tables_df.empty:
        st.download_button(
            "Download extracted tables CSV",
            data=dataframe_to_csv_bytes(tables_df),
            file_name="extracted_pdf_tables.csv",
            mime="text/csv",
        )

    st.download_button(
        "Download PDF cleanup Excel report",
        data=build_excel_export(pages_df, tables_df),
        file_name="pdf_cleanup_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.download_button(
        "Download full PDF cleanup ZIP",
        data=build_zip_export(pages_df, tables_df),
        file_name="pdf_cleanup_package.zip",
        mime="application/zip",
    )

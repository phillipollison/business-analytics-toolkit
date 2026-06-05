import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2] if CURRENT_FILE.parent.name == "pages" else CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from clean0ps_ui import (
    apply_clean0ps_style,
    privacy_notice,
    reset_workflow_button,
    hero,
    section_title,
    feature_card,
    workflow_stepper,
    badge_row,
    section_callout,
    empty_state,
    download_card
)

from clean0ps_core import (
    read_uploaded_file,
    check_file_size,
    normalize_columns,
    safe_numeric,
    missing_mask,
    dataframe_to_csv_bytes,
    text_to_bytes,
    make_excel_bytes,
    get_friendly_error
)


st.set_page_config(
    page_title="Document Standards Cleanup Lab",
    page_icon="📄",
    layout="wide"
)

apply_clean0ps_style()
privacy_notice()
reset_workflow_button()

hero(
    title="📄 Document Standards Cleanup Lab",
    subtitle=(
        "Clean and validate structured data extracted from PDFs, standards documents, "
        "LLM ingestion workflows, OCR outputs, and database-ready document records."
    ),
    pill="PDF EXTRACTION · LLM CLEANUP · STANDARDS DATA · VERIFICATION"
)


def make_demo_standards_data():
    return normalize_columns(pd.DataFrame({
        "Document Name": [
            "Aerospace Standard 100",
            "Aerospace Standard 100",
            "Aerospace Standard 100",
            "Aerospace Standard 100",
            "Aerospace Standard 100",
            "Aerospace Standard 200",
            "Aerospace Standard 200",
            "Aerospace Standard 200"
        ],
        "Page Number": [1, 2, 2, 3, None, 1, 4, "bad page"],
        "Section ID": ["1.0", "1.1", "1.1", "2.0", "2.1", "A", "B", ""],
        "Section Title": [
            "Scope",
            "Material Requirements",
            "Material Requirements",
            "Testing Procedure",
            "Tolerance",
            "Overview",
            "Inspection",
            "Final Review"
        ],
        "Requirement Text": [
            "All parts must be inspected before use.",
            "Material shall meet listed tensile strength values.",
            "Material shall meet listed tensile strength values.",
            "Testing shall be performed under controlled conditions.",
            "",
            "This standard defines minimum acceptance rules.",
            "Inspection must be documented.",
            "Final review must be completed before publication."
        ],
        "Extracted Value": [
            "Inspected before use",
            "Tensile strength values",
            "Tensile strength values",
            "Controlled conditions",
            None,
            "Minimum acceptance rules",
            "",
            "Completed before publication"
        ],
        "Unit": ["", "MPa", "MPa", "", "mm", "", "", ""],
        "Category": [
            "Requirement",
            "Requirement",
            "Requirement",
            "Procedure",
            "Tolerance",
            "Overview",
            "Inspection",
            "Review"
        ],
        "Confidence Score": [0.98, 0.82, 0.82, 0.61, 0.35, 95, 0.72, 0.44],
        "Review Status": [
            "verified",
            "needs_review",
            "needs_review",
            "needs_review",
            "",
            "verified",
            "needs_review",
            "unverified"
        ],
        "Source Verified": ["yes", "no", "no", "no", "", "yes", "no", "no"],
        "Review Notes": [
            "",
            "Check source wording",
            "Duplicate section",
            "Low confidence",
            "Missing requirement text",
            "",
            "Missing extracted value",
            "Bad page number"
        ]
    }))


FIELD_DEFINITIONS = {
    "document_name": {
        "label": "Document Name",
        "required": True,
        "candidates": ["document_name", "document", "file_name", "pdf_name", "standard_name", "source_document"]
    },
    "page_number": {
        "label": "Page Number",
        "required": True,
        "candidates": ["page_number", "page", "page_num", "pdf_page"]
    },
    "section_id": {
        "label": "Section ID",
        "required": True,
        "candidates": ["section_id", "section", "clause", "clause_id", "requirement_id"]
    },
    "section_title": {
        "label": "Section Title",
        "required": False,
        "candidates": ["section_title", "title", "heading", "clause_title"]
    },
    "requirement_text": {
        "label": "Requirement Text",
        "required": True,
        "candidates": ["requirement_text", "requirement", "source_text", "text", "clause_text", "standard_text"]
    },
    "extracted_value": {
        "label": "Extracted Value",
        "required": False,
        "candidates": ["extracted_value", "value", "answer", "llm_output", "extracted_text"]
    },
    "unit": {
        "label": "Unit",
        "required": False,
        "candidates": ["unit", "units", "measurement_unit"]
    },
    "category": {
        "label": "Category",
        "required": False,
        "candidates": ["category", "type", "record_type", "classification"]
    },
    "confidence_score": {
        "label": "Confidence Score",
        "required": False,
        "candidates": ["confidence_score", "confidence", "score", "llm_confidence"]
    },
    "review_status": {
        "label": "Review Status",
        "required": False,
        "candidates": ["review_status", "status", "verification_status"]
    },
    "source_verified": {
        "label": "Source Verified",
        "required": False,
        "candidates": ["source_verified", "verified", "source_check", "source_checked"]
    },
    "review_notes": {
        "label": "Review Notes",
        "required": False,
        "candidates": ["review_notes", "notes", "comments", "review_comment"]
    }
}


def get_default_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return "None"


def get_selected_col(mapping, field_name):
    value = mapping.get(field_name, "None")
    return None if value == "None" else value


def make_text_column(df, col, default=""):
    if col and col in df.columns:
        return df[col].fillna(default).astype(str).str.strip()
    return pd.Series([default] * len(df), index=df.index)


def parse_source_verified(value):
    text = str(value).strip().lower()

    if text in ["true", "yes", "y", "1", "verified", "source verified", "checked"]:
        return True

    return False


def normalize_confidence(series):
    values = safe_numeric(series)
    values = values.apply(lambda x: x / 100 if x > 1 and x <= 100 else x)
    return values.clip(lower=0, upper=1)


def build_standardized_table(df, mapping):
    standardized = pd.DataFrame(index=df.index)

    for field_name, definition in FIELD_DEFINITIONS.items():
        selected_col = get_selected_col(mapping, field_name)

        if field_name == "page_number":
            standardized[field_name] = safe_numeric(df[selected_col]) if selected_col else 0

        elif field_name == "confidence_score":
            standardized[field_name] = normalize_confidence(df[selected_col]) if selected_col else 0

        elif field_name == "source_verified":
            standardized[field_name] = df[selected_col].apply(parse_source_verified) if selected_col else False

        else:
            standardized[field_name] = make_text_column(df, selected_col, "")

    standardized["database_ready"] = True

    return standardized.reset_index(drop=True)


def add_review(rows, row_index, severity, issue, field, value, recommendation):
    rows.append({
        "Row Number": int(row_index) + 2 if row_index != "" else "",
        "Severity": severity,
        "Issue": issue,
        "Field": field,
        "Value": "" if pd.isna(value) else str(value),
        "Recommendation": recommendation
    })


def build_rows_needing_review(standardized, confidence_threshold):
    rows = []

    required_fields = [
        "document_name",
        "page_number",
        "section_id",
        "requirement_text"
    ]

    for field in required_fields:
        if field == "page_number":
            invalid_mask = standardized[field].isna() | (standardized[field] <= 0)

            for index in standardized[invalid_mask].index:
                add_review(
                    rows,
                    index,
                    "Critical Issue",
                    "Missing or Invalid Page Number",
                    field,
                    standardized.loc[index, field],
                    "Enter the correct source PDF page number."
                )

        else:
            missing_values = missing_mask(standardized[field])

            for index in standardized[missing_values].index:
                add_review(
                    rows,
                    index,
                    "Critical Issue",
                    "Missing Required Field",
                    field,
                    standardized.loc[index, field],
                    "Fill this required value from the source document."
                )

    duplicate_mask = standardized.duplicated(
        subset=["document_name", "section_id"],
        keep=False
    )

    duplicate_rows = standardized[duplicate_mask]

    for index, row in duplicate_rows.iterrows():
        if str(row["section_id"]).strip() == "":
            continue

        add_review(
            rows,
            index,
            "Manual Review Needed",
            "Duplicate Section ID",
            "section_id",
            row["section_id"],
            "Confirm whether this is a repeated section, duplicate extraction, or separate valid record."
        )

    low_confidence_mask = standardized["confidence_score"] < confidence_threshold

    for index in standardized[low_confidence_mask].index:
        add_review(
            rows,
            index,
            "Manual Review Needed",
            "Low Confidence Extraction",
            "confidence_score",
            standardized.loc[index, "confidence_score"],
            "Compare this row against the PDF source before publishing."
        )

    unverified_mask = standardized["source_verified"] == False

    for index in standardized[unverified_mask].index:
        add_review(
            rows,
            index,
            "Manual Review Needed",
            "Source Not Verified",
            "source_verified",
            standardized.loc[index, "source_verified"],
            "Verify this row against the original PDF source."
        )

    valid_statuses = [
        "verified",
        "needs_review",
        "unverified",
        "rejected",
        "published",
        ""
    ]

    status_values = standardized["review_status"].fillna("").astype(str).str.lower().str.strip()
    invalid_status_mask = ~status_values.isin(valid_statuses)

    for index in standardized[invalid_status_mask].index:
        add_review(
            rows,
            index,
            "Warning",
            "Unexpected Review Status",
            "review_status",
            standardized.loc[index, "review_status"],
            "Use one of: verified, needs_review, unverified, rejected, published."
        )

    blank_extracted_value = missing_mask(standardized["extracted_value"]) & ~missing_mask(standardized["requirement_text"])

    for index in standardized[blank_extracted_value].index:
        add_review(
            rows,
            index,
            "Warning",
            "Blank Extracted Value",
            "extracted_value",
            standardized.loc[index, "extracted_value"],
            "Confirm whether this row should have an extracted database value."
        )

    if not rows:
        return pd.DataFrame(columns=[
            "Row Number",
            "Severity",
            "Issue",
            "Field",
            "Value",
            "Recommendation"
        ])

    return pd.DataFrame(rows)


def build_validation_summary(rows_needing_review):
    if rows_needing_review.empty:
        return pd.DataFrame([
            {
                "Severity": "Ready",
                "Issue": "No review issues found",
                "Count": 0
            }
        ])

    return (
        rows_needing_review
        .groupby(["Severity", "Issue"], dropna=False)
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )


def build_database_ready_table(standardized, rows_needing_review, only_verified):
    db_ready = standardized.copy()
    db_ready["needs_manual_review"] = False

    if not rows_needing_review.empty:
        review_indexes = []

        for row_number in rows_needing_review["Row Number"].dropna().tolist():
            try:
                review_indexes.append(int(row_number) - 2)
            except Exception:
                pass

        db_ready.loc[db_ready.index.isin(review_indexes), "needs_manual_review"] = True

    if only_verified:
        db_ready = db_ready[
            (db_ready["source_verified"] == True)
            & (db_ready["review_status"].astype(str).str.lower().isin(["verified", "published"]))
            & (db_ready["needs_manual_review"] == False)
        ]

    return db_ready.reset_index(drop=True)


def calculate_metrics(standardized, rows_needing_review, database_ready, confidence_threshold):
    if rows_needing_review.empty:
        critical_issues = 0
        manual_review_items = 0
        warnings = 0
    else:
        critical_issues = int((rows_needing_review["Severity"] == "Critical Issue").sum())
        manual_review_items = int((rows_needing_review["Severity"] == "Manual Review Needed").sum())
        warnings = int((rows_needing_review["Severity"] == "Warning").sum())

    return {
        "rows_processed": len(standardized),
        "database_ready_rows": len(database_ready),
        "review_rows": len(rows_needing_review),
        "critical_issues": critical_issues,
        "manual_review_items": manual_review_items,
        "warnings": warnings,
        "source_verified_rows": int((standardized["source_verified"] == True).sum()),
        "low_confidence_rows": int((standardized["confidence_score"] < confidence_threshold).sum())
    }


def build_client_summary(metrics, confidence_threshold):
    return f"""
Clean0ps Document Standards Cleanup Summary

Rows Processed: {metrics["rows_processed"]:,}
Database-Ready Rows: {metrics["database_ready_rows"]:,}
Rows Needing Review: {metrics["review_rows"]:,}
Critical Issues: {metrics["critical_issues"]:,}
Manual Review Items: {metrics["manual_review_items"]:,}
Warnings: {metrics["warnings"]:,}
Source Verified Rows: {metrics["source_verified_rows"]:,}
Low Confidence Rows: {metrics["low_confidence_rows"]:,}
Confidence Threshold: {confidence_threshold:.2f}

Recommended Next Step:
Review all critical issues first, then manually verify low-confidence and unverified rows against the original PDF source before publishing the data to customers.
""".strip()


badge_row([
    ("PDF / LLM Output Cleanup", "info"),
    ("Source Verification Tracking", "success"),
    ("Database-Ready Export", "info"),
    ("Manual Review Workflow", "warning")
])

section_title("Workflow")

workflow_stepper(
    [
        "Load Extracted Data",
        "Map Fields",
        "Validate Source Records",
        "Review Issues",
        "Export Database-Ready Data"
    ],
    active_index=0
)

section_title("What This Page Checks")

c1, c2, c3 = st.columns(3)

with c1:
    feature_card(
        "Required Source Fields",
        "Checks document name, page number, section ID, and requirement text so extracted records stay tied to the PDF source."
    )

with c2:
    feature_card(
        "Accuracy Review Flags",
        "Flags low-confidence rows, unverified source records, duplicate section IDs, missing extracted values, and invalid statuses."
    )

with c3:
    feature_card(
        "Database-Ready Output",
        "Creates a clean export for publishing workflows while separating rows that still need manual review."
    )


section_title("Demo Dataset")

with st.expander("Download demo standards extraction dataset", expanded=False):
    demo_df = make_demo_standards_data()

    st.download_button(
        label="📥 Download demo_document_standards_extraction.csv",
        data=dataframe_to_csv_bytes(demo_df),
        file_name="demo_document_standards_extraction.csv",
        mime="text/csv"
    )


section_title("Load Extracted PDF / LLM Data")

data_source = st.radio(
    "Choose data source",
    ["Use built-in demo data", "Upload CSV / Excel file"],
    horizontal=True
)

try:
    if data_source == "Use built-in demo data":
        source_df = make_demo_standards_data()
        source_name = "demo_document_standards_extraction.csv"
    else:
        uploaded_file = st.file_uploader(
            "Upload extracted PDF / LLM output",
            type=["csv", "xlsx"]
        )

        if uploaded_file is None:
            empty_state(
                "No file uploaded yet",
                "Upload a CSV or Excel file containing structured rows extracted from PDFs, standards, OCR, or LLM ingestion.",)
            st.stop()

        source_df = read_uploaded_file(
            uploaded_file,
            normalize=True
        )

        source_name = uploaded_file.name

    file_size_info = check_file_size(source_df)

    for warning in file_size_info["warnings"]:
        st.warning(warning)

    section_title("Field Mapping")

    section_callout(
        "Map extracted columns to the Clean0ps standards schema.",
        "Auto-detection will guess common names, but you can override any field. The required fields are document name, page number, section ID, and requirement text.",
        kind="info"
    )

    mapping = {}

    map_cols = st.columns(3)
    field_items = list(FIELD_DEFINITIONS.items())

    for index, (field_name, definition) in enumerate(field_items):
        options = ["None"] + source_df.columns.tolist()
        default_col = get_default_column(source_df, definition["candidates"])
        default_index = options.index(default_col) if default_col in options else 0

        label = definition["label"]

        if definition["required"]:
            label = f"{label} *"

        with map_cols[index % 3]:
            mapping[field_name] = st.selectbox(
                label,
                options,
                index=default_index,
                key=f"doc_map_{field_name}"
            )

    with st.expander("Preview source data", expanded=False):
        st.dataframe(
            source_df.head(50),
            use_container_width=True
        )

    section_title("Validation Settings")

    s1, s2 = st.columns(2)

    with s1:
        confidence_threshold = st.slider(
            "Low confidence threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05
        )

    with s2:
        only_verified_export = st.checkbox(
            "Database-ready export should include only verified rows",
            value=False
        )

    standardized = build_standardized_table(
        source_df,
        mapping
    )

    rows_needing_review = build_rows_needing_review(
        standardized,
        confidence_threshold
    )

    validation_summary = build_validation_summary(
        rows_needing_review
    )

    database_ready = build_database_ready_table(
        standardized,
        rows_needing_review,
        only_verified_export
    )

    metrics = calculate_metrics(
        standardized,
        rows_needing_review,
        database_ready,
        confidence_threshold
    )

    client_summary = build_client_summary(
        metrics,
        confidence_threshold
    )

    section_title("Cleanup Results")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Rows Processed", f"{metrics['rows_processed']:,}")

    with m2:
        st.metric("DB-Ready Rows", f"{metrics['database_ready_rows']:,}")

    with m3:
        st.metric("Rows Needing Review", f"{metrics['review_rows']:,}")

    with m4:
        st.metric("Critical Issues", f"{metrics['critical_issues']:,}")

    with m5:
        st.metric("Source Verified", f"{metrics['source_verified_rows']:,}")

    if metrics["critical_issues"] > 0:
        section_callout(
            "Critical issues found",
            "Fix missing required fields or invalid page numbers before publishing this data.",
            kind="danger"
        )
    elif metrics["review_rows"] > 0:
        section_callout(
            "Manual review needed",
            "Some rows need source verification or confidence review before publishing.",
            kind="warning"
        )
    else:
        section_callout(
            "No major issues found",
            "The extracted data passed the current document standards cleanup checks.",
            kind="success"
        )

    section_title("Document Cleanup Review")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Standardized Data",
        "Rows Needing Review",
        "Validation Summary",
        "Database-Ready Export",
        "Client Summary"
    ])

    with tab1:
        st.dataframe(
            standardized.head(500),
            use_container_width=True
        )

    with tab2:
        if rows_needing_review.empty:
            empty_state(
                "No rows need review",
                "No row-level issues were found using the current validation settings.",)
        else:
            st.dataframe(
                rows_needing_review.head(1000),
                use_container_width=True
            )

    with tab3:
        st.dataframe(
            validation_summary,
            use_container_width=True
        )

    with tab4:
        st.dataframe(
            database_ready.head(1000),
            use_container_width=True
        )

    with tab5:
        st.text_area(
            "Client-ready cleanup summary",
            client_summary,
            height=320
        )

    section_title("Download Document Cleanup Deliverables")

    download_card(
        "Document Cleanup Package",
        "Includes standardized data, database-ready records, rows needing review, validation summary, and client summary."
    )

    summary_report = pd.DataFrame([
        {"Metric": "Source File", "Value": source_name},
        {"Metric": "Rows Processed", "Value": metrics["rows_processed"]},
        {"Metric": "Database-Ready Rows", "Value": metrics["database_ready_rows"]},
        {"Metric": "Rows Needing Review", "Value": metrics["review_rows"]},
        {"Metric": "Critical Issues", "Value": metrics["critical_issues"]},
        {"Metric": "Manual Review Items", "Value": metrics["manual_review_items"]},
        {"Metric": "Warnings", "Value": metrics["warnings"]},
        {"Metric": "Source Verified Rows", "Value": metrics["source_verified_rows"]},
        {"Metric": "Low Confidence Rows", "Value": metrics["low_confidence_rows"]},
        {"Metric": "Confidence Threshold", "Value": confidence_threshold},
        {"Metric": "Only Verified Export", "Value": only_verified_export}
    ])

    excel_report = make_excel_bytes({
        "Summary": summary_report,
        "Standardized Data": standardized,
        "Rows Needing Review": rows_needing_review,
        "Validation Summary": validation_summary,
        "Database Ready": database_ready,
        "Client Summary": pd.DataFrame({"Summary": client_summary.splitlines()})
    })

    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="📥 Database-Ready CSV",
            data=dataframe_to_csv_bytes(database_ready),
            file_name="clean0ps_document_database_ready.csv",
            mime="text/csv"
        )

    with d2:
        st.download_button(
            label="📥 Rows Needing Review CSV",
            data=dataframe_to_csv_bytes(rows_needing_review),
            file_name="clean0ps_document_rows_needing_review.csv",
            mime="text/csv"
        )

    with d3:
        st.download_button(
            label="📥 Full Document Cleanup Report",
            data=excel_report,
            file_name="clean0ps_document_cleanup_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.download_button(
        label="📥 Client Summary TXT",
        data=text_to_bytes(client_summary),
        file_name="clean0ps_document_cleanup_summary.txt",
        mime="text/plain"
    )

except Exception as error:
    user_message, technical_message = get_friendly_error(error)

    section_title("Document Cleanup Error")

    st.error(user_message)

    if technical_message:
        with st.expander("Technical details", expanded=False):
            st.code(technical_message)

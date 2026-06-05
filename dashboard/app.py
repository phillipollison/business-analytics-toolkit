import streamlit as st

from clean0ps_ui import (
    apply_clean0ps_style,
    hero,
    section_title,
    feature_card,
    mini_card
)

st.set_page_config(
    page_title="Clean0ps",
    page_icon="🧹",
    layout="wide"
)

apply_clean0ps_style()

hero(
    title="🧹 Clean0ps",
    subtitle=(
        "A modern data cleaning and audit toolkit for messy CSV and Excel files. "
        "Clean0ps helps clean, organize, validate, audit, and export client-ready datasets "
        "for business, CRM, inventory, sports, and extracted data workflows."
    ),
    pill="DATA CLEANING · AUDIT REPORTS · CLIENT DELIVERABLES"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Primary Workflow",
        "Clean + Audit"
    )

with col2:
    st.metric(
        "Best For",
        "CSV / Excel"
    )

with col3:
    st.metric(
        "Deliverables",
        "5 Exports"
    )

section_title("What Clean0ps Does")

card1, card2, card3 = st.columns(3)

with card1:
    feature_card(
        "🧽 Clean Messy Files",
        (
            "Remove blank rows, exact duplicates, messy column names, extra spaces, "
            "inconsistent formatting, and common spreadsheet clutter."
        )
    )

with card2:
    feature_card(
        "📋 Validate Data Quality",
        (
            "Detect must-fix issues, manual review items, optional improvements, "
            "missing values, negative values, duplicate records, and risky fields."
        )
    )

with card3:
    feature_card(
        "📦 Export Client Files",
        (
            "Generate cleaned CSV files, cleaned Excel workbooks, review files, "
            "audit reports, CRM hitlists, and plain-English client summaries."
        )
    )

section_title("Workflow")

w1, w2, w3, w4, w5 = st.columns(5)

with w1:
    mini_card(
        "STEP 1",
        "Upload File"
    )

with w2:
    mini_card(
        "STEP 2",
        "Choose Template"
    )

with w3:
    mini_card(
        "STEP 3",
        "Clean + Organize"
    )

with w4:
    mini_card(
        "STEP 4",
        "Audit Issues"
    )

with w5:
    mini_card(
        "STEP 5",
        "Download Files"
    )

section_title("Cleaning Templates")

t1, t2, t3, t4 = st.columns(4)

with t1:
    feature_card(
        "Quick Spreadsheet Cleanup",
        "Clean simple Excel and CSV files for duplicates, blanks, spacing, sorting, and formatting."
    )

with t2:
    feature_card(
        "Business Sales Data",
        "Prepare sales, revenue, product, date, and reporting data for analysis or dashboards."
    )

with t3:
    feature_card(
        "Inventory / Product Data",
        "Clean SKU, product, barcode, stock, vendor, reorder, and product catalog files."
    )

with t4:
    feature_card(
        "Lead List / CRM Data",
        "Clean B2B lead lists, CRM exports, websites, contacts, and sales hitlists."
    )

t5, t6, t7, t8 = st.columns(4)

with t5:
    feature_card(
        "Sports Stats / Props",
        "Validate player stats, prop logs, hit-rate records, sports datasets, and impossible values."
    )

with t6:
    feature_card(
        "NBA Player Reference",
        "Clean NBA player master tables, IDs, names, teams, and reference data."
    )

with t7:
    feature_card(
        "PDF / LLM Extraction",
        "Clean messy extracted tables from PDFs, OCR tools, and AI-generated outputs."
    )

with t8:
    feature_card(
        "Custom Dataset",
        "Run universal cleaning and auditing when no predefined template fits perfectly."
    )

section_title("Client Deliverables")

d1, d2, d3, d4, d5 = st.columns(5)

with d1:
    mini_card(
        "EXPORT",
        "Cleaned CSV"
    )

with d2:
    mini_card(
        "EXPORT",
        "Cleaned Excel"
    )

with d3:
    mini_card(
        "EXPORT",
        "Review File"
    )

with d4:
    mini_card(
        "EXPORT",
        "Audit Report"
    )

with d5:
    mini_card(
        "EXPORT",
        "Client Summary"
    )

section_title("Current Modules")

m1, m2, m3, m4 = st.columns(4)

with m1:
    feature_card(
        "📦 Inventory Dashboard",
        "Review inventory files, stock levels, reorder points, product counts, and low-stock records."
    )

with m2:
    feature_card(
        "📋 Data Quality Dashboard",
        "Profile datasets for missing values, duplicates, empty columns, data types, and quality score."
    )

with m3:
    feature_card(
        "✅ Validation Engine",
        "Run rule-based checks for business, sports, and NBA player reference datasets."
    )

with m4:
    feature_card(
        "🧹 Template Cleaning Engine",
        "Clean, rename, organize, audit, export, and generate client-ready deliverables."
    )

section_title("Built For Real Client Work")

u1, u2, u3 = st.columns(3)

with u1:
    feature_card(
        "Upwork Data Cleaning Jobs",
        (
            "Designed around common client requests like removing duplicates, "
            "organizing columns, cleaning Excel files, and preparing final deliverables."
        )
    )

with u2:
    feature_card(
        "CRM / Lead List Projects",
        (
            "Supports website validation, contact cleanup, field selection, "
            "column renaming, and clean hitlist exports."
        )
    )

with u3:
    feature_card(
        "Portfolio + Interview Demos",
        (
            "Shows practical data cleaning, validation rules, UI design, "
            "export workflows, and client-focused thinking."
        )
    )

st.divider()

st.success(
    "Use the sidebar to open the Template Cleaning Engine and start cleaning a file."
)

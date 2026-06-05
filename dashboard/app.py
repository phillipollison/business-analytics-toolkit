import streamlit as st

from clean0ps_ui import (
    apply_clean0ps_style,
    hero,
    section_title,
    feature_card,
    mini_card,
    workflow_stepper,
    badge_row,
    section_callout,
    info_panel,
    download_card,
    privacy_notice
)


st.set_page_config(
    page_title="Clean0ps Home",
    page_icon="C",
    layout="wide"
)

apply_clean0ps_style()

hero(
    title="Clean0ps",
    subtitle=(
        "A production-minded data cleaning and analytics toolkit for messy CSV and Excel files. "
        "Clean files, audit data quality, validate document standards extractions, analyze inventory, "
        "build e-commerce reports, and export client-ready deliverables."
    ),
    pill="DATA CLEANING - VALIDATION - DOCUMENTS - INVENTORY - E-COMMERCE"
)

privacy_notice()

badge_row([
    ("CSV + Excel Ready", "success"),
    ("Client Exports", "info"),
    ("Data Quality Checks", "success"),
    ("Document Standards Cleanup", "warning"),
    ("Inventory + E-commerce Analytics", "info")
])

section_title("Start Here")

section_callout(
    title="Choose the workflow that matches the file or job.",
    text=(
        "Use Template Cleaning for messy files, Data Quality + Validation for audits, "
        "Document Standards Cleanup for PDF/LLM extraction review, Inventory for product and stock files, "
        "and E-commerce Analytics Lab for orders, customers, ads, sessions, products, and subscriptions."
    ),
    kind="info"
)

workflow_stepper(
    [
        "Upload Data",
        "Choose Workflow",
        "Clean / Validate",
        "Review Results",
        "Download Deliverables"
    ],
    active_index=0
)

start1, start2, start3, start4, start5 = st.columns(5)

with start1:
    mini_card("MAIN", "Clean Messy Files")

with start2:
    mini_card("AUDIT", "Validate Data")

with start3:
    mini_card("DOCS", "Verify Extractions")

with start4:
    mini_card("OPS", "Analyze Inventory")

with start5:
    mini_card("BI", "Model E-commerce")

section_title("Choose a Workflow")

col1, col2 = st.columns(2)

with col1:
    info_panel(
        "Template Cleaning Engine",
        (
            "Best for messy CSV and Excel files. Clean columns, remove blanks, remove duplicates, "
            "sort records, rename fields, generate review files, and export client-ready deliverables."
        )
    )

    st.page_link(
        "pages/4_Template Cleaning Engine.py",
        label="Open Template Cleaning Engine"
    )

with col2:
    info_panel(
        "Data Quality + Validation",
        (
            "Best for auditing files before reporting or delivery. Detect missing values, duplicate rows, "
            "required-field problems, invalid dates, text issues, and records that need review."
        )
    )

    st.page_link(
        "pages/2_Data_Quality_Dashboard.py",
        label="Open Data Quality + Validation"
    )

col3, col4 = st.columns(2)

with col3:
    info_panel(
        "Document Standards Cleanup",
        (
            "Best for PDF/LLM extraction cleanup, standards records, page and section validation, "
            "source verification tracking, confidence review, and database-ready exports."
        )
    )

    st.page_link(
        "pages/6_Document_Standards_Cleanup_Lab.py",
        label="Open Document Standards Cleanup"
    )

with col4:
    info_panel(
        "Inventory Dashboard",
        (
            "Best for product catalogs, stock reports, SKU files, reorder planning, low-stock review, "
            "out-of-stock risk, overstock risk, and inventory value reporting."
        )
    )

    st.page_link(
        "pages/1_Inventory_Dashboard.py",
        label="Open Inventory Dashboard"
    )

col5, col6 = st.columns(2)

with col5:
    info_panel(
        "E-commerce Analytics Lab",
        (
            "Best for e-commerce BI work. Assign source files, map columns, build fact and dimension tables, "
            "validate relationships, calculate KPIs, and export dashboard-ready reports."
        )
    )

    st.page_link(
        "pages/5_Ecommerce_Analytics_Lab.py",
        label="Open E-commerce Analytics Lab"
    )

with col6:
    info_panel(
        "Production Readiness",
        (
            "The app includes shared backend helpers, shared UI components, error logging, health checks, "
            "privacy notices, reset controls, demo datasets, and export workflows."
        )
    )

section_title("What Clean0ps Can Produce")

d1, d2, d3 = st.columns(3)

with d1:
    download_card(
        "Cleaning Deliverables",
        (
            "Cleaned CSV files, Excel cleaning reports, rows needing review, client summary text files, "
            "and full deliverables ZIP exports."
        )
    )

with d2:
    download_card(
        "Audit + Document Deliverables",
        (
            "Data quality audit workbooks, missing value reports, duplicate reviews, document extraction review files, "
            "database-ready exports, validation summaries, and action plans."
        )
    )

with d3:
    download_card(
        "Analytics Deliverables",
        (
            "Inventory audit workbooks, reorder CSVs, e-commerce KPI reports, modeled table ZIPs, "
            "and BI-ready dashboard exports."
        )
    )

section_title("Best Use Cases")

use1, use2, use3 = st.columns(3)

with use1:
    feature_card(
        "Freelance Data Cleanup",
        (
            "Clean messy spreadsheets, CRM files, lead lists, inventory sheets, extracted tables, and client exports."
        )
    )

with use2:
    feature_card(
        "PDF / LLM Extraction Review",
        (
            "Validate extracted standards data, page numbers, section IDs, confidence scores, source verification, "
            "and records needing manual review."
        )
    )

with use3:
    feature_card(
        "Business Analytics Reporting",
        (
            "Model raw e-commerce files into reporting tables and calculate revenue, AOV, ROAS, CAC, LTV, churn, "
            "MRR, product performance, and customer value."
        )
    )

section_title("Recommended Starting Point")

section_callout(
    title="Most users should start with Template Cleaning or Document Standards Cleanup.",
    text=(
        "Start with Template Cleaning when the file is generally messy. Start with Document Standards Cleanup "
        "when the data came from a PDF, OCR, LLM, or standards ingestion workflow."
    ),
    kind="success"
)

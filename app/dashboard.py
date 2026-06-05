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
    download_card
)


st.set_page_config(
    page_title="Clean0ps Home",
    page_icon="🧹",
    layout="wide"
)

apply_clean0ps_style()

hero(
    title="🧹 Clean0ps",
    subtitle=(
        "A modern data cleaning and analytics toolkit for messy CSV and Excel files. "
        "Clean files, audit data quality, analyze inventory, build e-commerce reports, "
        "and export client-ready deliverables."
    ),
    pill="DATA CLEANING · VALIDATION · INVENTORY · E-COMMERCE REPORTING"
)


# --------------------------------------------------
# Status Badges
# --------------------------------------------------

badge_row([
    ("CSV + Excel Ready", "success"),
    ("Client Exports", "info"),
    ("Data Quality Checks", "success"),
    ("Inventory + E-commerce Analytics", "info")
])


# --------------------------------------------------
# Start Here
# --------------------------------------------------

section_title("Start Here")

section_callout(
    title="Choose the workflow that matches the file or job.",
    text=(
        "Use Template Cleaning for general messy files, Data Quality + Validation for audits, "
        "Inventory Dashboard for product and stock files, and E-commerce Analytics Lab for "
        "orders, customers, ads, sessions, products, and subscriptions."
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

start1, start2, start3, start4 = st.columns(4)

with start1:
    mini_card("MAIN WORKFLOW", "Clean Messy Files")

with start2:
    mini_card("AUDIT WORKFLOW", "Validate Data Quality")

with start3:
    mini_card("OPERATIONS", "Analyze Inventory")

with start4:
    mini_card("BI WORKFLOW", "Model E-commerce KPIs")


# --------------------------------------------------
# Workflow Selector
# --------------------------------------------------

section_title("Choose a Workflow")

col1, col2 = st.columns(2)

with col1:
    info_panel(
        "🧹 Template Cleaning Engine",
        (
            "Best for messy CSV and Excel files. Clean columns, remove blanks, remove duplicates, "
            "sort records, rename fields, generate review files, and export client-ready deliverables."
        )
    )

    st.page_link(
        "pages/4_Template Cleaning Engine.py",
        label="Open Template Cleaning Engine",
        icon="🧹"
    )

with col2:
    info_panel(
        "📋 Data Quality + Validation",
        (
            "Best for auditing files before reporting or delivery. Detect missing values, duplicate rows, "
            "required-field problems, invalid dates, text issues, and records that need review."
        )
    )

    st.page_link(
        "pages/2_Data_Quality_Dashboard.py",
        label="Open Data Quality + Validation",
        icon="📋"
    )

col3, col4 = st.columns(2)

with col3:
    info_panel(
        "📦 Inventory Dashboard",
        (
            "Best for product catalogs, stock reports, SKU files, reorder planning, low-stock review, "
            "out-of-stock risk, overstock risk, and inventory value reporting."
        )
    )

    st.page_link(
        "pages/1_Inventory_Dashboard.py",
        label="Open Inventory Dashboard",
        icon="📦"
    )

with col4:
    info_panel(
        "🛒 E-commerce Analytics Lab",
        (
            "Best for e-commerce BI work. Assign source files, map columns, build fact and dimension tables, "
            "validate relationships, calculate KPIs, and export dashboard-ready reports."
        )
    )

    st.page_link(
        "pages/5_Ecommerce_Analytics_Lab.py",
        label="Open E-commerce Analytics Lab",
        icon="🛒"
    )


# --------------------------------------------------
# Deliverables
# --------------------------------------------------

section_title("What Clean0ps Can Produce")

d1, d2, d3 = st.columns(3)

with d1:
    download_card(
        "Cleaning Deliverables",
        (
            "Cleaned CSV files, Excel cleaning reports, rows needing review, "
            "client summary text files, and full deliverables ZIP exports."
        )
    )

with d2:
    download_card(
        "Audit Deliverables",
        (
            "Data quality audit workbooks, missing value reports, duplicate record reviews, "
            "column summaries, issue reports, and action plans."
        )
    )

with d3:
    download_card(
        "Analytics Deliverables",
        (
            "Inventory audit workbooks, reorder report CSVs, e-commerce KPI reports, "
            "modeled table ZIPs, and BI-ready dashboard exports."
        )
    )


# --------------------------------------------------
# Best Use Cases
# --------------------------------------------------

section_title("Best Use Cases")

use1, use2, use3 = st.columns(3)

with use1:
    feature_card(
        "Freelance Data Cleanup",
        (
            "Clean messy spreadsheets, CRM files, lead lists, inventory sheets, and extracted tables. "
            "Useful for client jobs where the final file needs to be organized and easy to review."
        )
    )

with use2:
    feature_card(
        "Business Operations Review",
        (
            "Analyze inventory health, product risk, missing values, duplicate records, and files that need cleanup "
            "before they are used for reporting or decision-making."
        )
    )

with use3:
    feature_card(
        "E-commerce Reporting",
        (
            "Model raw e-commerce files into reporting tables and calculate metrics like revenue, AOV, ROAS, CAC, "
            "LTV, conversion rate, churn, MRR, and product performance."
        )
    )


# --------------------------------------------------
# Recommended Starting Point
# --------------------------------------------------

section_title("Recommended Starting Point")

section_callout(
    title="Most users should start with the Template Cleaning Engine.",
    text=(
        "Start there when the file is messy and needs to be cleaned. Use Data Quality + Validation "
        "when the file needs an audit. Use Inventory when the file has product or stock data. "
        "Use E-commerce Analytics Lab when you have multiple e-commerce exports and need dashboard-ready reporting."
    ),
    kind="success"
)
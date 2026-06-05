import re

import pandas as pd
import streamlit as st

from clean0ps_ui import (
    apply_clean0ps_style,
    privacy_notice,
    reset_workflow_button,
    hero,
    section_title,
    feature_card,
    mini_card
)

from clean0ps_core import (
    read_uploaded_file,
    check_file_size,
    clean_column_name,
    pretty_column_name,
    normalize_columns,
    trim_text_columns,
    remove_exact_duplicates,
    standardize_date_columns,
    missing_mask,
    get_missing_count,
    get_duplicate_row_count,
    build_column_summary,
    build_basic_quality_issues,
    calculate_quality_score,
    dataframe_to_csv_bytes,
    text_to_bytes,
    make_excel_bytes,
    make_zip_bytes,
    get_friendly_error
)


st.set_page_config(
    page_title="Template Cleaning Engine",
    page_icon="🧹",
    layout="wide"
)

apply_clean0ps_style()
privacy_notice()
reset_workflow_button()

hero(
    title="🧹 Template Cleaning Engine",
    subtitle=(
        "Clean messy CSV and Excel files, organize columns, sort records, rename fields, "
        "separate safe fixes from records needing review, and export client-ready deliverables."
    ),
    pill="DATA CLEANING · ORGANIZATION · AUDIT REPORTS · CLIENT EXPORTS"
)


# --------------------------------------------------
# Demo Data
# --------------------------------------------------

def make_demo_messy_data():
    return pd.DataFrame({
        "Customer Name": [
            "  James Carter ",
            "Mia Lopez",
            "Noah Smith",
            "Mia Lopez",
            "",
            "Ava Johnson",
            "Liam Brown",
            "Olivia Davis",
            "Ethan Wilson",
            None
        ],
        "Email Address": [
            " JAMES.CARTER@EMAIL.COM ",
            "mia.lopez@email.com",
            "bad-email",
            "mia.lopez@email.com",
            "",
            "ava.johnson@email.com",
            "liam.brown@email.com",
            None,
            "ethan.wilson@email.com",
            None
        ],
        "Phone Number": [
            "555-111-2222",
            "(555) 222-3333",
            "5553334444",
            "(555) 222-3333",
            "",
            "555.444.5555",
            "1-555-555-6666",
            None,
            "5557778888",
            None
        ],
        "Order Date": [
            "2026-01-05",
            "1/12/2026",
            "bad date",
            "1/12/2026",
            "",
            "2026-02-01",
            "2026-02-12",
            "2026-03-03",
            "2026-03-15",
            None
        ],
        "Product Category": [
            " Drinks ",
            "Snacks",
            "Supplements",
            "Snacks",
            "",
            "Drinks",
            "Snacks",
            "Bundles",
            "Supplements",
            None
        ],
        "Quantity": [
            2,
            1,
            -3,
            1,
            None,
            5,
            4,
            2,
            1,
            None
        ],
        "Revenue": [
            29.99,
            14.50,
            39.99,
            14.50,
            None,
            99.99,
            25.00,
            59.99,
            19.99,
            None
        ],
        "Notes": [
            "  new customer  ",
            "repeat customer",
            "needs review",
            "repeat customer",
            "",
            "large order",
            "  promo used",
            "missing email",
            "clean",
            None
        ]
    })


# --------------------------------------------------
# Template Setup
# --------------------------------------------------

TEMPLATES = {
    "Quick Spreadsheet Cleanup": {
        "description": (
            "Best for general CSV or Excel cleanup jobs: blank rows, duplicate rows, messy columns, "
            "extra spaces, sorting, and formatting issues."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": True,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": False,
            "standardize_phones": False
        }
    },
    "CRM / Lead List Cleanup": {
        "description": (
            "Best for customer lists, lead lists, email lists, outreach files, and contact exports."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": True,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": True,
            "standardize_phones": True
        }
    },
    "Inventory / Product Cleanup": {
        "description": (
            "Best for product catalogs, SKU lists, stock files, inventory exports, and vendor product sheets."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": True,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": False,
            "standardize_phones": False
        }
    },
    "E-commerce Export Cleanup": {
        "description": (
            "Best for orders, customers, products, ad spend, transactions, and subscription exports."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": True,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": True,
            "standardize_phones": False
        }
    },
    "Sports / Stats Cleanup": {
        "description": (
            "Best for player logs, prop tracking files, game stats, hit-rate sheets, and betting analytics exports."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": True,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": False,
            "standardize_phones": False
        }
    },
    "Extracted PDF / AI Output Cleanup": {
        "description": (
            "Best for messy extracted tables from PDFs, OCR, AI outputs, reports, and pasted exports."
        ),
        "safe_defaults": {
            "remove_blank_rows": True,
            "remove_duplicates": False,
            "drop_empty_columns": True,
            "trim_text": True,
            "standardize_dates": True,
            "standardize_emails": False,
            "standardize_phones": False
        }
    }
}


def get_template_defaults(template_name):
    return TEMPLATES[template_name]["safe_defaults"]


def infer_email_columns(df):
    return [
        col for col in df.columns
        if "email" in col.lower()
    ]


def infer_phone_columns(df):
    return [
        col for col in df.columns
        if any(word in col.lower() for word in ["phone", "mobile", "cell", "contact_number"])
    ]


def infer_date_columns(df):
    return [
        col for col in df.columns
        if any(word in col.lower() for word in ["date", "created", "updated", "sold", "order", "start", "cancel"])
    ]


def infer_numeric_review_columns(df):
    keywords = [
        "price",
        "cost",
        "amount",
        "revenue",
        "sales",
        "quantity",
        "qty",
        "units",
        "stock",
        "spend",
        "clicks",
        "impressions",
        "orders",
        "total"
    ]

    columns = []

    for col in df.columns:
        if any(word in col.lower() for word in keywords):
            columns.append(col)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    return sorted(set(columns + numeric_cols))


def infer_possible_key_columns(df):
    keywords = [
        "id",
        "sku",
        "email",
        "order_id",
        "customer_id",
        "product_id",
        "barcode",
        "upc"
    ]

    return [
        col for col in df.columns
        if any(word in col.lower() for word in keywords)
    ]


# --------------------------------------------------
# Cleaning Helpers
# --------------------------------------------------

def standardize_email_value(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip().lower()

    if text in ["", "nan", "none", "null", "n/a", "na"]:
        return pd.NA

    return text


def standardize_email_columns(df, email_columns):
    cleaned = df.copy()

    for col in email_columns:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].apply(standardize_email_value)

    return cleaned


def standardize_phone_value(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()

    if text.lower() in ["", "nan", "none", "null", "n/a", "na"]:
        return pd.NA

    digits = re.sub(r"\D", "", text)

    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"

    if len(digits) == 11 and digits.startswith("1"):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"

    if digits:
        return digits

    return text


def standardize_phone_columns(df, phone_columns):
    cleaned = df.copy()

    for col in phone_columns:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].apply(standardize_phone_value)

    return cleaned


def drop_completely_empty_columns(df):
    cleaned = df.copy()
    columns_to_drop = []

    for col in cleaned.columns:
        if get_missing_count(cleaned[col]) == len(cleaned):
            columns_to_drop.append(col)

    cleaned = cleaned.drop(columns=columns_to_drop)

    return cleaned, columns_to_drop


def remove_completely_blank_rows(df):
    cleaned = df.copy()
    temp = cleaned.replace(r"^\s*$", pd.NA, regex=True)
    blank_mask = temp.isna().all(axis=1)
    removed_count = int(blank_mask.sum())
    cleaned = cleaned[~blank_mask].reset_index(drop=True)

    return cleaned, removed_count


def apply_output_column_style(df, output_style):
    output_df = df.copy()

    if output_style == "Keep current column names":
        return output_df

    if output_style == "Clean snake_case":
        output_df.columns = [
            clean_column_name(col)
            for col in output_df.columns
        ]
        return output_df

    if output_style == "Client-friendly Title Case":
        output_df.columns = [
            pretty_column_name(col)
            for col in output_df.columns
        ]
        return output_df

    if output_style == "UPPERCASE":
        output_df.columns = [
            str(col).upper()
            for col in output_df.columns
        ]
        return output_df

    if output_style == "lowercase":
        output_df.columns = [
            str(col).lower()
            for col in output_df.columns
        ]
        return output_df

    return output_df


def move_columns_to_front(df, front_columns):
    if not front_columns:
        return df

    existing_front = [
        col for col in front_columns
        if col in df.columns
    ]

    remaining = [
        col for col in df.columns
        if col not in existing_front
    ]

    return df[existing_front + remaining]


def sort_dataframe(df, sort_column, ascending):
    if sort_column == "None" or sort_column not in df.columns:
        return df

    sorted_df = df.copy()

    return sorted_df.sort_values(
        by=sort_column,
        ascending=ascending,
        na_position="last"
    ).reset_index(drop=True)


def apply_manual_renames(df, rename_map):
    cleaned = df.copy()

    usable_map = {
        old_name: new_name.strip()
        for old_name, new_name in rename_map.items()
        if new_name and new_name.strip() and new_name.strip() != old_name
    }

    if usable_map:
        cleaned = cleaned.rename(columns=usable_map)

    return cleaned


def run_cleaning_pipeline(
    source_df,
    options,
    selected_email_columns,
    selected_phone_columns
):
    audit_rows = []
    safe_fix_rows = []

    cleaned = source_df.copy()

    starting_rows = len(cleaned)
    starting_columns = len(cleaned.columns)
    starting_duplicates = get_duplicate_row_count(cleaned)

    audit_rows.append({
        "Step": "Starting File",
        "Result": f"{starting_rows:,} rows and {starting_columns:,} columns loaded."
    })

    if options["remove_blank_rows"]:
        cleaned, removed_blank_rows = remove_completely_blank_rows(cleaned)

        safe_fix_rows.append({
            "Safe Fix": "Removed completely blank rows",
            "Count": removed_blank_rows
        })

        audit_rows.append({
            "Step": "Blank Row Cleanup",
            "Result": f"Removed {removed_blank_rows:,} completely blank rows."
        })

    if options["drop_empty_columns"]:
        cleaned, dropped_columns = drop_completely_empty_columns(cleaned)

        safe_fix_rows.append({
            "Safe Fix": "Dropped completely empty columns",
            "Count": len(dropped_columns)
        })

        audit_rows.append({
            "Step": "Empty Column Cleanup",
            "Result": f"Dropped {len(dropped_columns):,} completely empty columns."
        })

    if options["trim_text"]:
        cleaned = trim_text_columns(cleaned)

        safe_fix_rows.append({
            "Safe Fix": "Trimmed extra spaces from text fields",
            "Count": len(cleaned.select_dtypes(include="object").columns)
        })

        audit_rows.append({
            "Step": "Text Cleanup",
            "Result": "Trimmed leading and trailing spaces from text fields."
        })

    if options["standardize_dates"]:
        cleaned = standardize_date_columns(cleaned)

        safe_fix_rows.append({
            "Safe Fix": "Standardized date-like columns",
            "Count": len(infer_date_columns(cleaned))
        })

        audit_rows.append({
            "Step": "Date Cleanup",
            "Result": "Standardized date-like columns when possible."
        })

    if options["standardize_emails"] and selected_email_columns:
        cleaned = standardize_email_columns(
            cleaned,
            selected_email_columns
        )

        safe_fix_rows.append({
            "Safe Fix": "Standardized email fields",
            "Count": len(selected_email_columns)
        })

        audit_rows.append({
            "Step": "Email Cleanup",
            "Result": f"Standardized {len(selected_email_columns):,} email column(s)."
        })

    if options["standardize_phones"] and selected_phone_columns:
        cleaned = standardize_phone_columns(
            cleaned,
            selected_phone_columns
        )

        safe_fix_rows.append({
            "Safe Fix": "Standardized phone fields",
            "Count": len(selected_phone_columns)
        })

        audit_rows.append({
            "Step": "Phone Cleanup",
            "Result": f"Standardized {len(selected_phone_columns):,} phone column(s)."
        })

    if options["remove_duplicates"]:
        duplicates_before = get_duplicate_row_count(cleaned)
        cleaned = remove_exact_duplicates(cleaned)
        duplicates_removed = duplicates_before - get_duplicate_row_count(cleaned)

        safe_fix_rows.append({
            "Safe Fix": "Removed exact duplicate rows",
            "Count": duplicates_removed
        })

        audit_rows.append({
            "Step": "Duplicate Cleanup",
            "Result": f"Removed {duplicates_removed:,} exact duplicate rows."
        })

    ending_rows = len(cleaned)
    ending_columns = len(cleaned.columns)

    audit_rows.append({
        "Step": "Final Cleaned File",
        "Result": f"{ending_rows:,} rows and {ending_columns:,} columns ready for review/export."
    })

    audit_rows.append({
        "Step": "Starting Duplicate Rows",
        "Result": f"{starting_duplicates:,} exact duplicate rows were found before cleaning."
    })

    return (
        cleaned.reset_index(drop=True),
        pd.DataFrame(audit_rows),
        pd.DataFrame(safe_fix_rows)
    )


# --------------------------------------------------
# Review / Validation Helpers
# --------------------------------------------------

def is_valid_email(value):
    if pd.isna(value):
        return True

    text = str(value).strip()

    if text == "" or text.lower() in ["nan", "none", "null", "n/a", "na"]:
        return True

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, text))


def build_rows_needing_review(
    df,
    required_columns,
    duplicate_key_columns,
    email_columns,
    date_columns,
    numeric_nonnegative_columns
):
    rows = []

    def add_review(row_index, severity, issue, field, value, recommendation):
        rows.append({
            "Row Number": int(row_index) + 2,
            "Severity": severity,
            "Issue": issue,
            "Field": field,
            "Value": "" if pd.isna(value) else str(value),
            "Recommendation": recommendation
        })

    for col in required_columns:
        if col not in df.columns:
            rows.append({
                "Row Number": "",
                "Severity": "Critical Issue",
                "Issue": "Missing Required Column",
                "Field": col,
                "Value": "",
                "Recommendation": "Add this required column or confirm it is not needed."
            })
            continue

        missing_values = missing_mask(df[col])

        for index in df[missing_values].index:
            add_review(
                index,
                "Critical Issue",
                "Missing Required Value",
                col,
                df.loc[index, col],
                "Fill this required value or remove the record if it cannot be completed."
            )

    valid_duplicate_cols = [
        col for col in duplicate_key_columns
        if col in df.columns
    ]

    if valid_duplicate_cols:
        duplicate_mask = df.duplicated(
            subset=valid_duplicate_cols,
            keep=False
        )

        duplicate_df = df[duplicate_mask]

        for index, row in duplicate_df.iterrows():
            key_value = " | ".join(
                str(row[col])
                for col in valid_duplicate_cols
            )

            add_review(
                index,
                "Manual Review Needed",
                "Duplicate Key Match",
                ", ".join(valid_duplicate_cols),
                key_value,
                "Review whether this is a true duplicate or a legitimate repeated value."
            )

    for col in email_columns:
        if col not in df.columns:
            continue

        for index, value in df[col].items():
            if not is_valid_email(value):
                add_review(
                    index,
                    "Manual Review Needed",
                    "Invalid Email Format",
                    col,
                    value,
                    "Correct the email address or leave blank if unavailable."
                )

    for col in date_columns:
        if col not in df.columns:
            continue

        parsed = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        non_missing = ~missing_mask(df[col])
        invalid_mask = non_missing & parsed.isna()

        for index in df[invalid_mask].index:
            add_review(
                index,
                "Warning",
                "Invalid Date Format",
                col,
                df.loc[index, col],
                "Standardize this date value or confirm it is not a date."
            )

    for col in numeric_nonnegative_columns:
        if col not in df.columns:
            continue

        numeric_values = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        non_missing = ~missing_mask(df[col])
        invalid_numeric = non_missing & numeric_values.isna()
        negative_values = numeric_values < 0

        for index in df[invalid_numeric].index:
            add_review(
                index,
                "Manual Review Needed",
                "Non-Numeric Value",
                col,
                df.loc[index, col],
                "Correct this value or move it to a notes field."
            )

        for index in df[negative_values].index:
            add_review(
                index,
                "Manual Review Needed",
                "Negative Numeric Value",
                col,
                df.loc[index, col],
                "Confirm whether this negative value is valid."
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


def build_review_summary(review_df):
    if review_df.empty:
        return pd.DataFrame([
            {
                "Review Category": "Ready",
                "Count": 0,
                "Meaning": "No records require manual review based on selected rules."
            }
        ])

    return (
        review_df
        .groupby(["Severity", "Issue"], dropna=False)
        .size()
        .reset_index(name="Count")
        .rename(columns={
            "Severity": "Review Category",
            "Issue": "Issue Type"
        })
        .sort_values("Count", ascending=False)
    )


def build_client_summary(
    source_name,
    cleaned_df,
    safe_fixes,
    rows_needing_review,
    quality_score
):
    review_count = len(rows_needing_review)

    safe_fix_lines = []

    if safe_fixes.empty:
        safe_fix_lines.append("- No safe fixes were applied.")
    else:
        for _, row in safe_fixes.iterrows():
            safe_fix_lines.append(f"- {row['Safe Fix']}: {row['Count']}")

    if review_count == 0:
        review_text = "No records require manual review based on the selected checks."
    else:
        review_text = f"{review_count:,} row-level review item(s) were found and should be checked before final delivery."

    summary = f"""
Clean0ps Client Cleaning Summary

Source File:
{source_name}

Final Dataset:
Rows: {len(cleaned_df):,}
Columns: {len(cleaned_df.columns):,}
Quality Score: {quality_score}%

Safe Fixes Applied:
{chr(10).join(safe_fix_lines)}

Records Requiring Review:
{review_text}

Recommended Next Step:
Review the rows needing review file if any issues were found, then use the cleaned CSV or Excel workbook as the client-ready deliverable.
"""

    return summary.strip()


# --------------------------------------------------
# Page Intro
# --------------------------------------------------

section_title("Cleaning Workflow")

w1, w2, w3, w4, w5 = st.columns(5)

with w1:
    mini_card("STEP 1", "Upload File")

with w2:
    mini_card("STEP 2", "Choose Template")

with w3:
    mini_card("STEP 3", "Clean + Organize")

with w4:
    mini_card("STEP 4", "Audit Issues")

with w5:
    mini_card("STEP 5", "Download Files")


section_title("Cleaning Templates")

template_cols = st.columns(3)

template_names = list(TEMPLATES.keys())

for index, template_name in enumerate(template_names[:3]):
    with template_cols[index]:
        feature_card(
            template_name,
            TEMPLATES[template_name]["description"]
        )

template_cols_2 = st.columns(3)

for index, template_name in enumerate(template_names[3:]):
    with template_cols_2[index]:
        feature_card(
            template_name,
            TEMPLATES[template_name]["description"]
        )


# --------------------------------------------------
# Demo Download
# --------------------------------------------------

section_title("Demo Messy Dataset")

with st.expander("Download demo messy dataset", expanded=False):
    demo_df = make_demo_messy_data()

    st.download_button(
        label="📥 Download demo_messy_data.csv",
        data=dataframe_to_csv_bytes(demo_df),
        file_name="demo_messy_data.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# Load Data
# --------------------------------------------------

section_title("Load Data")

data_source = st.radio(
    "Choose data source",
    ["Use built-in demo data", "Upload CSV / Excel file"],
    horizontal=True
)

try:
    if data_source == "Use built-in demo data":
        source_df = normalize_columns(make_demo_messy_data())
        source_name = "demo_messy_data.csv"
    else:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=["csv", "xlsx"]
        )

        if uploaded_file is None:
            st.info("Upload a CSV or Excel file to begin cleaning.")
            st.stop()

        source_df = read_uploaded_file(
            uploaded_file,
            normalize=True
        )

        source_name = uploaded_file.name

    file_size_info = check_file_size(source_df)

    for warning in file_size_info["warnings"]:
        st.warning(warning)

    # --------------------------------------------------
    # Template + Options
    # --------------------------------------------------

    section_title("Choose Cleaning Template")

    selected_template = st.selectbox(
        "Cleaning template",
        template_names
    )

    st.info(TEMPLATES[selected_template]["description"])

    template_defaults = get_template_defaults(selected_template)
    template_key = clean_column_name(selected_template)

    section_title("Safe Cleaning Options")

    with st.expander("Safe cleaning options", expanded=True):
        option_cols = st.columns(2)

        with option_cols[0]:
            remove_blank_rows = st.checkbox(
                "Remove completely blank rows",
                value=template_defaults["remove_blank_rows"],
                key=f"{template_key}_remove_blank_rows"
            )

            remove_duplicates = st.checkbox(
                "Remove exact duplicate rows",
                value=template_defaults["remove_duplicates"],
                key=f"{template_key}_remove_duplicates"
            )

            drop_empty_columns = st.checkbox(
                "Drop completely empty columns",
                value=template_defaults["drop_empty_columns"],
                key=f"{template_key}_drop_empty_columns"
            )

            trim_text = st.checkbox(
                "Trim extra spaces from text fields",
                value=template_defaults["trim_text"],
                key=f"{template_key}_trim_text"
            )

        with option_cols[1]:
            standardize_dates = st.checkbox(
                "Standardize date columns when possible",
                value=template_defaults["standardize_dates"],
                key=f"{template_key}_standardize_dates"
            )

            standardize_emails = st.checkbox(
                "Standardize email fields",
                value=template_defaults["standardize_emails"],
                key=f"{template_key}_standardize_emails"
            )

            standardize_phones = st.checkbox(
                "Standardize phone fields",
                value=template_defaults["standardize_phones"],
                key=f"{template_key}_standardize_phones"
            )

    email_defaults = infer_email_columns(source_df)
    phone_defaults = infer_phone_columns(source_df)

    with st.expander("Email and phone columns", expanded=False):
        selected_email_columns = st.multiselect(
            "Email columns",
            source_df.columns.tolist(),
            default=email_defaults
        )

        selected_phone_columns = st.multiselect(
            "Phone columns",
            source_df.columns.tolist(),
            default=phone_defaults
        )

    cleaning_options = {
        "remove_blank_rows": remove_blank_rows,
        "remove_duplicates": remove_duplicates,
        "drop_empty_columns": drop_empty_columns,
        "trim_text": trim_text,
        "standardize_dates": standardize_dates,
        "standardize_emails": standardize_emails,
        "standardize_phones": standardize_phones
    }

    cleaned_df, cleaning_audit, safe_fixes = run_cleaning_pipeline(
        source_df,
        cleaning_options,
        selected_email_columns,
        selected_phone_columns
    )

    # --------------------------------------------------
    # Organize + Rename
    # --------------------------------------------------

    section_title("Organize and Format Output")

    with st.expander("Sorting and column organization", expanded=True):
        organize_cols = st.columns(3)

        with organize_cols[0]:
            sort_column = st.selectbox(
                "Sort rows by",
                ["None"] + cleaned_df.columns.tolist()
            )

        with organize_cols[1]:
            sort_order = st.selectbox(
                "Sort order",
                ["Ascending", "Descending"]
            )

        with organize_cols[2]:
            output_column_style = st.selectbox(
                "Output column style",
                [
                    "Client-friendly Title Case",
                    "Keep current column names",
                    "Clean snake_case",
                    "UPPERCASE",
                    "lowercase"
                ]
            )

        alphabetize_columns = st.checkbox(
            "Alphabetize columns",
            value=False
        )

        front_columns = st.multiselect(
            "Move selected columns to the front",
            cleaned_df.columns.tolist()
        )

    organized_df = cleaned_df.copy()

    if alphabetize_columns:
        organized_df = organized_df[
            sorted(organized_df.columns.tolist())
        ]

    organized_df = move_columns_to_front(
        organized_df,
        front_columns
    )

    organized_df = sort_dataframe(
        organized_df,
        sort_column,
        sort_order == "Ascending"
    )

    with st.expander("Rename selected columns", expanded=False):
        st.write("Select columns you want to rename. Leave blank to keep the current name.")

        columns_to_rename = st.multiselect(
            "Columns to rename",
            organized_df.columns.tolist()
        )

        rename_map = {}

        rename_cols = st.columns(2)

        for index, col in enumerate(columns_to_rename):
            with rename_cols[index % 2]:
                rename_map[col] = st.text_input(
                    f"Rename `{col}` to",
                    value=pretty_column_name(col),
                    key=f"rename_{clean_column_name(col)}"
                )

    renamed_df = apply_manual_renames(
        organized_df,
        rename_map if "rename_map" in locals() else {}
    )

    final_df = apply_output_column_style(
        renamed_df,
        output_column_style
    )

    # --------------------------------------------------
    # Validation / Review
    # --------------------------------------------------

    section_title("Review Rules")

    with st.expander("Rows needing review settings", expanded=True):
        default_required = []
        default_duplicate_keys = infer_possible_key_columns(cleaned_df)[:1]
        default_email_review = infer_email_columns(cleaned_df)
        default_date_review = infer_date_columns(cleaned_df)
        default_numeric_review = infer_numeric_review_columns(cleaned_df)

        review_col1, review_col2 = st.columns(2)

        with review_col1:
            required_columns = st.multiselect(
                "Required columns",
                cleaned_df.columns.tolist(),
                default=default_required
            )

            duplicate_key_columns = st.multiselect(
                "Duplicate key columns",
                cleaned_df.columns.tolist(),
                default=default_duplicate_keys
            )

            email_review_columns = st.multiselect(
                "Email format check columns",
                cleaned_df.columns.tolist(),
                default=default_email_review
            )

        with review_col2:
            date_review_columns = st.multiselect(
                "Date format check columns",
                cleaned_df.columns.tolist(),
                default=default_date_review
            )

            numeric_nonnegative_columns = st.multiselect(
                "Numeric fields that should not be negative",
                cleaned_df.columns.tolist(),
                default=default_numeric_review
            )

    rows_needing_review = build_rows_needing_review(
        cleaned_df,
        required_columns,
        duplicate_key_columns,
        email_review_columns,
        date_review_columns,
        numeric_nonnegative_columns
    )

    review_summary = build_review_summary(rows_needing_review)
    column_summary = build_column_summary(cleaned_df)
    quality_issues = build_basic_quality_issues(cleaned_df)
    quality_score = calculate_quality_score(cleaned_df, quality_issues)

    client_summary = build_client_summary(
        source_name,
        final_df,
        safe_fixes,
        rows_needing_review,
        quality_score
    )

    # --------------------------------------------------
    # Overview Metrics
    # --------------------------------------------------

    section_title("Cleaning Results")

    before_rows = len(source_df)
    after_rows = len(cleaned_df)
    before_columns = len(source_df.columns)
    after_columns = len(cleaned_df.columns)
    duplicate_rows_after = get_duplicate_row_count(cleaned_df)

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Rows Before", f"{before_rows:,}")

    with m2:
        st.metric("Rows After", f"{after_rows:,}")

    with m3:
        st.metric("Columns", f"{after_columns:,}")

    with m4:
        st.metric("Rows Needing Review", f"{len(rows_needing_review):,}")

    with m5:
        st.metric("Quality Score", f"{quality_score}%")

    section_title("Safe Fixes vs Review Items")

    f1, f2, f3 = st.columns(3)

    with f1:
        feature_card(
            "Safe Fixes Applied",
            f"{int(safe_fixes['Count'].sum()) if not safe_fixes.empty else 0} automatic cleanup action(s) were applied."
        )

    with f2:
        feature_card(
            "Records Requiring Review",
            f"{len(rows_needing_review):,} row-level review item(s) were found."
        )

    with f3:
        feature_card(
            "Download Ready",
            "The cleaned and organized version can be downloaded as CSV, Excel, or a full deliverable ZIP."
        )

    # --------------------------------------------------
    # Tabs
    # --------------------------------------------------

    section_title("Cleaning Review")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Cleaned Preview",
        "Rows Needing Review",
        "Safe Fixes",
        "Column Summary",
        "Audit Log",
        "Client Summary"
    ])

    with tab1:
        st.dataframe(
            final_df.head(250),
            width="stretch"
        )

    with tab2:
        if rows_needing_review.empty:
            st.success("No records require manual review based on the selected rules.")
        else:
            st.dataframe(
                rows_needing_review.head(1000),
                width="stretch"
            )

        st.subheader("Review Summary")
        st.dataframe(
            review_summary,
            width="stretch"
        )

    with tab3:
        if safe_fixes.empty:
            st.info("No safe fixes were applied.")
        else:
            st.dataframe(
                safe_fixes,
                width="stretch"
            )

    with tab4:
        st.dataframe(
            column_summary,
            width="stretch"
        )

        st.subheader("Basic Quality Issues")
        if quality_issues.empty:
            st.success("No major quality issues found.")
        else:
            st.dataframe(
                quality_issues,
                width="stretch"
            )

    with tab5:
        st.dataframe(
            cleaning_audit,
            width="stretch"
        )

    with tab6:
        st.text_area(
            "Client-ready summary",
            client_summary,
            height=360
        )

    # --------------------------------------------------
    # Downloads
    # --------------------------------------------------

    section_title("Download Client Deliverables")

    summary_report = pd.DataFrame([
        {
            "Metric": "Source File",
            "Value": source_name
        },
        {
            "Metric": "Selected Template",
            "Value": selected_template
        },
        {
            "Metric": "Rows Before",
            "Value": before_rows
        },
        {
            "Metric": "Rows After",
            "Value": after_rows
        },
        {
            "Metric": "Columns Before",
            "Value": before_columns
        },
        {
            "Metric": "Columns After",
            "Value": after_columns
        },
        {
            "Metric": "Duplicate Rows After Cleaning",
            "Value": duplicate_rows_after
        },
        {
            "Metric": "Rows Needing Review",
            "Value": len(rows_needing_review)
        },
        {
            "Metric": "Quality Score",
            "Value": f"{quality_score}%"
        }
    ])

    excel_report = make_excel_bytes({
        "Cleaned Data": final_df,
        "Rows Needing Review": rows_needing_review,
        "Review Summary": review_summary,
        "Safe Fixes": safe_fixes,
        "Column Summary": column_summary,
        "Quality Issues": quality_issues,
        "Cleaning Audit": cleaning_audit,
        "Summary": summary_report,
        "Client Summary": pd.DataFrame({"Summary": client_summary.splitlines()})
    })

    zip_file = make_zip_bytes({
        "cleaned_data.csv": dataframe_to_csv_bytes(final_df),
        "rows_needing_review.csv": dataframe_to_csv_bytes(rows_needing_review),
        "review_summary.csv": dataframe_to_csv_bytes(review_summary),
        "safe_fixes.csv": dataframe_to_csv_bytes(safe_fixes),
        "column_summary.csv": dataframe_to_csv_bytes(column_summary),
        "quality_issues.csv": dataframe_to_csv_bytes(quality_issues),
        "cleaning_audit.csv": dataframe_to_csv_bytes(cleaning_audit),
        "client_summary.txt": text_to_bytes(client_summary),
        "clean0ps_cleaning_report.xlsx": excel_report
    })

    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="📥 Cleaned CSV",
            data=dataframe_to_csv_bytes(final_df),
            file_name="clean0ps_cleaned_data.csv",
            mime="text/csv"
        )

    with d2:
        st.download_button(
            label="📥 Excel Cleaning Report",
            data=excel_report,
            file_name="clean0ps_cleaning_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with d3:
        st.download_button(
            label="📥 Full Deliverables ZIP",
            data=zip_file,
            file_name="clean0ps_client_deliverables.zip",
            mime="application/zip"
        )

    st.download_button(
        label="📥 Client Summary TXT",
        data=text_to_bytes(client_summary),
        file_name="clean0ps_client_summary.txt",
        mime="text/plain"
    )

except Exception as error:
    user_message, technical_message = get_friendly_error(error)

    section_title("Template Cleaning Error")

    st.error(user_message)

    if technical_message:
        with st.expander("Technical details", expanded=False):
            st.code(technical_message)
            
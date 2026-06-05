import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2] if CURRENT_FILE.parent.name == "pages" else CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from clean0ps_ui import (
    apply_clean0ps_style,
    privacy_notice,
    reset_workflow_button,
    hero,
    section_title,
    feature_card
)

from clean0ps_core import (
    read_uploaded_file,
    check_file_size,
    build_column_summary,
    build_missing_report,
    build_basic_quality_issues,
    calculate_quality_score,
    get_total_missing_values,
    get_duplicate_row_count,
    get_duplicate_rows,
    get_missing_count,
    missing_mask,
    safe_numeric,
    safe_date,
    make_excel_bytes,
    get_friendly_error
)


st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="📋",
    layout="wide"
)

apply_clean0ps_style()
privacy_notice()
reset_workflow_button()

hero(
    title="📋 Data Quality Dashboard",
    subtitle=(
        "Upload a CSV or Excel file to profile the dataset, detect quality risks, "
        "review missing values, check duplicate records, validate required fields, "
        "and export a client-ready data quality audit."
    ),
    pill="DATA QUALITY · PROFILING · VALIDATION · EXPORTS"
)


# --------------------------------------------------
# Page-Specific Helpers
# --------------------------------------------------

def build_required_field_report(df, required_columns):
    rows = []

    for col in required_columns:
        if col not in df.columns:
            rows.append({
                "Severity": "Must Fix",
                "Issue": "Missing Required Column",
                "Field": col,
                "Count": len(df),
                "Why It Matters": "A required field is missing from the dataset.",
                "Recommended Action": "Add this column or confirm that the client does not need it."
            })

        else:
            missing_count = get_missing_count(df[col])

            if missing_count > 0:
                rows.append({
                    "Severity": "Must Fix",
                    "Issue": "Missing Required Values",
                    "Field": col,
                    "Count": missing_count,
                    "Why It Matters": "Required fields are needed for reporting, imports, matching, or downstream analysis.",
                    "Recommended Action": "Fill missing required values or remove unusable records."
                })

    return pd.DataFrame(rows)


def build_duplicate_key_report(df, duplicate_key_columns):
    rows = []

    for col in duplicate_key_columns:
        if col not in df.columns:
            continue

        duplicate_count = int(
            df[col]
            .dropna()
            .astype(str)
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:
            rows.append({
                "Severity": "Needs Review",
                "Issue": "Duplicate Key Values",
                "Field": col,
                "Count": duplicate_count,
                "Why It Matters": "Duplicate key values may indicate repeated records or matching problems.",
                "Recommended Action": "Review duplicate key values before importing, merging, or sending to a client."
            })

    return pd.DataFrame(rows)


def build_date_checks(df):
    rows = []

    date_keywords = [
        "date",
        "created",
        "updated",
        "timestamp",
        "time",
        "ordered",
        "shipped",
        "sold",
        "start",
        "cancel"
    ]

    possible_date_columns = [
        col for col in df.columns
        if any(keyword in col.lower() for keyword in date_keywords)
    ]

    for col in possible_date_columns:
        parsed = safe_date(df[col])
        non_missing_count = int((~missing_mask(df[col])).sum())
        parsed_count = int(parsed.notna().sum())
        failed_parse_count = max(non_missing_count - parsed_count, 0)
        future_count = int((parsed > pd.Timestamp.now()).sum())

        if failed_parse_count > 0:
            rows.append({
                "Severity": "Warning",
                "Issue": "Possible Invalid Date Values",
                "Field": col,
                "Count": failed_parse_count,
                "Why It Matters": "Invalid dates can break time-based reports, filtering, and trend analysis.",
                "Recommended Action": "Review date formatting and standardize date values."
            })

        if future_count > 0:
            rows.append({
                "Severity": "Warning",
                "Issue": "Future Dates",
                "Field": col,
                "Count": future_count,
                "Why It Matters": "Future dates may be valid for schedules, but suspicious in historical files.",
                "Recommended Action": "Confirm whether future dates are expected."
            })

    return pd.DataFrame(rows)


def build_text_checks(df):
    rows = []

    text_columns = df.select_dtypes(include="object").columns.tolist()

    for col in text_columns:
        values = df[col].dropna().astype(str)

        if values.empty:
            continue

        leading_trailing_spaces = int(
            values.str.match(r"^\s|\s$").sum()
        )

        double_spaces = int(
            values.str.contains(r"\s{2,}", regex=True).sum()
        )

        if leading_trailing_spaces > 0:
            rows.append({
                "Severity": "Warning",
                "Issue": "Leading or Trailing Spaces",
                "Field": col,
                "Count": leading_trailing_spaces,
                "Why It Matters": "Extra spaces can cause duplicate-looking values, failed joins, and messy reports.",
                "Recommended Action": "Trim extra spaces from this text field."
            })

        if double_spaces > 0:
            rows.append({
                "Severity": "Warning",
                "Issue": "Double Spaces",
                "Field": col,
                "Count": double_spaces,
                "Why It Matters": "Inconsistent spacing makes the file look unpolished and can affect matching.",
                "Recommended Action": "Standardize spacing inside this text field."
            })

    return pd.DataFrame(rows)


def build_numeric_summary(df):
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame()

    summary = numeric_df.describe().transpose().reset_index()

    summary = summary.rename(
        columns={
            "index": "Column",
            "count": "Count",
            "mean": "Average",
            "std": "Std Dev",
            "min": "Minimum",
            "25%": "25%",
            "50%": "Median",
            "75%": "75%",
            "max": "Maximum"
        }
    )

    return summary


def build_date_summary(df):
    rows = []

    date_keywords = [
        "date",
        "created",
        "updated",
        "timestamp",
        "time",
        "ordered",
        "shipped",
        "sold",
        "start",
        "cancel"
    ]

    possible_date_columns = [
        col for col in df.columns
        if any(keyword in col.lower() for keyword in date_keywords)
    ]

    for col in possible_date_columns:
        parsed = safe_date(df[col])

        rows.append({
            "Column": col,
            "Parsed Dates": int(parsed.notna().sum()),
            "Failed Parses": int((~missing_mask(df[col])).sum() - parsed.notna().sum()),
            "Earliest Date": parsed.min(),
            "Latest Date": parsed.max(),
            "Future Dates": int((parsed > pd.Timestamp.now()).sum())
        })

    return pd.DataFrame(rows)


def combine_issue_reports(reports):
    usable_reports = [
        report for report in reports
        if report is not None and not report.empty
    ]

    if not usable_reports:
        return pd.DataFrame(columns=[
            "Severity",
            "Issue",
            "Field",
            "Count",
            "Why It Matters",
            "Recommended Action"
        ])

    return pd.concat(
        usable_reports,
        ignore_index=True
    )


def build_action_plan(issue_report):
    rows = []

    if issue_report.empty:
        return pd.DataFrame([
            {
                "Priority": "Good",
                "Action": "No major quality issues were found.",
                "Reason": "The dataset passed the current profiling checks."
            }
        ])

    must_fix = issue_report[
        issue_report["Severity"] == "Must Fix"
    ]

    needs_review = issue_report[
        issue_report["Severity"] == "Needs Review"
    ]

    warnings = issue_report[
        issue_report["Severity"] == "Warning"
    ]

    if not must_fix.empty:
        rows.append({
            "Priority": "1",
            "Action": "Fix must-fix issues before using this dataset.",
            "Reason": "These issues can block reporting, imports, matching, or accurate analysis."
        })

    if not needs_review.empty:
        rows.append({
            "Priority": "2",
            "Action": "Review suspicious values and incomplete fields.",
            "Reason": "These issues may or may not be valid depending on the business context."
        })

    if not warnings.empty:
        rows.append({
            "Priority": "3",
            "Action": "Clean optional warnings if the client needs a polished final file.",
            "Reason": "Warnings may not block use, but they can reduce trust in the dataset."
        })

    rows.append({
        "Priority": "4",
        "Action": "Export the audit report and share it with the client.",
        "Reason": "The audit report explains what was found and what should be reviewed next."
    })

    return pd.DataFrame(rows)


def count_issue_types(issue_report, severity):
    if issue_report.empty:
        return 0

    return len(
        issue_report[
            issue_report["Severity"] == severity
        ]
    )


# --------------------------------------------------
# Upload Section
# --------------------------------------------------

section_title("Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)


if uploaded_file:
    try:
        df = read_uploaded_file(
            uploaded_file,
            normalize=True
        )

        file_size_info = check_file_size(df)

        for warning in file_size_info["warnings"]:
            st.warning(warning)

        section_title("Quality Setup")

        st.write(
            "Optional: select fields that should be required and fields that should act as duplicate keys."
        )

        setup1, setup2 = st.columns(2)

        with setup1:
            required_columns = st.multiselect(
                "Required columns",
                options=df.columns.tolist()
            )

        with setup2:
            duplicate_key_columns = st.multiselect(
                "Duplicate key columns",
                options=df.columns.tolist()
            )

        basic_issue_report = build_basic_quality_issues(df)

        required_report = build_required_field_report(
            df,
            required_columns
        )

        duplicate_key_report = build_duplicate_key_report(
            df,
            duplicate_key_columns
        )

        date_checks = build_date_checks(df)
        text_checks = build_text_checks(df)

        issue_report = combine_issue_reports([
            basic_issue_report,
            required_report,
            duplicate_key_report,
            date_checks,
            text_checks
        ])

        missing_report = build_missing_report(df)
        duplicate_records = get_duplicate_rows(df, keep=False)
        column_summary = build_column_summary(df)
        numeric_summary = build_numeric_summary(df)
        date_summary = build_date_summary(df)
        action_plan = build_action_plan(issue_report)

        total_rows = len(df)
        total_columns = len(df.columns)
        missing_values = get_total_missing_values(df)
        duplicate_rows = get_duplicate_row_count(df)
        quality_score = calculate_quality_score(df, issue_report)

        must_fix_total = count_issue_types(
            issue_report,
            "Must Fix"
        )

        review_total = count_issue_types(
            issue_report,
            "Needs Review"
        )

        warning_total = count_issue_types(
            issue_report,
            "Warning"
        )

        # ------------------------------------------
        # Overview
        # ------------------------------------------

        section_title("Quality Overview")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Rows",
                total_rows
            )

        with col2:
            st.metric(
                "Columns",
                total_columns
            )

        with col3:
            st.metric(
                "Missing Values",
                missing_values
            )

        with col4:
            st.metric(
                "Duplicate Rows",
                duplicate_rows
            )

        with col5:
            st.metric(
                "Quality Score",
                f"{quality_score}%"
            )

        section_title("Dataset Preview")

        st.dataframe(
            df.head(50),
            use_container_width=True
        )

        section_title("Quality Summary")

        if issue_report.empty:
            st.success(
                "No major quality issues were found in this dataset."
            )
        else:
            summary1, summary2, summary3 = st.columns(3)

            with summary1:
                feature_card(
                    "Must Fix",
                    f"{must_fix_total} issue types should be corrected before using this file."
                )

            with summary2:
                feature_card(
                    "Needs Review",
                    f"{review_total} issue types should be manually reviewed."
                )

            with summary3:
                feature_card(
                    "Warnings",
                    f"{warning_total} issue types may be optional improvements."
                )

        section_title("Action Plan")

        st.dataframe(
            action_plan,
            use_container_width=True
        )

        # ------------------------------------------
        # Detail Tabs
        # ------------------------------------------

        section_title("Detailed Quality Review")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "Issue Report",
            "Column Summary",
            "Missing Values",
            "Duplicate Records",
            "Numeric Summary",
            "Date Checks",
            "Text Checks"
        ])

        with tab1:
            if issue_report.empty:
                st.success("No issues found.")
            else:
                st.dataframe(
                    issue_report,
                    use_container_width=True
                )

        with tab2:
            st.dataframe(
                column_summary,
                use_container_width=True
            )

        with tab3:
            if missing_report.empty:
                st.success("No missing values found.")
            else:
                st.dataframe(
                    missing_report,
                    use_container_width=True
                )

        with tab4:
            if duplicate_records.empty:
                st.success("No duplicate records found.")
            else:
                st.dataframe(
                    duplicate_records.head(250),
                    use_container_width=True
                )

        with tab5:
            if numeric_summary.empty:
                st.info("No numeric columns found.")
            else:
                st.dataframe(
                    numeric_summary,
                    use_container_width=True
                )

        with tab6:
            if date_summary.empty:
                st.info("No possible date columns found.")
            else:
                st.dataframe(
                    date_summary,
                    use_container_width=True
                )

        with tab7:
            if text_checks.empty:
                st.success("No text formatting issues found.")
            else:
                st.dataframe(
                    text_checks,
                    use_container_width=True
                )

        # ------------------------------------------
        # Downloads
        # ------------------------------------------

        section_title("Download Data Quality Report")

        summary_report = pd.DataFrame([
            {
                "Metric": "File Name",
                "Value": uploaded_file.name
            },
            {
                "Metric": "Rows",
                "Value": total_rows
            },
            {
                "Metric": "Columns",
                "Value": total_columns
            },
            {
                "Metric": "Missing Values",
                "Value": missing_values
            },
            {
                "Metric": "Duplicate Rows",
                "Value": duplicate_rows
            },
            {
                "Metric": "Quality Score",
                "Value": f"{quality_score}%"
            },
            {
                "Metric": "Must Fix Issue Types",
                "Value": must_fix_total
            },
            {
                "Metric": "Needs Review Issue Types",
                "Value": review_total
            },
            {
                "Metric": "Warning Issue Types",
                "Value": warning_total
            },
            {
                "Metric": "Required Columns Checked",
                "Value": ", ".join(required_columns) if required_columns else "None selected"
            },
            {
                "Metric": "Duplicate Key Columns Checked",
                "Value": ", ".join(duplicate_key_columns) if duplicate_key_columns else "None selected"
            }
        ])

        report_bytes = make_excel_bytes({
            "Summary": summary_report,
            "Action Plan": action_plan,
            "Issue Report": issue_report,
            "Column Summary": column_summary,
            "Missing Values": missing_report,
            "Duplicate Records": duplicate_records.head(1000),
            "Numeric Summary": numeric_summary,
            "Date Summary": date_summary,
            "Text Checks": text_checks
        })

        st.download_button(
            label="📥 Download Full Data Quality Audit",
            data=report_bytes,
            file_name="clean0ps_data_quality_audit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as error:
        user_message, technical_message = get_friendly_error(error)

        section_title("File Processing Error")

        st.error(user_message)

        if technical_message:
            with st.expander("Technical details", expanded=False):
                st.code(technical_message)

else:
    st.info(
        "Upload a CSV or Excel file to begin data quality review."
    )
    
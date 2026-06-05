import streamlit as st
import pandas as pd
from clean0ps_ui import apply_clean0ps_style, hero, section_title

st.set_page_config(
    page_title="Validation Engine",
    page_icon="✅",
    layout="wide"
)

apply_clean0ps_style()

hero(
    title="✅ Validation Engine",
    subtitle=(
        "Upload a CSV or Excel file to validate required fields, duplicate records, "
        "negative values, future dates, and records requiring manual review."
    ),
    pill="VALIDATION · RULE CHECKS · MANUAL REVIEW"
)

dataset_type = st.selectbox(
    "Dataset Type",
    [
        "Business Data",
        "Sports Data",
        "NBA Player Info"
    ]
)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)


def read_uploaded_file(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)

    if file.name.lower().endswith(".xlsx"):
        return pd.read_excel(file)

    raise ValueError("Unsupported file type.")


def clean_column_name(col):
    col = str(col).strip().lower()
    col = col.replace(" ", "_")
    col = col.replace("-", "_")

    cleaned = ""

    for char in col:
        if char.isalnum() or char == "_":
            cleaned += char

    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")

    return cleaned.strip("_")


def normalize_columns(df):
    normalized_df = df.copy()

    normalized_df.columns = [
        clean_column_name(col)
        for col in normalized_df.columns
    ]

    return normalized_df


def missing_mask(series):
    return (
        series.isnull()
        | series.astype(str).str.strip().eq("")
        | series.astype(str).str.lower().isin(["nan", "none", "null"])
    )


def get_missing_count(series):
    return int(missing_mask(series).sum())


def find_available_column(df, possible_columns):
    for col in possible_columns:
        if col in df.columns:
            return col

    return None


def get_rule_config(selected_dataset_type):
    if selected_dataset_type == "Business Data":
        return {
            "required_groups": [
                {
                    "label": "Product Name",
                    "columns": ["product_name", "product", "item_name", "item"],
                    "why": "Product names identify what was sold, tracked, or reported.",
                    "action": "Fill missing product names or remove records that cannot be identified."
                },
                {
                    "label": "Sale Date",
                    "columns": ["sale_date", "date", "order_date", "transaction_date"],
                    "why": "Dates are needed for time-based reporting, dashboards, and trend analysis.",
                    "action": "Add or correct missing dates before using the file for reporting."
                }
            ],
            "optional_columns": [
                "category",
                "customer_id",
                "source_file",
                "region",
                "store",
                "sales_rep"
            ],
            "non_negative_columns": [
                "sales_amount",
                "revenue",
                "profit",
                "quantity_sold",
                "unit_cost",
                "price",
                "inventory_on_hand"
            ]
        }

    if selected_dataset_type == "Sports Data":
        return {
            "required_groups": [
                {
                    "label": "Player",
                    "columns": ["player", "player_name", "athlete", "name"],
                    "why": "Player names connect stats, props, and results to the correct athlete.",
                    "action": "Add player names or map the file to a valid player identifier."
                },
                {
                    "label": "Game Date",
                    "columns": ["game_date", "date", "event_date"],
                    "why": "Game dates separate events and support trend or hit-rate analysis.",
                    "action": "Add game dates before analyzing props, trends, or results."
                }
            ],
            "optional_columns": [
                "team",
                "opponent",
                "position",
                "league",
                "market",
                "prop_line"
            ],
            "non_negative_columns": [
                "points",
                "rebounds",
                "assists",
                "hits",
                "goals",
                "shots",
                "yards",
                "passing_yards",
                "rushing_yards",
                "receiving_yards",
                "minutes",
                "steals",
                "blocks",
                "prop_line",
                "projection",
                "confidence"
            ]
        }

    return {
        "required_groups": [
            {
                "label": "Player ID",
                "columns": ["person_id", "player_id"],
                "why": "Player ID is the main unique identifier used to match player records.",
                "action": "Review records with missing IDs because they may not match correctly with other datasets."
            },
            {
                "label": "Player Name",
                "columns": ["display_first_last", "player_name", "full_name"],
                "why": "Player name is needed for readable dashboards, reports, and validation.",
                "action": "Create display names from first and last name if missing."
            }
        ],
        "optional_columns": [
            "jersey",
            "team_code",
            "team_city",
            "team_name",
            "team_abbreviation",
            "draft_number",
            "draft_round",
            "weight",
            "height",
            "position",
            "school",
            "playercode"
        ],
        "non_negative_columns": [
            "person_id",
            "player_id",
            "team_id",
            "season_exp",
            "from_year",
            "to_year"
        ]
    }


def build_duplicate_report(df):
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count == 0:
        return pd.DataFrame()

    return pd.DataFrame([
        {
            "Field": "Full Row",
            "Severity": "Must Fix",
            "Issue Type": "Exact Duplicate Row",
            "Count": duplicate_count,
            "Why It Matters": "Duplicate rows can inflate totals, distort averages, and create inaccurate reporting.",
            "Recommended Action": "Review and remove repeated rows before analysis, dashboarding, or import."
        }
    ])


def build_required_report(df, required_groups):
    rows = []

    for group in required_groups:
        available_col = find_available_column(
            df,
            group["columns"]
        )

        if available_col is None:
            rows.append({
                "Field": group["label"],
                "Severity": "Must Fix",
                "Issue Type": "Missing Required Column",
                "Count": len(df),
                "Why It Matters": group["why"],
                "Recommended Action": group["action"]
            })

        else:
            missing_count = get_missing_count(df[available_col])

            if missing_count > 0:
                rows.append({
                    "Field": available_col,
                    "Severity": "Manual Review Needed",
                    "Issue Type": "Missing Required Values",
                    "Count": missing_count,
                    "Why It Matters": group["why"],
                    "Recommended Action": group["action"]
                })

    return pd.DataFrame(rows)


def build_optional_report(df, optional_columns):
    rows = []

    for col in optional_columns:
        if col in df.columns:
            missing_count = get_missing_count(df[col])

            if missing_count > 0:
                missing_percent = (
                    missing_count / max(len(df), 1)
                ) * 100

                rows.append({
                    "Field": col,
                    "Severity": "Optional Improvement",
                    "Issue Type": "Missing Optional Values",
                    "Count": missing_count,
                    "Missing %": f"{missing_percent:.1f}%",
                    "Why It Matters": "This field may improve filtering, grouping, reporting, or enrichment.",
                    "Recommended Action": "Review whether this field is needed for the customer’s goal."
                })

    return pd.DataFrame(rows)


def build_negative_report(df, non_negative_columns):
    rows = []

    for col in non_negative_columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            negative_count = int((df[col] < 0).sum())

            if negative_count > 0:
                rows.append({
                    "Field": col,
                    "Severity": "Must Fix",
                    "Issue Type": "Negative Value",
                    "Count": negative_count,
                    "Why It Matters": "Negative values may be impossible or invalid for this field.",
                    "Recommended Action": "Review the original source and correct the value if it is an error."
                })

    return pd.DataFrame(rows)


def build_future_date_report(df):
    rows = []

    date_keywords = [
        "date",
        "birthdate",
        "game_date",
        "sale_date",
        "created_at",
        "updated_at"
    ]

    possible_date_columns = [
        col for col in df.columns
        if any(keyword in col.lower() for keyword in date_keywords)
    ]

    for col in possible_date_columns:
        parsed = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        future_count = int(
            (parsed > pd.Timestamp.now()).sum()
        )

        if future_count > 0:
            rows.append({
                "Field": col,
                "Severity": "Optional Improvement",
                "Issue Type": "Future Date",
                "Count": future_count,
                "Why It Matters": "Future dates may be valid for schedules or projections, but not for historical datasets.",
                "Recommended Action": "Confirm whether future dates are expected for this dataset."
            })

    return pd.DataFrame(rows)


def build_column_summary(df):
    rows = []

    for col in df.columns:
        missing_count = get_missing_count(df[col])
        missing_percent = (
            missing_count / max(len(df), 1)
        ) * 100

        rows.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing Values": missing_count,
            "Missing %": f"{missing_percent:.1f}%",
            "Unique Values": df[col].nunique(dropna=True)
        })

    return pd.DataFrame(rows)


def concat_reports(report_list):
    usable_reports = [
        report for report in report_list
        if report is not None and not report.empty
    ]

    if len(usable_reports) == 0:
        return pd.DataFrame(columns=[
            "Field",
            "Severity",
            "Issue Type",
            "Count",
            "Why It Matters",
            "Recommended Action"
        ])

    return pd.concat(
        usable_reports,
        ignore_index=True
    )


def count_report_items(report_df):
    if report_df.empty:
        return 0

    if "Count" in report_df.columns:
        return int(report_df["Count"].sum())

    return 0


def calculate_quality_score(
    total_rows,
    total_columns,
    must_fix_count,
    manual_review_count,
    optional_count
):
    total_cells = max(
        total_rows * max(total_columns, 1),
        1
    )

    must_fix_rate = must_fix_count / total_cells
    manual_review_rate = manual_review_count / total_cells
    optional_rate = optional_count / total_cells

    score = 100

    score -= must_fix_rate * 300
    score -= manual_review_rate * 100
    score -= optional_rate * 30

    return max(0, round(score))


def build_records_requiring_review(df, issue_reports):
    review_df = df.copy()
    review_df["review_needed"] = False
    review_df["review_reason"] = ""

    all_issues = concat_reports(issue_reports)

    for _, issue in all_issues.iterrows():
        field = issue.get("Field", "")
        issue_type = str(issue.get("Issue Type", ""))

        if field in review_df.columns:
            if "Missing" in issue_type:
                mask = missing_mask(review_df[field])
                review_df.loc[mask, "review_needed"] = True
                review_df.loc[mask, "review_reason"] += f"{issue_type}: {field}; "

            if "Negative" in issue_type:
                if pd.api.types.is_numeric_dtype(review_df[field]):
                    mask = review_df[field] < 0
                    review_df.loc[mask, "review_needed"] = True
                    review_df.loc[mask, "review_reason"] += f"Negative value: {field}; "

    duplicate_mask = review_df.duplicated(
        subset=[
            col for col in review_df.columns
            if col not in ["review_needed", "review_reason"]
        ],
        keep=False
    )

    review_df.loc[duplicate_mask, "review_needed"] = True
    review_df.loc[duplicate_mask, "review_reason"] += "Possible duplicate row; "

    return review_df[
        review_df["review_needed"] == True
    ]


if uploaded_file:
    original_df = read_uploaded_file(uploaded_file)

    df = normalize_columns(original_df)

    config = get_rule_config(dataset_type)

    section_title("Dataset Preview")

    st.dataframe(
        df.head(50),
        use_container_width=True
    )

    duplicate_report = build_duplicate_report(df)

    required_report = build_required_report(
        df,
        config["required_groups"]
    )

    optional_report = build_optional_report(
        df,
        config["optional_columns"]
    )

    negative_report = build_negative_report(
        df,
        config["non_negative_columns"]
    )

    future_date_report = build_future_date_report(df)

    must_fix_issues = concat_reports([
        duplicate_report,
        negative_report
    ])

    manual_review_issues = concat_reports([
        required_report
    ])

    optional_improvements = concat_reports([
        optional_report,
        future_date_report
    ])

    must_fix_count = count_report_items(must_fix_issues)
    manual_review_count = count_report_items(manual_review_issues)
    optional_count = count_report_items(optional_improvements)

    records_requiring_review = build_records_requiring_review(
        df,
        [
            must_fix_issues,
            manual_review_issues,
            optional_improvements
        ]
    )

    quality_score = calculate_quality_score(
        len(df),
        len(df.columns),
        must_fix_count,
        manual_review_count,
        optional_count
    )

    column_summary = build_column_summary(df)

    section_title("Validation Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Rows", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    with col3:
        st.metric("Quality Score", f"{quality_score}%")

    with col4:
        st.metric("Must Fix", must_fix_count)

    with col5:
        st.metric("Records Requiring Review", len(records_requiring_review))

    section_title("Validation Summary")

    if must_fix_count == 0 and manual_review_count == 0 and optional_count == 0:
        st.success(
            "No validation issues found based on the selected dataset type."
        )
    else:
        if must_fix_count > 0:
            st.error(
                "Must-fix issues were found. These should be corrected before using the dataset."
            )

        if manual_review_count > 0:
            st.warning(
                "Some records require manual review before final use."
            )

        if optional_count > 0:
            st.info(
                "Optional improvements were found. These may not block basic use, but they should be reviewed."
            )

    section_title("Validation Details")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Must Fix",
        "Manual Review Needed",
        "Optional Improvements",
        "Records Requiring Review",
        "Column Summary"
    ])

    with tab1:
        if must_fix_issues.empty:
            st.success("No must-fix issues found.")
        else:
            st.dataframe(
                must_fix_issues,
                use_container_width=True
            )

    with tab2:
        if manual_review_issues.empty:
            st.success("No manual review issues found.")
        else:
            st.dataframe(
                manual_review_issues,
                use_container_width=True
            )

    with tab3:
        if optional_improvements.empty:
            st.success("No optional improvement issues found.")
        else:
            st.dataframe(
                optional_improvements,
                use_container_width=True
            )

    with tab4:
        if records_requiring_review.empty:
            st.success("No records require manual review.")
        else:
            st.dataframe(
                records_requiring_review.head(100),
                use_container_width=True
            )

    with tab5:
        st.dataframe(
            column_summary,
            use_container_width=True
        )

else:
    st.info("Upload a CSV or Excel file to begin validation.")
    
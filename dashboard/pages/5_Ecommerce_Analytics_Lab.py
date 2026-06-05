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
    mini_card
)

from clean0ps_core import (
    read_multiple_uploaded_files,
    check_file_size,
    normalize_columns,
    safe_numeric,
    safe_date,
    dataframe_to_csv_bytes,
    text_to_bytes,
    make_excel_bytes,
    make_dataframe_zip,
    get_friendly_error
)


st.set_page_config(
    page_title="E-commerce Analytics Lab",
    page_icon="🛒",
    layout="wide"
)

apply_clean0ps_style()
privacy_notice()
reset_workflow_button()

hero(
    title="🛒 E-commerce Analytics Lab",
    subtitle=(
        "Build an e-commerce reporting workflow from raw files. Assign source tables, map columns, "
        "model fact and dimension tables, validate relationships, filter dashboard views, and export "
        "dashboard-ready tables and client reports."
    ),
    pill="ECOMMERCE · MODEL BUILDER · VALIDATION TESTS · BI DASHBOARD"
)


# --------------------------------------------------
# Demo Data
# --------------------------------------------------

def make_demo_data():
    orders = pd.DataFrame({
        "order_id": ["O1001", "O1002", "O1003", "O1004", "O1005", "O1006", "O1007", "O1008", "O1009", "O1010", "O1011", "O1012"],
        "customer_id": ["C001", "C002", "C001", "C003", "C004", "C005", "C002", "C006", "C007", "C008", "C007", "C009"],
        "order_date": ["2026-01-03", "2026-01-04", "2026-01-11", "2026-02-02", "2026-02-08", "2026-02-10", "2026-03-03", "2026-03-10", "2026-03-12", "2026-04-01", "2026-04-07", "2026-04-10"],
        "channel": ["Meta", "Google", "Email", "Meta", "TikTok", "Google", "Email", "Organic", "Meta", "Google", "Email", "Organic"],
        "revenue": [120.50, 85.00, 42.99, 199.99, 64.50, 155.75, 92.00, 45.25, 250.00, 110.00, 75.00, 39.99],
        "refund_amount": [0, 0, 0, 25.00, 0, 0, 0, 0, 0, 10.00, 0, 0]
    })

    order_items = pd.DataFrame({
        "order_id": ["O1001", "O1001", "O1002", "O1003", "O1004", "O1005", "O1006", "O1007", "O1008", "O1009", "O1010", "O1011", "O1012"],
        "product_id": ["P001", "P002", "P002", "P003", "P004", "P001", "P005", "P002", "P003", "P004", "P002", "P006", "P003"],
        "quantity": [2, 1, 1, 3, 2, 1, 5, 2, 1, 3, 1, 2, 1],
        "item_revenue": [80.00, 40.50, 85.00, 42.99, 199.99, 64.50, 155.75, 92.00, 45.25, 250.00, 110.00, 75.00, 39.99]
    })

    customers = pd.DataFrame({
        "customer_id": ["C001", "C002", "C003", "C004", "C005", "C006", "C007", "C008", "C009"],
        "customer_email": ["c001@email.com", "c002@email.com", "c003@email.com", "c004@email.com", "c005@email.com", "c006@email.com", "c007@email.com", "c008@email.com", "c009@email.com"],
        "first_order_date": ["2026-01-03", "2026-01-04", "2026-02-02", "2026-02-08", "2026-02-10", "2026-03-10", "2026-03-12", "2026-04-01", "2026-04-10"],
        "customer_segment": ["Repeat", "Repeat", "New", "New", "New", "New", "Repeat", "New", "New"]
    })

    products = pd.DataFrame({
        "product_id": ["P001", "P002", "P003", "P004", "P005", "P006"],
        "product_name": ["Protein Bar", "Energy Drink", "Trail Mix", "Supplement Pack", "Protein Shake", "Wellness Bundle"],
        "category": ["Snacks", "Drinks", "Snacks", "Supplements", "Drinks", "Bundles"]
    })

    ad_spend = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01", "2026-02-01", "2026-02-01", "2026-03-01", "2026-04-01"],
        "channel": ["Meta", "Google", "Meta", "TikTok", "Google", "Meta"],
        "campaign": ["Meta Prospecting", "Google Search", "Meta Retargeting", "TikTok TOF", "Google Shopping", "Meta Spring Sale"],
        "spend": [300.00, 250.00, 200.00, 175.00, 225.00, 280.00],
        "clicks": [900, 550, 450, 700, 480, 625],
        "impressions": [12000, 9000, 7000, 15000, 8500, 11000]
    })

    web_sessions = pd.DataFrame({
        "session_id": ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008", "S009", "S010", "S011", "S012", "S013", "S014"],
        "date": ["2026-01-03", "2026-01-04", "2026-01-05", "2026-01-11", "2026-02-02", "2026-02-08", "2026-02-10", "2026-03-03", "2026-03-05", "2026-03-10", "2026-03-12", "2026-04-01", "2026-04-07", "2026-04-10"],
        "channel": ["Meta", "Google", "Organic", "Email", "Meta", "TikTok", "Google", "Email", "Organic", "Organic", "Meta", "Google", "Email", "Organic"],
        "customer_id": ["C001", "C002", "", "C001", "C003", "C004", "C005", "C002", "", "C006", "C007", "C008", "C007", "C009"],
        "converted": [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1]
    })

    subscriptions = pd.DataFrame({
        "subscription_id": ["SUB001", "SUB002", "SUB003", "SUB004", "SUB005"],
        "customer_id": ["C001", "C002", "C003", "C005", "C007"],
        "start_date": ["2026-01-03", "2026-01-04", "2026-02-02", "2026-02-10", "2026-03-12"],
        "status": ["active", "canceled", "active", "active", "active"],
        "cancel_date": ["", "2026-03-01", "", "", ""],
        "monthly_price": [29.99, 39.99, 29.99, 49.99, 59.99]
    })

    return {
        "orders.csv": normalize_columns(orders),
        "order_items.csv": normalize_columns(order_items),
        "customers.csv": normalize_columns(customers),
        "products.csv": normalize_columns(products),
        "ad_spend.csv": normalize_columns(ad_spend),
        "web_sessions.csv": normalize_columns(web_sessions),
        "subscriptions.csv": normalize_columns(subscriptions)
    }


# --------------------------------------------------
# Table Definitions
# --------------------------------------------------

TABLE_DEFINITIONS = {
    "orders": {
        "label": "Orders",
        "required": ["order_id", "customer_id", "order_date", "revenue"],
        "fields": {
            "order_id": ["order_id", "id", "order_number"],
            "customer_id": ["customer_id", "customer", "user_id"],
            "order_date": ["order_date", "date", "created_at", "transaction_date"],
            "channel": ["channel", "source", "utm_source", "marketing_channel"],
            "revenue": ["revenue", "total", "total_amount", "order_total", "sales_amount"],
            "refund_amount": ["refund_amount", "refund", "returns", "return_amount"]
        }
    },
    "order_items": {
        "label": "Order Items",
        "required": ["order_id", "product_id", "quantity"],
        "fields": {
            "order_id": ["order_id", "order_number"],
            "product_id": ["product_id", "sku", "item_id"],
            "quantity": ["quantity", "qty", "units"],
            "item_revenue": ["item_revenue", "revenue", "line_revenue", "line_total", "sales_amount"]
        }
    },
    "customers": {
        "label": "Customers",
        "required": ["customer_id"],
        "fields": {
            "customer_id": ["customer_id", "id", "user_id"],
            "customer_email": ["customer_email", "email", "email_address"],
            "first_order_date": ["first_order_date", "created_at", "signup_date", "acquisition_date"],
            "customer_segment": ["customer_segment", "segment", "type"]
        }
    },
    "products": {
        "label": "Products",
        "required": ["product_id"],
        "fields": {
            "product_id": ["product_id", "sku", "item_id"],
            "product_name": ["product_name", "product", "item_name", "name"],
            "category": ["category", "product_category", "department"]
        }
    },
    "ad_spend": {
        "label": "Ad Spend",
        "required": ["date", "channel", "spend"],
        "fields": {
            "date": ["date", "spend_date", "day"],
            "channel": ["channel", "platform", "source"],
            "campaign": ["campaign", "campaign_name"],
            "spend": ["spend", "cost", "ad_spend"],
            "clicks": ["clicks", "link_clicks"],
            "impressions": ["impressions", "views"]
        }
    },
    "web_sessions": {
        "label": "Web Sessions",
        "required": ["session_id", "date", "channel"],
        "fields": {
            "session_id": ["session_id", "id"],
            "date": ["date", "session_date", "created_at"],
            "channel": ["channel", "source", "utm_source"],
            "customer_id": ["customer_id", "user_id"],
            "converted": ["converted", "conversion", "purchase", "has_order"]
        }
    },
    "subscriptions": {
        "label": "Subscriptions",
        "required": ["subscription_id", "customer_id", "status"],
        "fields": {
            "subscription_id": ["subscription_id", "sub_id", "id"],
            "customer_id": ["customer_id", "user_id"],
            "start_date": ["start_date", "subscription_start", "created_at"],
            "status": ["status", "subscription_status"],
            "cancel_date": ["cancel_date", "canceled_at", "cancelled_at"],
            "monthly_price": ["monthly_price", "price", "subscription_amount", "mrr"]
        }
    }
}


# --------------------------------------------------
# Detection / Mapping Helpers
# --------------------------------------------------

def detect_table_type(file_name, df):
    lower_name = file_name.lower()
    columns = set(df.columns)

    if "order_item" in lower_name or {"order_id", "product_id", "quantity"}.issubset(columns):
        return "order_items"

    if "subscription" in lower_name or "subscription_id" in columns:
        return "subscriptions"

    if "session" in lower_name or "web" in lower_name or "session_id" in columns:
        return "web_sessions"

    if "ad" in lower_name or "spend" in columns or "campaign" in columns:
        return "ad_spend"

    if "product" in lower_name or ("product_id" in columns and ("product_name" in columns or "category" in columns)):
        return "products"

    if "customer" in lower_name or ("customer_id" in columns and ("email" in columns or "customer_email" in columns)):
        return "customers"

    if "order" in lower_name or {"order_id", "customer_id"}.issubset(columns):
        return "orders"

    return "unknown"


def get_default_col(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate

    return "None"


def get_selected_col(mapping, table_name, field_name):
    value = mapping.get(table_name, {}).get(field_name, "None")
    return None if value == "None" else value


def make_string_series(df, col, default=""):
    if col and col in df.columns:
        return df[col].fillna(default).astype(str)

    return pd.Series([default] * len(df), index=df.index)


def make_numeric_series(df, col, default=0):
    if col and col in df.columns:
        return safe_numeric(df[col])

    return pd.Series([default] * len(df), index=df.index)


def make_date_series(df, col):
    if col and col in df.columns:
        return safe_date(df[col])

    return pd.Series(pd.NaT, index=df.index)


# --------------------------------------------------
# Modeling
# --------------------------------------------------

def build_fact_orders(tables, mapping):
    if "orders" not in tables:
        return pd.DataFrame()

    df = tables["orders"].copy()

    order_id_col = get_selected_col(mapping, "orders", "order_id")
    customer_id_col = get_selected_col(mapping, "orders", "customer_id")
    order_date_col = get_selected_col(mapping, "orders", "order_date")
    channel_col = get_selected_col(mapping, "orders", "channel")
    revenue_col = get_selected_col(mapping, "orders", "revenue")
    refund_col = get_selected_col(mapping, "orders", "refund_amount")

    fact = pd.DataFrame(index=df.index)
    fact["order_id"] = make_string_series(df, order_id_col, "")
    fact["customer_id"] = make_string_series(df, customer_id_col, "")
    fact["order_date_raw"] = make_date_series(df, order_date_col)
    fact["channel"] = make_string_series(df, channel_col, "Unknown")
    fact["revenue"] = make_numeric_series(df, revenue_col, 0)
    fact["refund_amount"] = make_numeric_series(df, refund_col, 0)
    fact["net_revenue"] = fact["revenue"] - fact["refund_amount"]
    fact["order_month"] = fact["order_date_raw"].dt.to_period("M").astype(str)
    fact["order_date"] = fact["order_date_raw"].dt.strftime("%Y-%m-%d")
    fact = fact.drop(columns=["order_date_raw"])

    return fact.reset_index(drop=True)


def build_fact_order_items(tables, mapping):
    if "order_items" not in tables:
        return pd.DataFrame()

    df = tables["order_items"].copy()

    order_id_col = get_selected_col(mapping, "order_items", "order_id")
    product_id_col = get_selected_col(mapping, "order_items", "product_id")
    quantity_col = get_selected_col(mapping, "order_items", "quantity")
    item_revenue_col = get_selected_col(mapping, "order_items", "item_revenue")

    fact = pd.DataFrame(index=df.index)
    fact["order_id"] = make_string_series(df, order_id_col, "")
    fact["product_id"] = make_string_series(df, product_id_col, "")
    fact["quantity"] = make_numeric_series(df, quantity_col, 0)
    fact["item_revenue"] = make_numeric_series(df, item_revenue_col, 0)

    return fact.reset_index(drop=True)


def build_dim_customers(tables, mapping):
    if "customers" not in tables:
        return pd.DataFrame()

    df = tables["customers"].copy()

    customer_id_col = get_selected_col(mapping, "customers", "customer_id")
    email_col = get_selected_col(mapping, "customers", "customer_email")
    first_order_col = get_selected_col(mapping, "customers", "first_order_date")
    segment_col = get_selected_col(mapping, "customers", "customer_segment")

    dim = pd.DataFrame(index=df.index)
    dim["customer_id"] = make_string_series(df, customer_id_col, "")
    dim["customer_email"] = make_string_series(df, email_col, "")
    dim["first_order_date_raw"] = make_date_series(df, first_order_col)
    dim["first_order_date"] = dim["first_order_date_raw"].dt.strftime("%Y-%m-%d")
    dim["customer_segment"] = make_string_series(df, segment_col, "Unknown")
    dim = dim.drop(columns=["first_order_date_raw"])

    return dim.reset_index(drop=True)


def build_dim_products(tables, mapping):
    if "products" not in tables:
        return pd.DataFrame()

    df = tables["products"].copy()

    product_id_col = get_selected_col(mapping, "products", "product_id")
    product_name_col = get_selected_col(mapping, "products", "product_name")
    category_col = get_selected_col(mapping, "products", "category")

    dim = pd.DataFrame(index=df.index)
    dim["product_id"] = make_string_series(df, product_id_col, "")
    dim["product_name"] = make_string_series(df, product_name_col, "")
    dim["category"] = make_string_series(df, category_col, "Unknown")

    return dim.reset_index(drop=True)


def build_fact_ad_spend(tables, mapping):
    if "ad_spend" not in tables:
        return pd.DataFrame()

    df = tables["ad_spend"].copy()

    date_col = get_selected_col(mapping, "ad_spend", "date")
    channel_col = get_selected_col(mapping, "ad_spend", "channel")
    campaign_col = get_selected_col(mapping, "ad_spend", "campaign")
    spend_col = get_selected_col(mapping, "ad_spend", "spend")
    clicks_col = get_selected_col(mapping, "ad_spend", "clicks")
    impressions_col = get_selected_col(mapping, "ad_spend", "impressions")

    fact = pd.DataFrame(index=df.index)
    fact["date_raw"] = make_date_series(df, date_col)
    fact["month"] = fact["date_raw"].dt.to_period("M").astype(str)
    fact["date"] = fact["date_raw"].dt.strftime("%Y-%m-%d")
    fact["channel"] = make_string_series(df, channel_col, "Unknown")
    fact["campaign"] = make_string_series(df, campaign_col, "Unknown")
    fact["spend"] = make_numeric_series(df, spend_col, 0)
    fact["clicks"] = make_numeric_series(df, clicks_col, 0)
    fact["impressions"] = make_numeric_series(df, impressions_col, 0)
    fact = fact.drop(columns=["date_raw"])

    return fact.reset_index(drop=True)


def build_fact_sessions(tables, mapping):
    if "web_sessions" not in tables:
        return pd.DataFrame()

    df = tables["web_sessions"].copy()

    session_id_col = get_selected_col(mapping, "web_sessions", "session_id")
    date_col = get_selected_col(mapping, "web_sessions", "date")
    channel_col = get_selected_col(mapping, "web_sessions", "channel")
    customer_id_col = get_selected_col(mapping, "web_sessions", "customer_id")
    converted_col = get_selected_col(mapping, "web_sessions", "converted")

    fact = pd.DataFrame(index=df.index)
    fact["session_id"] = make_string_series(df, session_id_col, "")
    fact["date_raw"] = make_date_series(df, date_col)
    fact["month"] = fact["date_raw"].dt.to_period("M").astype(str)
    fact["date"] = fact["date_raw"].dt.strftime("%Y-%m-%d")
    fact["channel"] = make_string_series(df, channel_col, "Unknown")
    fact["customer_id"] = make_string_series(df, customer_id_col, "")
    fact["converted"] = make_numeric_series(df, converted_col, 0)
    fact = fact.drop(columns=["date_raw"])

    return fact.reset_index(drop=True)


def build_fact_subscriptions(tables, mapping):
    if "subscriptions" not in tables:
        return pd.DataFrame()

    df = tables["subscriptions"].copy()

    subscription_id_col = get_selected_col(mapping, "subscriptions", "subscription_id")
    customer_id_col = get_selected_col(mapping, "subscriptions", "customer_id")
    start_col = get_selected_col(mapping, "subscriptions", "start_date")
    status_col = get_selected_col(mapping, "subscriptions", "status")
    cancel_col = get_selected_col(mapping, "subscriptions", "cancel_date")
    price_col = get_selected_col(mapping, "subscriptions", "monthly_price")

    fact = pd.DataFrame(index=df.index)
    fact["subscription_id"] = make_string_series(df, subscription_id_col, "")
    fact["customer_id"] = make_string_series(df, customer_id_col, "")
    fact["start_date_raw"] = make_date_series(df, start_col)
    fact["start_month"] = fact["start_date_raw"].dt.to_period("M").astype(str)
    fact["start_date"] = fact["start_date_raw"].dt.strftime("%Y-%m-%d")
    fact["status"] = make_string_series(df, status_col, "unknown").str.lower()
    fact["cancel_date_raw"] = make_date_series(df, cancel_col)
    fact["cancel_month"] = fact["cancel_date_raw"].dt.to_period("M").astype(str)
    fact["cancel_date"] = fact["cancel_date_raw"].dt.strftime("%Y-%m-%d")
    fact["monthly_price"] = make_numeric_series(df, price_col, 0)
    fact["is_active"] = fact["status"].isin(["active", "trialing"])
    fact["is_canceled"] = fact["status"].isin(["canceled", "cancelled", "churned"])
    fact = fact.drop(columns=["start_date_raw", "cancel_date_raw"])

    return fact.reset_index(drop=True)


def build_dim_dates(modeled):
    date_values = []

    for table_name, col in [
        ("fact_orders", "order_date"),
        ("fact_ad_spend", "date"),
        ("fact_sessions", "date"),
        ("fact_subscriptions", "start_date")
    ]:
        df = modeled.get(table_name, pd.DataFrame())

        if not df.empty and col in df.columns:
            date_values += df[col].dropna().tolist()

    if not date_values:
        return pd.DataFrame()

    dim = pd.DataFrame({
        "date": pd.to_datetime(pd.Series(date_values), errors="coerce")
    })

    dim = dim.dropna().drop_duplicates().sort_values("date")
    dim["year"] = dim["date"].dt.year
    dim["month"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.month_name()
    dim["quarter"] = dim["date"].dt.quarter
    dim["date"] = dim["date"].dt.strftime("%Y-%m-%d")

    return dim.reset_index(drop=True)


def build_dim_channels(modeled):
    channels = []

    for table_name in ["fact_orders", "fact_ad_spend", "fact_sessions"]:
        df = modeled.get(table_name, pd.DataFrame())

        if not df.empty and "channel" in df.columns:
            channels += df["channel"].dropna().astype(str).tolist()

    if not channels:
        return pd.DataFrame()

    dim = pd.DataFrame({"channel": sorted(set(channels))})
    dim["channel_type"] = dim["channel"].apply(
        lambda value: "Paid"
        if value.lower() in ["meta", "google", "tiktok", "facebook", "paid social", "paid search"]
        else "Owned / Organic"
    )

    return dim


def build_modeled_tables(tables, mapping):
    modeled = {
        "fact_orders": build_fact_orders(tables, mapping),
        "fact_order_items": build_fact_order_items(tables, mapping),
        "dim_customers": build_dim_customers(tables, mapping),
        "dim_products": build_dim_products(tables, mapping),
        "fact_ad_spend": build_fact_ad_spend(tables, mapping),
        "fact_sessions": build_fact_sessions(tables, mapping),
        "fact_subscriptions": build_fact_subscriptions(tables, mapping)
    }

    modeled["dim_dates"] = build_dim_dates(modeled)
    modeled["dim_channels"] = build_dim_channels(modeled)

    return modeled


# --------------------------------------------------
# Validation
# --------------------------------------------------

def add_test(rows, test_name, table, field, status, failing_rows, explanation, fix):
    rows.append({
        "Test": test_name,
        "Table": table,
        "Field": field,
        "Status": status,
        "Failing Rows": int(failing_rows),
        "Why It Matters": explanation,
        "Recommended Fix": fix
    })


def validate_not_null(rows, df, table, field):
    if df.empty or field not in df.columns:
        return

    values = df[field]
    failing = int(values.isna().sum() + values.astype(str).str.strip().eq("").sum())

    add_test(
        rows,
        "not_null",
        table,
        field,
        "Fail" if failing > 0 else "Pass",
        failing,
        f"{table}.{field} should not be blank.",
        f"Fill or remove records with missing {field}."
    )


def validate_unique(rows, df, table, field):
    if df.empty or field not in df.columns:
        return

    failing = int(df[field].dropna().astype(str).duplicated().sum())

    add_test(
        rows,
        "unique",
        table,
        field,
        "Fail" if failing > 0 else "Pass",
        failing,
        f"{table}.{field} should uniquely identify records.",
        f"Review duplicate {field} values."
    )


def validate_non_negative(rows, df, table, field):
    if df.empty or field not in df.columns:
        return

    values = safe_numeric(df[field])
    failing = int((values < 0).sum())

    add_test(
        rows,
        "non_negative",
        table,
        field,
        "Fail" if failing > 0 else "Pass",
        failing,
        f"{table}.{field} should not be negative.",
        f"Review negative {field} values."
    )


def validate_relationship(rows, child_df, parent_df, child_table, parent_table, field):
    if child_df.empty or parent_df.empty or field not in child_df.columns or field not in parent_df.columns:
        return

    child_values = set(child_df[field].dropna().astype(str))
    parent_values = set(parent_df[field].dropna().astype(str))
    orphan_values = child_values - parent_values
    failing = int(child_df[field].astype(str).isin(orphan_values).sum())

    add_test(
        rows,
        "relationship",
        child_table,
        field,
        "Fail" if failing > 0 else "Pass",
        failing,
        f"{child_table}.{field} should exist in {parent_table}.{field}.",
        f"Review orphan {field} values."
    )


def validate_accepted_values(rows, df, table, field, accepted_values):
    if df.empty or field not in df.columns:
        return

    values = df[field].dropna().astype(str).str.lower()
    failing = int((~values.isin(accepted_values)).sum())

    add_test(
        rows,
        "accepted_values",
        table,
        field,
        "Fail" if failing > 0 else "Pass",
        failing,
        f"{table}.{field} should contain expected values.",
        f"Standardize {field} values."
    )


def build_model_validation_report(modeled):
    rows = []

    fact_orders = modeled["fact_orders"]
    fact_order_items = modeled["fact_order_items"]
    dim_customers = modeled["dim_customers"]
    dim_products = modeled["dim_products"]
    fact_ad_spend = modeled["fact_ad_spend"]
    fact_sessions = modeled["fact_sessions"]
    fact_subscriptions = modeled["fact_subscriptions"]

    validate_not_null(rows, fact_orders, "fact_orders", "order_id")
    validate_unique(rows, fact_orders, "fact_orders", "order_id")
    validate_not_null(rows, fact_orders, "fact_orders", "customer_id")
    validate_not_null(rows, fact_orders, "fact_orders", "order_date")
    validate_non_negative(rows, fact_orders, "fact_orders", "revenue")
    validate_non_negative(rows, fact_orders, "fact_orders", "refund_amount")

    validate_not_null(rows, fact_order_items, "fact_order_items", "order_id")
    validate_not_null(rows, fact_order_items, "fact_order_items", "product_id")
    validate_non_negative(rows, fact_order_items, "fact_order_items", "quantity")
    validate_non_negative(rows, fact_order_items, "fact_order_items", "item_revenue")

    validate_unique(rows, dim_customers, "dim_customers", "customer_id")
    validate_unique(rows, dim_products, "dim_products", "product_id")

    validate_non_negative(rows, fact_ad_spend, "fact_ad_spend", "spend")
    validate_non_negative(rows, fact_ad_spend, "fact_ad_spend", "clicks")
    validate_non_negative(rows, fact_ad_spend, "fact_ad_spend", "impressions")

    validate_accepted_values(
        rows,
        fact_subscriptions,
        "fact_subscriptions",
        "status",
        ["active", "trialing", "canceled", "cancelled", "churned", "paused", "unknown"]
    )

    validate_non_negative(rows, fact_subscriptions, "fact_subscriptions", "monthly_price")

    validate_relationship(rows, fact_orders, dim_customers, "fact_orders", "dim_customers", "customer_id")
    validate_relationship(rows, fact_order_items, fact_orders, "fact_order_items", "fact_orders", "order_id")
    validate_relationship(rows, fact_order_items, dim_products, "fact_order_items", "dim_products", "product_id")
    validate_relationship(rows, fact_subscriptions, dim_customers, "fact_subscriptions", "dim_customers", "customer_id")

    if not fact_sessions.empty and "converted" in fact_sessions.columns:
        converted_values = safe_numeric(fact_sessions["converted"])
        bad_converted = int((~converted_values.isin([0, 1])).sum())

        add_test(
            rows,
            "accepted_values",
            "fact_sessions",
            "converted",
            "Fail" if bad_converted > 0 else "Pass",
            bad_converted,
            "fact_sessions.converted should usually be 0 or 1.",
            "Standardize conversion values to 0 or 1."
        )

    if not rows:
        return pd.DataFrame(columns=[
            "Test", "Table", "Field", "Status", "Failing Rows", "Why It Matters", "Recommended Fix"
        ])

    return pd.DataFrame(rows)


def build_model_health_report(table_assignment, tables, modeled):
    rows = []

    for table_name, definition in TABLE_DEFINITIONS.items():
        selected_file = table_assignment.get(table_name, "None")
        loaded = table_name in tables

        rows.append({
            "Layer": "Source",
            "Table": table_name,
            "Display Name": definition["label"],
            "Loaded": "Yes" if loaded else "No",
            "Source File": selected_file if selected_file != "None" else "",
            "Rows": len(tables[table_name]) if loaded else 0
        })

    for model_name, model_df in modeled.items():
        rows.append({
            "Layer": "Modeled",
            "Table": model_name,
            "Display Name": model_name,
            "Loaded": "Yes" if not model_df.empty else "No",
            "Source File": "",
            "Rows": len(model_df)
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# KPI + Reporting
# --------------------------------------------------

def calculate_kpis(modeled):
    fact_orders = modeled["fact_orders"]
    fact_ad_spend = modeled["fact_ad_spend"]
    fact_sessions = modeled["fact_sessions"]
    fact_subscriptions = modeled["fact_subscriptions"]

    total_revenue = 0
    total_orders = 0
    average_order_value = 0
    unique_customers = 0
    repeat_purchase_rate = 0
    ltv = 0
    refund_rate = 0

    if not fact_orders.empty:
        total_revenue = float(fact_orders["net_revenue"].sum())
        total_orders = int(fact_orders["order_id"].nunique())
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        unique_customers = int(fact_orders["customer_id"].replace("", pd.NA).dropna().nunique())

        customer_order_counts = fact_orders.groupby("customer_id")["order_id"].nunique()
        repeat_customers = int((customer_order_counts > 1).sum())
        repeat_purchase_rate = repeat_customers / max(unique_customers, 1)

        ltv = total_revenue / max(unique_customers, 1)

        gross_revenue = float(fact_orders["revenue"].sum())
        refunds = float(fact_orders["refund_amount"].sum())
        refund_rate = refunds / gross_revenue if gross_revenue > 0 else 0

    total_ad_spend = 0
    roas = 0
    cac = 0

    if not fact_ad_spend.empty:
        total_ad_spend = float(fact_ad_spend["spend"].sum())
        roas = total_revenue / total_ad_spend if total_ad_spend > 0 else 0
        cac = total_ad_spend / max(unique_customers, 1)

    total_sessions = 0
    conversion_rate = 0

    if not fact_sessions.empty:
        total_sessions = int(fact_sessions["session_id"].nunique())
        conversions = float(fact_sessions["converted"].sum())
        conversion_rate = conversions / max(total_sessions, 1)

    active_subscriptions = 0
    churn_rate = 0
    mrr = 0

    if not fact_subscriptions.empty:
        active_subscriptions = int(fact_subscriptions["is_active"].sum())
        canceled_subscriptions = int(fact_subscriptions["is_canceled"].sum())
        total_subscriptions = len(fact_subscriptions)
        churn_rate = canceled_subscriptions / max(total_subscriptions, 1)
        mrr = float(fact_subscriptions[fact_subscriptions["is_active"]]["monthly_price"].sum())

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "unique_customers": unique_customers,
        "repeat_purchase_rate": repeat_purchase_rate,
        "ltv": ltv,
        "refund_rate": refund_rate,
        "total_ad_spend": total_ad_spend,
        "roas": roas,
        "cac": cac,
        "total_sessions": total_sessions,
        "conversion_rate": conversion_rate,
        "active_subscriptions": active_subscriptions,
        "churn_rate": churn_rate,
        "mrr": mrr
    }


def build_revenue_by_month(fact_orders):
    if fact_orders.empty:
        return pd.DataFrame()

    return (
        fact_orders
        .groupby("order_month", dropna=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique")
        )
        .reset_index()
        .sort_values("order_month")
    )


def build_revenue_by_channel(fact_orders):
    if fact_orders.empty:
        return pd.DataFrame()

    return (
        fact_orders
        .groupby("channel", dropna=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def build_channel_performance(fact_orders, fact_ad_spend, fact_sessions):
    revenue_by_channel = build_revenue_by_channel(fact_orders)

    spend_by_channel = pd.DataFrame()

    if not fact_ad_spend.empty:
        spend_by_channel = (
            fact_ad_spend
            .groupby("channel", dropna=False)
            .agg(
                spend=("spend", "sum"),
                clicks=("clicks", "sum"),
                impressions=("impressions", "sum")
            )
            .reset_index()
        )

    sessions_by_channel = pd.DataFrame()

    if not fact_sessions.empty:
        sessions_by_channel = (
            fact_sessions
            .groupby("channel", dropna=False)
            .agg(
                sessions=("session_id", "nunique"),
                conversions=("converted", "sum")
            )
            .reset_index()
        )

    performance = pd.DataFrame()

    for df in [revenue_by_channel, spend_by_channel, sessions_by_channel]:
        if df.empty:
            continue

        if performance.empty:
            performance = df.copy()
        else:
            performance = pd.merge(
                performance,
                df,
                on="channel",
                how="outer"
            )

    if performance.empty:
        return pd.DataFrame()

    for col in ["revenue", "orders", "customers", "spend", "clicks", "impressions", "sessions", "conversions"]:
        if col not in performance.columns:
            performance[col] = 0

        performance[col] = safe_numeric(performance[col])

    performance["roas"] = performance.apply(
        lambda row: row["revenue"] / row["spend"] if row["spend"] > 0 else 0,
        axis=1
    )

    performance["cpc"] = performance.apply(
        lambda row: row["spend"] / row["clicks"] if row["clicks"] > 0 else 0,
        axis=1
    )

    performance["cpm"] = performance.apply(
        lambda row: (row["spend"] / row["impressions"]) * 1000 if row["impressions"] > 0 else 0,
        axis=1
    )

    performance["conversion_rate"] = performance.apply(
        lambda row: row["conversions"] / row["sessions"] if row["sessions"] > 0 else 0,
        axis=1
    )

    return performance.sort_values("revenue", ascending=False)


def build_product_performance(fact_order_items, dim_products):
    if fact_order_items.empty:
        return pd.DataFrame()

    product_perf = (
        fact_order_items
        .groupby("product_id", dropna=False)
        .agg(
            quantity_sold=("quantity", "sum"),
            product_revenue=("item_revenue", "sum"),
            order_count=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("product_revenue", ascending=False)
    )

    if not dim_products.empty:
        product_perf = pd.merge(
            product_perf,
            dim_products,
            on="product_id",
            how="left"
        )

    return product_perf


def build_customer_summary(fact_orders):
    if fact_orders.empty:
        return pd.DataFrame()

    summary = (
        fact_orders
        .groupby("customer_id", dropna=False)
        .agg(
            orders=("order_id", "nunique"),
            revenue=("net_revenue", "sum"),
            first_order=("order_date", "min"),
            last_order=("order_date", "max")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    summary["customer_type"] = summary["orders"].apply(
        lambda orders: "Repeat" if orders > 1 else "One-Time"
    )

    return summary


def build_subscription_summary(fact_subscriptions):
    if fact_subscriptions.empty:
        return pd.DataFrame()

    return (
        fact_subscriptions
        .groupby("status", dropna=False)
        .agg(
            subscriptions=("subscription_id", "nunique"),
            monthly_revenue=("monthly_price", "sum")
        )
        .reset_index()
        .sort_values("subscriptions", ascending=False)
    )


def filter_modeled_tables(modeled, start_date, end_date, selected_channels, selected_categories, selected_statuses):
    filtered = {name: df.copy() for name, df in modeled.items()}

    def filter_date(df, col):
        if df.empty or col not in df.columns:
            return df

        temp = df.copy()
        parsed = pd.to_datetime(temp[col], errors="coerce")
        mask = (parsed.dt.date >= start_date) & (parsed.dt.date <= end_date)

        return temp[mask]

    filtered["fact_orders"] = filter_date(filtered["fact_orders"], "order_date")
    filtered["fact_ad_spend"] = filter_date(filtered["fact_ad_spend"], "date")
    filtered["fact_sessions"] = filter_date(filtered["fact_sessions"], "date")
    filtered["fact_subscriptions"] = filter_date(filtered["fact_subscriptions"], "start_date")

    if selected_channels:
        for table_name in ["fact_orders", "fact_ad_spend", "fact_sessions"]:
            if not filtered[table_name].empty and "channel" in filtered[table_name].columns:
                filtered[table_name] = filtered[table_name][filtered[table_name]["channel"].isin(selected_channels)]

    if selected_categories and not filtered["dim_products"].empty:
        product_ids = filtered["dim_products"][
            filtered["dim_products"]["category"].isin(selected_categories)
        ]["product_id"].astype(str).tolist()

        filtered["dim_products"] = filtered["dim_products"][
            filtered["dim_products"]["product_id"].astype(str).isin(product_ids)
        ]

        if not filtered["fact_order_items"].empty:
            filtered["fact_order_items"] = filtered["fact_order_items"][
                filtered["fact_order_items"]["product_id"].astype(str).isin(product_ids)
            ]

            order_ids = filtered["fact_order_items"]["order_id"].astype(str).unique().tolist()

            if not filtered["fact_orders"].empty:
                filtered["fact_orders"] = filtered["fact_orders"][
                    filtered["fact_orders"]["order_id"].astype(str).isin(order_ids)
                ]

    if selected_statuses and not filtered["fact_subscriptions"].empty:
        filtered["fact_subscriptions"] = filtered["fact_subscriptions"][
            filtered["fact_subscriptions"]["status"].isin(selected_statuses)
        ]

    return filtered


def build_action_plan(kpis, validation_report):
    rows = []

    failed_tests = 0

    if validation_report is not None and not validation_report.empty:
        failed_tests = len(validation_report[validation_report["Status"] == "Fail"])

    if failed_tests > 0:
        rows.append({
            "Priority": "1",
            "Action": "Fix failed validation tests before trusting dashboard totals.",
            "Why It Matters": f"{failed_tests} validation test(s) failed."
        })

    if kpis["roas"] > 0 and kpis["roas"] < 1:
        rows.append({
            "Priority": "2",
            "Action": "Review paid channel profitability.",
            "Why It Matters": "ROAS below 1.0 means tracked revenue is lower than ad spend."
        })

    if kpis["refund_rate"] > 0.10:
        rows.append({
            "Priority": "3",
            "Action": "Review refund rate.",
            "Why It Matters": "Refunds above 10% may indicate fulfillment, product quality, or customer-fit issues."
        })

    if kpis["churn_rate"] > 0.20:
        rows.append({
            "Priority": "4",
            "Action": "Review subscription churn.",
            "Why It Matters": "High churn may indicate retention, pricing, or customer satisfaction problems."
        })

    if not rows:
        rows.append({
            "Priority": "Good",
            "Action": "Core e-commerce reporting model appears usable.",
            "Why It Matters": "The modeled tables and KPI dashboard support client reporting."
        })

    return pd.DataFrame(rows)


def build_client_summary(kpis, action_plan, validation_report):
    failed_tests = 0

    if validation_report is not None and not validation_report.empty:
        failed_tests = len(validation_report[validation_report["Status"] == "Fail"])

    summary = f"""
Clean0ps E-commerce Analytics Summary

Executive KPI Summary:
Revenue: ${kpis["total_revenue"]:,.2f}
Orders: {kpis["total_orders"]:,}
Average Order Value: ${kpis["average_order_value"]:,.2f}
Customers: {kpis["unique_customers"]:,}
ROAS: {kpis["roas"]:.2f}x
CAC: ${kpis["cac"]:,.2f}
LTV: ${kpis["ltv"]:,.2f}
Conversion Rate: {kpis["conversion_rate"] * 100:.1f}%
Repeat Purchase Rate: {kpis["repeat_purchase_rate"] * 100:.1f}%
Refund Rate: {kpis["refund_rate"] * 100:.1f}%
Active Subscriptions: {kpis["active_subscriptions"]:,}
Churn Rate: {kpis["churn_rate"] * 100:.1f}%
MRR: ${kpis["mrr"]:,.2f}

Model Validation:
Failed Tests: {failed_tests}

Recommended Next Steps:
"""

    for _, row in action_plan.iterrows():
        summary += f"- {row['Action']} {row['Why It Matters']}\n"

    return summary.strip()


# --------------------------------------------------
# Page Intro
# --------------------------------------------------

section_title("What This Lab Does")

intro1, intro2, intro3 = st.columns(3)

with intro1:
    feature_card(
        "Model Builder",
        "Assign uploaded files to source tables, then map messy customer columns to clean reporting fields."
    )

with intro2:
    feature_card(
        "Validation Tests",
        "Run not-null, unique, non-negative, relationship, and accepted-value checks across modeled tables."
    )

with intro3:
    feature_card(
        "BI Dashboard",
        "Filter by date, channel, product category, and subscription status, then export dashboard-ready reports."
    )

section_title("Workflow")

w1, w2, w3, w4, w5 = st.columns(5)

with w1:
    mini_card("STEP 1", "Load Files")

with w2:
    mini_card("STEP 2", "Assign Tables")

with w3:
    mini_card("STEP 3", "Map Columns")

with w4:
    mini_card("STEP 4", "Validate Model")

with w5:
    mini_card("STEP 5", "Export Reports")


# --------------------------------------------------
# Demo Downloads
# --------------------------------------------------

section_title("Demo E-commerce Files")

with st.expander("Download demo datasets", expanded=False):
    demo_files = make_demo_data()
    demo_cols = st.columns(4)

    for index, (file_name, demo_df) in enumerate(demo_files.items()):
        with demo_cols[index % 4]:
            st.download_button(
                label=f"📥 {file_name}",
                data=dataframe_to_csv_bytes(demo_df),
                file_name=file_name,
                mime="text/csv",
                key=f"demo_{file_name}"
            )


# --------------------------------------------------
# Load Data
# --------------------------------------------------

section_title("Load E-commerce Data")

data_source = st.radio(
    "Choose data source",
    ["Use built-in demo data", "Upload CSV / Excel files"],
    horizontal=True
)

try:
    if data_source == "Use built-in demo data":
        source_files = make_demo_data()
    else:
        uploaded_files = st.file_uploader(
            "Upload one or more e-commerce files",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )

        if not uploaded_files:
            st.info("Upload one or more e-commerce files to begin.")
            st.stop()

        source_files = read_multiple_uploaded_files(
            uploaded_files,
            normalize=True
        )

    for file_name, df in source_files.items():
        file_size_info = check_file_size(df)

        for warning in file_size_info["warnings"]:
            st.warning(f"{file_name}: {warning}")

    # --------------------------------------------------
    # Assign Tables
    # --------------------------------------------------

    section_title("Source Table Assignment")

    st.write(
        "Assign each uploaded file to the role it plays in the e-commerce model. Auto-detection helps, but you can override it."
    )

    file_options = ["None"] + list(source_files.keys())
    table_assignment = {}

    assign_cols = st.columns(3)

    for index, table_name in enumerate(TABLE_DEFINITIONS.keys()):
        definition = TABLE_DEFINITIONS[table_name]
        detected_file = "None"

        for file_name, df in source_files.items():
            if detect_table_type(file_name, df) == table_name:
                detected_file = file_name
                break

        with assign_cols[index % 3]:
            table_assignment[table_name] = st.selectbox(
                definition["label"],
                file_options,
                index=file_options.index(detected_file) if detected_file in file_options else 0,
                key=f"assign_{table_name}"
            )

    tables = {}

    for table_name, file_name in table_assignment.items():
        if file_name != "None":
            tables[table_name] = source_files[file_name].copy()

    if not tables:
        st.warning("No source tables have been assigned yet.")
        st.stop()

    # --------------------------------------------------
    # Column Mapping
    # --------------------------------------------------

    section_title("Column Mapping")

    st.write(
        "Map raw source columns to standardized reporting fields. This makes messy client files usable."
    )

    mapping = {}

    for table_name, df in tables.items():
        definition = TABLE_DEFINITIONS[table_name]

        with st.expander(f"Map columns for {definition['label']}", expanded=(table_name == "orders")):
            mapping[table_name] = {}

            field_cols = st.columns(3)
            fields = list(definition["fields"].items())

            for index, (field_name, candidates) in enumerate(fields):
                options = ["None"] + df.columns.tolist()
                default_col = get_default_col(df, candidates)
                default_index = options.index(default_col) if default_col in options else 0

                with field_cols[index % 3]:
                    mapping[table_name][field_name] = st.selectbox(
                        field_name,
                        options,
                        index=default_index,
                        key=f"map_{table_name}_{field_name}"
                    )

            st.dataframe(
                df.head(10),
                use_container_width=True
            )

    # --------------------------------------------------
    # Build Model
    # --------------------------------------------------

    modeled = build_modeled_tables(tables, mapping)
    model_health = build_model_health_report(table_assignment, tables, modeled)
    validation_report = build_model_validation_report(modeled)

    # --------------------------------------------------
    # Filters
    # --------------------------------------------------

    section_title("Dashboard Filters")

    all_dates = []

    for table_name, col in [
        ("fact_orders", "order_date"),
        ("fact_ad_spend", "date"),
        ("fact_sessions", "date"),
        ("fact_subscriptions", "start_date")
    ]:
        df = modeled.get(table_name, pd.DataFrame())

        if not df.empty and col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce").dropna()

            if not parsed.empty:
                all_dates += parsed.dt.date.tolist()

    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
    else:
        today = pd.Timestamp.today().date()
        min_date = today
        max_date = today

    filter1, filter2, filter3, filter4 = st.columns(4)

    with filter1:
        selected_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = min_date, max_date

    all_channels = []

    for table_name in ["fact_orders", "fact_ad_spend", "fact_sessions"]:
        df = modeled.get(table_name, pd.DataFrame())

        if not df.empty and "channel" in df.columns:
            all_channels += df["channel"].dropna().astype(str).tolist()

    all_channels = sorted(set(all_channels))

    with filter2:
        selected_channels = st.multiselect(
            "Channel",
            all_channels,
            default=all_channels
        )

    all_categories = []

    if not modeled["dim_products"].empty and "category" in modeled["dim_products"].columns:
        all_categories = sorted(
            modeled["dim_products"]["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    with filter3:
        selected_categories = st.multiselect(
            "Product category",
            all_categories,
            default=all_categories
        )

    all_statuses = []

    if not modeled["fact_subscriptions"].empty and "status" in modeled["fact_subscriptions"].columns:
        all_statuses = sorted(
            modeled["fact_subscriptions"]["status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    with filter4:
        selected_statuses = st.multiselect(
            "Subscription status",
            all_statuses,
            default=all_statuses
        )

    filtered_modeled = filter_modeled_tables(
        modeled,
        start_date,
        end_date,
        selected_channels,
        selected_categories,
        selected_statuses
    )

    # --------------------------------------------------
    # KPI + Reports
    # --------------------------------------------------

    kpis = calculate_kpis(filtered_modeled)
    revenue_by_month = build_revenue_by_month(filtered_modeled["fact_orders"])
    revenue_by_channel = build_revenue_by_channel(filtered_modeled["fact_orders"])
    channel_performance = build_channel_performance(
        filtered_modeled["fact_orders"],
        filtered_modeled["fact_ad_spend"],
        filtered_modeled["fact_sessions"]
    )
    product_performance = build_product_performance(
        filtered_modeled["fact_order_items"],
        filtered_modeled["dim_products"]
    )
    customer_summary = build_customer_summary(filtered_modeled["fact_orders"])
    subscription_summary = build_subscription_summary(filtered_modeled["fact_subscriptions"])
    action_plan = build_action_plan(kpis, validation_report)
    client_summary = build_client_summary(kpis, action_plan, validation_report)

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    section_title("Executive KPI Dashboard")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric("Revenue", f"${kpis['total_revenue']:,.2f}")

    with k2:
        st.metric("Orders", f"{kpis['total_orders']:,}")

    with k3:
        st.metric("AOV", f"${kpis['average_order_value']:,.2f}")

    with k4:
        st.metric("Customers", f"{kpis['unique_customers']:,}")

    with k5:
        st.metric("ROAS", f"{kpis['roas']:.2f}x")

    k6, k7, k8, k9, k10 = st.columns(5)

    with k6:
        st.metric("Ad Spend", f"${kpis['total_ad_spend']:,.2f}")

    with k7:
        st.metric("CAC", f"${kpis['cac']:,.2f}")

    with k8:
        st.metric("LTV", f"${kpis['ltv']:,.2f}")

    with k9:
        st.metric("Conversion", f"{kpis['conversion_rate'] * 100:.1f}%")

    with k10:
        st.metric("Churn", f"{kpis['churn_rate'] * 100:.1f}%")

    section_title("Client Action Plan")

    st.dataframe(
        action_plan,
        use_container_width=True
    )

    section_title("Model Validation Tests")

    val1, val2, val3 = st.columns(3)

    if validation_report.empty:
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
    else:
        total_tests = len(validation_report)
        passed_tests = len(validation_report[validation_report["Status"] == "Pass"])
        failed_tests = len(validation_report[validation_report["Status"] == "Fail"])

    with val1:
        st.metric("Total Tests", total_tests)

    with val2:
        st.metric("Passed", passed_tests)

    with val3:
        st.metric("Failed", failed_tests)

    st.dataframe(
        validation_report,
        use_container_width=True
    )

    section_title("Dashboard Views")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Revenue",
        "Channel / ROAS",
        "Products",
        "Customers",
        "Subscriptions",
        "Model Health",
        "Modeled Tables"
    ])

    with tab1:
        if revenue_by_month.empty:
            st.info("Revenue by month requires an orders table.")
        else:
            st.subheader("Revenue by Month")
            st.bar_chart(
                revenue_by_month.set_index("order_month")["revenue"]
            )
            st.dataframe(
                revenue_by_month,
                use_container_width=True
            )

        if not revenue_by_channel.empty:
            st.subheader("Revenue by Channel")
            st.bar_chart(
                revenue_by_channel.set_index("channel")["revenue"]
            )
            st.dataframe(
                revenue_by_channel,
                use_container_width=True
            )

    with tab2:
        if channel_performance.empty:
            st.info("Channel performance requires orders, ad spend, or session data.")
        else:
            st.subheader("Channel Performance")
            st.dataframe(
                channel_performance,
                use_container_width=True
            )

            chart_metric = st.selectbox(
                "Chart metric",
                ["roas", "revenue", "spend", "conversion_rate"]
            )

            if chart_metric in channel_performance.columns:
                st.bar_chart(
                    channel_performance.set_index("channel")[chart_metric]
                )

    with tab3:
        if product_performance.empty:
            st.info("Product performance requires order_items and product data.")
        else:
            st.subheader("Product Performance")
            st.dataframe(
                product_performance,
                use_container_width=True
            )

            label_col = "product_name" if "product_name" in product_performance.columns else "product_id"

            st.bar_chart(
                product_performance.set_index(label_col)["product_revenue"]
            )

    with tab4:
        if customer_summary.empty:
            st.info("Customer reporting requires orders data.")
        else:
            st.subheader("Customer Value Summary")
            st.dataframe(
                customer_summary,
                use_container_width=True
            )

            type_summary = (
                customer_summary
                .groupby("customer_type")
                .agg(
                    customers=("customer_id", "nunique"),
                    revenue=("revenue", "sum")
                )
                .reset_index()
            )

            st.bar_chart(
                type_summary.set_index("customer_type")["revenue"]
            )

    with tab5:
        if subscription_summary.empty:
            st.info("Subscription analysis requires subscription data.")
        else:
            st.subheader("Subscription Summary")
            st.dataframe(
                subscription_summary,
                use_container_width=True
            )
            st.bar_chart(
                subscription_summary.set_index("status")["subscriptions"]
            )

    with tab6:
        st.subheader("Source + Model Health")
        st.dataframe(
            model_health,
            use_container_width=True
        )

    with tab7:
        selected_model = st.selectbox(
            "Choose modeled table",
            list(modeled.keys())
        )

        selected_df = modeled[selected_model]

        if selected_df.empty:
            st.info(f"{selected_model} is empty because the related source data was not loaded.")
        else:
            st.dataframe(
                selected_df.head(250),
                use_container_width=True
            )

    section_title("Client Summary")

    st.text_area(
        "Client-ready explanation",
        client_summary,
        height=360
    )

    # --------------------------------------------------
    # SQL Examples
    # --------------------------------------------------

    section_title("dbt / BigQuery Style SQL Examples")

    sql_tab1, sql_tab2, sql_tab3, sql_tab4, sql_tab5 = st.tabs([
        "stg_orders.sql",
        "fct_orders.sql",
        "channel_performance.sql",
        "customer_ltv.sql",
        "schema_tests.yml"
    ])

    with sql_tab1:
        st.code(
            """
select
    cast(order_id as string) as order_id,
    cast(customer_id as string) as customer_id,
    cast(order_date as date) as order_date,
    coalesce(channel, 'Unknown') as channel,
    cast(revenue as numeric) as revenue,
    cast(refund_amount as numeric) as refund_amount
from raw.orders;
            """,
            language="sql"
        )

    with sql_tab2:
        st.code(
            """
with orders as (

    select
        order_id,
        customer_id,
        order_date,
        channel,
        revenue,
        refund_amount,
        revenue - refund_amount as net_revenue,
        date_trunc(order_date, month) as order_month
    from {{ ref('stg_orders') }}

)

select *
from orders;
            """,
            language="sql"
        )

    with sql_tab3:
        st.code(
            """
with revenue_by_channel as (

    select
        channel,
        sum(net_revenue) as revenue,
        count(distinct order_id) as orders,
        count(distinct customer_id) as customers
    from {{ ref('fct_orders') }}
    group by 1

),

spend_by_channel as (

    select
        channel,
        sum(spend) as spend,
        sum(clicks) as clicks,
        sum(impressions) as impressions
    from {{ ref('fct_ad_spend') }}
    group by 1

)

select
    s.channel,
    s.spend,
    r.revenue,
    r.orders,
    r.customers,
    r.revenue / nullif(s.spend, 0) as roas,
    s.spend / nullif(s.clicks, 0) as cpc,
    (s.spend / nullif(s.impressions, 0)) * 1000 as cpm
from spend_by_channel s
left join revenue_by_channel r
    on s.channel = r.channel;
            """,
            language="sql"
        )

    with sql_tab4:
        st.code(
            """
with customer_revenue as (

    select
        customer_id,
        count(distinct order_id) as orders,
        sum(net_revenue) as lifetime_revenue,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from {{ ref('fct_orders') }}
    group by 1

)

select
    customer_id,
    orders,
    lifetime_revenue,
    lifetime_revenue / nullif(orders, 0) as average_order_value,
    first_order_date,
    last_order_date
from customer_revenue;
            """,
            language="sql"
        )

    with sql_tab5:
        st.code(
            """
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

  - name: fct_order_items
    columns:
      - name: order_id
        tests:
          - not_null
          - relationships:
              to: ref('fct_orders')
              field: order_id
      - name: product_id
        tests:
          - relationships:
              to: ref('dim_products')
              field: product_id
            """,
            language="yaml"
        )

    # --------------------------------------------------
    # Downloads
    # --------------------------------------------------

    section_title("Download BI Deliverables")

    summary_report = pd.DataFrame([
        {"Metric": "Revenue", "Value": f"${kpis['total_revenue']:,.2f}"},
        {"Metric": "Orders", "Value": kpis["total_orders"]},
        {"Metric": "Average Order Value", "Value": f"${kpis['average_order_value']:,.2f}"},
        {"Metric": "Customers", "Value": kpis["unique_customers"]},
        {"Metric": "Repeat Purchase Rate", "Value": f"{kpis['repeat_purchase_rate'] * 100:.1f}%"},
        {"Metric": "LTV", "Value": f"${kpis['ltv']:,.2f}"},
        {"Metric": "Refund Rate", "Value": f"{kpis['refund_rate'] * 100:.1f}%"},
        {"Metric": "Ad Spend", "Value": f"${kpis['total_ad_spend']:,.2f}"},
        {"Metric": "ROAS", "Value": f"{kpis['roas']:.2f}x"},
        {"Metric": "CAC", "Value": f"${kpis['cac']:,.2f}"},
        {"Metric": "Sessions", "Value": kpis["total_sessions"]},
        {"Metric": "Conversion Rate", "Value": f"{kpis['conversion_rate'] * 100:.1f}%"},
        {"Metric": "Active Subscriptions", "Value": kpis["active_subscriptions"]},
        {"Metric": "Churn Rate", "Value": f"{kpis['churn_rate'] * 100:.1f}%"},
        {"Metric": "MRR", "Value": f"${kpis['mrr']:,.2f}"}
    ])

    report_sheets = {
        "KPI Summary": summary_report,
        "Client Summary": pd.DataFrame({"Summary": client_summary.splitlines()}),
        "Action Plan": action_plan,
        "Model Health": model_health,
        "Validation Tests": validation_report,
        "Revenue by Month": revenue_by_month,
        "Revenue by Channel": revenue_by_channel,
        "Channel Performance": channel_performance,
        "Product Performance": product_performance,
        "Customer Summary": customer_summary,
        "Subscription Summary": subscription_summary
    }

    for model_name, model_df in modeled.items():
        report_sheets[model_name] = model_df.head(10000)

    excel_report = make_excel_bytes(report_sheets)
    modeled_zip = make_dataframe_zip(modeled)
    filtered_modeled_zip = make_dataframe_zip(filtered_modeled)

    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="📥 Full E-commerce Analytics Report",
            data=excel_report,
            file_name="clean0ps_full_ecommerce_analytics_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with d2:
        st.download_button(
            label="📥 Modeled Tables ZIP",
            data=modeled_zip,
            file_name="clean0ps_modeled_tables.zip",
            mime="application/zip"
        )

    with d3:
        st.download_button(
            label="📥 Filtered Dashboard Tables ZIP",
            data=filtered_modeled_zip,
            file_name="clean0ps_filtered_dashboard_tables.zip",
            mime="application/zip"
        )

    st.download_button(
        label="📥 Client Summary TXT",
        data=text_to_bytes(client_summary),
        file_name="clean0ps_ecommerce_client_summary.txt",
        mime="text/plain"
    )

except Exception as error:
    user_message, technical_message = get_friendly_error(error)

    section_title("E-commerce Lab Error")

    st.error(user_message)

    if technical_message:
        with st.expander("Technical details", expanded=False):
            st.code(technical_message)
            
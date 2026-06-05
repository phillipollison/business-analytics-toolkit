# --------------------------------------------------
# Streamlit Cloud import-path fix
# --------------------------------------------------
# Streamlit Cloud can run page files from inside dashboard/pages.
# This block makes sure root-level files like clean0ps_ui.py and
# clean0ps_core.py can still be imported in both local and cloud runs.

import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2] if CURRENT_FILE.parent.name == "pages" else CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    feature_card,
    mini_card
)

from clean0ps_core import (
    read_uploaded_file,
    check_file_size,
    safe_numeric,
    safe_date,
    get_missing_count,
    build_column_summary,
    build_basic_quality_issues,
    calculate_quality_score,
    make_excel_bytes,
    dataframe_to_csv_bytes,
    get_friendly_error
)


st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="📦",
    layout="wide"
)

apply_clean0ps_style()
privacy_notice()
reset_workflow_button()

hero(
    title="📦 Inventory Dashboard",
    subtitle=(
        "Upload a product or inventory file to review stock levels, reorder needs, "
        "inventory value, low-stock risk, overstock risk, and product catalog quality."
    ),
    pill="INVENTORY · STOCK HEALTH · REORDER REVIEW · EXPORTS"
)


# --------------------------------------------------
# Demo Data
# --------------------------------------------------

def make_demo_inventory():
    return pd.DataFrame({
        "sku": [
            "SKU-1001", "SKU-1002", "SKU-1003", "SKU-1004", "SKU-1005",
            "SKU-1006", "SKU-1007", "SKU-1008", "SKU-1009", "SKU-1010"
        ],
        "product_name": [
            "Protein Bar", "Energy Drink", "Trail Mix", "Supplement Pack", "Protein Shake",
            "Granola Bites", "Vitamin Water", "Electrolyte Mix", "Wellness Bundle", "Snack Box"
        ],
        "category": [
            "Snacks", "Drinks", "Snacks", "Supplements", "Drinks",
            "Snacks", "Drinks", "Supplements", "Bundles", "Snacks"
        ],
        "vendor": [
            "Vendor A", "Vendor B", "Vendor A", "Vendor C", "Vendor B",
            "Vendor A", "Vendor D", "Vendor C", "Vendor C", "Vendor A"
        ],
        "quantity_on_hand": [8, 0, 45, 12, 4, 150, 2, 88, 6, 300],
        "reorder_point": [15, 10, 20, 15, 12, 50, 10, 40, 8, 75],
        "target_stock": [40, 30, 60, 45, 35, 100, 25, 85, 20, 150],
        "unit_cost": [1.25, 0.85, 1.10, 8.50, 2.25, 0.75, 0.95, 4.25, 12.00, 0.55],
        "selling_price": [2.99, 2.49, 3.49, 19.99, 4.99, 1.99, 2.29, 9.99, 29.99, 1.49],
        "sales_last_30_days": [34, 50, 12, 8, 29, 6, 41, 3, 4, 2],
        "last_sold_date": [
            "2026-06-01", "2026-06-02", "2026-05-28", "2026-05-21", "2026-06-03",
            "2026-04-20", "2026-06-04", "2026-03-10", "2026-05-01", "2026-02-15"
        ]
    })


# --------------------------------------------------
# Column Detection
# --------------------------------------------------

COLUMN_CANDIDATES = {
    "sku": ["sku", "product_id", "item_id", "upc", "barcode"],
    "product_name": ["product_name", "product", "item_name", "name", "description"],
    "category": ["category", "department", "product_category", "type"],
    "vendor": ["vendor", "supplier", "brand", "manufacturer"],
    "quantity_on_hand": [
        "quantity_on_hand", "stock", "inventory", "inventory_on_hand",
        "qty_on_hand", "quantity", "on_hand", "current_stock"
    ],
    "reorder_point": [
        "reorder_point", "reorder_level", "minimum_stock", "min_stock",
        "reorder_qty", "threshold"
    ],
    "target_stock": [
        "target_stock", "par_level", "max_stock", "ideal_stock", "restock_to"
    ],
    "unit_cost": ["unit_cost", "cost", "item_cost", "wholesale_cost"],
    "selling_price": ["selling_price", "price", "retail_price", "sale_price"],
    "sales_last_30_days": [
        "sales_last_30_days", "units_sold_30_days", "sold_last_30_days",
        "monthly_sales", "sales_30d", "units_sold"
    ],
    "last_sold_date": ["last_sold_date", "last_sale_date", "last_sold", "last_order_date"]
}


def find_best_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate

    return None


def default_mapping(df):
    mapping = {}

    for standard_field, candidates in COLUMN_CANDIDATES.items():
        found = find_best_column(df, candidates)
        mapping[standard_field] = found if found else "None"

    return mapping


def get_col(mapping, field):
    value = mapping.get(field, "None")
    return None if value == "None" else value


# --------------------------------------------------
# Inventory Modeling
# --------------------------------------------------

def build_inventory_model(df, mapping):
    sku_col = get_col(mapping, "sku")
    product_col = get_col(mapping, "product_name")
    category_col = get_col(mapping, "category")
    vendor_col = get_col(mapping, "vendor")
    quantity_col = get_col(mapping, "quantity_on_hand")
    reorder_col = get_col(mapping, "reorder_point")
    target_col = get_col(mapping, "target_stock")
    unit_cost_col = get_col(mapping, "unit_cost")
    price_col = get_col(mapping, "selling_price")
    sales_col = get_col(mapping, "sales_last_30_days")
    last_sold_col = get_col(mapping, "last_sold_date")

    inventory = pd.DataFrame()

    inventory["sku"] = df[sku_col].astype(str) if sku_col else [f"ITEM-{i + 1}" for i in range(len(df))]
    inventory["product_name"] = df[product_col].astype(str) if product_col else ""
    inventory["category"] = df[category_col].fillna("Unknown").astype(str) if category_col else "Unknown"
    inventory["vendor"] = df[vendor_col].fillna("Unknown").astype(str) if vendor_col else "Unknown"

    inventory["quantity_on_hand"] = safe_numeric(df[quantity_col]) if quantity_col else 0
    inventory["reorder_point"] = safe_numeric(df[reorder_col]) if reorder_col else 0
    inventory["target_stock"] = safe_numeric(df[target_col]) if target_col else inventory["reorder_point"] * 2

    inventory["unit_cost"] = safe_numeric(df[unit_cost_col]) if unit_cost_col else 0
    inventory["selling_price"] = safe_numeric(df[price_col]) if price_col else 0
    inventory["sales_last_30_days"] = safe_numeric(df[sales_col]) if sales_col else 0

    if last_sold_col:
        inventory["last_sold_date"] = safe_date(df[last_sold_col]).dt.strftime("%Y-%m-%d")
    else:
        inventory["last_sold_date"] = ""

    inventory["inventory_cost_value"] = inventory["quantity_on_hand"] * inventory["unit_cost"]
    inventory["inventory_retail_value"] = inventory["quantity_on_hand"] * inventory["selling_price"]
    inventory["gross_margin_per_unit"] = inventory["selling_price"] - inventory["unit_cost"]

    inventory["reorder_needed"] = inventory["quantity_on_hand"] <= inventory["reorder_point"]
    inventory["out_of_stock"] = inventory["quantity_on_hand"] <= 0
    inventory["low_stock"] = (inventory["quantity_on_hand"] > 0) & (inventory["quantity_on_hand"] <= inventory["reorder_point"])

    inventory["suggested_reorder_qty"] = inventory["target_stock"] - inventory["quantity_on_hand"]
    inventory.loc[inventory["suggested_reorder_qty"] < 0, "suggested_reorder_qty"] = 0

    inventory["days_of_supply"] = inventory.apply(
        lambda row: row["quantity_on_hand"] / (row["sales_last_30_days"] / 30)
        if row["sales_last_30_days"] > 0 else 999,
        axis=1
    )

    inventory["overstock_risk"] = (
        (inventory["quantity_on_hand"] > inventory["target_stock"] * 1.5)
        & (inventory["sales_last_30_days"] <= 5)
    )

    inventory["dead_stock_risk"] = (
        (inventory["quantity_on_hand"] > 0)
        & (inventory["sales_last_30_days"] <= 2)
    )

    inventory["inventory_status"] = inventory.apply(assign_inventory_status, axis=1)

    return inventory


def assign_inventory_status(row):
    if row["out_of_stock"]:
        return "Out of Stock"

    if row["low_stock"]:
        return "Low Stock"

    if row["overstock_risk"]:
        return "Overstock Risk"

    if row["dead_stock_risk"]:
        return "Dead Stock Risk"

    return "Healthy"


def build_category_summary(inventory):
    if inventory.empty:
        return pd.DataFrame()

    return (
        inventory
        .groupby("category", dropna=False)
        .agg(
            products=("sku", "nunique"),
            units_on_hand=("quantity_on_hand", "sum"),
            cost_value=("inventory_cost_value", "sum"),
            retail_value=("inventory_retail_value", "sum"),
            units_sold_30_days=("sales_last_30_days", "sum"),
            reorder_items=("reorder_needed", "sum"),
            out_of_stock_items=("out_of_stock", "sum"),
            overstock_items=("overstock_risk", "sum")
        )
        .reset_index()
        .sort_values("retail_value", ascending=False)
    )


def build_vendor_summary(inventory):
    if inventory.empty:
        return pd.DataFrame()

    return (
        inventory
        .groupby("vendor", dropna=False)
        .agg(
            products=("sku", "nunique"),
            units_on_hand=("quantity_on_hand", "sum"),
            cost_value=("inventory_cost_value", "sum"),
            retail_value=("inventory_retail_value", "sum"),
            reorder_items=("reorder_needed", "sum"),
            out_of_stock_items=("out_of_stock", "sum")
        )
        .reset_index()
        .sort_values("cost_value", ascending=False)
    )


def build_reorder_report(inventory):
    if inventory.empty:
        return pd.DataFrame()

    reorder = inventory[inventory["reorder_needed"] == True].copy()

    if reorder.empty:
        return pd.DataFrame()

    reorder["estimated_reorder_cost"] = reorder["suggested_reorder_qty"] * reorder["unit_cost"]

    return reorder[
        [
            "sku",
            "product_name",
            "category",
            "vendor",
            "quantity_on_hand",
            "reorder_point",
            "target_stock",
            "suggested_reorder_qty",
            "unit_cost",
            "estimated_reorder_cost",
            "inventory_status"
        ]
    ].sort_values("estimated_reorder_cost", ascending=False)


def build_inventory_issue_report(inventory, source_df):
    rows = []

    if inventory.empty:
        return pd.DataFrame()

    out_of_stock = int(inventory["out_of_stock"].sum())
    low_stock = int(inventory["low_stock"].sum())
    reorder_needed = int(inventory["reorder_needed"].sum())
    overstock = int(inventory["overstock_risk"].sum())
    dead_stock = int(inventory["dead_stock_risk"].sum())

    if out_of_stock > 0:
        rows.append({
            "Severity": "Must Fix",
            "Issue": "Out of Stock Products",
            "Count": out_of_stock,
            "Why It Matters": "Out-of-stock products can cause missed sales and customer frustration.",
            "Recommended Action": "Review reorder quantities and restock priority items."
        })

    if low_stock > 0:
        rows.append({
            "Severity": "Needs Review",
            "Issue": "Low Stock Products",
            "Count": low_stock,
            "Why It Matters": "Low-stock products may run out soon if sales continue.",
            "Recommended Action": "Review reorder points and upcoming demand."
        })

    if reorder_needed > 0:
        rows.append({
            "Severity": "Needs Review",
            "Issue": "Products Needing Reorder",
            "Count": reorder_needed,
            "Why It Matters": "These products are at or below their reorder threshold.",
            "Recommended Action": "Use the reorder report to plan replenishment."
        })

    if overstock > 0:
        rows.append({
            "Severity": "Warning",
            "Issue": "Overstock Risk",
            "Count": overstock,
            "Why It Matters": "Overstock ties up cash and storage space.",
            "Recommended Action": "Review slow-moving products and consider markdowns or promotions."
        })

    if dead_stock > 0:
        rows.append({
            "Severity": "Warning",
            "Issue": "Dead Stock Risk",
            "Count": dead_stock,
            "Why It Matters": "Dead stock may sit unsold and reduce inventory efficiency.",
            "Recommended Action": "Review demand, pricing, placement, or product discontinuation."
        })

    missing_product_names = get_missing_count(inventory["product_name"])

    if missing_product_names > 0:
        rows.append({
            "Severity": "Must Fix",
            "Issue": "Missing Product Names",
            "Count": missing_product_names,
            "Why It Matters": "Product names are needed for reports, ordering, and client readability.",
            "Recommended Action": "Fill missing product names before delivery."
        })

    duplicate_skus = int(inventory["sku"].dropna().astype(str).duplicated().sum())

    if duplicate_skus > 0:
        rows.append({
            "Severity": "Needs Review",
            "Issue": "Duplicate SKUs",
            "Count": duplicate_skus,
            "Why It Matters": "Duplicate SKUs can cause inventory counts and imports to be wrong.",
            "Recommended Action": "Review duplicate SKU records and confirm whether they should be merged."
        })

    if not rows:
        return pd.DataFrame(columns=[
            "Severity",
            "Issue",
            "Count",
            "Why It Matters",
            "Recommended Action"
        ])

    return pd.DataFrame(rows)


def build_action_plan(issue_report):
    rows = []

    if issue_report.empty:
        return pd.DataFrame([
            {
                "Priority": "Good",
                "Action": "Inventory file looks usable.",
                "Reason": "No major inventory risks were detected with the current checks."
            }
        ])

    if "Must Fix" in issue_report["Severity"].values:
        rows.append({
            "Priority": "1",
            "Action": "Fix out-of-stock and missing product issues first.",
            "Reason": "These issues directly affect sales, ordering, or report accuracy."
        })

    if "Needs Review" in issue_report["Severity"].values:
        rows.append({
            "Priority": "2",
            "Action": "Review low-stock items, reorder items, and duplicate SKUs.",
            "Reason": "These items may need restocking or cleanup before client delivery."
        })

    if "Warning" in issue_report["Severity"].values:
        rows.append({
            "Priority": "3",
            "Action": "Review overstock and dead stock risks.",
            "Reason": "These products may tie up cash or storage if demand is weak."
        })

    rows.append({
        "Priority": "4",
        "Action": "Download the inventory audit and reorder report.",
        "Reason": "The export gives the client a clear list of what to fix or restock."
    })

    return pd.DataFrame(rows)


def build_client_summary(metrics, issue_report):
    issue_lines = []

    if issue_report.empty:
        issue_lines.append("- No major inventory issues were detected.")
    else:
        for _, row in issue_report.iterrows():
            issue_lines.append(f"- {row['Issue']}: {row['Count']} item(s). {row['Recommended Action']}")

    summary = f"""
Clean0ps Inventory Summary

Inventory Overview:
Total Products: {metrics['total_products']:,}
Total Units On Hand: {metrics['total_units']:,.0f}
Inventory Cost Value: ${metrics['inventory_cost_value']:,.2f}
Inventory Retail Value: ${metrics['inventory_retail_value']:,.2f}
Potential Gross Margin: ${metrics['potential_margin']:,.2f}

Risk Summary:
Out of Stock Items: {metrics['out_of_stock_items']:,}
Low Stock Items: {metrics['low_stock_items']:,}
Items Needing Reorder: {metrics['reorder_items']:,}
Overstock Risk Items: {metrics['overstock_items']:,}
Dead Stock Risk Items: {metrics['dead_stock_items']:,}

Recommended Review:
{chr(10).join(issue_lines)}
"""

    return summary.strip()


def build_inventory_metrics(inventory):
    total_products = int(inventory["sku"].nunique()) if not inventory.empty else 0
    total_units = float(inventory["quantity_on_hand"].sum()) if not inventory.empty else 0
    inventory_cost_value = float(inventory["inventory_cost_value"].sum()) if not inventory.empty else 0
    inventory_retail_value = float(inventory["inventory_retail_value"].sum()) if not inventory.empty else 0
    potential_margin = inventory_retail_value - inventory_cost_value

    out_of_stock_items = int(inventory["out_of_stock"].sum()) if not inventory.empty else 0
    low_stock_items = int(inventory["low_stock"].sum()) if not inventory.empty else 0
    reorder_items = int(inventory["reorder_needed"].sum()) if not inventory.empty else 0
    overstock_items = int(inventory["overstock_risk"].sum()) if not inventory.empty else 0
    dead_stock_items = int(inventory["dead_stock_risk"].sum()) if not inventory.empty else 0

    return {
        "total_products": total_products,
        "total_units": total_units,
        "inventory_cost_value": inventory_cost_value,
        "inventory_retail_value": inventory_retail_value,
        "potential_margin": potential_margin,
        "out_of_stock_items": out_of_stock_items,
        "low_stock_items": low_stock_items,
        "reorder_items": reorder_items,
        "overstock_items": overstock_items,
        "dead_stock_items": dead_stock_items
    }


# --------------------------------------------------
# Page Intro
# --------------------------------------------------

section_title("Inventory Workflow")

w1, w2, w3, w4 = st.columns(4)

with w1:
    mini_card("STEP 1", "Load File")

with w2:
    mini_card("STEP 2", "Map Columns")

with w3:
    mini_card("STEP 3", "Review Risk")

with w4:
    mini_card("STEP 4", "Export Reports")


section_title("Demo Inventory File")

with st.expander("Download demo inventory dataset", expanded=False):
    demo_inventory = make_demo_inventory()

    st.download_button(
        label="📥 Download demo_inventory.csv",
        data=dataframe_to_csv_bytes(demo_inventory),
        file_name="demo_inventory.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# Load Data
# --------------------------------------------------

section_title("Load Inventory Data")

data_source = st.radio(
    "Choose data source",
    ["Use built-in demo data", "Upload CSV / Excel file"],
    horizontal=True
)

uploaded_file = None

try:
    if data_source == "Use built-in demo data":
        source_df = make_demo_inventory()
        source_name = "demo_inventory.csv"
    else:
        uploaded_file = st.file_uploader(
            "Upload inventory CSV or Excel file",
            type=["csv", "xlsx"]
        )

        if uploaded_file is None:
            st.info("Upload an inventory CSV or Excel file to begin.")
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
    # Column Mapping
    # --------------------------------------------------

    section_title("Column Mapping")

    st.write(
        "Map your source columns to standard inventory fields. Auto-detection handles common names, but you can override anything."
    )

    defaults = default_mapping(source_df)
    mapping = {}

    map_cols = st.columns(3)
    fields = list(COLUMN_CANDIDATES.keys())

    for index, field in enumerate(fields):
        options = ["None"] + source_df.columns.tolist()
        default_value = defaults.get(field, "None")
        default_index = options.index(default_value) if default_value in options else 0

        with map_cols[index % 3]:
            mapping[field] = st.selectbox(
                field,
                options,
                index=default_index,
                key=f"inventory_map_{field}"
            )

    with st.expander("Preview source file", expanded=False):
        st.dataframe(
            source_df.head(50),
            use_container_width=True
        )

    inventory = build_inventory_model(
        source_df,
        mapping
    )

    metrics = build_inventory_metrics(inventory)
    category_summary = build_category_summary(inventory)
    vendor_summary = build_vendor_summary(inventory)
    reorder_report = build_reorder_report(inventory)
    issue_report = build_inventory_issue_report(inventory, source_df)
    action_plan = build_action_plan(issue_report)
    column_summary = build_column_summary(source_df)
    basic_quality_issues = build_basic_quality_issues(source_df)
    quality_score = calculate_quality_score(source_df, basic_quality_issues)
    client_summary = build_client_summary(metrics, issue_report)

    # --------------------------------------------------
    # Inventory Overview
    # --------------------------------------------------

    section_title("Inventory Overview")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Products", f"{metrics['total_products']:,}")

    with m2:
        st.metric("Units On Hand", f"{metrics['total_units']:,.0f}")

    with m3:
        st.metric("Cost Value", f"${metrics['inventory_cost_value']:,.2f}")

    with m4:
        st.metric("Retail Value", f"${metrics['inventory_retail_value']:,.2f}")

    with m5:
        st.metric("Quality Score", f"{quality_score}%")

    r1, r2, r3, r4, r5 = st.columns(5)

    with r1:
        st.metric("Out of Stock", metrics["out_of_stock_items"])

    with r2:
        st.metric("Low Stock", metrics["low_stock_items"])

    with r3:
        st.metric("Reorder Items", metrics["reorder_items"])

    with r4:
        st.metric("Overstock Risk", metrics["overstock_items"])

    with r5:
        st.metric("Dead Stock Risk", metrics["dead_stock_items"])

    section_title("Client Action Plan")

    st.dataframe(
        action_plan,
        use_container_width=True
    )

    # --------------------------------------------------
    # Tabs
    # --------------------------------------------------

    section_title("Inventory Review")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Inventory Table",
        "Reorder Report",
        "Risk Issues",
        "Category Summary",
        "Vendor Summary",
        "Source Quality",
        "Client Summary"
    ])

    with tab1:
        st.dataframe(
            inventory,
            use_container_width=True
        )

    with tab2:
        if reorder_report.empty:
            st.success("No products currently need reorder based on the selected mapping.")
        else:
            st.dataframe(
                reorder_report,
                use_container_width=True
            )

    with tab3:
        if issue_report.empty:
            st.success("No major inventory risks were detected.")
        else:
            st.dataframe(
                issue_report,
                use_container_width=True
            )

    with tab4:
        if category_summary.empty:
            st.info("No category summary available.")
        else:
            st.dataframe(
                category_summary,
                use_container_width=True
            )

            st.bar_chart(
                category_summary.set_index("category")["retail_value"]
            )

    with tab5:
        if vendor_summary.empty:
            st.info("No vendor summary available.")
        else:
            st.dataframe(
                vendor_summary,
                use_container_width=True
            )

            st.bar_chart(
                vendor_summary.set_index("vendor")["cost_value"]
            )

    with tab6:
        st.subheader("Column Summary")
        st.dataframe(
            column_summary,
            use_container_width=True
        )

        st.subheader("Basic Quality Issues")
        if basic_quality_issues.empty:
            st.success("No basic source quality issues found.")
        else:
            st.dataframe(
                basic_quality_issues,
                use_container_width=True
            )

    with tab7:
        st.text_area(
            "Client-ready inventory summary",
            client_summary,
            height=360
        )

    # --------------------------------------------------
    # Downloads
    # --------------------------------------------------

    section_title("Download Inventory Deliverables")

    summary_report = pd.DataFrame([
        {"Metric": "Source File", "Value": source_name},
        {"Metric": "Total Products", "Value": metrics["total_products"]},
        {"Metric": "Total Units On Hand", "Value": metrics["total_units"]},
        {"Metric": "Inventory Cost Value", "Value": f"${metrics['inventory_cost_value']:,.2f}"},
        {"Metric": "Inventory Retail Value", "Value": f"${metrics['inventory_retail_value']:,.2f}"},
        {"Metric": "Potential Gross Margin", "Value": f"${metrics['potential_margin']:,.2f}"},
        {"Metric": "Out of Stock Items", "Value": metrics["out_of_stock_items"]},
        {"Metric": "Low Stock Items", "Value": metrics["low_stock_items"]},
        {"Metric": "Items Needing Reorder", "Value": metrics["reorder_items"]},
        {"Metric": "Overstock Risk Items", "Value": metrics["overstock_items"]},
        {"Metric": "Dead Stock Risk Items", "Value": metrics["dead_stock_items"]},
        {"Metric": "Source Quality Score", "Value": f"{quality_score}%"}
    ])

    excel_report = make_excel_bytes({
        "Summary": summary_report,
        "Client Summary": pd.DataFrame({"Summary": client_summary.splitlines()}),
        "Inventory Table": inventory,
        "Reorder Report": reorder_report,
        "Risk Issues": issue_report,
        "Action Plan": action_plan,
        "Category Summary": category_summary,
        "Vendor Summary": vendor_summary,
        "Source Column Summary": column_summary,
        "Source Quality Issues": basic_quality_issues
    })

    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="📥 Inventory Audit Excel",
            data=excel_report,
            file_name="clean0ps_inventory_audit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with d2:
        st.download_button(
            label="📥 Clean Inventory CSV",
            data=dataframe_to_csv_bytes(inventory),
            file_name="clean0ps_clean_inventory.csv",
            mime="text/csv"
        )

    with d3:
        st.download_button(
            label="📥 Reorder Report CSV",
            data=dataframe_to_csv_bytes(reorder_report),
            file_name="clean0ps_reorder_report.csv",
            mime="text/csv"
        )

except Exception as error:
    user_message, technical_message = get_friendly_error(error)

    section_title("Inventory Processing Error")

    st.error(user_message)

    if technical_message:
        with st.expander("Technical details", expanded=False):
            st.code(technical_message)
            
# busines# Clean0ps: Data Cleaning and E-commerce Analytics Toolkit

Clean0ps is a Python and Streamlit-based data cleaning, validation, and analytics toolkit designed to turn messy CSV and Excel files into clean, organized, client-ready deliverables.

The project started as a data cleaning tool for spreadsheet cleanup jobs, then expanded into a multi-purpose analytics toolkit with support for CRM lead lists, inventory files, data quality audits, and e-commerce analytics reporting.

## Project Purpose

Many small businesses, freelancers, and data teams deal with messy spreadsheets that are difficult to analyze or import into dashboards. These files often contain duplicate rows, blank values, inconsistent column names, missing required fields, poor formatting, or incomplete records.

Clean0ps solves this by helping users:

* Upload messy CSV or Excel files
* Clean and organize spreadsheet data
* Rename and standardize columns
* Validate data quality issues
* Generate records requiring review
* Export cleaned client-ready files
* Build e-commerce KPI dashboards
* Model e-commerce data into fact and dimension tables
* Export dashboard-ready reports and modeled tables

## Case Study: E-commerce Analytics Lab

### Problem

E-commerce brands often rely on multiple disconnected data sources, including orders, products, customers, web sessions, ad spend, and subscriptions. These datasets are commonly exported from different platforms and may not be ready for reporting.

A data consulting workflow usually needs to answer questions such as:

* Which marketing channels drive the most revenue?
* What is ROAS by channel?
* What is average order value?
* Which products perform best?
* What is customer lifetime value?
* What is the repeat purchase rate?
* What is the subscription churn rate?
* Are source tables clean enough to trust the dashboard?

### Solution

The E-commerce Analytics Lab inside Clean0ps allows users to load e-commerce datasets, assign each file to a source table, map raw columns into clean reporting fields, and generate modeled analytics tables.

The workflow follows an analytics engineering pattern:

```text
Raw Files
↓
Source Table Assignment
↓
Column Mapping
↓
Staging Logic
↓
Fact and Dimension Tables
↓
Model Validation Tests
↓
Dashboard KPIs
↓
Client Reports and Exports
```

### Modeled Tables

Clean0ps builds a star-schema-style reporting layer using fact and dimension tables.

#### Fact Tables

* `fact_orders`
* `fact_order_items`
* `fact_ad_spend`
* `fact_sessions`
* `fact_subscriptions`

#### Dimension Tables

* `dim_customers`
* `dim_products`
* `dim_channels`
* `dim_dates`

#### Reporting Models

* `channel_performance`
* `customer_ltv`
* `product_performance`
* `ecommerce_kpis`

## Key Metrics

The E-commerce Analytics Lab calculates core business KPIs, including:

* Revenue
* Total orders
* Average order value
* Customer count
* Customer lifetime value
* Repeat purchase rate
* Refund rate
* Ad spend
* ROAS
* CAC
* CPC
* CPM
* Sessions
* Conversion rate
* Active subscriptions
* Subscription churn
* Monthly recurring revenue

## Model Validation

Clean0ps includes validation checks designed to support accurate reporting.

Current validation checks include:

* Not-null checks
* Unique ID checks
* Non-negative value checks
* Relationship checks between facts and dimensions
* Accepted value checks for subscription status and conversion fields
* Orphan record detection
* Duplicate row detection
* Missing value detection

Examples:

```text
fact_orders.customer_id should exist in dim_customers.customer_id
fact_order_items.product_id should exist in dim_products.product_id
fact_order_items.order_id should exist in fact_orders.order_id
fact_subscriptions.customer_id should exist in dim_customers.customer_id
```

## Data Cleaning Features

The Template Cleaning Engine supports common spreadsheet cleanup workflows.

Features include:

* Remove blank rows
* Remove exact duplicate rows
* Clean column names
* Trim extra spaces from text fields
* Standardize dates when possible
* Keep or remove selected columns
* Rename columns for client delivery
* Sort rows
* Alphabetize columns
* Generate client summaries
* Export cleaned CSV and Excel files
* Export records requiring review
* Export audit reports

## Supported Workflows

Clean0ps currently supports multiple data workflows:

* Quick spreadsheet cleanup
* Business sales data
* Inventory and product data
* Lead list and CRM data
* Sports stats and player props
* NBA player reference data
* PDF and LLM extraction cleanup
* E-commerce analytics reporting

## Main App Pages

### Home

A simple overview of Clean0ps, what it does, and where users should start.

### Template Cleaning Engine

The main data cleaning workflow for uploading, cleaning, organizing, auditing, and exporting messy files.

### Data Quality Dashboard

Profiles datasets for quality risks, missing values, duplicate rows, column issues, text problems, date problems, and required field problems.

### Inventory Dashboard

Analyzes product and inventory files for stock levels, zero-stock items, low-stock items, overstock risk, reorder planning, inventory value, and inventory health.

### Validation Engine

Runs rule-based validation checks for selected data templates.

### E-commerce Analytics Lab

Builds e-commerce reporting models, validates relationships, calculates KPIs, creates dashboard views, and exports modeled tables and client reports.

## dbt-Style Model Layer

The repository includes a dbt-style model structure to show how the e-commerce workflow could translate into a warehouse-based analytics project.

```text
models/
├── staging/
│   ├── stg_orders.sql
│   ├── stg_order_items.sql
│   ├── stg_customers.sql
│   ├── stg_products.sql
│   ├── stg_ad_spend.sql
│   ├── stg_web_sessions.sql
│   └── stg_subscriptions.sql
├── marts/
│   ├── fct_orders.sql
│   ├── fct_order_items.sql
│   ├── fct_ad_spend.sql
│   ├── fct_sessions.sql
│   ├── fct_subscriptions.sql
│   ├── dim_customers.sql
│   ├── dim_products.sql
│   ├── dim_channels.sql
│   ├── dim_dates.sql
│   ├── channel_performance.sql
│   ├── customer_ltv.sql
│   ├── product_performance.sql
│   └── ecommerce_kpis.sql
└── schema.yml
```

The SQL models use BigQuery-style syntax and demonstrate analytics engineering concepts such as staging, fact tables, dimension tables, reporting marts, and model tests.

## Example SQL Model

```sql
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
    safe_divide(r.revenue, s.spend) as roas,
    safe_divide(s.spend, s.clicks) as cpc,
    safe_divide(s.spend, s.impressions) * 1000 as cpm

from spend_by_channel s

left join revenue_by_channel r
    on s.channel = r.channel;
```

## Screenshots

Add screenshots to the `assets/screenshots/` folder.

Recommended screenshots:

```text
assets/screenshots/home_page.png
assets/screenshots/template_cleaning_engine.png
assets/screenshots/data_quality_dashboard.png
assets/screenshots/inventory_dashboard.png
assets/screenshots/ecommerce_kpi_dashboard.png
assets/screenshots/ecommerce_model_validation.png
assets/screenshots/ecommerce_modeled_tables.png
assets/screenshots/ecommerce_sql_examples.png
```

## Tech Stack

* Python
* Streamlit
* Pandas
* OpenPyXL
* SQL
* dbt-style model organization
* BigQuery-style SQL syntax
* CSV and Excel file handling

## Project Structure

```text
business-analytics-toolkit/
├── clean0ps_ui.py
├── dashboard/
│   ├── app.py
│   └── pages/
│       ├── 1_Inventory_Dashboard.py
│       ├── 2_Data_Quality_Dashboard.py
│       ├── 3_Validation_Engine.py
│       ├── 4_Template Cleaning Engine.py
│       └── 5_Ecommerce_Analytics_Lab.py
├── models/
│   ├── staging/
│   ├── marts/
│   └── schema.yml
├── assets/
│   └── screenshots/
├── requirements.txt
└── README.md
```

## How to Run Locally

Clone the repository and install dependencies.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

If using `.venv`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

## Example Use Case

A client provides messy e-commerce exports:

* `orders.csv`
* `order_items.csv`
* `customers.csv`
* `products.csv`
* `ad_spend.csv`
* `web_sessions.csv`
* `subscriptions.csv`

Clean0ps can:

1. Load the files
2. Assign each file to a source table
3. Map messy columns to standard reporting fields
4. Build fact and dimension tables
5. Run validation tests
6. Calculate KPIs
7. Display dashboard views
8. Export modeled tables
9. Export a client-ready analytics report

## Portfolio Value

This project demonstrates practical skills in:

* Data cleaning
* Data validation
* Data profiling
* Dashboard development
* E-commerce analytics
* KPI design
* SQL modeling
* Star schema design
* Fact and dimension modeling
* Client-ready reporting
* Analytics engineering concepts
* Business intelligence workflows

## Future Improvements

Planned improvements include:

* Add real dbt project configuration
* Add DuckDB or PostgreSQL execution for local SQL models
* Add BigQuery deployment notes
* Add more advanced dashboard filters
* Add saved project sessions
* Add user authentication
* Add automated report generation
* Add scheduled data refresh workflows
* Add Looker Studio export examples
* Add more sample datasets

## Status

Clean0ps is currently a portfolio-ready MVP focused on data cleaning, validation, and e-commerce analytics workflows.

It is not yet a full SaaS product, but it demonstrates a realistic analytics workflow from messy raw files to clean reporting outputs.
s-analytics-toolkit
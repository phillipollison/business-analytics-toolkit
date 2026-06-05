# Clean0ps: Data Cleaning, Validation, and Automation Toolkit

Clean0ps is a Python and Streamlit-based data cleaning and analytics toolkit designed to turn messy CSV, Excel, extracted PDF, inventory, e-commerce, and API data into clean, validated, client-ready outputs.

The project was built to solve a common real-world problem: businesses often receive messy files from different systems, vendors, exports, PDFs, CRMs, inventory tools, and APIs. Before the data can be used for reporting, automation, or decision-making, it has to be cleaned, standardized, validated, reviewed, and exported in a reliable format.

Clean0ps brings those workflows into one application.

---

## Project Overview

Clean0ps supports multiple data workflows:

* General CSV and Excel cleanup
* Data quality auditing and validation
* Inventory analysis and reorder review
* E-commerce analytics modeling
* PDF / LLM / OCR extraction cleanup
* Local API automation with scheduled output generation
* Client-ready CSV, Excel, TXT, and ZIP deliverables

The goal of this project is not just to display data. The goal is to help users move from messy input files to reliable output files with a clear audit trail.

---

## Why This Project Matters

Many data projects fail before analysis even begins because the input data is inconsistent, incomplete, duplicated, poorly named, or incorrectly formatted.

Clean0ps focuses on the practical first mile of analytics work:

1. Read messy data
2. Normalize fields
3. Detect data quality issues
4. Separate safe fixes from manual-review items
5. Generate cleaned outputs
6. Export audit-ready deliverables
7. Support repeatable workflows

This project demonstrates skills in data cleaning, validation, backend logic, UI design, file processing, automation, reporting, and production-oriented project organization.

---

## Core Features

### Template Cleaning Engine

The Template Cleaning Engine is the main cleaning workflow for messy CSV and Excel files.

It can:

* Clean column names
* Remove completely blank rows
* Remove exact duplicate rows
* Drop empty columns
* Trim extra spaces from text fields
* Standardize date-like columns
* Standardize email and phone fields
* Rename selected columns
* Sort rows
* Reorder columns
* Create rows-needing-review reports
* Export cleaned files and audit reports

This workflow is useful for freelance data cleanup, CRM cleanup, spreadsheet preparation, business reporting, and client-ready file delivery.

---

### Data Quality + Validation Dashboard

The Data Quality + Validation page reviews a file for common data problems before it is used for analysis or reporting.

It checks for:

* Missing values
* Duplicate rows
* Empty columns
* Risky fields
* Required field issues
* Invalid formats
* Basic quality score
* Column-level summaries

Outputs include quality reports, issue summaries, and cleaned exports.

---

### Inventory Dashboard

The Inventory Dashboard helps analyze product and stock data.

It supports:

* Product-level inventory review
* Low-stock detection
* Out-of-stock risk
* Overstock risk
* Inventory value estimates
* Reorder planning
* Category-level summaries
* Inventory audit exports

This workflow is designed for product catalogs, SKU lists, stock exports, retail operations, and vendor files.

---

### E-commerce Analytics Lab

The E-commerce Analytics Lab models raw e-commerce files into reporting-ready tables.

It supports source files such as:

* Orders
* Order items
* Customers
* Products
* Ad spend
* Web sessions
* Subscriptions

It calculates business metrics including:

* Revenue
* Orders
* Average order value
* Customer count
* ROAS
* CAC
* LTV
* Conversion rate
* Repeat purchase rate
* Refund rate
* Churn rate
* MRR
* Product performance

It also includes dbt and BigQuery-style SQL examples to show how the modeled logic could be translated into analytics engineering workflows.

---

### Document Standards Cleanup Lab

The Document Standards Cleanup Lab supports structured data extracted from PDFs, standards documents, OCR tools, or LLM ingestion workflows.

It is designed for records that include fields such as:

* Document name
* Page number
* Section ID
* Section title
* Requirement text
* Extracted value
* Unit
* Category
* Confidence score
* Review status
* Source verification status
* Review notes

It flags:

* Missing document names
* Invalid page numbers
* Missing section IDs
* Missing requirement text
* Duplicate section IDs
* Low-confidence extraction rows
* Unverified source records
* Unexpected review statuses
* Blank extracted values

This workflow is useful for PDF extraction cleanup, LLM output validation, standards document review, and database-ready publishing workflows.

---

### Scheduled Data Automation Lab

The Scheduled Data Automation Lab supports lightweight API-to-local-output automation.

It can:

* Read configurable API source settings
* Pull structured data from approved API endpoints
* Normalize API response fields
* Remove exact duplicates
* Remove key-based duplicates
* Validate required fields
* Log source errors
* Save local CSV outputs
* Save Excel audit reports
* Run manually
* Run on a schedule with cron

The current production-ready V1 focuses on local outputs. Google Sheets integration is intentionally paused for now to keep the workflow simpler and safer while the core automation logic is tested.

---

## Technical Stack

### Application

* Python
* Streamlit
* Pandas

### File Processing

* CSV
* Excel
* OpenPyXL
* XlsxWriter

### Automation

* Python scripts
* Configurable JSON settings
* API requests
* Local output generation
* Cron scheduling support

### Testing and Reliability

* Pytest
* Compile health check script
* Local error logging
* Local event logging
* Config validation
* Workflow reset controls
* Privacy notices

---

## Project Structure

```text
business-analytics-toolkit/
├── automation/
│   ├── configs/
│   │   └── config.example.json
│   ├── outputs/
│   ├── locks/
│   ├── __init__.py
│   ├── workflow.py
│   └── run_daily.py
│
├── dashboard/
│   ├── app.py
│   └── pages/
│       ├── 1_Inventory_Dashboard.py
│       ├── 2_Data_Quality_Dashboard.py
│       ├── 4_Template Cleaning Engine.py
│       ├── 5_Ecommerce_Analytics_Lab.py
│       ├── 6_Document_Standards_Cleanup_Lab.py
│       └── 7_Scheduled_Data_Automation_Lab.py
│
├── docs/
│   └── production_automation_setup.md
│
├── logs/
│   └── .gitkeep
│
├── scripts/
│   ├── health_check.py
│   ├── install_clean0ps_cron.sh
│   └── view_logs.py
│
├── tests/
│   ├── test_clean0ps_core.py
│   ├── test_health_compile.py
│   └── test_production_automation.py
│
├── clean0ps_core.py
├── clean0ps_ui.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## How to Run the App

Clone the project and move into the project folder:

```bash
cd business-analytics-toolkit
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the Streamlit app:

```bash
python3 -m streamlit run dashboard/app.py --server.port 8503
```

Open the app in your browser:

```text
http://localhost:8503
```

---

## Running the Health Check

Clean0ps includes a health check script that compiles key files and runs tests.

```bash
python3 scripts/health_check.py
```

A successful check should show that all compile checks and tests passed.

---

## Running Local API Automation

The local automation workflow uses a configurable JSON file.

Run the demo automation:

```bash
python3 -m automation.run_daily --config automation/configs/config.example.json
```

Outputs are saved to:

```text
automation/outputs/
```

Each run generates a folder containing:

* `cleaned_output.csv`
* `validation_issues.csv`
* `run_summary.csv`
* `source_errors.csv`
* `automation_report.xlsx`

---

## Scheduling the Automation

Clean0ps includes a cron installer script for daily local automation.

```bash
bash scripts/install_clean0ps_cron.sh
```

The scheduled workflow can be inspected with:

```bash
crontab -l
```

Cron logs are written to:

```text
logs/automation_cron.log
```

---

## Privacy Notice

Clean0ps is designed to process files during the current app session. Uploaded files are not permanently stored by default.

Users should avoid uploading sensitive data unless they trust the environment where the app is running.

Generated local outputs, logs, and temporary files are excluded from Git tracking through `.gitignore`.

---

## Production Readiness

Clean0ps includes several production-oriented features:

* Shared backend utilities
* Shared UI components
* Health check script
* Unit tests
* Local error logging
* Local event logging
* Privacy notice
* Reset workflow buttons
* Configurable automation settings
* Local output folders
* Lock file for scheduled automation
* Git hygiene through `.gitignore`
* Example environment file
* Streamlit theme configuration

Current production readiness focus:

| Area                                | Status                              |
| ----------------------------------- | ----------------------------------- |
| CSV / Excel cleaning                | Ready                               |
| Data quality validation             | Ready                               |
| Inventory analysis                  | Ready                               |
| E-commerce analytics modeling       | Working V1                          |
| PDF / LLM extraction cleanup        | Working V1                          |
| API to local CSV / Excel automation | Production-ready V1 after test run  |
| Scheduled local workflow            | Production-ready V1 after cron test |
| Google Sheets automation            | Paused                              |
| Enterprise SaaS platform            | Future roadmap                      |

---

## Testing

Run all tests:

```bash
python3 -m pytest -q
```

Run the full health check:

```bash
python3 scripts/health_check.py
```

Tests currently cover:

* Column cleaning
* Duplicate handling
* Missing value detection
* Excel export generation
* ZIP export generation
* Quality score calculation
* Automation config validation
* API response extraction
* Required field validation
* Application file compilation

---

## Example Use Cases

Clean0ps can support jobs such as:

* Clean this messy CSV file
* Remove duplicates from a CRM export
* Format an Excel file for client delivery
* Audit a dataset for missing values
* Prepare product inventory for reporting
* Analyze e-commerce orders and customers
* Validate LLM-extracted PDF data
* Create database-ready records from standards documents
* Pull structured API data and generate daily local outputs
* Build repeatable data cleaning workflows

---

## What I Learned Building This

This project strengthened my experience with:

* Python application structure
* Streamlit dashboards
* Pandas data cleaning
* CSV and Excel processing
* Data validation logic
* File export workflows
* Error handling
* Logging
* Unit testing
* Automation scripts
* Config-driven workflows
* Analytics modeling
* Business-facing reporting
* Product thinking

It also helped me think about how real users interact with data tools: they need clear workflows, reliable outputs, understandable errors, and reports they can actually send to someone else.

---

## Future Roadmap

Planned improvements include:

* Google Sheets integration
* More API connector templates
* Saved project sessions
* User authentication
* Cloud deployment
* Background job processing
* Role-based workspaces
* More advanced data profiling
* Larger-file performance improvements
* Better table editing
* More downloadable case studies
* Screenshot-based portfolio documentation

---

## Project Positioning

Clean0ps is a practical data operations project. It combines data cleaning, validation, analytics, automation, and reporting into one workflow-focused application.

It demonstrates the ability to think beyond a single script and build a tool that helps users complete real data tasks from start to finish.

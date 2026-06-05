import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


def clean_column_name(value):
    text = str(value).strip().lower()
    text = text.replace(" ", "_").replace("-", "_")
    text = "".join(char if char.isalnum() or char == "_" else "_" for char in text)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_") or "unnamed_column"


def normalize_columns(df):
    cleaned = df.copy()
    cleaned.columns = [clean_column_name(col) for col in cleaned.columns]
    return cleaned


def load_config(config_path):
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_records_from_response(response_json, record_path=""):
    if record_path:
        current = response_json

        for part in record_path.split("."):
            if isinstance(current, dict):
                current = current.get(part, [])
            else:
                current = []

        response_json = current

    if isinstance(response_json, list):
        return response_json

    if isinstance(response_json, dict):
        for key in ["data", "results", "items", "records"]:
            if key in response_json and isinstance(response_json[key], list):
                return response_json[key]
        return [response_json]

    return []


def fetch_api_source(source):
    method = source.get("method", "GET").upper()

    if method != "GET":
        raise ValueError("This V1 automation runner supports GET requests only.")

    url = source.get("url", "")
    headers = source.get("headers", {})
    params = source.get("params", {})
    timeout_seconds = int(source.get("timeout_seconds", 30))
    record_path = source.get("record_path", "")

    if not url:
        raise ValueError(f"Source {source.get('name', 'unknown')} is missing a URL.")

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=timeout_seconds
    )

    response.raise_for_status()

    records = extract_records_from_response(
        response.json(),
        record_path
    )

    if not records:
        return pd.DataFrame()

    return pd.json_normalize(records)


def normalize_source_records(df, source):
    if df.empty:
        return df

    normalized = normalize_columns(df)
    source_name = source.get("name", "unknown_source")

    field_map = {
        clean_column_name(old): new
        for old, new in source.get("field_map", {}).items()
    }

    normalized = normalized.rename(columns=field_map)

    normalized["source_name"] = source_name
    normalized["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    selected_fields = source.get("selected_fields", [])

    if selected_fields:
        for field in selected_fields:
            if field not in normalized.columns:
                normalized[field] = ""

        normalized = normalized[selected_fields]

    return normalized.reset_index(drop=True)


def remove_duplicate_records(df, dedupe_keys):
    if df.empty:
        return df, 0, 0

    exact_duplicates = int(df.duplicated().sum())
    cleaned = df.drop_duplicates().reset_index(drop=True)

    valid_keys = [key for key in dedupe_keys if key in cleaned.columns]
    key_duplicates = 0

    if valid_keys:
        key_duplicates = int(cleaned.duplicated(subset=valid_keys).sum())
        cleaned = cleaned.drop_duplicates(
            subset=valid_keys,
            keep="first"
        ).reset_index(drop=True)

    return cleaned, exact_duplicates, key_duplicates


def is_missing(series):
    return (
        series.isna()
        | series.astype(str).str.strip().str.lower().isin(["", "nan", "none", "null", "n/a", "na"])
    )


def validate_required_fields(df, required_fields):
    rows = []

    for field in required_fields:
        if field not in df.columns:
            rows.append({
                "Severity": "Critical",
                "Issue": "Missing Required Column",
                "Field": field,
                "Row Number": "",
                "Recommendation": f"Add required column: {field}"
            })
            continue

        missing = is_missing(df[field])

        for index in df[missing].index:
            rows.append({
                "Severity": "Critical",
                "Issue": "Missing Required Value",
                "Field": field,
                "Row Number": int(index) + 2,
                "Recommendation": f"Fill {field} or remove the record."
            })

    return pd.DataFrame(rows)


def write_outputs(config, cleaned_df, validation_df, summary_df, source_errors_df):
    output_dir = Path(config.get("local_outputs", {}).get("output_dir", "automation/outputs"))
    run_dir = output_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = run_dir / "cleaned_output.csv"
    validation_path = run_dir / "validation_issues.csv"
    summary_path = run_dir / "run_summary.csv"
    errors_path = run_dir / "source_errors.csv"
    excel_path = run_dir / "automation_report.xlsx"

    cleaned_df.to_csv(cleaned_path, index=False)
    validation_df.to_csv(validation_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    source_errors_df.to_csv(errors_path, index=False)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        cleaned_df.to_excel(writer, sheet_name="Cleaned Output", index=False)
        validation_df.to_excel(writer, sheet_name="Validation Issues", index=False)
        summary_df.to_excel(writer, sheet_name="Run Summary", index=False)
        source_errors_df.to_excel(writer, sheet_name="Source Errors", index=False)

    return {
        "run_dir": str(run_dir),
        "cleaned_output": str(cleaned_path),
        "validation_issues": str(validation_path),
        "run_summary": str(summary_path),
        "source_errors": str(errors_path),
        "excel_report": str(excel_path)
    }


def run_configured_automation(config_path):
    config = load_config(config_path)

    frames = []
    source_errors = []

    for source in config.get("sources", []):
        if not source.get("enabled", True):
            continue

        try:
            raw_df = fetch_api_source(source)
            normalized_df = normalize_source_records(raw_df, source)
            frames.append(normalized_df)

        except Exception as error:
            source_errors.append({
                "Source": source.get("name", "unknown"),
                "Error": str(error)
            })

    if frames:
        raw_combined = pd.concat(frames, ignore_index=True)
    else:
        raw_combined = pd.DataFrame()

    cleaned_df, exact_dupes, key_dupes = remove_duplicate_records(
        raw_combined,
        config.get("dedupe_keys", [])
    )

    validation_df = validate_required_fields(
        cleaned_df,
        config.get("required_fields", [])
    )

    source_errors_df = pd.DataFrame(source_errors)

    summary_df = pd.DataFrame([
        {"Metric": "Workflow Name", "Value": config.get("workflow_name", "Clean0ps Automation")},
        {"Metric": "Run Timestamp", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"Metric": "Raw Records", "Value": len(raw_combined)},
        {"Metric": "Cleaned Records", "Value": len(cleaned_df)},
        {"Metric": "Exact Duplicates Removed", "Value": exact_dupes},
        {"Metric": "Key Duplicates Removed", "Value": key_dupes},
        {"Metric": "Validation Issues", "Value": len(validation_df)},
        {"Metric": "Source Errors", "Value": len(source_errors_df)}
    ])

    output_paths = write_outputs(
        config,
        cleaned_df,
        validation_df,
        summary_df,
        source_errors_df
    )

    return {
        "raw_data": raw_combined,
        "cleaned_data": cleaned_df,
        "validation_issues": validation_df,
        "source_errors": source_errors_df,
        "summary": summary_df,
        "output_paths": output_paths
    }


def make_client_summary(result):
    return f"""
Clean0ps Local API Automation Summary

Cleaned Records: {len(result["cleaned_data"]):,}
Validation Issues: {len(result["validation_issues"]):,}
Source Errors: {len(result["source_errors"]):,}

Output Folder:
{result["output_paths"].get("run_dir", "")}

Recommended Next Step:
Review validation issues and source errors before using the cleaned output for reporting or delivery.
""".strip()

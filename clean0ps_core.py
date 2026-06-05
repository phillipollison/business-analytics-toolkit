import io
import re
import zipfile
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import pandas as pd


@dataclass
class Clean0psError(Exception):
    user_message: str
    technical_message: str = ""

    def __str__(self):
        if self.technical_message:
            return f"{self.user_message}\n\nTechnical details: {self.technical_message}"
        return self.user_message


def clean_column_name(column_name) -> str:
    cleaned = str(column_name).strip().lower()
    cleaned = cleaned.replace(" ", "_")
    cleaned = cleaned.replace("-", "_")
    cleaned = re.sub(r"[^\w_]", "", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned.strip("_")

    if cleaned == "":
        cleaned = "unnamed_column"

    return cleaned


def pretty_column_name(column_name) -> str:
    words = str(column_name).replace("_", " ").strip().split()
    return " ".join(word.capitalize() for word in words)


def make_column_names_unique(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()
    seen = {}
    new_columns = []

    for col in new_df.columns:
        base = str(col).strip()

        if base == "":
            base = "unnamed_column"

        if base not in seen:
            seen[base] = 0
            new_columns.append(base)
        else:
            seen[base] += 1
            new_columns.append(f"{base}_{seen[base]}")

    new_df.columns = new_columns
    return new_df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = make_column_names_unique(df.copy())
    normalized_df.columns = [clean_column_name(col) for col in normalized_df.columns]
    normalized_df = make_column_names_unique(normalized_df)
    return normalized_df


def validate_dataframe(df: pd.DataFrame) -> None:
    if df is None:
        raise Clean0psError(
            user_message="The file could not be loaded into a usable table.",
            technical_message="DataFrame was None."
        )

    if df.empty:
        raise Clean0psError(
            user_message="The uploaded file is empty. Upload a file with at least one row of data.",
            technical_message="DataFrame was empty."
        )

    if len(df.columns) == 0:
        raise Clean0psError(
            user_message="The uploaded file does not contain usable columns.",
            technical_message="DataFrame had zero columns."
        )


def read_uploaded_file(uploaded_file, normalize: bool = True) -> pd.DataFrame:
    if uploaded_file is None:
        raise Clean0psError(
            user_message="No file was uploaded.",
            technical_message="uploaded_file was None."
        )

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin1")

        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        else:
            raise Clean0psError(
                user_message="Unsupported file type. Please upload a CSV or Excel file.",
                technical_message=f"Unsupported file name: {uploaded_file.name}"
            )

    except Clean0psError:
        raise

    except Exception as error:
        raise Clean0psError(
            user_message="Clean0ps could not read this file. Check that it is not corrupted, password-protected, or saved in an unsupported format.",
            technical_message=str(error)
        )

    validate_dataframe(df)

    df = make_column_names_unique(df)

    if normalize:
        df = normalize_columns(df)

    return df


def read_multiple_uploaded_files(uploaded_files, normalize: bool = True) -> Dict[str, pd.DataFrame]:
    if not uploaded_files:
        raise Clean0psError(
            user_message="No files were uploaded.",
            technical_message="uploaded_files was empty."
        )

    files = {}

    for uploaded_file in uploaded_files:
        files[uploaded_file.name] = read_uploaded_file(uploaded_file, normalize=normalize)

    return files


def check_file_size(df: pd.DataFrame) -> Dict[str, object]:
    rows = len(df)
    columns = len(df.columns)

    warnings = []

    if rows > 250_000:
        warnings.append("This file has more than 250,000 rows. Processing and exporting may be slow.")
    elif rows > 100_000:
        warnings.append("This file has more than 100,000 rows. Previews will be limited, but exports should still work.")

    if columns > 100:
        warnings.append("This file has more than 100 columns. Consider removing unused columns before final delivery.")

    return {
        "rows": rows,
        "columns": columns,
        "warnings": warnings
    }


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def safe_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def missing_mask(series: pd.Series) -> pd.Series:
    return (
        series.isnull()
        | series.astype(str).str.strip().eq("")
        | series.astype(str).str.lower().isin(
            ["nan", "none", "null", "n/a", "na", "unknown", "-"]
        )
    )


def get_missing_count(series: pd.Series) -> int:
    return int(missing_mask(series).sum())


def get_total_missing_values(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    return int(sum(get_missing_count(df[col]) for col in df.columns))


def get_duplicate_row_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    return int(df.duplicated().sum())


def get_duplicate_rows(df: pd.DataFrame, keep: bool = False) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    return df[df.duplicated(keep=keep)].copy()


def trim_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()

    for col in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        cleaned_df[col] = cleaned_df[col].replace(
            ["nan", "None", "NONE", "null", "NULL", "", "N/A", "n/a", "NA", "na"],
            pd.NA
        )

    return cleaned_df


def remove_blank_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)


def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def standardize_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()

    date_keywords = [
        "date", "created", "updated", "timestamp", "time",
        "birthdate", "game_date", "sale_date", "order_date",
        "start_date", "cancel_date"
    ]

    for col in cleaned_df.columns:
        if any(keyword in col.lower() for keyword in date_keywords):
            parsed = pd.to_datetime(cleaned_df[col], errors="coerce")

            if len(parsed) > 0 and parsed.notna().mean() >= 0.50:
                cleaned_df[col] = parsed.dt.strftime("%Y-%m-%d")

    return cleaned_df


def safe_clean_dataframe(
    df: pd.DataFrame,
    clean_columns: bool = True,
    trim_text: bool = True,
    remove_blanks: bool = True,
    remove_duplicates: bool = False,
    standardize_dates: bool = True
) -> pd.DataFrame:
    cleaned_df = df.copy()

    validate_dataframe(cleaned_df)

    if clean_columns:
        cleaned_df = normalize_columns(cleaned_df)
    else:
        cleaned_df = make_column_names_unique(cleaned_df)

    if trim_text:
        cleaned_df = trim_text_columns(cleaned_df)

    if remove_blanks:
        cleaned_df = remove_blank_rows(cleaned_df)

    if standardize_dates:
        cleaned_df = standardize_date_columns(cleaned_df)

    if remove_duplicates:
        cleaned_df = remove_exact_duplicates(cleaned_df)

    if cleaned_df.empty:
        raise Clean0psError(
            user_message="After cleaning, the dataset has no rows left. Check whether the uploaded file only contained blank rows.",
            technical_message="DataFrame became empty after cleaning."
        )

    return cleaned_df.reset_index(drop=True)


def build_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for col in df.columns:
        missing_count = get_missing_count(df[col])
        missing_percent = (missing_count / max(len(df), 1)) * 100

        non_null_values = df[col].dropna()
        example_value = ""

        if len(non_null_values) > 0:
            example_value = str(non_null_values.iloc[0])

        rows.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing Values": missing_count,
            "Missing %": f"{missing_percent:.1f}%",
            "Unique Values": int(df[col].nunique(dropna=True)),
            "Example Value": example_value
        })

    return pd.DataFrame(rows)


def build_missing_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for col in df.columns:
        missing_count = get_missing_count(df[col])

        if missing_count > 0:
            missing_percent = (missing_count / max(len(df), 1)) * 100

            rows.append({
                "Column": col,
                "Missing Values": missing_count,
                "Missing %": f"{missing_percent:.1f}%"
            })

    return pd.DataFrame(rows)


def build_basic_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    duplicate_count = get_duplicate_row_count(df)

    if duplicate_count > 0:
        rows.append({
            "Severity": "Must Fix",
            "Issue": "Duplicate Rows",
            "Field": "Full Row",
            "Count": duplicate_count,
            "Why It Matters": "Duplicate rows can inflate totals, distort averages, and create inaccurate reporting.",
            "Recommended Action": "Review and remove repeated records before analysis or client delivery."
        })

    for col in df.columns:
        missing_count = get_missing_count(df[col])
        missing_percent = (missing_count / max(len(df), 1)) * 100

        if missing_percent == 100:
            rows.append({
                "Severity": "Must Fix",
                "Issue": "Completely Empty Column",
                "Field": col,
                "Count": missing_count,
                "Why It Matters": "Completely empty columns add no usable information.",
                "Recommended Action": "Remove this column unless it is required later."
            })

        elif missing_percent >= 75:
            rows.append({
                "Severity": "Needs Review",
                "Issue": "Mostly Empty Column",
                "Field": col,
                "Count": missing_count,
                "Why It Matters": "Mostly empty columns may be optional, incomplete, or poorly extracted.",
                "Recommended Action": "Decide whether this field should be removed, filled, or kept."
            })

        elif missing_percent >= 25:
            rows.append({
                "Severity": "Warning",
                "Issue": "High Missing Values",
                "Field": col,
                "Count": missing_count,
                "Why It Matters": "High missing values can reduce reporting accuracy.",
                "Recommended Action": "Review whether missing values are expected."
            })

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    for col in numeric_columns:
        negative_count = int((df[col] < 0).sum())

        if negative_count > 0:
            rows.append({
                "Severity": "Needs Review",
                "Issue": "Negative Values",
                "Field": col,
                "Count": negative_count,
                "Why It Matters": "Negative values may be invalid depending on the field.",
                "Recommended Action": "Review negative values against the source file."
            })

    if not rows:
        return pd.DataFrame(columns=[
            "Severity", "Issue", "Field", "Count",
            "Why It Matters", "Recommended Action"
        ])

    return pd.DataFrame(rows)


def calculate_quality_score(df: pd.DataFrame, issue_report: Optional[pd.DataFrame] = None) -> int:
    if df.empty:
        return 0

    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = max(total_rows * max(total_columns, 1), 1)

    missing_values = get_total_missing_values(df)
    duplicate_rows = get_duplicate_row_count(df)

    score = 100
    score -= (missing_values / total_cells) * 35
    score -= (duplicate_rows / max(total_rows, 1)) * 30

    if issue_report is not None and not issue_report.empty:
        if "Severity" in issue_report.columns and "Count" in issue_report.columns:
            must_fix_count = int(issue_report[issue_report["Severity"] == "Must Fix"]["Count"].sum())
            review_count = int(issue_report[issue_report["Severity"].isin(["Needs Review", "Manual Review Needed"])]["Count"].sum())
            warning_count = int(issue_report[issue_report["Severity"].isin(["Warning", "Optional Improvement"])]["Count"].sum())

            score -= (must_fix_count / total_cells) * 80
            score -= (review_count / total_cells) * 40
            score -= (warning_count / total_cells) * 15

    return max(0, round(score))


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text: str) -> bytes:
    return str(text).encode("utf-8")


def make_excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()

    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet_name, dataframe in sheets.items():
                safe_sheet_name = str(sheet_name)[:31]

                if dataframe is None:
                    dataframe = pd.DataFrame()

                dataframe.to_excel(writer, sheet_name=safe_sheet_name, index=False)

    except Exception as error:
        raise Clean0psError(
            user_message="Clean0ps could not create the Excel export.",
            technical_message=str(error)
        )

    output.seek(0)
    return output.getvalue()


def make_zip_bytes(files: Dict[str, bytes]) -> bytes:
    output = io.BytesIO()

    try:
        with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for file_name, file_bytes in files.items():
                zip_file.writestr(file_name, file_bytes)

    except Exception as error:
        raise Clean0psError(
            user_message="Clean0ps could not create the ZIP export.",
            technical_message=str(error)
        )

    output.seek(0)
    return output.getvalue()


def make_dataframe_zip(dataframes: Dict[str, pd.DataFrame]) -> bytes:
    files = {}

    for name, df in dataframes.items():
        if df is not None and not df.empty:
            files[f"{name}.csv"] = dataframe_to_csv_bytes(df)

    return make_zip_bytes(files)


def get_friendly_error(error: Exception) -> Tuple[str, str]:
    if isinstance(error, Clean0psError):
        return error.user_message, error.technical_message

    return (
        "Clean0ps ran into a problem while processing this file.",
        str(error)
    )
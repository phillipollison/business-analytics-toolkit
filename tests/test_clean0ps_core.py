import io
import zipfile

import pandas as pd

import clean0ps_core as core


def test_clean_column_name_basic():
    assert core.clean_column_name(" Customer Name ") == "customer_name"
    assert core.clean_column_name("Order-Date!") == "order_date"
    assert core.clean_column_name("") == "unnamed_column"


def test_normalize_columns_handles_duplicates():
    df = pd.DataFrame([[1, 2]], columns=["Customer Name", "Customer Name"])
    result = core.normalize_columns(df)

    assert len(result.columns) == 2
    assert result.columns[0] == "customer_name"
    assert result.columns[1] != result.columns[0]


def test_missing_mask_common_missing_values():
    series = pd.Series(["", " ", None, "N/A", "null", "value"])
    mask = core.missing_mask(series)

    assert int(mask.sum()) == 5


def test_safe_clean_dataframe_removes_blank_and_duplicates():
    df = pd.DataFrame({
        " Name ": [" Phillip ", " Phillip ", None],
        "Value": [10, 10, None],
    })

    cleaned = core.safe_clean_dataframe(
        df,
        clean_columns=True,
        trim_text=True,
        remove_blanks=True,
        remove_duplicates=True,
        standardize_dates=True
    )

    assert len(cleaned) == 1
    assert "name" in cleaned.columns
    assert cleaned.loc[0, "name"] == "Phillip"


def test_build_column_summary():
    df = pd.DataFrame({
        "name": ["A", None],
        "amount": [10, 20],
    })

    summary = core.build_column_summary(df)

    assert "Column" in summary.columns
    assert len(summary) == 2


def test_build_basic_quality_issues_detects_duplicates():
    df = pd.DataFrame({
        "name": ["A", "A"],
        "amount": [10, 10],
    })

    issues = core.build_basic_quality_issues(df)

    assert not issues.empty
    assert "Duplicate Rows" in issues["Issue"].tolist()


def test_make_excel_bytes_creates_workbook():
    df = pd.DataFrame({"a": [1, 2]})
    data = core.make_excel_bytes({"Sheet1": df})

    assert isinstance(data, bytes)
    assert len(data) > 0


def test_make_zip_bytes_creates_zip():
    data = core.make_zip_bytes({
        "file1.txt": b"hello",
        "file2.txt": b"world",
    })

    zf = zipfile.ZipFile(io.BytesIO(data))

    assert "file1.txt" in zf.namelist()
    assert "file2.txt" in zf.namelist()


def test_quality_score_is_between_zero_and_100():
    df = pd.DataFrame({
        "name": ["A", None],
        "amount": [10, 20],
    })

    issues = core.build_basic_quality_issues(df)
    score = core.calculate_quality_score(df, issues)

    assert 0 <= score <= 100


def test_logging_helpers_do_not_crash():
    core.log_event("test_event", "pytest")
    core.log_error(Exception("test error"), context="pytest")

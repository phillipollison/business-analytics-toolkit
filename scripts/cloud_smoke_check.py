"""
Clean0ps Cloud Smoke Check

Purpose:
    This script checks whether the app files compile before pushing to GitHub
    and redeploying on Streamlit Cloud.

Run:
    python3 scripts/cloud_smoke_check.py
"""

from pathlib import Path
import py_compile
import sys


FILES_TO_CHECK = [
    "clean0ps_core.py",
    "clean0ps_ui.py",
    "dashboard/app.py",
]

pages_dir = Path("dashboard/pages")

if pages_dir.exists():
    for page in sorted(pages_dir.glob("*.py")):
        FILES_TO_CHECK.append(str(page))


def main():
    failed = []

    print("Running Clean0ps cloud smoke check...")
    print("")

    for file_path in FILES_TO_CHECK:
        path = Path(file_path)

        if not path.exists():
            print(f"Missing: {file_path}")
            failed.append(file_path)
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            print(f"Passed: {file_path}")
        except Exception as error:
            print(f"Failed: {file_path}")
            print(error)
            failed.append(file_path)

    print("")

    if failed:
        print("Smoke check failed.")
        print("Files needing attention:")
        for item in failed:
            print(f"- {item}")
        sys.exit(1)

    print("Smoke check passed.")


if __name__ == "__main__":
    main()

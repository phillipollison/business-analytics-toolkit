from pathlib import Path
import py_compile
import sys


FILES_TO_CHECK = [
    "clean0ps_core.py",
    "clean0ps_ui.py",
    "dashboard/app.py",
    "dashboard/pages/1_Inventory_Dashboard.py",
    "dashboard/pages/2_Data_Quality_Dashboard.py",
    "dashboard/pages/4_Template Cleaning Engine.py",
    "dashboard/pages/5_Ecommerce_Analytics_Lab.py",
]


def main():
    print("Running Clean0ps health check...\n")

    failed = []

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

    print("\nHealth check complete.")

    if failed:
        print("\nFiles needing attention:")
        for item in failed:
            print(f"- {item}")
        sys.exit(1)

    print("All checked files passed.")


if __name__ == "__main__":
    main()

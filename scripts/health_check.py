from pathlib import Path
import py_compile
import subprocess
import sys


FILES_TO_CHECK = [
    "clean0ps_core.py",
    "clean0ps_ui.py",
    "dashboard/app.py",
    "dashboard/pages/1_Inventory_Dashboard.py",
    "dashboard/pages/2_Data_Quality_Dashboard.py",
    "dashboard/pages/4_Template Cleaning Engine.py",
    "dashboard/pages/5_Ecommerce_Analytics_Lab.py",
    "dashboard/pages/6_Document_Standards_Cleanup_Lab.py",
]


def compile_files():
    print("Running Clean0ps compile check...\n")

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

    return failed


def run_pytest():
    print("\nRunning pytest...\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        text=True
    )

    return result.returncode


def main():
    failed = compile_files()

    if failed:
        print("\nFiles needing attention:")
        for item in failed:
            print(f"- {item}")
        sys.exit(1)

    pytest_code = run_pytest()

    if pytest_code != 0:
        print("\nPytest failed.")
        sys.exit(pytest_code)

    print("\nAll compile checks and tests passed.")


if __name__ == "__main__":
    main()

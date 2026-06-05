from pathlib import Path
import py_compile


FILES_TO_COMPILE = [
    "clean0ps_core.py",
    "clean0ps_ui.py",
    "dashboard/app.py",
    "dashboard/pages/1_Inventory_Dashboard.py",
    "dashboard/pages/2_Data_Quality_Dashboard.py",
    "dashboard/pages/4_Template Cleaning Engine.py",
    "dashboard/pages/5_Ecommerce_Analytics_Lab.py",
    "dashboard/pages/6_Document_Standards_Cleanup_Lab.py",
]


def test_app_files_compile():
    for file_path in FILES_TO_COMPILE:
        path = Path(file_path)
        assert path.exists(), f"Missing file: {file_path}"
        py_compile.compile(str(path), doraise=True)

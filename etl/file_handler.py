from pathlib import Path
import shutil


def move_to_processed(file_path):

    processed_folder = Path("data/processed")

    shutil.move(
        str(file_path),
        processed_folder / file_path.name
    )


def move_to_rejected(file_path):

    rejected_folder = Path("data/rejected")

    shutil.move(
        str(file_path),
        rejected_folder / file_path.name
    )
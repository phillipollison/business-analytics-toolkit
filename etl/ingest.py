import pandas as pd
from pathlib import Path

from validate import validate_sales
from file_handler import (
    move_to_processed,
    move_to_rejected
)

print("\n==============================")
print(" BUSINESS ANALYTICS TOOLKIT ")
print("==============================\n")

incoming_folder = Path("data/incoming")

csv_files = list(incoming_folder.glob("*.csv"))

if len(csv_files) == 0:
    print("No files found in data/incoming")
    quit()

all_data = []

for file in csv_files:

    print(f"\nLoading: {file.name}")

    try:

        df = pd.read_csv(file)

        errors = validate_sales(df)

        if errors:

            print(f"\nRejected: {file.name}")

            for error in errors:
                print(f" - {error}")

            move_to_rejected(file)

            continue

        df["source_file"] = file.name

        all_data.append(df)

        move_to_processed(file)

        print(f"Accepted: {file.name}")

    except Exception as e:

        print(f"Failed: {file.name}")
        print(e)

        move_to_rejected(file)

if len(all_data) == 0:

    print("\nNo valid files loaded.")

    quit()

master_df = pd.concat(
    all_data,
    ignore_index=True
)

print("\n==============================")
print(" FINAL DATASET ")
print("==============================\n")

print(master_df)

print("\n==============================")
print(" SUMMARY ")
print("==============================\n")

print(f"Files Processed: {len(csv_files)}")
print(f"Rows Loaded: {len(master_df)}")
print(f"Revenue: ${master_df['sales_amount'].sum():,.2f}")
print(f"Units Sold: {master_df['quantity_sold'].sum()}")
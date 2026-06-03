import pandas as pd
from pathlib import Path

from validate import validate_sales
from file_handler import (
    move_to_processed,
    move_to_rejected
)
from database import load_sales_data


print("\n==============================")
print(" BUSINESS ANALYTICS TOOLKIT ")
print("==============================\n")

incoming_folder = Path("data/incoming")

csv_files = list(incoming_folder.glob("*.csv"))

if len(csv_files) == 0:
    print("No files found in data/incoming")
    exit()

all_data = []

for file in csv_files:

    print(f"\nLoading: {file.name}")

    try:

        df = pd.read_csv(file)

        if validate_sales(df):

            all_data.append(df)

            # Load into PostgreSQL
            load_sales_data(df)

            move_to_processed(file)

            print(f"Accepted: {file.name}")

        else:

            move_to_rejected(file)

            print(f"Rejected: {file.name}")

    except Exception as e:

        move_to_rejected(file)

        print(f"Error processing {file.name}")
        print(e)

if len(all_data) > 0:

    combined_df = pd.concat(all_data)

    print("\n==============================")
    print(" ETL SUMMARY ")
    print("==============================")

    print(f"Files Processed: {len(all_data)}")
    print(f"Rows Loaded: {len(combined_df)}")

    if "sales_amount" in combined_df.columns:
        print(f"Revenue: ${combined_df['sales_amount'].sum():,.2f}")

    if "quantity_sold" in combined_df.columns:
        print(f"Units Sold: {combined_df['quantity_sold'].sum():,.0f}")

    print("\nPipeline Complete\n")

else:

    print("\nNo valid data loaded.\n")
    
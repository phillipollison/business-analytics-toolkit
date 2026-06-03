def validate_sales(df):

    required_columns = [
        "sale_date",
        "product_name",
        "category",
        "quantity_sold",
        "sales_amount"
    ]

    for column in required_columns:

        if column not in df.columns:
            print(f"Missing column: {column}")
            return False

    return True
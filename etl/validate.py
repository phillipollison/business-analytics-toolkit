def validate_sales(df):

    errors = []

    required_columns = [
        "sale_date",
        "product_name",
        "category",
        "quantity_sold",
        "sales_amount"
    ]

    for column in required_columns:
        if column not in df.columns:
            errors.append(f"Missing column: {column}")

    if errors:
        return errors

    if df["sale_date"].isnull().any():
        errors.append("Missing sale date")

    if df["product_name"].isnull().any():
        errors.append("Missing product name")

    if (df["quantity_sold"] < 0).any():
        errors.append("Negative quantity found")

    if (df["sales_amount"] < 0).any():
        errors.append("Negative sales amount found")

    return errors
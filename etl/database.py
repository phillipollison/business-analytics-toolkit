from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "8020405"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "business_toolkit"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def load_sales_data(df):

    df.to_sql(
        "sales_raw",
        engine,
        if_exists="append",
        index=False
    )

    print("Loaded into PostgreSQL")
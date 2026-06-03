import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:8020405@localhost:5432/business_toolkit"
)

df = pd.read_sql("SELECT * FROM sales_raw", engine)

st.set_page_config(
    page_title="Business Analytics Toolkit",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Business Analytics Toolkit")

total_revenue = df["sales_amount"].sum()
total_units = df["quantity_sold"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Revenue", f"${total_revenue:,.2f}")

with col2:
    st.metric("Units Sold", int(total_units))

st.divider()

st.subheader("Sales Data")

st.dataframe(df)
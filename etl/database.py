import streamlit as st

st.set_page_config(
    page_title="Business Analytics Toolkit",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Business Analytics Toolkit")

st.markdown("""
### Welcome

This toolkit helps users:

- Clean messy datasets
- Analyze data quality
- Organize datasets
- Explore inventory data
- Generate reports
- Validate sports and business datasets

Use the navigation menu on the left to open each module.
""")

st.success("Toolkit Loaded Successfully")
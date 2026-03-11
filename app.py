import streamlit as st
import pandas as pd

st.title("Your Data Wrangler and Visualizer")

uploaded_file = st.file_uploader("Upload your file", type=["csv", "excel", "json"])

if uploaded_file is not None:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.type == "application/json":
        df = pd.read_json(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    st.markdown("**Data Preview:**")
    st.write(df)
    if st.checkbox("Show Data Shape"):
        st.markdown("**Data Shape:**")
        st.write(df.shape)
    if st.checkbox("Show Column Names"):
        st.markdown("**Column Names:**")
        st.write(df.columns.tolist())
    if st.checkbox("Show Data Types"):
        st.markdown("**Data Types:**")
        st.write(df.dtypes)
    if st.checkbox("Show Summary Statistics"):
        st.markdown("**Summary Statistics:**")
        st.write(df.describe(include='all'))
    if st.checkbox("Show Missing Values"):
        missing = pd.DataFrame({
            "Missing Count": df.isnull().sum(),
            "Missing Percentage": (df.isnull().sum() / len(df) * 100).round(2)
        })
        st.markdown("**Missing Values:**")
        st.write(missing)
    if st.checkbox("Duplicate Rows"):
        # duplicates = df[df.duplicated()]
        st.markdown("**Duplicate Rows:**")
        if df.duplicated().sum() > 0:
            st.markdown("**Number of Duplicate Rows:**")
            st.write(df[df.duplicated()])
        else:   
            st.write(df.duplicated().sum())

import streamlit as st
import time
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Data Upload & Overview",
    page_icon="📈",
    layout="wide",
    )

# Title and welcome message
st.title("Your Data Wrangler and Visualizer")
st.write("Welcome to your Data Wrangler and Visualizer! Upload your data and explore them with ease!")

# Sidebar with progress bar
st.sidebar.header("Sidebar settings")
progress_bar = st.progress(0)
status_text = st.sidebar.empty()
for i in range(100):
    status_text.info("%i%% Complete" % i)
    progress_bar.progress(i + 1)
    time.sleep(0.005)
progress_bar.empty()
status_text.empty()

# File uploader
uploaded_file = st.file_uploader("Upload your file", type=["csv", "excel", "json"])

if uploaded_file is not None:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.type == "application/json":
        df = pd.read_json(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    #saving dataset for other pages to access it
    st.session_state["data"] = df
    
    # Display dataset overview
    st.markdown("**Data Preview:**")
    st.write(df)
    # Data shape
    if st.sidebar.checkbox("Show Data Shape"):
        st.markdown("**Data Shape:**")
        st.write("Number of rows: ", df.shape[0])
        st.write("Number of columns: ", df.shape[1])
    # Column names
    if st.sidebar.checkbox("Show Column Names"):
        st.markdown("**Column Names:**")
        st.write(df.columns.tolist())
    # Data types
    if st.sidebar.checkbox("Show Data Types"):
        st.markdown("**Data Types:**")
        st.write(df.dtypes)
    # Summary stats
    if st.sidebar.checkbox("Show Summary Statistics"):
        st.markdown("**Summary Statistics:**")
        st.write(df.describe(include='all'))
    # Missing values
    if st.sidebar.checkbox("Show Missing Values"):
        missing = pd.DataFrame({
            "Missing Count": df.isnull().sum(),
            "Missing Percentage (%)": (df.isnull().sum() / len(df) * 100).round(2)
        })
        st.markdown("**Missing Values:**")
        st.write(missing)
    # Duplicate rows
    if st.sidebar.checkbox("Duplicate Rows"):
        st.markdown("**Duplicate Rows:**")
        if df.duplicated().sum() > 0:
            st.markdown("**Number of Duplicate Rows:**")
            st.write(df[df.duplicated()])
        else:   
            st.info("No duplicate rows found")
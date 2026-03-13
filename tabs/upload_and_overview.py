import streamlit as st
import pandas as pd

def upload_overview():

    # Set page configuration
    st.set_page_config(
        page_title="Data Upload & Overview",
        page_icon="📈",
        layout="wide",
        )

    # Title and welcome message
    st.title("Your Data Wrangler and Visualizer")
    st.write("Welcome to your Data Wrangler and Visualizer! Upload your data and explore them with ease!")
    
    # Get dataset from session state
    df = st.session_state.get("data")
    if df is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return
    
    # Display dataset overview
    st.header("Data Preview:")
    if st.checkbox("Show full dataset"):
        st.write(df)

    # Data shape
    with st.container(border=True):
        st.markdown("**Data Shape:**")
        col1, col2 = st.columns(2, border=True)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])

    # Duplicate rows
    with st.expander("Duplicate Rows"):
        # st.markdown("**Duplicate Rows:**")
        if df.duplicated().sum() > 0:
            st.markdown("**Number of Duplicate Rows:**")
            st.write(df[df.duplicated()])
        else:   
            st.info("No duplicate rows found")

    with st.container(horizontal=True):
        # Column names
        # if st.sidebar.checkbox("Show Column Names"):
        with st.container(border=True):
            st.markdown("**Column Names:**")
            st.write(df.columns)
        # Data types
        # if st.sidebar.checkbox("Show Data Types"):
        with st.container(border=True):
            st.markdown("**Data Types:**")
            st.write(df.dtypes)
        # Missing values
        with st.container(border=True):
            missing = pd.DataFrame({
                "Missing Count": df.isnull().sum(),
                "Missing Percentage (%)": (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.markdown("**Missing Values:**")
            st.write(missing)
    # Summary stats
    with st.container(border=True):
        st.markdown("**Summary Statistics:**")
        st.write(df.describe(include='all'))
        

        
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

    # File uploader
    with st.container(border=True):
        # st.write("Upload your dataset here:")
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
        

        
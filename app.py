import streamlit as st
import pandas as pd

from tabs import upload_and_overview
from tabs import cleaning_and_prep
from tabs import visualization
from tabs import export_and_report

#Page config
st.set_page_config(
    page_title="Data Wrangler and Visualizer",
    layout="wide",
    page_icon="👋"
)

#sidebar title
st.sidebar.header("Upload Dataset")

#file uploader 
uploaded_file = st.sidebar.file_uploader(
    "Upload your file",
    type=["csv", "xlsx", "json"]
)

#load file
if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        df = pd.read_json(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.session_state["data"] = df
    # OG dataset for reset
    st.session_state["original_data"] = df.copy()

#tabs 
tab1, tab2, tab3, tab4 = st.tabs([
    "Upload and Overview",
    "Cleaning and Prep",
    "Visualization",
    "Export and Report"
])

with tab1:
    upload_and_overview.upload_overview()

with tab2:
    cleaning_and_prep.clean_prep()

with tab3:
    visualization.visualization()

with tab4:
    export_and_report.export_report()
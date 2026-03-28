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
st.sidebar.header("Upload Dataset", help="Upload any dataset of type CSV, JSON or EXCEL")

@st.cache_data
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        return pd.read_json(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return None

#file uploader 
uploaded_file = st.sidebar.file_uploader(
    "Upload your file",
    type=["csv", "xlsx", "json"],
    label_visibility="collapsed"
)

# st.sidebar.space("xxsmall")

#load file
if uploaded_file is not None:
    # Check if this is a completely new upload
    if "current_file" not in st.session_state or st.session_state["current_file"] != uploaded_file.name:
        df = load_file(uploaded_file)

        if df is None:
            st.error("Unsupported file format")
            # st.stop()

        st.session_state["data"] = df
        # OG dataset for reset
        st.session_state["original_data"] = df.copy()
        # Save the current file name so Streamlit knows not to reload it
        st.session_state["current_file"] = uploaded_file.name

        # reset system
        st.session_state["history"] = []
        st.session_state["transform_log"] = []

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
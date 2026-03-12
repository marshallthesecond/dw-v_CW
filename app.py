import streamlit as st
import pandas as pd
import time

from tabs import upload_and_overview
from tabs import cleaning_and_prep
from tabs import visualization
from tabs import export_and_report

# Page configuration
st.set_page_config(
    page_title="Data Wrangler and Visualizer", 
    layout="wide",
    page_icon="👋")


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


# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Upload and Overview", "Cleaning and Prep", "Visuallization", "Export and Report"], on_change="rerun")

if tab1.open:
    with st.spinner("Loading Upload and Overview..."):
        time.sleep(1)
    with tab1:
        upload_and_overview.upload_overview()
if tab2.open:
    with st.spinner("Loading Cleaning and Prep..."):
        time.sleep(1)
    with tab2:
        cleaning_and_prep.clean_prep()
if tab3.open:
    with st.spinner("Loading Visualization..."):
        time.sleep(1)
    with tab3:
        st.write("Visualization")
if tab4.open:
    with st.spinner("Loading Export and Report..."):
        time.sleep(1)
    with tab4:
        export_and_report.export_report()
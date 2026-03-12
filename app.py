import streamlit as st
import pandas as pd

from tabs import upload_and_overview
from tabs import cleaning_and_prep

# Set page configuration
st.set_page_config(
    page_title="Data Wrangler and Visualizer", 
    layout="wide",
    page_icon="👋")

# Pages
# homepage = st.Page("Home.py", title="Home", icon="🏠")
# page_1 = st.Page("pages/upload_and_overview.py", title="Upload & Overview", icon="📈")
# page_2 = st.Page("pages/cleaning_and_prep.py", title="Cleaning & Prep", icon="🧹")
# page_3 = st.Page("pages/visualization.py", title="Visualization", icon="📊")
# page_4 = st.Page("pages/export_and_report.py", title="Modeling", icon="🤖")

# pg = st.navigation([page_1, page_2, page_3, page_4])
# pg.run()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Upload and Overview", "Cleaning and Prep", "Visuallization", "Modeling"])

with tab1:
    upload_and_overview.upload_overview()
with tab2:
    cleaning_and_prep.clean_prep()
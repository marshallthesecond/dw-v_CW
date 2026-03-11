import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Data Wrangler and Visualizer", 
    layout="wide",
    page_icon="👋")

# Pages
# homepage = st.Page("Home.py", title="Home", icon="🏠")
page_1 = st.Page("pages/1_upload_and_overview.py", title="Upload & Overview", icon="📈")
page_2 = st.Page("pages/2_cleaning_and_prep.py", title="Cleaning & Prep", icon="🧹")
page_3 = st.Page("pages/3_visualization.py", title="Visualization", icon="📊")
page_4 = st.Page("pages/4_export_and_report.py", title="Modeling", icon="🤖")

pg = st.navigation([page_1, page_2, page_3, page_4])
pg.run()

import streamlit as st
import pandas as pd
import json
from datetime import datetime


def export_report():
    st.title("Export & Report")

    # Check dataset
    if "data" not in st.session_state or st.session_state["data"] is None:
        st.warning("Please upload and process a dataset first.")
        return

    df = st.session_state["data"]

    if "transform_log" not in st.session_state:
        st.session_state["transform_log"] = []

    st.subheader("1. Export Cleaned Dataset")

    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    # Excel Export (optional)
    try:
        excel_file = "cleaned_data.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                label="Download Excel",
                data=f,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.info("Excel export not available")


    st.divider()

    # ------------------- REPORT -------------------
    st.subheader("2. Transformation Report")

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "steps": st.session_state["transform_log"]
    }

    st.json(report)

    report_json = json.dumps(report, indent=4)

    st.download_button(
        label="Download Report (JSON)",
        data=report_json,
        file_name="transformation_report.json",
        mime="application/json"
    )


    st.divider()

    # ------------------- RECIPE -------------------
    st.subheader("3. Pipeline Recipe")

    recipe = {
        "steps": st.session_state["transform_log"]
    }

    recipe_json = json.dumps(recipe, indent=4)

    st.download_button(
        label="Download Recipe (JSON)",
        data=recipe_json,
        file_name="pipeline_recipe.json",
        mime="application/json"
    )


    st.divider()

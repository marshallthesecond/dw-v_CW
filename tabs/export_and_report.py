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

    # ------------------- PYTHON SCRIPT (stretch) -------------------
    st.subheader("4. Generate Python Script (Basic)")

    if st.button("Generate Script"):
        script = "import pandas as pd\n\n"
        script += "df = pd.read_csv('your_file.csv')\n\n"

        for step in st.session_state["transform_log"]:
            op = step.get("operation")

            if op == "Drop Columns":
                cols = step.get("columns")
                script += f"df = df.drop(columns={cols})\n"

            elif op == "Rename Column":
                cols = step.get("columns")
                new_name = step.get("parameters", {}).get("new_name")
                script += f"df = df.rename(columns={{'{cols[0]}': '{new_name}'}})\n"

            elif op == "Remove Duplicates":
                keep = step.get("parameters", {}).get("keep", "first")
                script += f"df = df.drop_duplicates(keep='{keep}')\n"

            elif op == "Fill Missing Values":
                val = step.get("parameters", {}).get("value", 0)
                script += f"df = df.fillna({val})\n"

        script += "\ndf.to_csv('cleaned_output.csv', index=False)"

        st.code(script, language="python")

        st.download_button(
            label="Download Script",
            data=script,
            file_name="pipeline_script.py",
            mime="text/plain"
        )
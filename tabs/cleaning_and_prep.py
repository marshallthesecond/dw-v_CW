import streamlit as st
import pandas as pd

def clean_prep():
    st.title("Data Cleaning and Preparation")

    #get dataset
    df = st.session_state.get("data")

    if df is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return

    df = st.session_state["data"]

    #store original dataset for reset
    if "original_data" not in st.session_state:
        st.session_state["original_data"] = df.copy()

    #to initialize transf. log
    if "transform_log" not in st.session_state:
        st.session_state["transform_log"] = []

    st.subheader("Current Dataset")
    st.write(df.head())

    #remove duplicates
    if st.checkbox("Remove duplicate rows"):
        before = len(st.session_state["data"])
        st.session_state["data"].drop_duplicates(inplace=True)
        after = len(st.session_state["data"])
        st.success("Duplicates removed")

        st.session_state["transform_log"].append({
            "operation": "Remove Duplicates",
            "parameters": {"rows_removed": before - after},
            "columns": "All"
        })

    #missing value handling
    st.subheader("Handle Missing Values")

    df_missing = df.loc[:, df.isnull().any()]

    with st.container(border=True):
        if st.checkbox("Show missing values"):
            missing = pd.DataFrame({
                "Column": df_missing.columns,
                "Missing Count": df_missing.isnull().sum(),
                "Missing Percentage (%)": (
                    df_missing.isnull().sum() / len(df) * 100
                ).round(2)
            })
            st.markdown("**Missing Values Overview:**")
            st.dataframe(
                missing,
                use_container_width=True,
                hide_index=True
            )

    if st.checkbox("Drop rows with missing values"):
        st.session_state["data"].dropna(inplace=True)
        st.success("Rows with missing values removed")
        st.session_state["transform_log"].append({
            "operation": "Drop Missing Rows",
            "parameters": "Removed rows containing NA",
            "columns": "All"
        })

    if st.checkbox("Fill missing values with 0"):
        st.session_state["data"].fillna(0, inplace=True)
        st.success("Missing values filled with 0")
        st.session_state["transform_log"].append({
            "operation": "Fill Missing Values",
            "parameters": {"value": 0},
            "columns": "All"
        })

    #column selection
    st.subheader("Select Columns to Keep")
    selected_columns = st.multiselect(
        "Choose columns",
        df.columns,
        default=df.columns
    )
    df = df[selected_columns]

    #drop columns
    st.subheader("Drop Columns")
    columns_to_drop = st.multiselect(
        "Select columns to drop",
        df.columns
    )

    if st.button("Drop Selected Columns"):
        st.session_state["data"].drop(columns=columns_to_drop, inplace=True)
        st.success("Selected columns dropped")
        st.session_state["transform_log"].append({
            "operation": "Drop Columns",
            "parameters": {"count": len(columns_to_drop)},
            "columns": columns_to_drop
        })
    #rename column
    st.subheader("Rename Column")
    df = st.session_state["data"]

    old_name = st.selectbox(
        "Select column to rename",
        df.columns
    )
    new_name = st.text_input(
        "Enter new column name"
    )

    if st.button("Rename Column"):
        if new_name:
            st.session_state["data"].rename(
                columns={old_name: new_name},
                inplace=True
            )
            st.success("Column renamed successfully")
            st.session_state["transform_log"].append({
                "operation": "Rename Column",
                "parameters": {"new_name": new_name},
                "columns": [old_name]
            })

    #cleaned dataset
    st.subheader("Cleaned Dataset")
    st.write(st.session_state["data"])

    #sidebar trnf.log
    with st.sidebar:
        st.markdown("## Transformation Log")
        if st.session_state["transform_log"]:
            for i, step in enumerate(st.session_state["transform_log"], 1):
                with st.container(border=True):
                    st.markdown(f"**Operation {i}: {step['operation']}**")
                    st.markdown(f"Columns: {step['columns']}")
                    st.markdown(f"Parameters: {step['parameters']}")
        else:
            st.info("No transformations applied yet.")

        #reset btn
        if st.button("Reset All Transformations"):
            st.session_state["data"] = st.session_state["original_data"].copy()
            st.session_state["transform_log"] = []
            st.success("Dataset reset to original")

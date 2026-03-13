import streamlit as st
import pandas as pd

def clean_prep():

    st.title("Data Cleaning and Preparation")

    #Get dataset from session state
    df = st.session_state.get("data")

    if df is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return
    df = st.session_state["data"]

    #initialize transformation log
    if "transform_log" not in st.session_state:
     st.session_state["transform_log"] = []

    st.subheader("Current Dataset")
    st.write(df.head())

    #remove duplicates
    if st.checkbox("Remove duplicate rows"):
     st.session_state["data"].drop_duplicates(inplace=True)
    st.success("Duplicates removed")
    st.session_state["transform_log"].append("Removed duplicate rows")

    #handle missing values
    st.subheader("Handle missing Values")

    df_missing = df.loc[:, df.isnull().any()]

    with st.container(border=True):
        if st.checkbox("Show missing values"):
            missing = pd.DataFrame({
                "Row names": df_missing.columns,
                "Missing Count": df_missing.isnull().sum(),
                "Missing Percentage (%)": (df_missing.isnull().sum() / len(df) * 100).round(5)
            })
            st.markdown("**Missing Values Overview:**")
            # st.write(missing)
            event = st.dataframe(
                missing,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row",
            )
            # st.write("Selected rows:", selection)

    if st.checkbox("Drop rows with missing values"):
     st.session_state["data"].dropna(inplace=True)
    st.success("Rows with missing values removed")
    st.session_state["transform_log"].append("Dropped rows with missing values")

    if st.checkbox("Fill missing values with 0"):
     st.session_state["data"].fillna(0, inplace=True)
    st.success("Missing values filled with 0")
    st.session_state["transform_log"].append("Filled missing values with 0")

    #column selection
    st.subheader("Select columns to keep")

    selected_columns = st.multiselect(
        "Choose columns",
        df.columns,
        default=df.columns
    )

    df = df[selected_columns]
    #column deletion
    st.subheader("Drop Columns")

    columns_to_drop = st.multiselect(
       "Select columns to drop",
    df.columns
)
    if st.button("Drop Selected Columns", key="drop_columns_btn"):
     if st.button("Drop Selected Columns", key="drop_columns_btn"):
      st.session_state["data"].drop(columns=columns_to_drop, inplace=True)
    # st.success("Selected columns dropped")

    st.session_state["transform_log"].append(
        f"Dropped columns: {', '.join(columns_to_drop)}"
    )
    
    #column renaming
    st.subheader("Rename Column")
    df = st.session_state["data"]

    old_name = st.selectbox(
    "Select column to rename",
    df.columns,
    key="rename_select"
)

    new_name = st.text_input(
    "Enter new column name",
    key="rename_input"
)

    if st.button("Rename Column", key="rename_button"):
     if new_name != "":
        st.session_state["data"].rename(
            columns={old_name: new_name},
            inplace=True
        )
        st.success("Column renamed successfully")
        st.session_state["transform_log"].append(
            f"Renamed column '{old_name}' to '{new_name}'"
)
    
    st.subheader("Cleaned Dataset")
    st.write(st.session_state["data"])

    st.subheader("Transformation Log")

    if st.session_state["transform_log"]:
        for step in st.session_state["transform_log"]:
         st.write("✔", step)
    else:
        st.info("No transformations applied yet.")
    
    #saving cleaned dataset 
    # st.session_state["data"] = df
    st.subheader("Cleaned Dataset")
    st.write(st.session_state["data"])

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


    #store original dataset for reset
    if "original_data" not in st.session_state:
        st.session_state["original_data"] = df.copy()

    #initialize transf. log
    if "transform_log" not in st.session_state:
        st.session_state["transform_log"] = []

    st.subheader("Current Dataset")
    st.write(df.head())

#duplicate detection nd removal
    st.subheader("Duplicate Detection")

    df = st.session_state["data"]

    dup_columns = st.multiselect(
        "Select columns to check duplicates (leave empty for full-row duplicates)",
        df.columns
    )

    keep_option = st.radio(
        "Keep which duplicate?",
        ["first", "last"]
    )

    if st.button("Detect Duplicates"):

        if dup_columns:
            duplicates = df[df.duplicated(subset=dup_columns, keep=False)]
        else:
            duplicates = df[df.duplicated(keep=False)]

        st.session_state["duplicates_found"] = duplicates

        st.info(f"{len(duplicates)} duplicate rows found")

    if "duplicates_found" in st.session_state:

        if st.checkbox("Show duplicate rows"):
            st.dataframe(st.session_state["duplicates_found"])

        if st.button("Remove Duplicates"):

            before = len(df)

            if dup_columns:
                st.session_state["data"].drop_duplicates(
                    subset=dup_columns,
                    keep=keep_option,
                    inplace=True
                )
            else:
                st.session_state["data"].drop_duplicates(
                    keep=keep_option,
                    inplace=True
                )

            after = len(st.session_state["data"])

            st.success(f"{before - after} duplicate rows removed")

            st.session_state["transform_log"].append({
                "operation": "Remove Duplicates",
                "parameters": {"keep": keep_option},
                "columns": dup_columns if dup_columns else "All"
            })

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
    # df = st.session_state["data"]

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

    #normalization nd scaling
    st.subheader("Normalization / Scaling")
    df = st.session_state["data"]

    #get numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns available for scaling.")
    else:

    #column selection for scaling
        scale_columns = st.multiselect(
            "Select numeric columns to scale",
        numeric_cols
    )

    #choose scaling method
    scaling_method = st.radio(
        "Choose scaling method",
        ["Min-Max Scaling", "Z-Score Standardization"]
    )

    if st.button("Apply Scaling"):

        if not scale_columns:
            st.warning("Please select at least one column.")
        else:

            #before stats
            before_stats = df[scale_columns].describe()

            #min-max scaling
            if scaling_method == "Min-Max Scaling":
                for col in scale_columns:
                    min_val = df[col].min()
                    max_val = df[col].max()

                    if max_val - min_val != 0:
                        st.session_state["data"][col] = (
                            (df[col] - min_val) / (max_val - min_val)
                        )

            #Z-score standardizating
            elif scaling_method == "Z-Score Standardization":
                for col in scale_columns:
                    mean_val = df[col].mean()
                    std_val = df[col].std()

                    if std_val != 0:
                        st.session_state["data"][col] = (
                            (df[col] - mean_val) / std_val
                        )

            #after stats
            after_stats = st.session_state["data"][scale_columns].describe()

            st.success("Scaling applied successfully")

            st.markdown("### Before Scaling Stats")
            st.dataframe(before_stats)

            st.markdown("### After Scaling Stats")
            st.dataframe(after_stats)

            #log the transformation
            st.session_state["transform_log"].append({
                "operation": "Scaling",
                "parameters": {"method": scaling_method},
                "columns": scale_columns
            })  

        #Data types nd Parsing
    st.subheader("Data Type Conversion")

    df = st.session_state["data"]

    column_to_convert = st.selectbox(
        "Select column to convert",
        df.columns
    )

    new_type = st.selectbox(
        "Convert to",
        ["Numeric", "Categorical", "Datetime"]
    )

    if st.button("Convert Column Type"):

        before_type = df[column_to_convert].dtype

        try:

            #convert to numeric
            if new_type == "Numeric":

                #remove common dirty charact. like commas or $
                st.session_state["data"][column_to_convert] = (
                    df[column_to_convert]
                    .astype(str)
                    .str.replace(",", "")
                    .str.replace("$", "")
                )

                st.session_state["data"][column_to_convert] = pd.to_numeric(
                    st.session_state["data"][column_to_convert],
                    errors="coerce"
                )

            #convert to categorical
            elif new_type == "Categorical":

                st.session_state["data"][column_to_convert] = (
                    df[column_to_convert].astype("category")
                )

            #convert to datetime
            elif new_type == "Datetime":

                st.session_state["data"][column_to_convert] = pd.to_datetime(
                    df[column_to_convert],
                    errors="coerce"
                )

            after_type = st.session_state["data"][column_to_convert].dtype

            st.success(f"Column converted from {before_type} to {after_type}")

            st.session_state["transform_log"].append({
                "operation": "Convert Data Type",
                "parameters": {"new_type": new_type},
                "columns": [column_to_convert]
            })

        except Exception as e:
            st.error("Conversion failed")
            st.write(e)              

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

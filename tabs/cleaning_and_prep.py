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
    st.write(df.tail())


    # Duplicates and Missing Values
    with st.container(horizontal=True):
        # Duplicate detection and removal
        with st.container(border=True):
            st.subheader("Duplicate Detection")

            # Use the current working dataset
            df = st.session_state["data"]

            # Select columns
            @st.fragment
            def duplicate_columns_fragment():
                st.multiselect(
                    "Select columns to check duplicates (leave empty for full-row duplicates)",
                    df.columns,
                    key="duplicate_columns_selector"
                )

            duplicate_columns_fragment()

            # Keep option
            @st.fragment
            def keep_option_fragment():
                st.radio(
                    "Keep which duplicate?",
                    ["first", "last"],
                    key="keep_duplicate_option"
                )

            keep_option_fragment()

            # Detect duplicates
            @st.fragment
            def detect_duplicates_fragment():

                if st.button("Detect Duplicates", key="detect_duplicates_btn"):

                    cols = st.session_state.get("duplicate_columns_selector", [])

                    if cols:
                        duplicates = df[df.duplicated(subset=cols, keep=False)]
                    else:
                        duplicates = df[df.duplicated(keep=False)]

                    st.session_state["duplicates_found"] = duplicates

                    st.info(f"{len(duplicates)} duplicate rows found")
                    st.dataframe(duplicates.head())

            detect_duplicates_fragment()

            @st.fragment
            def remove_duplicates_fragment():

                if "duplicates_found" not in st.session_state:
                    return

                if st.button("Remove Selected Duplicates", key="remove_duplicates_btn"):

                    cols = st.session_state.get("duplicate_columns_selector", [])
                    keep_option = st.session_state.get("keep_duplicate_option", "first")

                    before = len(st.session_state["data"])

                    if cols:
                        st.session_state["data"].drop_duplicates(
                            subset=cols,
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

                    if "transform_log" not in st.session_state:
                        st.session_state["transform_log"] = []

                    st.session_state["transform_log"].append({
                        "operation": "Remove Duplicates",
                        "parameters": {"keep": keep_option},
                        "columns": cols if cols else "All"
                    })
            remove_duplicates_fragment()

        with st.container(border=True):
            st.subheader("Handle Missing Values")

            df = st.session_state["data"]

            # Initialize states
            if "confirm_dropna" not in st.session_state:
                st.session_state.confirm_dropna = False

            # Missing values overview
            df_missing = df.loc[:, df.isnull().any()]

            @st.fragment
            def show_missing_values():
                if st.checkbox("Show missing values", value=True):
                    if df_missing.shape[1] > 0:
                        missing = pd.DataFrame({
                            "Column": df_missing.columns,
                            "Missing Count": df_missing.isnull().sum(),
                            "Missing Percentage (%)": (
                                df_missing.isnull().sum() / len(df) * 100
                            ).round(2)
                        })

                        st.markdown("**Missing Values Overview:**")
                        st.dataframe(missing, use_container_width=True, hide_index=True)
                    else:
                        st.success("No missing values remaining!")
            show_missing_values()

            # DROP NA WITH CONFIRMATION
            rows_to_drop = df.isna().any(axis=1).sum()

            @st.fragment
            def drod_missing_rows():
                if rows_to_drop > 0:
                    if st.button("Drop rows with missing values"):
                        st.session_state.confirm_dropna = True

                    if st.session_state.confirm_dropna:
                        st.warning(f"This will remove {rows_to_drop} rows. Continue?")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("Yes, drop rows"):
                                st.session_state["data"] = df.dropna()

                                st.session_state["transform_log"].append({
                                    "operation": "Drop Missing Rows",
                                    "parameters": f"Removed {rows_to_drop} rows",
                                    "columns": "All"
                                })

                                st.session_state.confirm_dropna = False
                                st.rerun()

                        with col2:
                            if st.button("Cancel"):
                                st.session_state.confirm_dropna = False
            drod_missing_rows()

            # Fill NA
            if df.isnull().values.any():
                fill_value = st.text_input("Fill missing values with:", value="0")

                if st.button("Apply Fill"):
                    try:
                        value = float(fill_value)
                    except:
                        value = fill_value  # allow strings too

                    st.session_state["data"] = df.fillna(value)

                    st.session_state["transform_log"].append({
                        "operation": "Fill Missing Values",
                        "parameters": {"value": value},
                        "columns": "All"
                    })

                    st.success(f"Missing values filled with {value}")
                    st.rerun()

    #column selection
    st.subheader("Select Columns to Keep")
    selected_columns = st.multiselect(
        "Choose columns",
        df.columns,
        default=df.columns
    )
    st.session_state["data"] = df[selected_columns]
    #always work on the latest dataframe
    def get_df():
        return st.session_state["data"]

    def set_df(new_df):
        st.session_state["data"] = new_df

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

        #CATEGORICAL DATA TOOLS
    st.subheader("Categorical Data Tools")

    df = st.session_state["data"]

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if cat_cols:

        cat_col = st.selectbox(
            "Select categorical column",
            cat_cols
        )

        clean_option = st.selectbox(
            "Standardization option",
            ["Trim whitespace", "Lowercase", "Title Case"]
        )

        if st.button("Apply Standardization"):

            if clean_option == "Trim whitespace":
                st.session_state["data"][cat_col] = (
                    st.session_state["data"][cat_col].astype(str).str.strip()
                )

            elif clean_option == "Lowercase":
                st.session_state["data"][cat_col] = (
                    st.session_state["data"][cat_col].astype(str).str.lower()
                )

            elif clean_option == "Title Case":
                st.session_state["data"][cat_col] = (
                    st.session_state["data"][cat_col].astype(str).str.title()
                )

            st.success("Categorical values standardized")

            st.session_state["transform_log"].append({
                "operation": "Categorical Standardization",
                "parameters": {"method": clean_option},
                "columns": [cat_col]
            })


        st.markdown("Rare Category Grouping")

        threshold = st.slider(
            "Minimum frequency (%)",
            0,
            20,
            5
        )

        if st.button("Group Rare Categories"):

            freq = st.session_state["data"][cat_col].value_counts(normalize=True)

            rare = freq[freq < threshold / 100].index

            st.session_state["data"][cat_col] = (
                st.session_state["data"][cat_col].replace(rare, "Other")
            )

            st.success("Rare categories grouped into 'Other'")

            st.session_state["transform_log"].append({
                "operation": "Rare Category Grouping",
                "parameters": {"threshold_percent": threshold},
                "columns": [cat_col]
            })
    #Numeric Cleaning
    st.subheader("Numeric Cleaning / Outlier Detection")

    df = st.session_state["data"]

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if num_cols:

        outlier_col = st.selectbox(
            "Select numeric column",
            num_cols
        )

        action = st.radio(
            "Action for outliers",
            ["Show Outliers", "Remove Outliers", "Cap Outliers"]
        )

        if st.button("Run Outlier Detection"):

            #IQR cal.
            Q1 = df[outlier_col].quantile(0.25)
            Q3 = df[outlier_col].quantile(0.75)

            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            # detect outliers
            outliers = df[(df[outlier_col] < lower) | (df[outlier_col] > upper)]

            #column stats
            col_mean = df[outlier_col].mean()
            col_median = df[outlier_col].median()
            col_min = df[outlier_col].min()
            col_max = df[outlier_col].max()

            st.divider()

            st.markdown("### Column Statistics")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Mean", round(col_mean, 2))

            with c2:
                st.metric("Median", round(col_median, 2))

            with c3:
                st.metric("Min", col_min)

            with c4:
                st.metric("Max", col_max)

            #outlier boundaries
            st.markdown("### Outlier Boundaries (IQR Method)")

            b1, b2 = st.columns(2)

            with b1:
                st.metric("Lower Limit", round(lower, 2))

            with b2:
                st.metric("Upper Limit", round(upper, 2))

            st.divider()

            #outlier summary
            st.markdown("### Outlier Detection Summary")

            total_rows = len(df)
            outlier_count = len(outliers)
            percent = (outlier_count / total_rows) * 100

            s1, s2, s3 = st.columns(3)

            with s1:
                st.metric("Total Rows", total_rows)

            with s2:
                st.metric("Outliers Found", outlier_count)

            with s3:
                st.metric("Percentage", f"{round(percent,2)}%")

            #action
            if action == "Show Outliers":

                st.markdown("### Detected Outliers")
                st.dataframe(outliers)

                st.session_state["transform_log"].append({
                    "operation": "Detect Outliers",
                    "parameters": {"method": "IQR", "count": outlier_count},
                    "columns": [outlier_col]
                })

            elif action == "Remove Outliers":

                before = len(df)

                st.session_state["data"] = df[
                    (df[outlier_col] >= lower) &
                    (df[outlier_col] <= upper)
                ]

                after = len(st.session_state["data"])
                removed = before - after

                st.success(f"{removed} rows removed")

                st.session_state["transform_log"].append({
                    "operation": "Remove Outliers",
                    "parameters": {"method": "IQR", "rows_removed": removed},
                    "columns": [outlier_col]
                })

            elif action == "Cap Outliers":

                cap_count = len(outliers)

                st.session_state["data"][outlier_col] = df[outlier_col].clip(lower, upper)

                st.success(f"{cap_count} values capped")

                st.session_state["transform_log"].append({
                    "operation": "Cap Outliers",
                    "parameters": {"method": "IQR", "values_capped": cap_count},
                    "columns": [outlier_col]
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

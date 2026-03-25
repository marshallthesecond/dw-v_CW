import streamlit as st
import pandas as pd

def clean_prep():
    st.title("Data Cleaning and Preparation") 

    # Show last action if exists
    if "last_action" in st.session_state:
        st.success(st.session_state["last_action"])
        del st.session_state["last_action"]

    # Check dataset
    if "data" not in st.session_state or st.session_state["data"] is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return

    # Initialize transform log
    if "transform_log" not in st.session_state:
        st.session_state["transform_log"] = []

    st.space("medium")




    # ------------------- 4.2 DUPLICATE DETECTION -------------------

    with st.container(border=True, horizontal=True):
        with st.container():
            st.subheader("4.2 Duplicate Detection")

            # Include - exclude toggle
            mode = st.radio(
                "Column Selection Mode",
                ["Including selected columns", "Excluding selected columns"],
                key="column_mode",
                horizontal=True
            )

            # Column selector
            cols = st.multiselect(
                "Select columns to check duplicates (leave empty for full-row duplicates)",
                st.session_state["data"].columns,
                key="duplicate_columns"
            )

            # Detect duplicates
            if st.button("Detect Duplicates", key="detect_duplicates_btn"):
                
                new_df = st.session_state["data"].copy()

                if cols:
                    if mode == "Including selected columns":
                        subset_cols = cols
                    else:
                        subset_cols = [c for c in new_df.columns if c not in cols]
                    if not subset_cols:
                        st.warning("No columns selected for duplicate detection.")
                        return
                    duplicates = new_df[new_df.duplicated(subset=subset_cols, keep=False)]
                else:
                    duplicates = new_df[new_df.duplicated(keep=False)]
                
                st.dataframe(duplicates.head())
                st.info(f"{len(duplicates)} duplicate rows found")
                
            st.divider()

            left, right = st.columns([2, 1], vertical_alignment="bottom")

            # Keep option
            keep_option = left.radio(
                "Keep which duplicate?",
                ["first", "last"],
                key="keep_option",
                horizontal=True
            )

            st.space("stretch")

            # Remove duplicates
            if right.button("Remove Duplicates", key="remove_duplicates_btn", type="primary", width="stretch"):
                
                new_df = st.session_state["data"].copy()

                if cols:
                    if mode == "Including selected columns":
                        subset_cols = cols
                    else:
                        subset_cols = [c for c in new_df.columns if c not in cols]

                    new_df = new_df.drop_duplicates(subset=subset_cols, keep=keep_option).reset_index(drop=True)
                else:
                    new_df = new_df.drop_duplicates(keep=keep_option).reset_index(drop=True)
                st.session_state["data"] = new_df.reset_index(drop=True)
                st.success("Duplicates removed")



        st.space("medium")



        #------------------- 4.1 MISSING VALUES (NULL HANDLING) -------------------   

        with st.container():
           
            st.subheader("4.1 Handle Missing Values")

            # Show missing values
            df_missing = st.session_state["data"].loc[:, st.session_state["data"].isnull().any()]
            if st.checkbox("Show missing values", key="show_missing_checkbox"):
                if df_missing.shape[1] > 0:
                    missing = pd.DataFrame({
                        "Column": df_missing.columns,
                        "Missing Count": df_missing.isnull().sum(),
                        "Missing Percentage (%)": (df_missing.isnull().sum() / len(st.session_state["data"]) * 100).round(2)
                    })
                    st.markdown("**Missing Values Overview:**")
                    st.dataframe(missing, use_container_width=True, hide_index=True)
                else:
                    st.success("No missing values remaining!")

            if st.button("Drop rows with missing values", key="drop_missing_btn"):
                new_df = st.session_state["data"].copy()
                rows_to_drop = new_df.isna().any(axis=1).sum()
                new_df = new_df.dropna()
                st.session_state["data"] = new_df.reset_index(drop=True)
                st.success(f"Dropped {rows_to_drop} rows successfully!")

            # Fill missing values
            fill_value = st.text_input("Fill missing values with:", value="0", key="fill_value_input")
            if st.button("Apply Fill", key="apply_fill_btn"):
                new_df = st.session_state["data"].copy()
                try:
                    value = float(fill_value)
                except:
                    value = fill_value
                new_df = new_df.fillna(value)
                st.session_state["data"] = new_df

            # Normalize missing values
            if st.button("Normalize Missing Values"):
                new_df = st.session_state["data"].replace(
                    ["None", "none", "NULL", "null", "", " "],
                    pd.NA
                )
                st.session_state["data"] = new_df
                st.session_state["last_action"] = "Normalized missing values"


    st.space("medium")


    # --------- 4.7, 4.3 and 4.4 - Column Operations + Data Type Conversion + Categorical Tools ---------

    with st.container(horizontal=True):

        # ------------------- 4.7 COLUMN OPERATIONS -------------------

        with st.container(border=True):
            st.subheader("4.7 Column Operations")

            # Column selection
            st.subheader("Select Columns to Keep")

            selected_columns = st.multiselect(
                "Choose columns",
                st.session_state["data"].columns,
                key="column_selection"
            )
            if st.button("Apply Column Selection", key="apply_column_selection"):
                if selected_columns:
                    st.session_state["data"] = st.session_state["data"][selected_columns].copy()
                    st.success("Columns updated")

            # Drop columns
            st.subheader("Drop Columns")
            columns_to_drop = st.multiselect(
                "Select columns to drop",
                st.session_state["data"].columns,
                key="columns_to_drop"
            )
            if st.button("Drop Selected Columns", key="drop_selected_columns"):
                new_df = st.session_state["data"].drop(columns=columns_to_drop)
                st.session_state["data"] = new_df
                st.success("Selected columns dropped")

            # Rename column
            st.subheader("Rename Column")

            old_name = st.selectbox(
                "Select column to rename",
                st.session_state["data"].columns,
                key="rename_column"
            )
            new_name = st.text_input(
                "Enter new column name",
                key="new_column_name"
            )
            if st.button("Rename Column", key="rename_column_btn") and new_name:
                new_df = st.session_state["data"].rename(columns={old_name: new_name})
                st.session_state["data"] = new_df
                st.success("Column renamed successfully")


        st.space("medium")


        # -------------------- 4.3 and 4.4 DATA TYPES, CATEGORICAL TOOLS --------------------

        with st.container():

            # ------------------------ 4.3 DATA TYPES AND PARSING ------------------------

            with st.container(border=True):
                st.subheader("4.3 Data Types and Parsing")
                st.subheader("Data Type Conversion")

                column_to_convert = st.selectbox(
                    "Select column to convert",
                    st.session_state["data"].columns,
                    key="column_to_convert"
                )
                new_type = st.selectbox(
                    "Convert to",
                    ["Numeric", "Categorical", "Datetime"],
                    key="new_type"
                )

                if st.button("Convert Column Type", key="convert_column_type"):

                    new_df = st.session_state["data"].copy()
                    
                    try:
                        #convert to numeric
                        if new_type == "Numeric":
                            #remove common dirty charact. like commas or $
                            new_df[column_to_convert] = (
                                new_df[column_to_convert]
                                .astype(str)
                                .str.replace(",", "")
                                .str.replace("$", "")
                            )
                            new_df[column_to_convert] = pd.to_numeric(
                                new_df[column_to_convert],
                                errors="coerce"
                            )
                        #convert to categorical
                        elif new_type == "Categorical":
                            new_df[column_to_convert] = (
                                new_df[column_to_convert].astype("category")
                            )
                        #convert to datetime
                        elif new_type == "Datetime":
                            new_df[column_to_convert] = pd.to_datetime(
                                new_df[column_to_convert],
                                errors="coerce"
                            )

                        st.success(f"Column converted to {new_type} successfully")

                    except Exception as e:
                        st.error("Conversion failed")
                        st.write(e) 
                    
                    st.session_state["data"] = new_df

            st.space("medium")


            # ---------------------------- 4.4 CATEGORICAL DATA TOOLS ----------------------------

            with st.container(border=True):
                st.subheader("4.4 Categorical Data Tools")

                cat_cols = st.session_state["data"].select_dtypes(include=["object", "category"]).columns

                if len(cat_cols) > 0:

                    cat_col = st.selectbox(
                        "Select categorical column",
                        cat_cols,
                        key="categorical_column"
                    )

                    clean_option = st.selectbox(
                        "Standardization option",
                        ["Trim whitespace", "Lowercase", "Title Case"],
                        key="categorical_clean_option"
                    )

                    if st.button("Apply Standardization", key="apply_standardization"):
                        new_df = st.session_state["data"].copy()

                        if clean_option == "Trim whitespace":
                            new_df[cat_col] = (
                                new_df[cat_col].astype(str).str.strip()
                            )
                        elif clean_option == "Lowercase":
                            new_df[cat_col] = (
                                new_df[cat_col].astype(str).str.lower()
                            )
                        elif clean_option == "Title Case":
                            new_df[cat_col] = (
                                new_df[cat_col].astype(str).str.title()
                            )

                        st.session_state["data"] = new_df
                        st.success("Categorical values standardized")


                    st.markdown("Rare Category Grouping")

                    threshold = st.slider(
                        "Minimum frequency (%)",
                        0,
                        20,
                        5
                    )

                    if st.button("Group Rare Categories", key="group_rare_btn"):

                        new_df = st.session_state["data"].copy()

                        freq = new_df[cat_col].value_counts(normalize=True)
                        rare = freq[freq < threshold / 100].index

                        new_df[cat_col] = (
                            new_df[cat_col].replace(rare, "Other")
                        )
                        
                        st.session_state["data"] = new_df
                        st.success("Rare categories grouped into 'Other'")


    st.space("medium")


    # --------------------- 4.5 and 4.6 NUMERIC CLEANING AND SCALING ---------------------

    with st.container(horizontal=True):

        # ----------------------------- 4.5 NUMERIC CLEANING ------------------------------

        with st.container(border=True):
            st.subheader("4.5 Numeric Cleaning / Outlier Detection")

            num_cols = st.session_state["data"].select_dtypes(include=["number"]).columns.tolist()

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
                    Q1 = st.session_state["data"][outlier_col].quantile(0.25)
                    Q3 = st.session_state["data"][outlier_col].quantile(0.75)

                    IQR = Q3 - Q1

                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR

                    # detect outliers
                    outliers = st.session_state["data"][(st.session_state["data"][outlier_col] < lower) | (st.session_state["data"][outlier_col] > upper)]

                    #column stats
                    col_mean = st.session_state["data"][outlier_col].mean()
                    col_median = st.session_state["data"][outlier_col].median()
                    col_min = st.session_state["data"][outlier_col].min()
                    col_max = st.session_state["data"][outlier_col].max()

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

                    total_rows = len(st.session_state["data"])
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

                        before = len(st.session_state["data"])

                        st.session_state["data"] = st.session_state["data"][
                            (st.session_state["data"][outlier_col] >= lower) &
                            (st.session_state["data"][outlier_col] <= upper)
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

                        st.session_state["data"][outlier_col] = st.session_state["data"][outlier_col].clip(lower, upper)

                        st.success(f"{cap_count} values capped")

                        st.session_state["transform_log"].append({
                            "operation": "Cap Outliers",
                            "parameters": {"method": "IQR", "values_capped": cap_count},
                            "columns": [outlier_col]
                        })



        st.space("medium")



        # -------------------- 4.6 NORMALIZATION AND SCALING --------------------

        with st.container(border=True):
            st.subheader("4.6 Normalization / Scaling")

            #get numeric columns
            numeric_cols = st.session_state["data"].select_dtypes(include=["number"]).columns.tolist()

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
                    before_stats = st.session_state["data"][scale_columns].describe()

                    #min-max scaling
                    if scaling_method == "Min-Max Scaling":
                        for col in scale_columns:
                            min_val = st.session_state["data"][col].min()
                            max_val = st.session_state["data"][col].max()

                            if max_val - min_val != 0:
                                st.session_state["data"][col] = (
                                    (st.session_state["data"][col] - min_val) / (max_val - min_val)
                                )

                    #Z-score standardizating
                    elif scaling_method == "Z-Score Standardization":
                        for col in scale_columns:
                            mean_val = st.session_state["data"][col].mean()
                            std_val = st.session_state["data"][col].std()

                            if std_val != 0:
                                st.session_state["data"][col] = (
                                    (st.session_state["data"][col] - mean_val) / std_val
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


    st.space("medium")


    # ------------------------- 4.8 Data Validation Rules --------------------------

    with st.container(border=True):

        st.subheader("Data Validation Rules")

        with st.expander("Define Validation Rules", expanded=True):

            col1, col2, col3 = st.columns(3)

            # --- Select column ---
            with col1:
                selected_column = st.selectbox(
                    "Select Column",
                    st.session_state["data"].columns,
                    key="validation_column"
                )

            # --- Rule type ---
            with col2:
                rule_type = st.selectbox(
                    "Rule Type",
                    ["Numeric Range", "Allowed Categories", "Non-Null Constraint"],
                    key="validation_rule_type"
                )

            # --- Rule inputs ---
            rule_config = {}

            with col3:
                if rule_type == "Numeric Range":
                    min_val = st.number_input("Min Value", value=0.0, key="min_val")
                    max_val = st.number_input("Max Value", value=100.0, key="max_val")
                    rule_config = {"min": min_val, "max": max_val}

                elif rule_type == "Allowed Categories":
                    categories = st.text_input(
                        "Allowed Categories (comma-separated)",
                        key="allowed_categories"
                    )
                    rule_config = {"categories": [c.strip() for c in categories.split(",") if c.strip()]}

                elif rule_type == "Non-Null Constraint":
                    rule_config = {"non_null": True}

            # --- Apply rule ---
            if st.button("Validate Data"):
                violations = pd.DataFrame()

                if rule_type == "Numeric Range":
                    mask = (st.session_state["data"][selected_column] < rule_config["min"]) | (st.session_state["data"][selected_column] > rule_config["max"])

                elif rule_type == "Allowed Categories":
                    mask = st.session_state["data"][selected_column].isin(rule_config["categories"])

                elif rule_type == "Non-Null Constraint":
                    mask = st.session_state["data"][selected_column].isna()

                violations = st.session_state["data"][mask].copy()

                if not violations.empty:
                    violations["Violation_Column"] = selected_column
                    violations["Violation_Type"] = rule_type

                    st.session_state["violations"] = violations
                    st.error(f"Found {len(violations)} violations.")
                else:
                    st.session_state["violations"] = pd.DataFrame()
                    st.success("No violations found")

        # Show Violations Table
        if "violations" in st.session_state and not st.session_state["violations"].empty:
            st.subheader("Violations Table")

            st.dataframe(st.session_state["violations"], use_container_width=True)

    
    st.space("xxlarge")


    # ------------------- Dataset preview -------------------

    st.subheader("Current Dataset (Updated)")

    view_option = st.radio(
        "View Options",
        ["First 5 Rows", "Last 5 Rows", "Full Dataset"],
        horizontal=True
    )

    if view_option == "First 5 Rows":
        st.dataframe(st.session_state["data"].head())
    elif view_option == "Last 5 Rows":
        st.dataframe(st.session_state["data"].tail())
    else:
        st.dataframe(st.session_state["data"])



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

    
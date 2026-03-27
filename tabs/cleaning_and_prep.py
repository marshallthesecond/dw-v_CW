import streamlit as st
import pandas as pd







# ---------- TRANSFORMATION ENGINE ----------

def init_transform_system():
    if "transform_log" not in st.session_state:
        st.session_state["transform_log"] = []

    if "history" not in st.session_state:
        st.session_state["history"] = []

def log_step(operation, parameters, columns):
    st.session_state["transform_log"].append({
        "operation": operation,
        "parameters": parameters,
        "columns": columns
    })

def save_state():
    # Save a copy BEFORE transformation
    st.session_state["history"].append(
        st.session_state["data"].copy()
    )

def undo_last():
    if st.session_state["history"]:
        st.session_state["data"] = st.session_state["history"].pop()
        if st.session_state["transform_log"]:
            st.session_state["transform_log"].pop()

def reset_all():
    st.session_state["data"] = st.session_state["original_data"].copy()
    st.session_state["transform_log"] = []
    st.session_state["history"] = []







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
    init_transform_system()

    st.space("medium")




    #------------------- 4.1 MISSING VALUES (NULL HANDLING) -------------------   

    with st.container(border=True):
        
        st.subheader("4.1 Handle Missing Values")

        if "data" in st.session_state:
            df_before = st.session_state["data"].copy()

        # Show missing values
        df_missing = st.session_state["data"].loc[:, st.session_state["data"].isnull().any()]
        if st.checkbox("Show missing values", key="show_missing_checkbox"):
            if df_missing.shape[1] > 0:
                missing = pd.DataFrame({
                    "Column": df_missing.columns,
                    "Missing Count": df_missing.isnull().sum(),
                    "Missing Percentage (%)": (df_missing.isnull().sum() / len(st.session_state["data"]) * 100).round(2),
                    "Data type": st.session_state["data"].dtypes[df_missing.columns].astype(str)
                })
                st.markdown("**Missing Values Overview:**")
                st.dataframe(missing, use_container_width=True, hide_index=True, width="content")
            else:
                st.success("No missing values remaining!")

        # Drop all rows with missing values
        with st.container(horizontal_alignment="right"):
            if st.button("Drop all rows with missing values", key="drop_missing_btn", type="primary"):
                save_state()

                new_df = st.session_state["data"].copy()
                rows_to_drop = new_df.isna().any(axis=1).sum()
                new_df = new_df.dropna()

                st.session_state["data"] = new_df.reset_index(drop=True)

                log_step(
                    "Drop missing rows",
                    {"rows_removed": int(rows_to_drop)},
                    "ALL"
                )

                st.success(f"Dropped {rows_to_drop} rows successfully!")
                action_triggered = True

        # Per-column missing value handling
        # Column selector
        col_select = st.selectbox(
            "Select columns to handle missing values",
            [None] + st.session_state["data"].columns.tolist(),
            key="fill_column_select"
        )
        action_triggered = False

        st.space("xsmall")

        left, right = st.columns([1, 2])
        # Drop rows in selected column
        with left:
            with st.container(horizontal=True, horizontal_alignment="right", gap=None):
                with st.container():
                    if st.button("Drop selected", key="drop_missing_col_btn", type="primary") and col_select:
                        new_df = st.session_state["data"].copy()

                        rows_to_drop = new_df[col_select].isna().sum()
                        new_df = new_df.dropna(subset=[col_select])

                        st.session_state["data"] = new_df.reset_index(drop=True)
                        st.success(f"Dropped {rows_to_drop} rows with missing values in '{col_select}' successfully!")
                        action_triggered = True
                with st.container(width="content"):
                    # Fill selected values with most frequent categorical value
                    if st.button("Fill with Most Frequent Category", key="fill_frequent_cat_btn"):
                        new_df = st.session_state["data"].copy()
                        new_df[col_select] = new_df[col_select].fillna(new_df[col_select].mode().iloc[0])
                        st.session_state["data"] = new_df
                        st.success(f"Filled missing values in '{col_select}' with most frequent category")
                        action_triggered = True

        # Drop columns above a threshold
        with right:
            with st.container(horizontal=True, horizontal_alignment="right"):
                with st.container(width="content"):
                    with st.popover("Threshold"):
                        threshold = st.slider(
                            "Drop selected columns with more than % missing values",
                            0, 100, 50,
                            key="missing_threshold_slider"
                        )
                with st.container(width="content"):
                    if st.button("Drop Columns Above Threshold", key="drop_missing_threshold_btn", type="primary"):
                        new_df = st.session_state["data"].copy()

                        missing_percent = new_df.isnull().mean() * 100
                        cols_to_drop = missing_percent[missing_percent > threshold].index

                        new_df = new_df.drop(columns=cols_to_drop)
                        st.session_state["data"] = new_df.reset_index(drop=True)
                        st.success(f"Dropped {len(cols_to_drop)} columns with more than {threshold}% missing values")
                        action_triggered = True

        st.space("xsmall")

        # Mean, Median, Mode
        st.write("Replace the selected numeric with:")
        btn1, btn2, btn3 = st.columns(3)
        if btn1.button("Mean", key="fill_mean_btn", width="stretch"):
            save_state()

            new_df = st.session_state["data"].copy()
            new_df[col_select] = new_df[col_select].fillna(new_df[col_select].mean())

            st.session_state["data"] = new_df

            log_step(
                "Fill Missing",
                {"method": "mean"},
                [col_select]
            )

            st.success(f"Filled missing values in '{col_select}' with mean")
            action_triggered = True
        if btn2.button("Median", key="fill_median_btn", width="stretch"):
            new_df = st.session_state["data"].copy()
            new_df[col_select] = new_df[col_select].fillna(new_df[col_select].median())
            st.session_state["data"] = new_df
            st.success(f"Filled missing values in '{col_select}' with median")
            action_triggered = True
        if btn3.button("Mode", key="fill_mode_btn", width="stretch"):
            new_df = st.session_state["data"].copy()
            new_df[col_select] = new_df[col_select].fillna(new_df[col_select].mode().iloc[0])
            st.session_state["data"] = new_df
            st.success(f"Filled missing values in '{col_select}' with mode")
            action_triggered = True

        st.space("xsmall")

        with st.container(horizontal=True):
            # Fill selected values with custom value
            with st.container():
                constant = st.text_input("Fill selected missing values with:", value="0", key="fill_constant_input")
                if st.button("Apply Custom Fill", key="apply_custom_fill_btn"):
                    new_df = st.session_state["data"].copy()
                    try:
                        value = float(constant)
                    except:
                        value = constant
                    new_df[col_select] = new_df[col_select].fillna(value)
                    st.session_state["data"] = new_df
                    st.success(f"Filled missing values in '{col_select}' with '{value}'")
                    action_triggered = True

            st.space("medium")

            # Forward / backward fill
            with st.container():
                forward_backward = st.radio(
                    "Select option",
                    ["Forward fill", "Backward fill"],
                    horizontal=True
                )
                if st.button("Apply Forward / Backward fill"):
                    new_df = st.session_state["data"].copy()
                    if forward_backward == "Forward fill":
                        new_df[col_select] = new_df[col_select].ffill()
                    elif forward_backward == "Backward fill":
                        new_df[col_select] = new_df[col_select].bfill()
                    st.session_state["data"] = new_df
                    st.success("Forward/Backward setting applied")
                    action_triggered = True

        # ------ BEFORE/AFTER PREVIEW -----
        if action_triggered:
            st.divider()
            st.subheader("Action Preview")
            df_after = st.session_state["data"]
            
            m1, m2, m3 = st.columns(3)
            
            # Row Count Change
            rows_b, rows_a = len(df_before), len(df_after)
            m1.metric("Total Rows", rows_a, delta=rows_a - rows_b)
            
            # Null Count Change (Inverse color: negative delta = green)
            nulls_b = df_before.isnull().sum().sum()
            nulls_a = df_after.isnull().sum().sum()
            m2.metric("Total Nulls", nulls_a, delta=nulls_a - nulls_b, delta_color="inverse")
            
            # Columns Remaining
            cols_b, cols_a = len(df_before.columns), len(df_after.columns)
            m3.metric("Columns", cols_a, delta=cols_a - cols_b)
            
            st.toast("Data updated!")



    st.space("medium")


    # ------------------- 4.2 DUPLICATE DETECTION -------------------

    with st.container(border=True):
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


    # --------- 4.7, 4.3 and 4.4 - Column Operations + Data Type Conversion + Categorical Tools ---------

    with st.container(horizontal=True):

        # ------------------- 4.7 COLUMN OPERATIONS -------------------

        with st.container(border=True):
            st.subheader("4.7 Column Operations", text_alignment="center")
            
            st.space("medium")

            with st.container(horizontal=True):
                with st.container():
                    # Drop columns
                    st.write("**Drop Columns**")
                    columns_to_drop = st.multiselect(
                        "Select columns to drop",
                        st.session_state["data"].columns,
                        key="columns_to_drop"
                    )
                    if st.button("Drop Columns", key="drop_selected_columns", type="primary"):
                        new_df = st.session_state["data"].drop(columns=columns_to_drop)
                        st.session_state["data"] = new_df
                        st.success("Selected columns dropped")

                with st.container():
                    # Rename column
                    st.write("**Rename Column**")

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
            
            st.divider()

            # Create new columns
            st.write("**Create New Columns**")

            st.write("Write formulas using your exact column names. \n\n"
                        "*Examples:* `Price / Quantity`, `Age * 1.2`, `Salary - Salary.mean()`")
                
            with st.container():
                new_formula_col = st.text_input("New Column Name", key="new_formula_col")
            with st.container():
                formula_input = st.text_input("Formula", key="formula_input")

            if st.button("Apply Formula", key="btn_apply_formula"):
                if new_formula_col and formula_input:
                    new_df = st.session_state["data"].copy()
                    try:
                        # pd.eval evaluates the string expression dynamically
                        new_df[new_formula_col] = new_df.eval(formula_input)
                        
                        st.session_state["data"] = new_df
                        # st.session_state["transform_log"].append(f"Created column '{new_formula_col}' using formula: {formula_input}")
                        st.success(f"Successfully created '{new_formula_col}'.")
                        
                    except Exception as e:
                        st.error(f"Error evaluating formula. Check your column names and syntax. Details: {e}")
                else:
                    st.warning("Please provide both a new column name and a formula.")
            
            st.divider()

            # Binning Numeric Columns
            st.write("**Binning Numeric Columns**")

            numeric_columns = st.session_state["data"].select_dtypes(include=["number"]).columns.tolist()
                
            if numeric_columns:
                bin_target_col = st.selectbox("Select column to bin", numeric_columns, key="bin_target_col")
                new_binned_col = st.text_input("New Binned Column Name", key="new_binned_col")
                
                bin_col1, bin_col2 = st.columns(2)
                with bin_col1:
                    bin_method = st.radio(
                        "Binning Method", 
                        ["Equal-width (Standard)", "Quantile (Equal-sized groups)"], 
                        key="bin_method"
                    )
                with bin_col2:
                    num_bins = st.number_input("Number of bins", min_value=2, max_value=50, value=4, key="num_bins")

                if st.button("Apply Binning", key="btn_apply_binning"):
                    if new_binned_col:
                        new_df = st.session_state["data"].copy()
                        try:
                            if bin_method == "Equal-width (Standard)":
                                # pd.cut divides the range into equal-width intervals
                                new_df[new_binned_col] = pd.cut(new_df[bin_target_col], bins=num_bins)
                            else:
                                # pd.qcut divides the data so each bin has roughly the same number of records
                                # duplicates="drop" prevents errors if many identical values fall on a bin edge
                                new_df[new_binned_col] = pd.qcut(new_df[bin_target_col], q=num_bins, duplicates="drop")
                            
                            st.session_state["data"] = new_df
                            # st.session_state["transform_log"].append(f"Binned '{bin_target_col}' into {num_bins} {bin_method} bins as '{new_binned_col}'")
                            st.success(f"Successfully created binned column '{new_binned_col}'.")
                            
                        except Exception as e:
                            st.error(f"Error during binning: {e}")
                    else:
                        st.warning("Please provide a name for the new binned column.")
            else:
                st.info("No numeric columns found in the dataset to bin.")



        # -------------------- 4.3 and 4.4 DATA TYPES, CATEGORICAL TOOLS --------------------

        # with st.container():

            # ------------------------ 4.3 DATA TYPES AND PARSING ------------------------

        with st.container(border=True):
            st.subheader("4.3 Data Types and Parsing")
            st.space("medium")

            # Datatype conversion
            st.write("**Data Type Conversion**")
            with st.container(horizontal=True):
                with st.container():
                    column_to_convert = st.selectbox(
                        "Select column to convert",
                        st.session_state["data"].columns,
                        key="column_to_convert"
                    )
                with st.container():
                    new_type = st.selectbox(
                        "Convert to",
                        ["Numeric", "Categorical", "Datetime"],
                        key="new_type"
                    )
            with st.container(horizontal_alignment="right"):
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

            st.divider()
            
            # Datetime parsing
            st.markdown("**Datetime Parsing**")

            with st.container(horizontal=True):
                with st.container():
                    # Separate column selector for datetime
                    datetime_column = st.selectbox(
                        "Select column to parse as Datetime",
                        st.session_state["data"].columns,
                        key="datetime_column"
                    )
                with st.container():
                    # Format selection
                    date_format_choice = st.radio(
                        "Select parsing method",
                        ["Auto-detect", "Manual Format"],
                        key="date_format_choice"
                    )

            manual_format = None
            if date_format_choice == "Manual Format":
                manual_format = st.selectbox(
                    "Select or type format (e.g., %d/%m/%Y)",
                    ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y"],
                    key="manual_format_input"
                )
                st.caption("Hint: %d=Day, %m=Month, %Y=Year (4-digit)")

            with st.container(horizontal_alignment="right"):
                if st.button("Parse to Datetime", key="parse_datetime_btn"):
                    new_df = st.session_state["data"].copy()
                    
                    try:
                        if date_format_choice == "Auto-detect":
                            new_df[datetime_column] = pd.to_datetime(
                                new_df[datetime_column], 
                                errors="coerce"
                            )
                        else:
                            new_df[datetime_column] = pd.to_datetime(
                                new_df[datetime_column], 
                                format=manual_format, 
                                errors="coerce"
                            )
                        
                        # Check if parsing failed completely
                        if new_df[datetime_column].isna().all():
                            st.warning("All values became NaT (Not a Time). Check if your chosen format matches the data.")
                        else:
                            st.session_state["data"] = new_df
                            st.success(f"Successfully parsed '{datetime_column}' as Datetime.")
                            
                    except Exception as e:
                        st.error(f"Error during parsing: {e}")

            
            # Show datatypes
            datatypes = pd.DataFrame({
                "Column": st.session_state["data"].columns,
                "Data type": st.session_state["data"].dtypes[st.session_state["data"].columns].astype(str)
            })
            st.subheader("Data types:")
            st.dataframe(datatypes, use_container_width=True, hide_index=True, width="content")



        # st.space("medium")


        # ---------------------------- 4.4 CATEGORICAL DATA TOOLS ----------------------------

        with st.container(border=True):
            st.subheader("4.4 Categorical Data Tools")
            st.space("medium")

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



    # sidebar trnf.log
    with st.sidebar:
        st.markdown("## Transformation Log")

        if st.session_state["transform_log"]:
            for i, step in enumerate(st.session_state["transform_log"], 1):
                with st.container(border=True):
                    st.markdown(f"**{i}. {step['operation']}**")
                    st.caption(f"Columns: {step['columns']}")
                    st.caption(f"Parameters: {step['parameters']}")
        else:
            st.info("No transformations yet.")

        st.divider()

        col1, col2 = st.columns(2)

        if col1.button("↩️ Undo"):
            undo_last()
            st.rerun()

        if col2.button("🔄 Reset"):
            reset_all()
            st.rerun()

        
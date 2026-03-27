import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def visualization():

    st.title("Visualization Builder")

    #Check dataset
    if "data" not in st.session_state or st.session_state["data"] is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return

    df = st.session_state["data"].copy()

    st.space("medium")

    #Filtering

    with st.container(border=True):
        st.subheader("Filter Data")

        col1, col2 = st.columns(2)

        #categorical filt.
        with col1:
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            if cat_cols:
                cat_col = st.selectbox("Select category column", [None] + cat_cols)

                if cat_col:
                    values = df[cat_col].dropna().unique()
                    selected_vals = st.multiselect("Choose values", values)

                    if selected_vals:
                        df = df[df[cat_col].isin(selected_vals)]

        #Numeric filter
        with col2:
            num_cols = df.select_dtypes(include=["number"]).columns.tolist()

            if num_cols:
                num_col = st.selectbox("Select numeric column", [None] + num_cols)

                if num_col:
                    min_val = float(df[num_col].min())
                    max_val = float(df[num_col].max())

                    if min_val == max_val:
                        st.info(f"Column '{num_col}' has a single value: {min_val}. Filtering not needed.")
                    else:
                        selected_range = st.slider(
                            "Select range",
                            min_val,
                            max_val,
                            (min_val, max_val)
                        )

                        df = df[
                            (df[num_col] >= selected_range[0]) &
                            (df[num_col] <= selected_range[1])
                        ]

    st.space("medium")

    #Chart Builder

    with st.container(border=True):
        st.subheader("Create Visualization")

        c1, c2, c3 = st.columns(3)

        with c1:
            plot_type = st.selectbox(
                "Plot Type",
                ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Bar Chart", "Heatmap"]
            )

        with c2:
            x_col = st.selectbox("X Axis", df.columns)

        with c3:
            y_col = st.selectbox("Y Axis (if needed)", [None] + df.columns.tolist())

        agg = st.selectbox(
            "Aggregation (optional)",
            [None, "sum", "mean", "count", "median"]
        )

        top_n = st.number_input("Top N (for bar chart)", min_value=1, value=10)

        st.space("small")

        #Suggestions

        if y_col:
            if not pd.api.types.is_numeric_dtype(df[y_col]):
                st.info("Selected Y column is categorical → Bar Chart may be more suitable")

        if plot_type == "Heatmap":
            num_cols = df.select_dtypes(include=["number"]).columns
            if len(num_cols) < 2:
                st.warning("Heatmap needs at least 2 numeric columns")

        #Generate chart

        if st.button("Generate Chart", type="primary"):

            #Dynamic fg size
            if plot_type == "Bar Chart":
                fig, ax = plt.subplots(figsize=(7, 4))
            elif plot_type == "Heatmap":
                fig, ax = plt.subplots(figsize=(6, 5))
            else:
                fig, ax = plt.subplots(figsize=(6, 4))

            try:

                #Histogram
                if plot_type == "Histogram":
                    if not pd.api.types.is_numeric_dtype(df[x_col]):
                        st.error("Histogram requires numeric column")
                        return

                    ax.hist(df[x_col].dropna())
                    ax.set_title(f"Histogram of {x_col}")

                #BoxPlot
                elif plot_type == "Box Plot":
                    if not pd.api.types.is_numeric_dtype(df[x_col]):
                        st.error("Box plot requires numeric column")
                        return

                    ax.boxplot(df[x_col].dropna())
                    ax.set_title(f"Box Plot of {x_col}")

                #Scatter Plot
                elif plot_type == "Scatter Plot":
                    if not y_col:
                        st.warning("Please select Y column")
                        return

                    if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
                        st.error("Scatter plot requires numeric X and Y")
                        return

                    ax.scatter(df[x_col], df[y_col], alpha=0.6)
                    ax.set_title(f"{x_col} vs {y_col}")

                #LineChart
                elif plot_type == "Line Chart":
                    if not y_col:
                        st.warning("Please select Y column")
                        return

                    if not pd.api.types.is_numeric_dtype(df[y_col]):
                        st.error("Line chart requires numeric Y column")
                        return

                    df_sorted = df.sort_values(by=x_col)

                    if agg:
                        grouped = df_sorted.groupby(x_col)[y_col].agg(agg).reset_index()
                        ax.plot(grouped[x_col], grouped[y_col], linewidth=2)

                    else:
                        if len(df_sorted) > 300:
                            st.info("Large dataset → using mean aggregation for clarity")
                            grouped = df_sorted.groupby(x_col)[y_col].mean().reset_index()
                            ax.plot(grouped[x_col], grouped[y_col], linewidth=2)
                        else:
                            ax.plot(df_sorted[x_col], df_sorted[y_col], linewidth=1, alpha=0.6)

                    ax.set_title(f"{x_col} vs {y_col}")
                    ax.grid(True, linestyle="--", alpha=0.5)

                #Bar chart
                elif plot_type == "Bar Chart":

                    if agg and y_col:
                        if not pd.api.types.is_numeric_dtype(df[y_col]):
                            st.error("Aggregation requires numeric Y column")
                            return

                        grouped = df.groupby(x_col)[y_col].agg(agg).reset_index()
                    else:
                        grouped = df[x_col].value_counts().reset_index()
                        grouped.columns = [x_col, "count"]
                        y_col = "count"

                    grouped = grouped.head(top_n)

                    ax.bar(grouped[x_col], grouped[y_col])
                    plt.xticks(rotation=45)
                    ax.set_title("Bar Chart")

                #heatmap
                elif plot_type == "Heatmap":
                    num_df = df.select_dtypes(include=["number"])

                    if num_df.shape[1] < 2:
                        st.error("Need at least 2 numeric columns for heatmap")
                        return

                    corr = num_df.corr()

                    cax = ax.imshow(corr)
                    ax.set_xticks(range(len(corr.columns)))
                    ax.set_yticks(range(len(corr.columns)))
                    ax.set_xticklabels(corr.columns, rotation=90)
                    ax.set_yticklabels(corr.columns)

                    fig.colorbar(cax)
                    ax.set_title("Correlation Heatmap")

                plt.tight_layout()
                st.pyplot(fig)

            except Exception as e:
                st.error("Error generating chart")
                st.write(e)

    st.space("medium")


    #Preview
    with st.container(border=True):
        st.subheader("Filtered Data Preview")
        
        #column filter for preview
        all_cols = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display",
            all_cols,
            default=all_cols  
        )
        
        #show filtered dataframe with only selected columns
        st.dataframe(df[selected_columns])
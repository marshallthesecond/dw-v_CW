import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def visualization():

    st.title("Visualization Builder")

    #initialize vizlg
    if "viz_log" not in st.session_state:
        st.session_state["viz_log"] = []

    #get dataset
    df = st.session_state.get("data")
    if df is None:
        st.warning("Please upload and clean data first.")
        return

    st.subheader("Current Dataset")
    st.write(df.head())

    columns = df.columns.tolist()

    #chart controls 
    st.subheader("Build Your Chart")

    with st.container(border=True):

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Bar Chart", "Correlation Heatmap"]
        )

        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox("X-axis", columns)

        with col2:
            y_col = st.selectbox("Y-axis (optional)", [None] + columns)

        group_col = st.selectbox("Group (optional)", [None] + columns)

        aggregation = st.selectbox(
            "Aggregation (for bar/line)",
            [None, "mean", "sum", "count", "median"]
        )

    #filtering 
    st.subheader("Filter Data")

    with st.container(border=True):

        filter_col = st.selectbox("Filter column", [None] + columns)

        if filter_col:

            if pd.api.types.is_numeric_dtype(df[filter_col]):

                min_val = float(df[filter_col].min())
                max_val = float(df[filter_col].max())

                selected_range = st.slider(
                    "Select range",
                    min_val, max_val,
                    (min_val, max_val)
                )

                df = df[
                    (df[filter_col] >= selected_range[0]) &
                    (df[filter_col] <= selected_range[1])
                ]

            else:
                values = df[filter_col].dropna().unique()
                selected_values = st.multiselect("Select values", values)

                if selected_values:
                    df = df[df[filter_col].isin(selected_values)]

    #top N for barchart
    top_n = None
    if chart_type == "Bar Chart":
        top_n = st.slider("Top N categories", 1, 20, 10)

    #plotting
    st.subheader("Visualization Output")

    fig, ax = plt.subplots()

    try:

        #histogram
        if chart_type == "Histogram":
            if not pd.api.types.is_numeric_dtype(df[x_col]):
                st.error("Histogram requires numeric column")
            else:
                ax.hist(df[x_col].dropna())
                ax.set_title("Histogram")

        #box plot
        elif chart_type == "Box Plot":
            if not pd.api.types.is_numeric_dtype(df[x_col]):
                st.error("Box plot requires numeric column")
            else:
                ax.boxplot(df[x_col].dropna())
                ax.set_title("Box Plot")

        #scatter plot
        elif chart_type == "Scatter Plot":
            if y_col is None:
                st.warning("Please select Y-axis")
            else:
                ax.scatter(df[x_col], df[y_col])
                ax.set_title("Scatter Plot")

        #Line Chart
        elif chart_type == "Line Chart":
            if y_col is None:
                st.warning("Please select Y-axis")
            else:
                if aggregation:
                    grouped = df.groupby(x_col)[y_col].agg(aggregation)
                    ax.plot(grouped.index, grouped.values)
                else:
                    df_sorted = df.sort_values(by=x_col)
                    ax.plot(df_sorted[x_col], df_sorted[y_col])
                ax.set_title("Line Chart")

        #Bar chart
        elif chart_type == "Bar Chart":
            if aggregation and y_col:
                grouped = df.groupby(x_col)[y_col].agg(aggregation)
                if top_n:
                    grouped = grouped.sort_values(ascending=False).head(top_n)
                ax.bar(grouped.index.astype(str), grouped.values)
            else:
                counts = df[x_col].value_counts().head(top_n)
                ax.bar(counts.index.astype(str), counts.values)
            plt.xticks(rotation=45)
            ax.set_title("Bar Chart")

        #Correlation Heatmap
        elif chart_type == "Correlation Heatmap":
            corr = df.corr(numeric_only=True)
            cax = ax.matshow(corr)
            fig.colorbar(cax)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=90)
            ax.set_yticklabels(corr.columns)
            ax.set_title("Correlation Matrix")
        
        st.pyplot(fig)
        
        #Log Visualization 
        if st.button("Save chart to history"):
            st.session_state["viz_log"].append({
                "chart_type": chart_type,
                "x": x_col,
                "y": y_col,
                "group": group_col,
                "aggregation": aggregation
            })
            st.success("Chart saved to history")

        
    except Exception as e:
        st.error("Error creating chart")
        st.write(e)

    #Visualization History 
    st.subheader("Visualization History")

    if "viz_log" in st.session_state and st.session_state["viz_log"]:
        for i, step in enumerate(st.session_state["viz_log"], 1):
            st.write(f"{i}. {step}")
    else:
        st.info("No visualizations created yet.")
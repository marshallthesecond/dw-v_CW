import streamlit as st
import pandas as pd

def clean_prep():

    st.title("Data Cleaning and Preparation")

    #Get dataset from session state
    df = st.session_state.get("data")

    if df is None:
        st.warning("Please upload a dataset first in the sidebar.")
        return

    st.subheader("Current Dataset")
    st.write(df.head())

    #remove duplicates
    if st.checkbox("Remove duplicate rows"):
        df = df.drop_duplicates()
        st.success("Duplicates removed")

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
        df = df.dropna()
        st.success("Rows with missing values removed")

    if st.checkbox("Fill missing values with 0"):
        df = df.fillna(0)
        st.success("Missing values filled with 0")

    #column selection
    st.subheader("Select columns to keep")

    selected_columns = st.multiselect(
        "Choose columns",
        df.columns,
        default=df.columns
    )

    df = df[selected_columns]

    st.subheader("Cleaned Dataset")
    st.write(df)

    #saving cleaned dataset back to session
    st.session_state["data"] = df

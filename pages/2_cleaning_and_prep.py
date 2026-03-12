import streamlit as st
import pandas as pd

st.title("Data Cleaning and Preparation")

#Get dataset from session state
df = st.session_state.get("data")

if df is None:
    st.warning("Please upload a dataset first in the Upload & Overview page")
else:

    st.subheader("Current Dataset")
    st.write(df)

    #remove duplicates
    if st.checkbox("Remove duplicate rows"):
        df = df.drop_duplicates()
        st.success("Duplicates removed")

    #handle missing values
    st.subheader("Handle missing Values")

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
    
    #column deletion
st.subheader("Drop Columns")

columns_to_drop = st.multiselect(
    "Select columns to drop",
    df.columns
)

if st.button("Drop Selected Columns"):
    df = df.drop(columns=columns_to_drop)
    st.success("Selected columns dropped")

    st.subheader("Cleaned Dataset")
    st.write(df)

    #column rename
st.subheader("Rename column")

old_name = st.selectbox("Select column to rename", df.columns)
new_name = st.text_input("Enter new column name")

if st.button("Rename Column"):
    if new_name.strip() != "":
        df.rename(columns={old_name: new_name}, inplace=True)
        st.session_state["data"] = df
        st.success(f"Column '{old_name}' renamed to '{new_name}'")
        st.rerun()

    #saving cleaned dataset back to session
    st.session_state["data"] = df
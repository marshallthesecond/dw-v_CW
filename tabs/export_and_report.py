import streamlit as st
import time

def export_report():
    col1, col2, col3 = st.columns(3, border=True)
    col1.metric("Revenue", "$12K", "8%")
    col2.metric("Users", "1,204", "12%")
    col3.metric("Latency", "42ms", "-3%")

    left, right = st.columns([2, 1], border=True)
    left.write("This column is twice as wide.")
    right.write("This column is narrower.")

    with st.expander("Show details"):
        st.write("Here are the details...")
        st.image("https://static.streamlit.io/examples/dice.jpg")

    with st.popover("Filter settings"):
        st.checkbox("Include archived")
        st.slider("Min score", 0, 100, 50)


    # placeholder = st.empty()

    # with placeholder.container():
    #     st.write("First set of content")
    #     st.button("A button")

    # time.sleep(2)

    # with placeholder:
    #     st.write("Replacement content")


    with st.container(horizontal=True):
        st.button("One")
        st.button("Two")
        st.button("Three")
    
    with st.container(horizontal=True):
        st.text_input("Name")
        st.text_input("Email")
        st.date_input("Birthday")
    
    st.write("Above")
    st.space("large")
    st.write("Below, with a large gap")
import streamlit as st

st.tilte("My name is Klaus")

st.write("Anything you like a lot")
st.header("My first app")
st.subheader("My second app")

count = 0

if st.button("Click me"):
    count += 1
st.write("count is", count)


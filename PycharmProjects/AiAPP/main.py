from urllib.request import urlopen
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

st.set_page_config(page_title="Aura AI.", layout="wide")

st.title("Welcome to Aura AI, my first AI web app")
st.write("Anything you like a lot")
st.header("My first app")
st.subheader("My second app")
count = 0
if st.button("Click me"):
    count += 1
st.write("count is", count)
name = st.text_input("What is your name")
if st.button("Submit"):
    st.write(f"Hello {name}! Welcome to AI Level 2.")
with st.sidebar:
    st.header("Settings Tab")
    with st.form("Settings"):
        st.selectbox("Select an option", ["My first app", "My second app"])
        source = st.multiselect("Select an option", ["My first app", "My second app"])
        creativity = st.slider("Creativity", 0.0, 1.0, 0.3)
        saved = st.form_submit_button("Save")
    if saved:
        st.write(f"Saved sources : {source} and creativity : {creativity}.")

left, right = st.columns(2)
left.write("sources: 3")
right.write("Creativity: 0,3")

with st.chat_message("user"):
    st.write(f"Hello, I am Aura AI! Welcome to AI Level 2.")
prompt = st.chat_input("Ask something here...")
response = urlopen("https://example.com")
data = response.read().decode("utf-8")
print(data)

if prompt:
    with st.chat_message("user"):
        st.write(f"{prompt}")
    with st.chat_message("Chat Bot"):
        st.write(f"Hello {name}, I am Aura! Welcome to AI level 2.")
else:
    load_dotenv()
    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=os.getenv("AI_TOKEN"),
    )
    r = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    st.write(r.choices[0].message.content)




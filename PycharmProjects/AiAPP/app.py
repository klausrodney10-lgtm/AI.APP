import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from doc_helper import read_file
import chromadb
import pypdf

db = chromadb.PersistentClient(path="./chroma_db")
brain = db.get_or_create_collection("Aura")

def chunk_by_sentence(text, max_size = 400):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += sentence + ". "
        else:

           if current.strip():
            chunks.append(current.strip())
            current = sentence + "."
    if current.strip():
        chunks.append(current.strip())
    return chunks


def store_document(file):
    text = read_file(file)
    chunks = chunk_by_sentence(text)

    prefix = file.name.replace(" ", "_")
    brain.add(
        documents=chunks,
        ids=[f"{prefix}_chunk{i}" for i in range(len(chunks))],
    )
    return len(text), len(chunks)

st.set_page_config(page_title="Aura AI", page_icon="⚡", layout="wide")

st.title("Welcome to Aura, our own AI model on the Web!")
st.subheader("This is my first app")
count = 0
with st.sidebar:
    st.header("Settings tab")
    with st.form("settings"):
        name = st.text_input("What is your name?")
        sources = st.multiselect("Mood:", ["My first app", "My second app"])
        creativity = st.slider("Creativity:", 0.0, 1.0, 0.5)
        uploaded = st.file_uploader("Save system instructions:", type = ["pdf", "txt"])
        saved = st.form_submit_button("Save")
    if saved:
        st.write(f"{name} saved sources: {sources} and creativity: {creativity}")
    st.caption(f"In memory: {brain.count()} chunks")


# commit : git commit -m "Added interface options, settings, etc"
# git push -u origin main

user_input = st.chat_input(
    "Ask something here...",
    accept_file=True,
    file_type=["pdf", "txt"],)

if user_input:
    prompt = user_input.text
    prompt_file = None
    if user_input.files:
        prompt_file = user_input.files[0]
    with st.chat_message("user"):
        if prompt_file:
            text = read_file(prompt_file)
            clean_len, n_chunks = store_document(prompt_file)
            st.write(f"📎 **{prompt_file.name}**")
            st.caption(
                f"{clean_len} characters "
                f"stored as {n_chunks} chunks"
            )
        if prompt:
            st.write(f"{prompt}")
    with st.chat_message("assistant"):
        if prompt == "Cat Fact":
            r = requests.get("https://catfact.ninja/fact")
            fact = r.json()["fact"]
            st.write(f"{fact}")
        elif not prompt:
            st.write("Saved now ask me something about it!")
        else:
            notes=""
            if brain.count()>0:
                hits = brain.query(query_texts=[prompt], n_results=5)
                notes = "\n\n".join(hits["documents"][0])
            if notes:
                full_prompt = (f"Answer using only the notes below."
                               f"If notes don't contain the answer, say so"
                               f"the notes could contain some irrelevant information."
                               f"{notes}"
                               f"User question: {prompt}")

            load_dotenv()
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key = os.environ.get("AI_TOKEN") or st.secrets["AI_TOKEN"],
            )
            r = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=creativity,
                messages=[{"role": "user", "content": full_prompt}],
            )
            st.write(r.choices[0].message.content)
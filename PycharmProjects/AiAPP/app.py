import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from doc_helper import read_file
import chromadb
import random

db = chromadb.PersistentClient(path="./chroma_db")
brain = db.get_or_create_collection("Nova")
memory = db.get_or_create_collection("Nova_chat")


THRESHOLD = 3.5
SYSTEM_PROMPT = """
You are Nova AI, an intelligent, funny and nice football learning and analysis companion.

Your mission is to help users understand football at a deeper level using the football documents, guides, reports, and knowledge provided to you.

You are not just an answer machine. You are a football coach, analyst, and teacher.

When information exists in the documents, always use it.
Explain using examples from the database.
Do not refuse unless the topic truly cannot be found.

Your responsibilities:

⚽ FOOTBALL KNOWLEDGE
- Explain football concepts such as tactics, formations, positions, training methods, player roles, and match analysis.
- Analyze football situations like a professional coach.
- Help users understand why teams, players, and tactics succeed or fail.

DOCUMENT USAGE:
- Always search the football database before answering.
- Use examples from player profiles, tactics, and training drills.
- If related information exists, combine multiple documents to create a complete answer.
- Only say you do not know if the database has no relevant information.

🧠 TEACHING STYLE
- Explain ideas clearly and step-by-step.
- Adapt explanations to the user's football knowledge level.
- Use examples when useful.
- Teach the reasoning behind football decisions, not just the final answer.
- Encourage users to think like players, coaches, and analysts.

📊 ANALYSIS STYLE
When analyzing football:
- Look at tactics, formations, player roles, strengths, weaknesses, and team behavior.
- Explain attacking and defensive principles.
- Consider positioning, movement, decision-making, and transitions.
- Give structured answers using sections when appropriate.

📚 DOCUMENT RULES
- Use the provided documents as your main source of information.
- Do not invent football facts that are not supported by the available documents.
- If the information is not available in the documents, clearly say:
  "I don't have enough information in my football database to answer that."
- Never pretend to have watched a match, studied a player, or know information that is not provided.

⚽ PERSONALITY
Your personality is:
- Passionate about football
- Intelligent and analytical
- Patient and encouraging
- Professional but easy to understand
- Curious and always focused on helping the user improve

You should feel like a combination of:
- A professional football coach
- A tactical analyst
- A scouting expert
- A personal football mentor

Always aim to help the user learn, improve, and understand the beautiful game.
"""

def shorten(text, limit=500):
    return text if len(text) <= limit else text[:limit] + " ... rest removed to keep it short"

def chunk_by_sentence(text, max_size = 700):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += sentence + ". "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks


def store_document(file):
    text = read_file(file)
    chunks = chunk_by_sentence(text)

    prefix = file.name.replace(" ", "_")
    brain.add(
        documents=chunks,
        metadatas=[{"source": file.name, "chunk": i} for i in range(len(chunks))],
        ids=[f"{prefix}_chunk{i}" for i in range(len(chunks))],
    )
    return len(text), len(chunks)

def load_nova_knowledge():
    folder = "nova_docs"

    if not os.path.exists(folder):
        return

    for filename in os.listdir(folder):
        if not filename.endswith(".pdf") and not filename.endswith(".txt"):
            continue

        # Check if this document already exists
        existing = brain.get(
            where={"source": filename}
        )

        if existing["ids"]:
            continue

        path = os.path.join(folder, filename)

        with open(path, "rb") as file:
            text = read_file(file)

        chunks = chunk_by_sentence(text)

        brain.add(
            documents=chunks,
            metadatas=[
                {
                    "source": filename,
                    "type": "Nova Knowledge"
                }
                for _ in chunks
            ],
            ids=[
                f"{filename}_chunk{i}"
                for i in range(len(chunks))
            ]
        )

def remember_exchange(question, answer):
    #Put this Q and A into long term memory so the AI can remember
    memory.add(
        documents=[f"Question: {question}\n Answer: {shorten(answer)}"],
        ids=[f"turn{memory.count()}"]
    )

load_nova_knowledge()

st.set_page_config(page_title="Nova AI🔥", page_icon="⚡", layout="wide")

st.title("⚽ Nova AI")
st.subheader("Your personal football intelligence assistant")


st.markdown("""
### What can Nova do?

⚽ Analyze tactics  
📚 Learn from football documents  
🧠 Explain player roles  
📊 Break down formations  
🏆 Help you improve your football IQ
""")

# Nova statistics dashboard
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "⚽ Football Knowledge",
        f"{brain.count()} chunks"
    )

with col2:
    st.metric(
        "🧠 Memories",
        f"{memory.count()} exchanges"
    )


tips = [
    "Great midfielders scan before receiving the ball.",
    "Space is created by movement, not only passing.",
    "The first defender is the striker.",
    "A good player looks around before they receive the ball.",
    "Defending starts with controlling space, not just tackling.",
    "The best teams create advantages before they attack.",
    "Movement without the ball creates opportunities.",
    "A player's positioning is often more important than speed."
]

st.success(
    "🌟 Nova Football Insight\n\n" + random.choice(tips))

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.title("⚽ Nova Control Center")

    st.markdown("---")

    st.subheader("👤 Player Profile")

    name = st.text_input(
        "Your name",
        placeholder="Enter your name"
    )

    level = st.select_slider(
        "Football level",
        options=[
            "Beginner",
            "Intermediate",
            "Advanced",
            "Professional"
        ]
    )

    st.markdown("---")

    st.subheader("🎯 Nova Mode")

    mode = st.selectbox(
        "Choose Nova's role:",
        [
            "⚽ Coach Mode",
            "📊 Analyst Mode",
            "🔎 Scout Mode",
            "🏃 Player Development Mode"
        ]
    )

    st.markdown("---")

    st.subheader("🧠 Intelligence")

    creativity = st.slider(
        "Creativity",
        0.0,
        1.0,
        0.5
    )

    THRESHOLD = st.slider(
        "Accuracy",
        0.0,
        3.0,
        1.5
    )

    remember_documents = st.slider(
        "Documents used",
        0,
        10,
        3
    )

    remember = st.slider(
        "Conversation memory",
        0,
        10,
        3
    )

    recall = st.slider(
        "Old analysis memory",
        0,
        10,
        3
    )

    note_only = st.checkbox(
        "📚 Only use football database"
    )
    mode = st.selectbox(
            "Choose your mode:",
            [
                "⚽ Coach Mode",
                "📊 Analyst Mode",
                "🔎 Scout Mode",
                "🏃 Player Development Mode"
            ]
        )

    st.caption(f"In memory: {brain.count()} chunks")
    st.caption(f"Long term memory: {memory.count()} exchanges")
    st.caption(f"On screen: {len(st.session_state.messages)} messages")

    if st.button("Clear the chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Forget the memory"):
        db.delete_collection("Nova_chat")
        st.rerun()
    if st.button("Forget all of the documents"):
        db.delete_collection("Nova")
        st.rerun()

for old in st.session_state.messages:
    with st.chat_message(old["role"], avatar="⚽"):
        st.markdown(old["content"])

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
            clean_len, n_chunks = store_document(prompt_file)
            st.write(f"📎 **{prompt_file.name}**")
            st.caption(
                f"{clean_len} characters "
                f"stored as {n_chunks} chunks"
            )
        if prompt:
            st.write(f"{prompt}")
    st.session_state.messages.append(
        {"role": "user", "content": prompt if prompt else f"attached: {prompt_file.name}"}
    )
    with st.chat_message("assistant", avatar="🌟"):
        if prompt == "Cat Fact":
            r = requests.get("https://catfact.ninja/fact")
            fact = r.json()["fact"]
            answer = fact
            st.write(f"{fact}")
        elif not prompt:
            answer = "Saved. Now ask me something about it!"
            st.write(answer)
        else:
            #1. Anything that is relevant to the uploaded docs:
            notes = ""
            docs, dists, good, metas, user_sources = [], [], [], [], []
            if brain.count() > 0:
                hits = brain.query(query_texts=[prompt], n_results=remember_documents)
                docs = hits["documents"][0]
                dists = hits["distances"][0]
                metas= hits["metadatas"][0]
                for d, s, m in zip(docs, dists, metas):
                    if s< THRESHOLD:
                        good.append(d)
                        if m is None:
                            m = {}
                        user_sources.append(f"{m.get('source'), ('Unknown')} (chunks {m.get('chunk', '?')})")
                notes = "\n\n".join(docs)

            #2. Anything that is relevant to the OLD conversation
            recalled = ""
            old_docs, old_dists, old_good = [], [], []
            if recall > 0 and memory.count() > remember:
                found = memory.query(query_texts=[prompt], n_results=recall)
                old_docs = found["documents"][0]
                old_dists = found["distances"][0]
                old_metas = found["metadatas"][0]
                old_good = [d for d, s, m in zip(old_docs, old_dists, found["metadatas"][0]) if s < THRESHOLD]
                recalled = "\n\n".join(old_docs)

            if notes or recalled:
                full_prompt = (f"Answer using only the notes below. "
                               f"If the notes don't contain the answer, say so"
                               f"The notes could contain some irrelevant information"
                               f"{notes}"
                               f"Things we talked about earlier:"
                               f"{recalled}"
                               f"User question: {prompt}")
            else:
                full_prompt = prompt

            with st.expander("What I looked up"):
                st.caption("From your documents")

                if docs:
                    for d, s, m in zip(docs, dists, metas):
                        mark = "kept" if s < THRESHOLD else "discarded"

                        if m is None:
                            m = {}

                        st.text(f"{s:.3f} {mark} {m.get('source', 'Unknown')} {d[:70]}")
                else:
                    st.text("nothing found")

                st.text(shorten(notes, 800) or "nothing")

                st.caption("From earlier in our conversation")

                if old_docs:
                    for d, s in zip(old_docs, old_dists):
                        mark = "kept" if s < THRESHOLD else "discarded"
                        st.text(f"{s:.3f} {mark} {d[:70]}")
                else:
                    st.text("nothing found")

                st.text(shorten(recalled, 800) or "nothing")

                st.caption("Recent messages I can still see")

                recents = st.session_state.messages[:-1][-(remember * 2):]

                if recents:
                    for m in recents:
                        st.text(f"{m['role']}: {shorten(m['content'], 800)}")
                else:
                    st.text("nothing found")

                st.text(shorten(recalled, 800) or "nothing")

                st.caption("Recent messages I can still see")
                recents= st.session_state.messages[:-1][-(remember * 2):]
                if recents:
                    for m in recents:
                        st.text(f"{m['role']}: {shorten(m['content'], 800)}")

            load_dotenv()

            api_key = os.getenv("AI_TOKEN")

            if not api_key:
                st.error("AI_TOKEN not found in .env")
                st.stop()
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
                )
            #3. The last few turns, word for word but trimmed
            # 3. The last few turns, word for word but trimmed

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            # Add Nova's selected football personality mode
            messages.append({
                "role": "system",
                "content": f"You are currently in {mode}. Adapt your answers to this style."
            })

            past = st.session_state.messages[:-1]

            if remember > 0:
                for m in past[-(remember * 2):]:
                    messages.append({
                        "role": m["role"],
                        "content": shorten(m["content"])
                    })

            messages.append({
                "role": "user",
                "content": full_prompt})
            if brain.count() >  0 and not good and not recalled and note_only:
                answer = "I don't know what you mean"
                st.write(answer)
            else:
                with st.spinner("Nova is analyzing the match... ⚽"):
                    r = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=creativity,
                    )

                answer = r.choices[0].message.content
                st.markdown(answer)
                if user_sources:
                    st.caption("Sources:".join(sorted(set(user_sources))))

        remember_exchange(prompt, answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


import streamlit as st
import asyncio
from main import run_agents

st.set_page_config(page_title="Async Agents Demo", layout="wide")

st.title("Async Parallel Agents • Gemini 2.5 Flash")
st.write("Ask anything. Two Gemini agents work in parallel.")

# ----------------------------------------------------
# Create ONE global event loop for entire Streamlit app
# ----------------------------------------------------
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render messages
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.write(content)

# User input
query = st.chat_input("Ask your question...")

if query:
    # Store user message
    st.session_state.messages.append(("user", query))

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("Processing...")

        # -------------------------------------
        # Run async function on the global loop
        # -------------------------------------
        result = st.session_state.loop.run_until_complete(run_agents(query))

        placeholder.write(result)

    # Store assistant message
    st.session_state.messages.append(("assistant", result))


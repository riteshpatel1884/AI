# from chatbot import chatbot
# from langchain_core.messages import BaseMessage, HumanMessage

# thread_id = "1"
# config = {'configurable': {'thread_id': thread_id}}
# resposne = chatbot.invoke({'messages':[HumanMessage(content="What is the capital of India")]}, config=config)

# print(resposne['messages'][-1].content)


# run: python app.py
# # (genai) PS D:\GenAI\21_Agentic_AI\11_projects\01_project> python app.py
# # The capital of India is **New Delhi**.



## UI 
import streamlit as st
import uuid

from chatbot import chatbot
from langchain_core.messages import HumanMessage, AIMessage


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="NOVA — AI Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown("""
<style>

    /* ---------- Global ---------- */

    .stApp {
        background: #0b0d12;
        color: #f5f5f5;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background: #0f1117;
        border-right: 1px solid #20232d;
    }

    .sidebar-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .sidebar-subtitle {
        color: #777d8c;
        font-size: 13px;
        margin-bottom: 28px;
    }

    .thread-box {
        background: #151820;
        border: 1px solid #252936;
        border-radius: 12px;
        padding: 14px;
        margin-top: 18px;
    }

    .thread-label {
        color: #777d8c;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .thread-id {
        color: #d7d9df;
        font-family: monospace;
        font-size: 13px;
        margin-top: 6px;
    }

    /* ---------- Main ---------- */

    .main-wrapper {
        max-width: 900px;
        margin: auto;
    }

    .hero {
        text-align: center;
        padding-top: 70px;
        padding-bottom: 35px;
    }

    .logo {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -1px;
        margin: 0;
    }

    .hero-subtitle {
        color: #777d8c;
        font-size: 15px;
        margin-top: 8px;
    }

    /* ---------- Messages ---------- */

    .user-label {
        color: #8f96a8;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .assistant-label {
        color: #8f96a8;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    /* ---------- Empty state ---------- */

    .suggestions {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 25px;
    }

    .suggestion {
        background: #12151c;
        border: 1px solid #242833;
        border-radius: 10px;
        padding: 10px 15px;
        color: #aeb3c0;
        font-size: 13px;
    }

    /* ---------- Chat input ---------- */

    div[data-testid="stChatInput"] {
        border-top: 1px solid #20232d;
        padding-top: 10px;
    }

    div[data-testid="stChatInput"] textarea {
        background: #151820 !important;
        border: 1px solid #292d38 !important;
        border-radius: 14px !important;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #292d38;
        background: #151820;
        color: #d7d9df;
    }

    .stButton > button:hover {
        border-color: #555b6c;
        color: white;
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Session State
# -----------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Config
# -----------------------------

config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


# -----------------------------
# Load existing conversation
# -----------------------------

def load_conversation():

    try:
        state = chatbot.get_state(config)

        if state.values:
            messages = state.values.get("messages", [])

            st.session_state.messages = []

            for message in messages:

                if isinstance(message, HumanMessage):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": message.content
                    })

                elif isinstance(message, AIMessage):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": message.content
                    })

    except Exception:
        pass


# Only load if we don't already have messages
if not st.session_state.messages:
    load_conversation()


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">✦ NOVA</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">LangGraph AI Workspace</div>',
        unsafe_allow_html=True
    )

    if st.button("＋  New conversation", use_container_width=True):

        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []

        st.rerun()

    st.markdown(
        f"""
        <div class="thread-box">
            <div class="thread-label">Active thread</div>
            <div class="thread-id">
                {st.session_state.thread_id}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("Powered by LangGraph")
    st.caption("Memory: InMemory Checkpointer")


# -----------------------------
# Main UI
# -----------------------------

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)


# Empty state
if not st.session_state.messages:

    st.markdown(
        """
        <div class="hero">
            <div class="logo">✦</div>
            <div class="hero-title">What can I help you solve?</div>
            <div class="hero-subtitle">
                Ask anything. Your conversation is remembered inside this thread.
            </div>
        </div>

        <div class="suggestions">
            <div class="suggestion">Explain Object Oriented Programming</div>
            <div class="suggestion">Help me debug Python</div>
            <div class="suggestion">Explain LangGraph</div>
            <div class="suggestion">Prepare me for an AI interview</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# Display Messages
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------
# Chat Input
# -----------------------------

user_message = st.chat_input(
    "Message NOVA..."
)


if user_message:

    # Show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)


    # Call LangGraph
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = chatbot.invoke(
                {
                    "messages": [
                        HumanMessage(content=user_message)
                    ]
                },
                config=config
            )

            ai_response = response["messages"][-1].content

            st.markdown(ai_response)


    # Save locally for Streamlit rendering
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })


st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
from chatbot import chatbot

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }
    h1 {
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.2rem;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -0.6rem;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.6rem 0.2rem;
    }
    .stChatInput textarea {
        border-radius: 12px !important;
    }
    .thread-pill {
        display: inline-block;
        background: #1e293b;
        color: #38bdf8;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "threads" not in st.session_state:
    st.session_state.threads = {}          # thread_id -> list of {role, content}

if "current_thread" not in st.session_state:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.threads[new_id] = []
    st.session_state.current_thread = new_id


def new_chat():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.threads[new_id] = []
    st.session_state.current_thread = new_id


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Conversations")
    if st.button("➕ New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.divider()

    for tid in reversed(list(st.session_state.threads.keys())):
        messages = st.session_state.threads[tid]
        label = messages[0]["content"][:28] + "…" if messages else "New conversation"
        is_active = tid == st.session_state.current_thread
        if st.button(
            f"{'🟢' if is_active else '⚪'} {label}",
            key=f"thread_{tid}",
            use_container_width=True,
        ):
            st.session_state.current_thread = tid
            st.rerun()

    st.divider()
    if st.button("🗑️ Delete current chat", use_container_width=True):
        del st.session_state.threads[st.session_state.current_thread]
        if not st.session_state.threads:
            new_chat()
        else:
            st.session_state.current_thread = list(st.session_state.threads.keys())[-1]
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🤖 LangGraph Chatbot")
st.markdown(
    f'<div class="subtitle">'
    f'<span class="thread-pill">thread: {st.session_state.current_thread}</span> '
    f'Powered by LangGraph · streaming responses</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------------
current_messages = st.session_state.threads[st.session_state.current_thread]

for msg in current_messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input + streaming response
# ---------------------------------------------------------------------------
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show + store user message
    current_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # Stream assistant response
    config = {"configurable": {"thread_id": st.session_state.current_thread}}

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        with st.spinner("Thinking..."):
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                if message_chunk.content:
                    full_response += message_chunk.content
                    placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    current_messages.append({"role": "assistant", "content": full_response})
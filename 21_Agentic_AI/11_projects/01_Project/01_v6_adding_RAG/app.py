import streamlit as st
import uuid
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from chatbot import chatbot, get_all_threads

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
    .tool-pill {
        display: inline-block;
        background: #0b3b2e;
        color: #34d399;
        border: 1px solid #065f46;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin: 0 4px 6px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


def load_thread_messages(thread_id):
    """Pull a thread's message history out of the checkpointer, in UI format.

    Reconstructs which tools were used for each assistant turn by looking
    at ToolMessage entries that sit between the triggering AIMessage and
    the final AIMessage response.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = chatbot.get_state(config)
    messages = state.values.get("messages", []) if state.values else []

    ui_messages = []
    pending_tools = []

    for m in messages:
        if isinstance(m, HumanMessage):
            ui_messages.append({"role": "user", "content": m.content})
            pending_tools = []

        elif isinstance(m, ToolMessage):
            name = getattr(m, "name", None) or "tool"
            if name not in pending_tools:
                pending_tools.append(name)

        elif isinstance(m, AIMessage):
            # Intermediate AIMessages that only request tool calls have no
            # content and are followed by more turns; only the final
            # content-bearing AIMessage becomes a rendered assistant turn.
            if m.content:
                ui_messages.append({
                    "role": "assistant",
                    "content": m.content,
                    "tools": pending_tools,
                })
                pending_tools = []

    return ui_messages


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "threads" not in st.session_state:
    # Rehydrate every conversation already sitting in the sqlite db
    st.session_state.threads = {
        tid: load_thread_messages(tid) for tid in get_all_threads()
    }

if "current_thread" not in st.session_state:
    if st.session_state.threads:
        # jump into an existing thread (arbitrary order since
        # get_all_threads returns a set -- swap for a real "last active"
        # thread if you start tracking timestamps)
        st.session_state.current_thread = next(iter(st.session_state.threads))
    else:
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
# Helper: render tool pills
# ---------------------------------------------------------------------------
def render_tool_pills(tool_names):
    if not tool_names:
        return
    pills = "".join(f'<span class="tool-pill">🔧 {name}</span>' for name in tool_names)
    st.markdown(pills, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------------
current_messages = st.session_state.threads[st.session_state.current_thread]

for msg in current_messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant" and msg.get("tools"):
            render_tool_pills(msg["tools"])
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
        tool_status = st.empty()
        placeholder = st.empty()
        full_response = ""
        active_tools = []

        with st.spinner("Thinking..."):
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                node = metadata.get("langgraph_node")

                if node == "chat_node":
                    # Tool calls are visible on the AI chunk as soon as the
                    # LLM decides to invoke one (before execution happens).
                    for call in getattr(message_chunk, "tool_calls", None) or []:
                        name = call.get("name")
                        if name and name not in active_tools:
                            active_tools.append(name)
                            with tool_status:
                                render_tool_pills(active_tools)

                    if message_chunk.content:
                        full_response += message_chunk.content
                        placeholder.markdown(full_response + "▌")

                elif node == "tools":
                    # Actual tool execution result (ToolMessage chunk)
                    name = getattr(message_chunk, "name", None) or "tool"
                    if name not in active_tools:
                        active_tools.append(name)
                        with tool_status:
                            render_tool_pills(active_tools)

        placeholder.markdown(full_response)

    current_messages.append({
        "role": "assistant",
        "content": full_response,
        "tools": active_tools,
    })
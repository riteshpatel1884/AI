import streamlit as st
import uuid
import os
import tempfile
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.types import Command
from chatbot import chatbot, get_all_threads, ingest_rag_document

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
    .doc-pill {
        display: inline-block;
        background: #1e2a44;
        color: #38bdf8;
        border: 1px solid #1e3a5f;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .approval-pill {
        display: inline-block;
        background: #3f1d1d;
        color: #fca5a5;
        border: 1px solid #7f1d1d;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
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


def get_pending_interrupt(thread_id):
    """Check if a thread's graph is currently paused on an interrupt()
    (e.g. purchase_stock waiting for human approval) and return the
    interrupt's payload, or None if the graph isn't paused."""
    config = {"configurable": {"thread_id": thread_id}}
    state = chatbot.get_state(config)
    for task in state.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


def render_tool_pills(tool_names):
    if not tool_names:
        return
    pills = "".join(f'<span class="tool-pill">🔧 {name}</span>' for name in tool_names)
    st.markdown(pills, unsafe_allow_html=True)


def stream_and_render(input_data, config, tool_status, placeholder):
    """Stream a graph invocation (fresh input or a Command(resume=...))
    and live-render tokens + tool pills into the given placeholders."""
    full_response = ""
    active_tools = []

    with st.spinner("Thinking..."):
        for message_chunk, metadata in chatbot.stream(
            input_data,
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
    return full_response, active_tools


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

if "indexed_document" not in st.session_state:
    st.session_state.indexed_document = None

if "pending_interrupts" not in st.session_state:
    # A thread whose graph is paused mid-tool-call (e.g. purchase_stock
    # waiting on human approval) shows up here, survives app restarts
    # since it's derived straight from the checkpointer.
    st.session_state.pending_interrupts = {
        tid: get_pending_interrupt(tid) for tid in st.session_state.threads
    }
    st.session_state.pending_interrupts = {
        tid: val for tid, val in st.session_state.pending_interrupts.items() if val
    }


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
        awaiting = tid in st.session_state.pending_interrupts
        icon = "🟢" if is_active else ("🟠" if awaiting else "⚪")
        if st.button(
            f"{icon} {label}",
            key=f"thread_{tid}",
            use_container_width=True,
        ):
            st.session_state.current_thread = tid
            st.rerun()

    st.divider()
    if st.button("🗑️ Delete current chat", use_container_width=True):
        del st.session_state.threads[st.session_state.current_thread]
        st.session_state.pending_interrupts.pop(st.session_state.current_thread, None)
        if not st.session_state.threads:
            new_chat()
        else:
            st.session_state.current_thread = list(st.session_state.threads.keys())[-1]
        st.rerun()

    st.divider()

    # -----------------------------------------------------------------
    # Document upload (RAG)
    # -----------------------------------------------------------------
    st.markdown("### 📄 Document")

    if st.session_state.indexed_document:
        st.markdown(
            f'<span class="doc-pill">📎 {st.session_state.indexed_document}</span>',
            unsafe_allow_html=True,
        )

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        key="pdf_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is not None and uploaded_file.name != st.session_state.indexed_document:
        with st.spinner(f"Indexing '{uploaded_file.name}'..."):
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, uploaded_file.name)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                ingest_rag_document(temp_path)
                st.session_state.indexed_document = uploaded_file.name
                st.success("Document indexed! Ask away.")
            except Exception as e:
                st.error(f"Failed to index document: {e}")
            finally:
                os.remove(temp_path)

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
current_thread = st.session_state.current_thread
current_messages = st.session_state.threads[current_thread]
config = {"configurable": {"thread_id": current_thread}}

for msg in current_messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant" and msg.get("tools"):
            render_tool_pills(msg["tools"])
        if msg["content"]:
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Human-in-the-loop approval card (purchase_stock, etc.)
# ---------------------------------------------------------------------------
pending_question = st.session_state.pending_interrupts.get(current_thread)

if pending_question:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown('<span class="approval-pill">⏸️ Awaiting your approval</span>', unsafe_allow_html=True)
        st.markdown(pending_question)

        col1, col2 = st.columns(2)
        approve = col1.button("✅ Approve", use_container_width=True, key=f"approve_{current_thread}")
        decline = col2.button("❌ Decline", use_container_width=True, key=f"decline_{current_thread}")

        if approve or decline:
            decision = "yes" if approve else "no"

            tool_status = st.empty()
            placeholder = st.empty()
            full_response, active_tools = stream_and_render(
                Command(resume=decision), config, tool_status, placeholder
            )

            if full_response or active_tools:
                current_messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "tools": active_tools,
                })

            del st.session_state.pending_interrupts[current_thread]

            # In case the resumed run immediately hits another interrupt
            follow_up = get_pending_interrupt(current_thread)
            if follow_up:
                st.session_state.pending_interrupts[current_thread] = follow_up

            st.rerun()

# ---------------------------------------------------------------------------
# Chat input + streaming response
# ---------------------------------------------------------------------------
user_input = st.chat_input(
    "Approve or decline the pending request above first…" if pending_question else "Ask me anything...",
    disabled=bool(pending_question),
)

if user_input and not pending_question:
    # Show + store user message
    current_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # Stream assistant response
    with st.chat_message("assistant", avatar="🤖"):
        tool_status = st.empty()
        placeholder = st.empty()
        full_response, active_tools = stream_and_render(
            {"messages": [HumanMessage(content=user_input)]}, config, tool_status, placeholder
        )

    if full_response or active_tools:
        current_messages.append({
            "role": "assistant",
            "content": full_response,
            "tools": active_tools,
        })

    # If a tool (e.g. purchase_stock) paused the graph waiting on a human
    # decision, surface it and rerun so the approval card shows up.
    interrupt_value = get_pending_interrupt(current_thread)
    if interrupt_value:
        st.session_state.pending_interrupts[current_thread] = interrupt_value
        st.rerun()
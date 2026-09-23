# Method 1: Using init_chat_model
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# load_dotenv() 

# model = init_chat_model("google_genai:gemini-2.5-f

# response = model.invoke("What is Cricket?")
# print(response.content)




# Method 2: Using model class

# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# load_dotenv()

# model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
# response = model.invoke("Why do parrots talk?")
# print(response.content)


# groq model
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# load_dotenv() 

# model = init_chat_model("groq:meta-llama/llama-4-scout-17b-16e-instruct")

# response = model.invoke("What is GenAI?")
# print(response.content)


# Mistral model
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# load_dotenv() 

# model = init_chat_model("mistral-small-2603")

# response = model.invoke("What is GenAI?")
# print(response.content)

# Mistral model using model class 
# from dotenv import load_dotenv
# from langchain_mistralai import ChatMistralAI
# load_dotenv() 

# model = ChatMistralAI(model = "mistral-small-2603")

# response = model.invoke("What is GenAI?")
# print(response.content)


# Temperature: Value must be between 0 - 1
# For a creative response use value closer to 1
# For logics/mathematics use value closer to 0


#max_tokens 
# from dotenv import load_dotenv
# from langchain_mistralai import ChatMistralAI
# load_dotenv() 

# model = ChatMistralAI(model = "mistral-small-2603", max_tokens=20)

# response = model.invoke("What is GenAI?")
# print(response.content)   # **GenAI (Generative AI)** refers to a category of artificial intelligence (AI) models 

# from dotenv import load_dotenv
# from langchain_mistralai import ChatMistralAI
# load_dotenv() 

# model = ChatMistralAI(model = "mistral-small-2603", max_tokens=100)

# response = model.invoke("What is GenAI?")
# print(response.content) 
# **Generative AI (GenAI)** is a type of artificial intelligence (AI) that can create new content—such astext, images, audio, video, or code—based on patterns and data it has learned from. Unlike traditional AI, which analyzes or classifies existing data, GenAI generates original outputs that resemble human-like creativity.

# ### **Key Features of GenAI:**
# 1. **Creative Output** – Produces new content rather than just analyzing or classifying data.
# 2. **



import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

st.set_page_config(page_title="GenAI Chat", page_icon="💬", layout="centered")

st.title("RP GenAI Model")

# --- Sidebar settings ---
with st.sidebar:
    st.header("Settings")
    max_tokens = st.slider("Max tokens", min_value=50, max_value=2000, value=500, step=50)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.7, step=0.1)
    model_name = st.text_input("Model name", value="mistral-small-2603")

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    

# --- Init model (cached so it isn't rebuilt on every rerun) ---
@st.cache_resource(show_spinner=False)
def get_model(model_name: str, max_tokens: int, temperature: float):
    return ChatMistralAI(model=model_name, max_tokens=max_tokens, temperature=temperature)

try:
    model = get_model(model_name, max_tokens, temperature)
except Exception as e:
    st.error(f"Could not initialize model: {e}")
    st.stop()

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask something, e.g. 'What is GenAI?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = model.invoke(prompt)
                answer = response.content
            except Exception as e:
                answer = f"⚠️ Error: {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

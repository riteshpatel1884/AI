# GenAI

A hands-on, structured learning repository covering the core building blocks of Generative AI application development - from chat models and embeddings to RAG pipelines and vector databases, primarily built with **LangChain**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-🔗-1C3C3C)
![uv](https://img.shields.io/badge/Package%20Manager-uv-DE5FE9)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Overview

This repository is a personal knowledge base and playground for exploring **Generative AI** concepts step by step - starting from the fundamentals of chat and embedding models, moving through prompt engineering and structured outputs, and culminating in full **Retrieval-Augmented Generation (RAG)** pipelines backed by vector databases.

Each folder is self-contained, with working code examples and templates that build on one another.

---

## 🗂️ Repository Structure

| Folder | Description |
|---|---|
| [`01_chat_models`](./01_chat_models) | Basics of interacting with chat-based LLMs (OpenAI, Anthropic, etc.) |
| [`02_embedding_models`](./02_embedding_models) | Working with embedding models for semantic representation of text |
| [`03_local_models`](./03_local_models) | Running and experimenting with locally hosted open-source models |
| [`04_chatBot`](./04_chatBot) | A conversational chatbot built using chat model concepts |
| [`05_prompt_templets`](./05_prompt_templets) | Reusable and dynamic prompt templates for LLM calls |
| [`06_structured_outputs`](./06_structured_outputs) | Techniques for enforcing structured, schema-based LLM responses |
| [`07_RAG`](./07_RAG) | Retrieval-Augmented Generation pipelines and workflows |
| [`08_vector_DB`](./08_vector_DB) | Vector database integration for storage and similarity search |
| [`09_Project`](./09_Project) | End-to-end mini projects combining the above concepts |
| [`10_runnables`](./10_runnables) | LangChain Runnables — chaining, composition, and execution graphs |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

Clone the repository:

```bash
git clone https://github.com/riteshpatel1884/GenAI.git
cd GenAI
```

**Using `uv` (recommended):**
```bash
uv sync
```

**Using `pip`:**
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory and add your API keys as needed:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## 🧭 Suggested Learning Path

```
01_chat_models  →  02_embedding_models  →  03_local_models
       ↓
04_chatBot  →  05_prompt_templets  →  06_structured_outputs
       ↓
07_RAG  →  08_vector_DB  →  10_runnables  →  09_Project
```

Start with the fundamentals of chat and embedding models, then move into prompting and structured outputs, and finally combine everything into RAG pipelines and complete projects.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Framework:** LangChain
- **Package Management:** `uv` / `pip`
- **Vector Stores:** (e.g. FAISS / Chroma — as used in `08_vector_DB`)
- **LLM Providers:** OpenAI, Anthropic, Groq, and local models

---

## 🤝 Contributing

This is primarily a learning repository, but suggestions, issue reports, and pull requests are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a pull request

---

## 📄 License

This project is licensed under the **MIT License** - feel free to use and adapt it for your own learning.

---

## ⭐ Acknowledgements

Built while learning and experimenting with the **LangChain** ecosystem and modern GenAI tooling.

If this repo helped you, consider giving it a ⭐!


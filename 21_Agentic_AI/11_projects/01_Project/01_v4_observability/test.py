from dotenv import load_dotenv
load_dotenv(override=True)

import os

print("PROJECT:", os.getenv("LANGSMITH_PROJECT"))
print("TRACING:", os.getenv("LANGSMITH_TRACING"))

from langchain_groq import ChatGroq

model = ChatGroq(
    model="openai/gpt-oss-120b"
)

response = model.invoke("Tell me a joke about programming")

print(response.content)
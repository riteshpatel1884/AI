from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
load_dotenv()

# HuggingFaceEndpoint: uasing this we will reterive the model from huggingface

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    temperature=0.7,
    max_new_tokens=200
)
model = ChatHuggingFace(llm=llm)

response = model.invoke("Economy of India in 2030 will be ")

print(response.

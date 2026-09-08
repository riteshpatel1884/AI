from chatbot import chatbot
from langchain_core.messages import BaseMessage, HumanMessage

thread_id = "1"
config = {'configurable': {'thread_id': thread_id}}
# resposne = chatbot.invoke({'messages':[HumanMessage(content="What is the capital of India")]}, config=config)

# using streaming
# response = chatbot.stream({'messages':[HumanMessage(content="What is the capital of India")]}, config=config, stream_mode='messages')
# there are differnt types of stream messages. read the docs.


# we will get a generator: <generator object Pregel.stream at 0x0000014E1FEACFE0>
# so we can use for loop to get the output

for message_chunk, metadata in chatbot.stream({'messages':[HumanMessage(content="Explain RAG")]}, config=config, stream_mode='messages'):
    if message_chunk.content:
        print(message_chunk.content, end="", flush= True)


# run: python app.py
# # (genai) PS D:\GenAI\21_Agentic_AI\11_projects\01_project> python app.py
# # The capital of India is **New Delhi**.


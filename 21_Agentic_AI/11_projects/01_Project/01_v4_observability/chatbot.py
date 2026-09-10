from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3



llm = ChatGroq(
    model="openai/gpt-oss-120b"
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# BaseMessage = user message + AI message


def chat_node(state: ChatState):
    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}


# create db connection object
connection = sqlite3.connect(database="database.db", check_same_thread=False)
#by default sqlite does not support multi threading so we cant craate multiple thread so we need to chat in the same session. so using false sqlite will now allow to create multiple threads.


checkpoint = SqliteSaver(connection)
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpoint)


# all_threads = set()
# for ckpt in checkpoint.list(None): # It will return all the threads available 
#     all_threads.add(ckpt.config['configurable']['thread_id'])

# print(list(all_threads))
# (genai) PS D:\GenAI\21_Agentic_AI\11_projects\01_v3_permanent_storage> python chatbot.py
# {'e6cfdaca'}
# (genai) PS D:\GenAI\21_Agentic_AI\11_projects\01_v3_permanent_storage> 

def get_all_threads():
    seen = set()
    ordered = []
    for ckpt in checkpoint.list(None):
        tid = ckpt.config['configurable']['thread_id']
        if tid not in seen:
            seen.add(tid)
            ordered.append(tid)
    return ordered
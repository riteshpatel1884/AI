# This client.py is used to interact with the mathServer.py
# and weatherServer.py using the MCP protocol.

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def main():

    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },

            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable-http",
            },
        }
    )

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    tools = await client.get_tools()

    model = ChatGroq(
        model="openai/gpt-oss-120b"
    )

    agent = create_react_agent(
        model,
        tools
    )

    math_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "what's (3 + 5) x 12?"
                }
            ]
        }
    )

    weather_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "what's the weather like in New York?"
                    }
                ]
            }
        )

    print(
        "Math response:",
        math_response["messages"][-1].content
    )

    print(
            "Weather response:",
            weather_response["messages"][-1].content
        )

asyncio.run(main())

# first run python weatherServer.py then run python client.py to see the output of the mathServer.py and weatherServer.py using the MCP protocol.
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather") 

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    return f"The current weather in {location} is sunny with a temperature of 25°C."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")    
    # using transport="streamable-http" allows the server to handle requests over HTTP, making it suitable for web-based applications like http://127.0.0.1:8000 
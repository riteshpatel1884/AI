from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")  # MATH is the server name.

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")   

# transport="stdio" tells the server to use standard input/output(stdin/stdout) to receive and respond  to tool function calls. but there will be no web interface(like http://127.0.0.1:8000 ) for this server. It is suitable for command-line or script-based interactions.

# try: python mathServer.py

from fastmcp import FastMCP

# 1. Initialize the FastMCP server
mcp = FastMCP("Math Helper 🚀")

# 2. Define a tool using a decorator
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers and returns the sum."""
    return a + b

# 3. Run the server
if __name__ == "__main__":
    mcp.run()
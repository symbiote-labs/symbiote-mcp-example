"""A minimal local MCP integration."""

from fastmcp import FastMCP

mcp = FastMCP("Symbiote Hello World")


@mcp.tool()
def example_hello_world(name: str) -> str:
    """Return a greeting from the local computer running this MCP server.

    Args:
        name: The person or test phrase to greet.
    """
    return f"Hello, {name}!"


def main() -> None:
    # stdout belongs to MCP. Never print debugging messages there.
    mcp.run(transport="stdio", show_banner=False)

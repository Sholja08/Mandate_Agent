from fastmcp import FastMCP
import mcp_tools

mcp = FastMCP("upi-mandate-mcp")

# -------- Register tools --------

@mcp.tool()
def get_all_mandates():
    """Get all UPI mandates"""
    return mcp_tools.get_all_mandates()


@mcp.tool()
def get_mandate_details(query: str):
    """Get mandate details by name, bank, phone, or id"""
    return mcp_tools.get_mandate_details(query)


@mcp.tool()
def pause_mandate(query: str):
    """Pause a mandate"""
    return mcp_tools.pause_mandate(query)


@mcp.tool()
def unpause_mandate(query: str):
    """Unpause a mandate"""
    return mcp_tools.unpause_mandate(query)


@mcp.tool()
def revoke_mandate(query: str):
    """Revoke (cancel) a mandate"""
    return mcp_tools.revoke_mandate(query)


# -------- Run MCP server --------

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8001,
        path="/mcp"
    )

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


# ==========================================
# LOAD MCP TOOLS (ASYNC)
# ==========================================
async def get_mcp_tool_list():
    print(" Connecting to Mandate MCP server...")

    client = MultiServerMCPClient(
        {
            "mandate": {
                "url": "http://localhost:8001/mcp",
                "transport": "http",
            }
        }
    )

    tools = await client.get_tools()

    print(" Mandate tools found:")
    for tool in tools:
        print(f"   • {tool.name}")

    return tools


def load_mcp_tools():
    tools = asyncio.run(get_mcp_tool_list())
    return {tool.name: tool for tool in tools}


# ==========================================
# TEST CLIENT DIRECTLY
# ==========================================
if __name__ == "__main__":
    tools = asyncio.run(get_mcp_tool_list())

    expected = [
        "get_all_mandates",
        "get_mandate_details",
        "pause_mandate",
        "unpause_mandate",
        "revoke_mandate"
    ]

    print("\n Tool availability check:")
    for name in expected:
        found = any(t.name == name for t in tools)
        print(f"   {name}: {'Available ' if found else 'Missing '}")

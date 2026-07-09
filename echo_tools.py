from langchain_core.tools import tool
from dotenv import load_dotenv
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os

load_dotenv(override=True)
OUTPUT_DIR = Path("output")


@tool
def write_file(filename: str, content: str):
    """Write content to a file."""

    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Saved to {filename}"

my_tools=[ write_file ]



READ_ONLY_TOOLS = {
    "get_file_contents",
    "search_code",
    "search_repositories",
    "list_commits",
    "get_commit",
    "list_pull_requests",
    "list_issues",
}




GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment. Check your .env file.")


async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {
                    "Authorization": f"Bearer {GITHUB_TOKEN}"
                },
            }
        }
    )
    tools=await client.get_tools()
    tools = [tool for tool in tools if tool.name in READ_ONLY_TOOLS]
    return tools




def sanitize_tool_schema(schema):
    """Recursively fix invalid enum values (non-strings) in a JSON schema dict."""
    if isinstance(schema, dict):
        if "enum" in schema and isinstance(schema["enum"], list):
            schema["enum"] = [str(v) for v in schema["enum"]]
        for value in schema.values():
            sanitize_tool_schema(value)
    elif isinstance(schema, list):
        for item in schema:
            sanitize_tool_schema(item)
    return schema


def sanitize_tools(tools):
    for t in tools:
        if hasattr(t, "args_schema") and isinstance(t.args_schema, dict):
            sanitize_tool_schema(t.args_schema)
    return tools

async def get_all_tools():
    """Returns local tools + MCP tools combined into one list."""
    mcp_tools = await get_mcp_tools()
    tools = sanitize_tools(mcp_tools+my_tools)

    return tools





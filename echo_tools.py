from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from trafilatura import fetch_url, extract
from langchain_core.tools import tool
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from langchain_tavily import TavilySearch
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os

load_dotenv(override=True)


OUTPUT_DIR = Path("output")

@tool
def scrap_url(url: str)-> str:
    """
    Fetches and extracts the full text content of a webpage given its URL.
    Use this whenever you need the actual content of a specific page —
    e.g. a search result snippet isn't enough, or a link found on an
    already-scraped page looks relevant. Only call this on URLs that
    actually appeared in search results or prior tool output — never
    invent a URL.
    """
    downloaded = fetch_url(url)
    result = extract(downloaded)
    return result

search_tool = TavilySearch(max_results=5,topic="general")


@tool
def write_file(filename: str, content: str):
    """Write content to a file."""

    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Saved to {filename}"

my_tools=[search_tool , scrap_url , write_file ]


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
    return await client.get_tools()



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





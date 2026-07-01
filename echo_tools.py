from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from trafilatura import fetch_url, extract
from langchain_core.tools import tool
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from langchain_tavily import TavilySearch

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

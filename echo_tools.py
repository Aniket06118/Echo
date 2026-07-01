from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from trafilatura import fetch_url, extract
from langchain_core.tools import tool
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)


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

search_tool = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())

my_tools=[search_tool , scrap_url ]

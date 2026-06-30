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
    Extract the main textual content from a webpage.
    Use this after obtaining a URL from a search result when you need the full article or page content.
    """
    downloaded = fetch_url(url)
    result = extract(downloaded)
    return result

search_tool = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())

my_tools=[search_tool , scrap_url ]

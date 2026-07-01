from langchain.agents import create_agent
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
from langchain_core.tools import tool
from trafilatura import fetch_url, extract
from pathlib import Path
from langchain_tavily import TavilySearch

load_dotenv(override=True)

OUTPUT_DIR = Path("output")


SYSTEM_PROMPT="""You are a seasoned researcher.

Workflow:
1. Use tavily_search to find recent, relevant sources for the user's question.
2. For the 2-4 most relevant/promising results, use scrape_url to get full page 
   content — search snippets alone are usually too thin to write a good answer.
3. Synthesize what you found into a clear, well-organized answer, noting dates 
   and sources where relevant since this involves current events.
4. If the user asks you to save output to a file, call write_file exactly once 
   at the end with the complete final answer in markdown.

Prioritize recency for anything news/sports related — check dates in search 
results and prefer the most current information."""

tavily_search=TavilySearch(max_results=5,topic="general")


@tool
def write_file(filename: str, content: str):
    """Write content to a file."""

    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Saved to {filename}"


@tool
def scrap_url(url:str)->str:
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

serper_tool=GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())
tools=[tavily_search,scrap_url,write_file]

my_agent=create_agent(model='google_genai:gemini-2.5-flash',tools=tools,system_prompt=SYSTEM_PROMPT)
response=my_agent.invoke({'messages':[{'role':'user','content':"write me a detailed summary of the latest advancements in the field of AI make sure to return the output in the answer.md file "}]})
print("-----------------------DONEEEE!!-------------------------")


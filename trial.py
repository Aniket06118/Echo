from langchain.agents import create_agent
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
from langchain_core.tools import tool
from trafilatura import fetch_url, extract
from pathlib import Path

load_dotenv(override=True)

OUTPUT_DIR = Path("output")

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
    Extract the main textual content from a webpage.
    Use this after obtaining a URL from a search result when you need the full article or page content.
    """
    downloaded = fetch_url(url)
    result = extract(downloaded)
    return result


serper_tool=GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())
tools=[serper_tool,scrap_url,write_file]

my_agent=create_agent(model='google_genai:gemini-2.5-flash',tools=tools,system_prompt="you are a seasoned researcher")
response=my_agent.invoke({'messages':[{'role':'user','content':"what are the latest indian cricket updates ? make sure to return the output in the response.md file "}]})
print("-----------------------DONEEEE!!-------------------------")
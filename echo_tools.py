from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper






search_wrapper = GoogleSerperAPIWrapper()
search_tool = GoogleSerperRun(api_wrapper=search_wrapper)


tools=[search_tool ,  ]
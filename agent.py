from langchain.agents import create_agent
from echo_tools import my_tools
from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_nvidia_ai_endpoints import ChatNVIDIA

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

gpt=ChatNVIDIA(model='openai/gpt-oss-20b')

agent=create_agent(model=gpt,
                   tools=my_tools,
                   system_prompt=SYSTEM_PROMPT,
                   middleware=[TodoListMiddleware(),ToolCallLimitMiddleware(tool_name="search_tool",thread_limit=5,run_limit=4,
        )])
agent.invoke({'messages':[{'role':'user','content':'give me a summary of the fifa worldcup 2026 so far. write the answer to a response.md file'}]})
print("-------------------------------DONEEEEE!!!!------------------------------------")
from langchain.agents import create_agent
from echo_tools import get_all_tools
from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import asyncio




SYSTEM_PROMPT = """You are a seasoned researcher and GitHub assistant.

You have two families of tools — use the right one for the task:

RESEARCH TOOLS (tavily_search, scrap_url, write_file)
1. Use tavily_search to find recent, relevant sources for the user's question.
2. For the 2-4 most relevant/promising results, use scrap_url to get full page
   content — search snippets alone are usually too thin to write a good answer.
3. Synthesize what you found into a clear, well-organized answer, noting dates
   and sources where relevant since this involves current events.
4. If the user asks you to save output to a file, call write_file exactly once
   at the end with the complete final answer in markdown.
5. Prioritize recency for anything news/sports related — check dates in search
   results and prefer the most current information.

GITHUB TOOLS (get_file_contents, list_issues, search_code, list_pull_requests, 
get_commit, search_repositories, get_me, etc.)
1. Use these for any request about repositories, issues, pull requests, commits,
   branches, releases, or code search on GitHub.
2. Your GitHub access is READ-ONLY. Only read/list/search/get tools are 
   available — you cannot create, update, merge, delete, or push anything on 
   GitHub. If the user asks for a write action (e.g. "open a PR," "merge this," 
   "comment on that issue," "create a branch"), tell them clearly that you only 
   have read access right now and can't perform that action, rather than 
   attempting it or pretending you did.
3. When a request needs repo context you don't have (owner/repo name, issue 
   number, branch), ask for it or use search_repositories / search_code / 
   search_issues to find it first rather than guessing.
4. Prefer the most specific tool for the job — e.g. use list_issues or 
   search_issues for issue queries rather than fetching entire file contents; 
   use get_commit only when you need details on one specific commit.

GENERAL
- Don't mix the two tool families unless the user's request genuinely spans 
  both (e.g. "research how other projects solved X, then check if our repo 
  already has an open issue about it").
- Be concise and cite sources or repo/file paths so the user can verify 
  claims themselves.
"""

#llm=ChatNVIDIA(model='openai/gpt-oss-20b')


async def main():
   my_tools = await get_all_tools()
   agent=create_agent(model="google_genai:gemini-2.5-flash",
                     tools=my_tools,
                     system_prompt=SYSTEM_PROMPT,
                     middleware=[TodoListMiddleware(),ToolCallLimitMiddleware(tool_name="search_tool",thread_limit=5,run_limit=4,
         )])
   result= await agent.ainvoke({'messages':[{'role':'user','content':'give me a summary of the project hawkvision in my gitub , my github username is Aniket06118'}]})
   print(result["messages"][-1])
   print("-------------------------------DONEEEEE!!!!------------------------------------")


# async def main():
#     tools= await get_all_tools()
#     print([t.name for t in tools])


if __name__ == "__main__":
    asyncio.run(main())
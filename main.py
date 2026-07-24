from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from echo_tools import get_all_tools
from prompts import MAIN_AGENT_SYSTEM_PROMPT
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv(override=True)

async def main_agent(config=None):
    """LangGraph server calls this to build the agent per run."""
    my_tools = await get_all_tools()
    return create_agent(
        model="google_genai:gemini-3.1-flash-lite",
        tools=my_tools,
        system_prompt=MAIN_AGENT_SYSTEM_PROMPT,
        middleware=[TodoListMiddleware()],
    )
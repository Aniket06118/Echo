from langchain_core.tools import tool
from dotenv import load_dotenv
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from langgraph.types import Command,interrupt
from langchain_core.messages import ToolMessage
from planning import agent as intake_agent
from planning import write_file



load_dotenv(override=True)
OUTPUT_DIR = Path("output")


@tool
async def start_new_project(project_idea: str) -> str:
    """Call this ONLY when the user explicitly wants to start or work on
    a NEW project. Hands off to Echo, who interviews the user, builds a
    roadmap, and (after human approval) writes it to response.md. Returns
    once the roadmap is saved — do not call this for existing repos."""

    config = {"configurable": {"thread_id": f"intake-{project_idea[:20]}"}}
    state = {"messages": [{"role": "user", "content": project_idea}]}

    while True:
        result = await intake_agent.ainvoke(state, config=config)

        if "__interrupt__" in result:
            interrupt = result["__interrupt__"][0]
            for action in interrupt.value["action_requests"]:
                print("\n--- APPROVAL NEEDED (Echo) ---")
                print(f"Proposed content:\n{action['args'].get('content', '')}\n")

            decision = input("Approve and save? (approve / edit / reject): ").strip().lower()
            if decision == "approve":
                resume = {"decisions": [{"type": "approve"}]}
            elif decision == "edit":
                new_content = input("Paste corrected content:\n")
                resume = {"decisions": [{
                    "type": "edit",
                    "editedAction": {"name": "write_file", "args": {"content": new_content}},
                }]}
            else:
                reason = input("Reason for rejecting: ")
                resume = {"decisions": [{"type": "reject", "message": reason}]}

            state = Command(resume=resume)
            continue

        last = result["messages"][-1]
        tool_executed = any(
            isinstance(m, ToolMessage) and m.name == "write_file"
            for m in result["messages"]
        )
        if tool_executed:
            return f"Roadmap saved to response.md. Summary: {last.content}"

        # Echo asked a clarifying question mid-intake — keep the loop going
        print(f"\nEcho: {last.content}\n")
        state = {"messages": result["messages"] + [{"role": "user", "content": input("> ")}]}

my_tools=[ write_file , start_new_project ]



READ_ONLY_TOOLS = {
    "get_file_contents",
    "search_code",
    "search_repositories",
    "list_commits",
    "get_commit",
    "list_pull_requests",
    "list_issues",
}




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
    tools=await client.get_tools()
    tools = [tool for tool in tools if tool.name in READ_ONLY_TOOLS]
    return tools




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





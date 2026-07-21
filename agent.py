from langchain.agents import create_agent
from echo_tools import get_all_tools
from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import asyncio
from prompts import MAIN_AGENT_SYSTEM_PROMPT


def extract_text(message) -> str:
    """Pull plain text out of a message whose .content may be a string
    or a list of content blocks (text/tool_use/etc)."""
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)

    return str(content)


async def main():
    my_tools = await get_all_tools()
    agent = create_agent(
        model="google_genai:gemini-3.1-flash-lite",
        tools=my_tools,
        system_prompt=MAIN_AGENT_SYSTEM_PROMPT,
        middleware=[TodoListMiddleware()],
    )

    print("Main agent ready. Type your message ('exit' or 'quit' to stop).\n")

    state = {"messages": []}

    while True:
        user_input = input("> ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        if not user_input:
            continue

        state["messages"].append({"role": "user", "content": user_input})

        try:
            result = await agent.ainvoke(state)
        except Exception as e:
            print(f"\n[Error running agent: {e}]\n")
            continue

        state = result

        last_message = result["messages"][-1]
        print(f"\nAgent: {extract_text(last_message)}\n")


if __name__ == "__main__":
    asyncio.run(main())
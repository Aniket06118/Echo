"""
Echo — Intake Agent

Conversational agent that turns a project idea into an approved,
step-based roadmap using LangChain's create_agent + HumanInTheLoopMiddleware.
The write_file tool is gated: it always pauses for explicit human approval
(approve / edit / reject) before response.md is actually written.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pathlib import Path
from prompts import CONVERSATIONAL_AGENT_SYSTEM_PROMPT
from dotenv import load_dotenv


load_dotenv(override=True)
#--------------------------------------------------------
OUTPUT_DIR = Path("output")

@tool
def write_file(filename: str, content: str):
    """Write content to a file."""

    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Saved to {filename}"
#---------------------------------------------------------------

checkpointer = InMemorySaver()  # required: HITL pauses/resumes via checkpointing

agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    system_prompt=CONVERSATIONAL_AGENT_SYSTEM_PROMPT,
    tools=[write_file],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": {"allowed_decisions": ["approve", "edit", "reject"]},
            },
            description_prefix="Ready to save the final roadmap",
        ),
    ],
    checkpointer=checkpointer
    
)

#---------------------------------------------------------------------------
#4. Simple CLI driver loop
#---------------------------------------------------------------------------

def run():
    thread_id = "intake-session-1"
    config = {"configurable": {"thread_id": thread_id}}

    print("Describe your project idea (Echo is listening):")
    state = {"messages": [{"role": "user", "content": input("> ")}]}

    while True:
        result = agent.invoke(state, config=config)

        # --- Case 1: agent paused because write_file needs approval ---
        if "__interrupt__" in result:
            interrupt = result["__interrupt__"][0]
            for action in interrupt.value["action_requests"]:
                print("\n--- APPROVAL NEEDED ---")
                print(f"Tool: {action['name']}")
                print(f"Proposed content:\n{action['args'].get('content', '')}\n")

            decision = input("Approve and save? (approve / edit / reject): ").strip().lower()

            if decision == "approve":
                resume = {"decisions": [{"type": "approve"}]}
            elif decision == "edit":
                new_content = input("Paste the corrected content:\n")
                resume = {
                    "decisions": [{
                        "type": "edit",
                        "editedAction": {"name": "write_file", "args": {"content": new_content}},
                    }]
                }
            else:
                reason = input("Reason for rejecting (feedback for the agent): ")
                resume = {"decisions": [{"type": "reject", "message": reason}]}

            state = Command(resume=resume)
            continue

        # --- Case 2: normal conversational turn ---
        last_message = result["messages"][-1]
        print(f"\nEcho: {last_message.content}\n")

        # crude completion check for this demo — swap for checking the
        # actual ToolMessage from write_file in a real implementation
        tool_executed = any(
            isinstance(msg, ToolMessage) and msg.name == "write_file"
            for msg in result["messages"]
        )

        if tool_executed:
            print("\n[System: Roadmap successfully written to response.md. Exiting Echo.]")
            break

        state = {"messages": [{"role": "user", "content": input("> ")}]}


if __name__ == "__main__":
    run()
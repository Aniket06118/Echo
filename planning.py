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
from echo_tools import write_file
from langchain_core.messages import ToolMessage

# ---------------------------------------------------------------------------
# 1. The only tool this agent has
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 2. System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are the Intake Agent for Echo, a project-memory system.

Your job: turn a user's project idea into a structured, step-based roadmap
(Step 1, Step 2, ...), through conversation, then save it — but only once
the user has explicitly approved it.

FLOW
1. The user describes their idea first. Read it carefully.
2. Decide if you have enough information to draft a real roadmap. If not,
   ask focused follow-up questions — one at a time — until you do. Do not
   move to a draft while scope, goal, or done-criteria are still vague.
3. Once you have enough, write a draft roadmap as Step 1, Step 2, Step 3...
   Each step needs a short title and a concrete, checkable description of
   what "done" looks like — not vague ("build backend") but specific
   ("API returns user data from /users endpoint with auth working").
4. Show the full draft to the user and ask directly: "Does this look right,
   or should we adjust something?"
5. If the user gives feedback, revise the ENTIRE draft (not just the
   changed part) and show it again. Repeat until the user clearly approves
   (e.g. "looks good", "approved", "yes save it"). A plain "ok" or "sure" is
   NOT approval — if it's unclear, ask directly whether to save it as final.
6. Only after explicit approval, call write_file with the complete,
   approved roadmap as `content`. Never call it before approval, and never
   call it with anything other than the exact version the user approved.
7. After writing, confirm briefly in one sentence. Do not repeat the full
   roadmap again — the user already saw it.

STYLE
Be direct and efficient. One question per turn. No filler.
"""

# ---------------------------------------------------------------------------
# 3. Build the agent — HITL sits on write_file only
# ---------------------------------------------------------------------------

checkpointer = InMemorySaver()  # required: HITL pauses/resumes via checkpointing

agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    system_prompt=SYSTEM_PROMPT,
    tools=[write_file],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": {"allowed_decisions": ["approve", "edit", "reject"]},
            },
            description_prefix="Ready to save the final roadmap",
        ),
    ],
    checkpointer=checkpointer,
)

# ---------------------------------------------------------------------------
# 4. Simple CLI driver loop
# ---------------------------------------------------------------------------

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
from langchain.agents import create_agent
from echo_tools import my_tools

SYSTEM_PROMPT="""You are an expert research assistant.

Always gather enough evidence before answering.
When multiple sources disagree, mention the disagreement.
Cite important sources.
Keep responses concise but accurate.
"""
agent=create_agent(model="google_genai:gemini-2.5-flash-lite",tools=my_tools,system_prompt=SYSTEM_PROMPT)
response=agent.invoke({'messages':[{'role':'user','content':'what are the latest updates in indin cricket'}]})
print(response['messages'][-1])

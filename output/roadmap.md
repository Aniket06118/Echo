### AI Research Assistant Implementation Roadmap

**Step 1: Application scaffolding and State definition**
Define the shared state schema for the LangGraph workflow and set up the base Streamlit UI to accept user queries.
* Define the `AgentState` object to persist the research question, search results, synthesized notes, and final report.
* Initialize the Streamlit app with a text input field and a display area for the report.
* Implement basic configuration management for Tavily/Serper and OpenAI/LLM API keys.

**Step 2: Search and Data Retrieval Module**
Implement the search agent node that interacts with the Tavily/Serper API to gather raw data.
* Create a LangGraph node that converts the research question into targeted search queries.
* Implement the API client logic to execute searches and retrieve snippets/content.
* Add a simple filtering mechanism to clean and truncate the retrieved raw text.

**Step 3: Synthesis and Conflict Detection Logic**
Develop the core "researcher" logic that processes search results and identifies contradictions.
* Implement an LLM-based processing node that summarizes content from multiple sources.
* Implement a secondary LLM verification step specifically prompted to compare sources and flag factual discrepancies.
* Ensure the output format is structured (e.g., Markdown) with clear sections for "Key Findings" and "Identified Discrepancies."

**Step 4: Report Generation and Citation Handler**
Build the final output formatter that aggregates synthesized content into a user-facing report.
* Implement logic to map search result metadata (URLs/source names) to the synthesized content for accurate citations.
* Format the final output for the Streamlit UI, ensuring it renders Markdown clearly.
* Verify that the "Discrepancies" section is logically separated from the primary report.

**Step 5: Interactive Follow-up Loop**
Enable the ability to perform follow-up research based on the initial report.
* Update the `AgentState` to maintain the history of the current research session.
* Modify the LangGraph entry point to allow the user to send "follow-up" prompts that refine the existing research or explore new sub-topics.
* Ensure the UI correctly appends follow-up answers to the existing session view.

**Step 6: Persistence and Error Handling**
Add basic robustness to the application.
* Implement basic error handling for API timeouts or empty search results.
* Add a local session cache or simple JSON storage to allow users to save or export their generated reports.
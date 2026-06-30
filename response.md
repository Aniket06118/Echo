**MCP** stands for **Model Context Protocol**.

It is an **open standard** (introduced by **Anthropic** in November 2024) designed to solve the "M×N integration problem" of connecting Large Language Models (LLMs) to external data sources and tools.

---

### 1. The Problem: The M×N Integration Nightmare
Before MCP, if you wanted to connect **M** different AI models (Claude, GPT, Llama, etc.) to **N** different data sources (GitHub, Slack, SQL DBs, File Systems, APIs), you had to build **M × N** custom integrations.
*   Every model used a different function-calling format.
*   Every tool required a custom plugin/adapter for every model.
*   Context handling (resources, prompts, tools) was inconsistent.

### 2. The Solution: MCP (The "USB-C for AI")
MCP standardizes the connection. It acts as a **universal protocol** allowing any MCP-compatible **Client** (the AI app/model) to talk to any MCP-compatible **Server** (the data/tool provider).

*   **M Clients** + **N Servers** = **M + N** integrations (not M × N).
*   It uses **JSON-RPC 2.0** over **stdin/stdout** (local) or **HTTP/SSE** (remote).

---

### 3. Core Architecture

#### **The Host (Application)**
The user-facing app (e.g., Claude Desktop, Cursor, VS Code with Cline, custom Python/JS app). It manages the lifecycle and UI.

#### **The Client (Inside the Host)**
A lightweight library inside the Host that maintains a **1:1 connection** with a specific Server. It handles the protocol handshake, capability negotiation, and message routing.

#### **The Server (The "MCP Server")**
A lightweight program (written in Python, TypeScript, Go, Rust, etc.) that exposes specific **Capabilities** to the Client. This is what people usually mean when they ask "What is an MCP server?"

---

### 4. What an MCP Server Actually Exposes (Primitives)
An MCP server provides three core primitives to the LLM. The LLM decides *when* to use them.

| Primitive | Description | Control | Analogy |
| :--- | :--- | :--- | :--- |
| **Resources** | **Read-only** data/context (files, DB rows, API responses, logs). | **Application/User** controlled (User picks "Attach GitHub Repo"). | `GET` request / File Read / RAG Context |
| **Tools** | **Executable functions** with side effects (write file, call API, send email, query SQL). | **Model** controlled (LLM decides "I need to run this SQL"). | `POST` request / Function Calling / RPC |
| **Prompts** | **Reusable, parameterized prompt templates** (workflows, styles, complex instructions). | **User** controlled (User selects "Generate PR Description"). | Shared Prompt Library / Macros |

---

### 5. Concrete Example: A "GitHub MCP Server"
You run `mcp-server-github` (configured with your PAT token).

1.  **Resources:** `github://repos/owner/repo/contents/src/main.py` -> Returns file content for context.
2.  **Tools:**
    *   `create_issue(title, body)` -> LLM calls this to file a bug.
    *   `create_pr(title, branch, base)` -> LLM opens a PR.
    *   `search_code(query)` -> LLM searches the codebase.
3.  **Prompts:** `generate_pr_description` -> A template guiding the LLM to write a perfect PR description based on diff context.

---

### 6. Why MCP Servers Are a Big Deal

| Feature | Benefit |
| :--- | :--- |
| **Standardization** | Write a server **once** (in Python/TS), works in Claude Desktop, Cursor, Cline, Continue, Zed, custom agents. |
| **Security & Permissioning** | The **Host** (not the server) asks the user for permission before a Tool is executed. Servers run locally (usually) with only the credentials *you* give them. |
| **Discovery** | Clients automatically discover capabilities (`list_resources`, `list_tools`) on connection. No hardcoding schemas. |
| **Stateful Context** | Resources support subscriptions (live updates) and pagination. |
| **Transport Agnostic** | Works locally (stdio - most secure) or remotely (HTTP/SSE - for cloud/shared servers). |

---

### 7. How to Run / Build One

#### **Running Existing Servers (User Perspective)**
Usually configured in a JSON file (e.g., `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/name/allowed-folder"]
    },
    "postgres": {
      "command": "mcp-server-postgres",
      "args": ["postgresql://user:pass@localhost/db"]
    }
  }
}
```

#### **Building a Server (Developer Perspective)**
**Python (FastMCP - High Level):**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Tools")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("config://app")
def get_config() -> str:
    return "App Config v1.0"

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**TypeScript (SDK):**
```typescript
const server = new Server({ name: "weather", version: "1.0" }, { capabilities: { tools: {} } });
server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: [...] }));
server.setRequestHandler(CallToolRequestSchema, async (req) => { ... });
const transport = new StdioServerTransport();
await server.connect(transport);
```

---

### 8. Current Ecosystem (Early 2025)
*   **Official SDKs:** Python, TypeScript, Kotlin, C#, Swift, Go, Rust.
*   **Popular Servers (Official/Community):** Filesystem, GitHub, GitLab, PostgreSQL, SQLite, MySQL, Redis, S3, Puppeteer/Playwright (Browser), Brave Search, Google Maps, Slack, Notion, AppleScript (Mac control), Docker, Kubernetes.
*   **Client Support:** Claude Desktop (Native), Cursor, Cline, Continue, Zed, Windsurf, VS Code (via extensions), LangChain, LlamaIndex, Semantic Kernel, AutoGen.
*   **Registries:** `mcp.so`, `glama.ai/mcp`, `smithery.ai` (for discovery/installation).

---

### 9. MCP vs. Alternatives
| | **MCP** | **OpenAI Function Calling / Tools** | **LangChain/LlamaIndex Tools** | **Plugin Systems (ChatGPT Plugins)** |
| :--- | :--- | :--- | :--- | :--- |
| **Scope** | **Universal Standard** (Any Model, Any Client) | Proprietary (OpenAI Models only) | Framework Specific (Python/JS Libs) | Proprietary (ChatGPT Only) |
| **Architecture** | Client-Server (Separate Process) | In-Process Function Call | In-Process Function Call | Remote HTTP API (Manifest) |
| **Context (Resources)** | **First Class Citizen** (Read-only, Subscriptions) | Not Supported (Only Tools) | Via Retrievers/Loaders (Custom) | Not Supported |
| **Prompts** | **First Class Citizen** (Versioned Templates) | System Prompt only | PromptTemplate Objects | No |
| **Security** | User Approval per Call (Host Enforced) | Dev Defined / Auto | Dev Defined / Auto | OAuth / User Install |

---

### Summary
An **MCP Server** is a **lightweight, standalone program** that exposes **Resources (context), Tools (actions), and Prompts (workflows)** via a **standardized JSON-RPC protocol**.

It decouples **AI Applications (Clients)** from **Data/Action Providers (Servers)**, allowing you to plug a PostgreSQL server into Claude, Cursor, or a custom LangGraph agent **without rewriting integration code**.
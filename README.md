# AI Developer Support Agent

An AI-powered developer support agent that investigates application issues using **Gemini**, **Model Context Protocol (MCP)**, and a set of developer-support tools.

The agent can understand a troubleshooting question, decide which tools are useful, execute those tools through an MCP server, analyze the returned information, perform additional investigation when required, and finally generate a **Root Cause Analysis (RCA)** with recommended next steps.

> **Current status:** Proof of Concept using mock employee, policy, log, and error data.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    │                     │
                    │ "Why hasn't the     │
                    │  DPDP policy been   │
                    │  assigned?"         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Gemini Agent     │
                    │                     │
                    │ Reasoning +         │
                    │ Tool Selection      │
                    └──────────┬──────────┘
                               │
                               │ MCP
                               ▼
                    ┌─────────────────────┐
                    │     MCP Client      │
                    │                     │
                    │ Tool orchestration  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     MCP Server      │
                    │                     │
                    │ FastMCP             │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌────────────┐   ┌────────────┐
       │ Employees  │   │ UserPolicy │   │   Logs     │
       │    Data    │   │    Data    │   │   & Errors │
       └────────────┘   └────────────┘   └────────────┘
```

---

## How It Works

The agent follows an iterative tool-calling workflow.

```text
1. User asks a troubleshooting question
              ↓
2. Gemini analyzes the question
              ↓
3. Gemini selects one or more MCP tools
              ↓
4. MCP client executes the selected tools
              ↓
5. Tool results are sent back to Gemini
              ↓
6. Gemini decides whether more investigation is required
              ↓
7. Additional tools are called if required
              ↓
8. Gemini generates the final RCA
```

This demonstrates an **agentic loop** rather than a simple single LLM request.

---

## Example

### User Question

```text
Why hasn't the DPDP policy been assigned to employee 1024?
```

### Agent Investigation

The agent automatically selected:

```text
Step 1
├── get_employee(1024)
└── get_user_policy(1024)

Step 2
├── search_logs("1024")
└── search_logs("DPDP")

Step 3
├── search_logs("Existing UserPolicy")
├── search_logs("EXIT")
└── get_recent_errors("policy-service")

Step 4
└── Generate final RCA
```

The agent therefore performed a multi-step investigation instead of relying on a single tool call.

---

## Sample RCA

The mock data contains the following information:

```json
{
  "id": 1024,
  "username": "john.doe",
  "legal_entity": "INDIA",
  "status": "ACTIVE"
}
```

The corresponding policy record contains:

```json
{
  "employee_id": 1024,
  "policy_type": "DPDP",
  "verified": false,
  "event": "EXIT"
}
```

The logs contain:

```text
DPDP policy assignment started for employee 1024
Existing UserPolicy found for employee 1024
UserPolicy event EXIT - skipping policy assignment
```

The error data contains:

```text
UserPolicy skipped because event=EXIT
```

Based on these findings, the agent concludes that the existing `UserPolicy` record has `event=EXIT`, causing the policy assignment flow to skip the employee even though the employee is currently `ACTIVE`.

---

# MCP Tools

The MCP server currently exposes four tools.

### 1. `get_employee`

Returns employee information.

```text
get_employee(employee_id)
```

Example:

```text
get_employee(1024)
```

Returns:

```json
{
  "id": 1024,
  "username": "john.doe",
  "legal_entity": "INDIA",
  "status": "ACTIVE"
}
```

---

### 2. `get_user_policy`

Returns the user's policy information.

```text
get_user_policy(employee_id)
```

Example:

```text
get_user_policy(1024)
```

Returns:

```json
{
  "employee_id": 1024,
  "policy_type": "DPDP",
  "verified": false,
  "event": "EXIT"
}
```

---

### 3. `search_logs`

Searches application logs using a keyword.

```text
search_logs(keyword)
```

Example:

```text
search_logs("EXIT")
```

Returns matching logs:

```text
UserPolicy event EXIT - skipping policy assignment
```

---

### 4. `get_recent_errors`

Returns recent errors for a service.

```text
get_recent_errors(service)
```

Example:

```text
get_recent_errors("policy-service")
```

Returns:

```json
{
  "service": "policy-service",
  "error": "UserPolicy skipped because event=EXIT",
  "employee_id": 1024
}
```

---

# Project Structure

```text
ai-developer-support-agent/
│
├── agent/
│   ├── __init__.py
│   └── agent.py
│
├── mcp_server/
│   ├── __init__.py
│   └── server.py
│
├── data/
│   ├── __init__.py
│   └── mock_data.py
│
├── main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Components

| Component              | Responsibility                                   |
| ---------------------- | ------------------------------------------------ |
| `agent/agent.py`       | Gemini agent and agentic tool-calling loop       |
| `mcp_server/server.py` | MCP server and exposed tools                     |
| `data/mock_data.py`    | Mock employee, policy, log and error data        |
| `main.py`              | Application entry point / future API integration |
| `.env`                 | Gemini API configuration                         |
| `requirements.txt`     | Python dependencies                              |

---

# Tech Stack

* **Python 3.12**
* **Google Gemini API**
* **Gemini Flash**
* **Model Context Protocol (MCP)**
* **FastMCP**
* **Google Gen AI SDK**
* **python-dotenv**
* **Mock data**

---

# Prerequisites

Make sure the following are installed:

* Python 3.12+
* pip
* Git
* A Gemini API key

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd ai-developer-support-agent
```

---

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Gemini API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do **not** commit the `.env` file.

The project `.gitignore` should contain:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# Running the Project

Activate the virtual environment:

```bash
source venv/bin/activate
```

Then run:

```bash
python agent/agent.py
```

The agent will start the MCP server automatically as a subprocess.

Expected output:

```text
User:
Why hasn't the DPDP policy been assigned to employee 1024?

--- Agent Step 1 ---

Agent selected tool: get_employee
Arguments: {'employee_id': 1024}

Tool result:
{
  "id": 1024,
  "username": "john.doe",
  "legal_entity": "INDIA",
  "status": "ACTIVE"
}

Agent selected tool: get_user_policy
Arguments: {'employee_id': 1024}

Tool result:
{
  "employee_id": 1024,
  "policy_type": "DPDP",
  "verified": false,
  "event": "EXIT"
}

--- Agent Step 2 ---

...

==============================
FINAL RCA
==============================
```

---

# Running the MCP Server Separately

The MCP server can also be started independently.

Use:

```bash
python -m mcp_server.server
```

The module form is important because the server imports:

```python
from data.mock_data import ...
```

Therefore, running:

```bash
python mcp_server/server.py
```

may cause Python import-path issues.

The agent itself starts the server correctly using:

```python
StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)
```

---

# Agentic Tool Calling

The most important part of this project is the agent loop.

Gemini receives the available MCP tools as function declarations.

For example:

```text
get_employee
get_user_policy
search_logs
get_recent_errors
```

Gemini then decides which tools are relevant.

For example:

```text
User Question
      ↓
Gemini
      ↓
get_employee(1024)
      ↓
Tool Result
      ↓
Gemini
      ↓
get_user_policy(1024)
      ↓
Tool Result
      ↓
Gemini
      ↓
search_logs("EXIT")
      ↓
Tool Result
      ↓
Gemini
      ↓
get_recent_errors("policy-service")
      ↓
Tool Result
      ↓
Final RCA
```

This is the core agentic behavior demonstrated by the POC.

---

# Why MCP?

Instead of directly coupling the LLM to application-specific implementations, MCP provides a standard interface through which the agent can access tools.

Conceptually:

```text
LLM
 │
 │ Tool calls
 ▼
MCP Client
 │
 ▼
MCP Server
 │
 ├── Employee tools
 ├── Policy tools
 ├── Log tools
 └── Error tools
```

This makes it easier to add additional developer-support capabilities later without changing the core agent reasoning flow.

---

# Current Mock Data

The current POC intentionally uses mock data.

Example employee:

```text
Employee ID: 1024
Username: john.doe
Legal Entity: INDIA
Status: ACTIVE
```

Example policy:

```text
Policy Type: DPDP
Verified: false
Event: EXIT
```

Example error:

```text
UserPolicy skipped because event=EXIT
```

This keeps the POC simple and allows the agentic architecture to be demonstrated without requiring access to real application databases, logs, or internal services.

---

# Design Goals

The POC focuses on demonstrating:

* LLM-based reasoning
* Tool selection
* MCP integration
* Dynamic tool execution
* Multi-step investigation
* Tool-result feedback to the LLM
* Automated RCA generation
* Recommended remediation steps

The goal is **not** to build a production-ready support platform at this stage.

---

# Current Limitations

This is currently a POC, so there are several limitations.

### Mock data

All application information comes from:

```text
data/mock_data.py
```

There is no real database or production log integration.

### Hardcoded question

The current demo question is defined in the agent code.

### No authentication

There is currently no authentication or authorization layer.

### No persistent conversation

Each execution starts a new investigation.

### No production observability

The POC does not currently integrate with:

* Elasticsearch
* Kibana
* Grafana
* Application databases
* Distributed tracing
* Production log systems

### No automated remediation

The agent currently recommends fixes but does not execute changes against application systems.

---

# Future Enhancements

The project can be extended incrementally.

## Phase 1 — User Input

Allow the user to enter questions dynamically.

```text
python agent/agent.py

> Why hasn't the DPDP policy been assigned to employee 1024?
```

---

## Phase 2 — FastAPI

Expose the agent through a REST API.

```http
POST /ask
```

Request:

```json
{
  "question": "Why hasn't the DPDP policy been assigned to employee 1024?"
}
```

Response:

```json
{
  "answer": "...",
  "tools_used": [
    "get_employee",
    "get_user_policy",
    "search_logs",
    "get_recent_errors"
  ]
}
```

---

## Phase 3 — Real Data Sources

Replace mock data with real application integrations.

```text
MCP Server
    │
    ├── PostgreSQL / MySQL
    ├── Application APIs
    ├── Elasticsearch
    ├── Log systems
    └── Monitoring systems
```

---

## Phase 4 — More Developer Tools

Additional MCP tools could include:

```text
get_recent_deployments()
get_service_health()
get_database_record()
search_application_logs()
get_api_response()
get_trace()
get_git_commit()
get_jira_ticket()
```

---

## Phase 5 — Better RCA

The final response could be structured as:

```text
Issue
  ↓
Evidence
  ↓
Timeline
  ↓
Root Cause
  ↓
Impact
  ↓
Recommended Fix
  ↓
Relevant Logs
  ↓
Relevant Deployment
```

---

## Phase 6 — Production Architecture

A possible production architecture:

```text
                    ┌───────────────┐
                    │ Developer /   │
                    │ Support Team  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  AI Support   │
                    │     Agent     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  MCP Client   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  MCP Server   │
                    └───────┬───────┘
                            │
        ┌───────────────────┼────────────────────┐
        │                   │                    │
        ▼                   ▼                    ▼
   Application          Databases             Logs
      APIs                                    / APM
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                    ┌───────────────┐
                    │    Gemini     │
                    │  RCA / Fix    │
                    └───────────────┘
```

---

# Example Use Cases

The same architecture can be used for questions such as:

```text
Why hasn't an employee received the DPDP policy?
```

```text
Why is onboarding stuck for employee 1024?
```

```text
Why did the policy assignment job fail?
```

```text
Why is this API returning 401?
```

```text
Why did the user provisioning process skip this employee?
```

```text
What caused the latest policy-service failure?
```

The agent can determine which tools are relevant to each investigation.

---

# Key Learning

This POC demonstrates the transition from a traditional LLM application:

```text
User → LLM → Answer
```

to an agentic application:

```text
User
  ↓
LLM
  ↓
Reason
  ↓
Select Tool
  ↓
Execute Tool
  ↓
Observe Result
  ↓
Reason Again
  ↓
Select Another Tool
  ↓
Observe Result
  ↓
Final Answer
```

The important capability is that the LLM is not limited to generating text. It can **interact with external tools, observe their results, and continue reasoning based on those results**.

---

# Project Status

```text
[✓] Python project setup
[✓] Gemini integration
[✓] MCP server
[✓] MCP client
[✓] MCP tool discovery
[✓] MCP tool execution
[✓] Gemini function calling
[✓] Multi-step agent loop
[✓] Tool-result feedback loop
[✓] Automated RCA generation
[✓] Mock developer-support data
[ ] Dynamic user input
[ ] FastAPI endpoint
[ ] Real application data
[ ] Real log integration
[ ] Production deployment
```

---

# Conclusion

**AI Developer Support Agent** is a proof of concept for using **LLMs + MCP + agentic tool calling** to automate application troubleshooting.

The current implementation demonstrates how an AI agent can:

1. Understand a developer's troubleshooting question.
2. Select appropriate tools.
3. Query application information.
4. Search logs and errors.
5. Perform multi-step investigation.
6. Correlate information from multiple sources.
7. Generate an RCA.
8. Recommend possible remediation steps.

The current implementation deliberately uses mock data so that the **agentic architecture can be developed and demonstrated independently of production systems**.

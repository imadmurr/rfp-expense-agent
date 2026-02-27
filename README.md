# RFP Expense Analyzer Agent

**AI BootCamp 102 - Day 1 Assignment**  
**Author:** Imad EL MURR  
**Date:** February 2026

## Overview

This project combines **all concepts** from the three Day 1 labs into a single AI agent themed around the Javista RFP project.

## Concepts Covered Per Lab

### Lab 1 — Agent Fundamentals
- Agent instructions for grounding behavior
- File search / knowledge base (expense policy)
- Code Interpreter tool for data analysis

### Lab 2 — Develop an AI Agent (SDK)
- `AIProjectClient` connection to Foundry project
- File upload via `agents.upload_file_and_poll()`
- `CodeInterpreterTool` with file IDs
- Thread-based conversations (create, message, run)
- Conversation history retrieval
- Cleanup (delete agent)

### Lab 3 — Custom Functions
- Custom function definitions in `user_functions.py`
- `FunctionTool` + `ToolSet`
- `enable_auto_function_calls` for automatic tool execution
- `AgentsClient` direct connection
- `create_and_process` for auto function handling
- `get_last_message_text_by_role` for response retrieval
- `ListSortOrder.ASCENDING` conversation history

## Project Structure

```
rfp-expense-agent/
├── .env                    # Configuration (endpoint + model)
├── requirements.txt        # Python dependencies
├── data.txt                # RFP expense data for analysis
├── expense_policy.txt      # Expense policy for grounding
├── user_functions.py       # Custom functions (Lab 3)
├── agent.py                # MAIN: All 3 labs combined (Code Interpreter + Functions)
├── agent_functions.py      # ALT: Lab 3 standalone (Functions only)
└── README.md               # This file
```

## Two Implementations

### `agent.py` — All Labs Combined (Recommended)
Uses `AIProjectClient` → `.agents` → `AgentsClient` with:
- File upload + CodeInterpreterTool (Lab 1 + 2)
- FunctionTool + ToolSet with auto calling (Lab 3)
- Both tools available simultaneously

### `agent_functions.py` — Lab 3 Standalone
Uses `AgentsClient` directly with:
- FunctionTool only (no Code Interpreter)
- Data embedded in instructions instead of file upload

## Setup & Run (Azure Cloud Shell)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "RFP Expense Agent assignment"
git remote add origin https://github.com/YOUR_USERNAME/rfp-expense-agent.git
git push -u origin main
```

### 2. In Azure Cloud Shell (PowerShell, Classic version)
```powershell
rm -r rfp-expense-agent -f
git clone https://github.com/YOUR_USERNAME/rfp-expense-agent.git
cd rfp-expense-agent

python -m venv labenv
./labenv/bin/Activate.ps1
pip install -r requirements.txt

code .env    # Set PROJECT_ENDPOINT, then CTRL+S, CTRL+Q
az login

python agent.py              # All labs combined
# OR
python agent_functions.py    # Lab 3 standalone
```

## Sample Prompts

**Data Analysis (agent.py):**
- `What's the category with the highest cost?`
- `Create a text-based bar chart of costs by consultant`
- `What's the standard deviation of hourly rates?`
- `Which consultants exceed their policy rate caps?`

**Policy Questions (both agents):**
- `What's the maximum rate for an AI Engineer?`
- `What approval is needed for a $75,000 project?`

**Custom Functions (both agents):**
- `Submit an expense report` → agent collects info → calls function → creates file
- `Flag a budget overrun for travel` → agent collects info → calls function → creates alert

## Key SDK Pattern (v1 GA)

```python
# Lab 2: Connect via AIProjectClient
project_client = AIProjectClient(endpoint=..., credential=...)
agents_client = project_client.agents  # Gets AgentsClient

# Lab 2: Upload files
file = agents_client.upload_file_and_poll(file_path=..., purpose="agents")

# Lab 1+2: Code Interpreter + Lab 3: Custom Functions
toolset = ToolSet()
toolset.add(CodeInterpreterTool(file_ids=[file.id]))
toolset.add(FunctionTool(user_functions))
agents_client.enable_auto_function_calls(toolset)

# Create agent + thread + run
agent = agents_client.create_agent(model=..., toolset=toolset, ...)
thread = agents_client.threads.create()
agents_client.messages.create(thread_id=thread.id, role="user", content=...)
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
```

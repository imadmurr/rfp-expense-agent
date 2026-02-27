# RFP Expense Analyzer Agent

**AI BootCamp 102 - Day 1 Assignment**  
**Author:** Imad EL MURR  
**Date:** February 2026

## Overview

This project combines **all concepts** from the three Day 1 labs into a single, cohesive AI agent application themed around the Javista Services RFP project.

## Concepts Covered

### From Lab 1 — Agent Fundamentals (Foundry Portal)
| Concept | Where in Code |
|---------|---------------|
| Agent instructions (grounding) | `agent.py` line ~120: `agent_instructions` |
| File search / knowledge base | `agent.py`: uploads `expense_policy.txt` for grounding |
| Code Interpreter tool | `agent.py`: `CodeInterpreterTool` creation |

### From Lab 2 — Develop an AI Agent (SDK)
| Concept | Where in Code |
|---------|---------------|
| `AIProjectClient` connection | `agent.py`: `with` block with credential + client |
| File upload via `openai_client.files.create` | `agent.py`: uploads `data.txt` and `expense_policy.txt` |
| `CodeInterpreterTool` + `CodeInterpreterToolAuto` | `agent.py`: code interpreter with file IDs |
| `PromptAgentDefinition` | `agent.py`: `project_client.agents.create_version` |
| Conversations API | `agent.py`: `conversations.create`, `items.create`, `responses.create` |
| Conversation history | `agent.py`: `conversations.items.list` |
| Cleanup | `agent.py`: `conversations.delete` + `agents.delete_version` |

### From Lab 3 — Custom Functions
| Concept | Where in Code |
|---------|---------------|
| Custom function definitions | `user_functions.py`: `submit_expense_report`, `flag_budget_overrun` |
| `FunctionTool` + `ToolSet` | `agent_functions.py`: toolset creation |
| `enable_auto_function_calls` | `agent_functions.py`: auto-calling enabled |
| `AgentsClient` connection | `agent_functions.py`: direct agent client |
| Thread + messages API | `agent_functions.py`: `threads.create`, `messages.create` |
| `create_and_process` for auto function execution | `agent_functions.py`: run with auto-processing |
| `get_last_message_text_by_role` | `agent_functions.py`: retrieve agent response |
| `ListSortOrder.ASCENDING` history | `agent_functions.py`: conversation log |

## Project Structure

```
rfp-expense-agent/
├── .env                    # Configuration (endpoint + model)
├── requirements.txt        # Python dependencies
├── data.txt                # RFP expense data for analysis
├── expense_policy.txt      # Expense policy for grounding
├── user_functions.py       # Custom functions (Lab 3)
├── agent.py                # Main agent: Code Interpreter + Files (Lab 1+2)
├── agent_functions.py      # Alt agent: Custom Functions (Lab 3)
└── README.md               # This file
```

## Two Agent Implementations

### `agent.py` — Code Interpreter Agent (Lab 1 + Lab 2)
Uses `AIProjectClient` + `OpenAI` client with:
- File upload for grounding
- CodeInterpreterTool for data analysis
- Conversations API

**Best for:** Analyzing data, creating charts, statistical calculations

### `agent_functions.py` — Custom Functions Agent (Lab 3)
Uses `AgentsClient` with:
- FunctionTool + ToolSet
- Auto function calling
- Thread-based messaging

**Best for:** Submitting expense reports, flagging budget overruns

## Setup & Run

### 1. Prerequisites
- Azure subscription with AI Foundry access
- Python 3.12+
- A deployed model (gpt-4.1) in your Foundry project

### 2. Install Dependencies
```bash
python -m venv labenv
source labenv/bin/activate        # Linux/Mac
# .\labenv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 3. Configure
Edit `.env` and set your project endpoint:
```
PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project-id
MODEL_DEPLOYMENT_NAME=gpt-4.1
```

### 4. Sign into Azure
```bash
az login
```

### 5. Run

**Option A — Code Interpreter Agent:**
```bash
python agent.py
```

**Option B — Custom Functions Agent:**
```bash
python agent_functions.py
```

## Sample Prompts to Try

### Data Analysis (agent.py)
- `What's the category with the highest cost?`
- `Create a text-based bar chart showing cost by consultant`
- `What's the standard deviation of hourly rates?`
- `Which consultants exceed their policy rate caps?`
- `What's the total profit margin if we add 15%?`

### Policy Questions (both agents)
- `What's the maximum rate for an AI Engineer?`
- `What approval is needed for a $75,000 project?`
- `What are the travel expense rules?`

### Custom Functions (agent_functions.py)
- `I want to submit an expense report`
- `Flag a budget overrun for travel expenses`

## Key Differences Between Lab 2 and Lab 3 Patterns

| Feature | Lab 2 (agent.py) | Lab 3 (agent_functions.py) |
|---------|-------------------|---------------------------|
| Client | `AIProjectClient` + `OpenAI` | `AgentsClient` |
| Agent creation | `agents.create_version` | `create_agent` |
| Conversation | `conversations.create` | `threads.create` |
| Send message | `conversations.items.create` | `messages.create` |
| Run | `responses.create` | `runs.create_and_process` |
| Response | `response.output_text` | `get_last_message_text_by_role` |
| Tools | `CodeInterpreterTool` | `FunctionTool` + `ToolSet` |
| File access | Upload files to project | Embed data in instructions |
| Cleanup | `conversations.delete` + `agents.delete_version` | `delete_agent` |

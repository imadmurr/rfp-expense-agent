"""
RFP Expense Analyzer Agent
===========================
Assignment: AI BootCamp 102 - Day 1

Combines ALL concepts from the three labs into one agent:

Lab 1 (Agent Fundamentals):
  - Agent with grounding instructions
  - File search / knowledge base (expense policy)
  - Code Interpreter tool (data analysis & charts)

Lab 2 (Develop an AI Agent):
  - Programmatic agent creation via SDK
  - File upload to the project
  - CodeInterpreterTool with uploaded data
  - Thread-based conversations
  - Conversation history retrieval
  - Proper cleanup

Lab 3 (Custom Functions):
  - Custom function definitions (user_functions.py)
  - FunctionTool and ToolSet
  - Auto function calling (enable_auto_function_calls)
  - create_and_process for automatic tool execution
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------
# Load configuration
# ---------------------------------------------------------------
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4.1")

if not project_endpoint or project_endpoint == "your_project_endpoint":
    print("ERROR: Please set PROJECT_ENDPOINT in the .env file.")
    print("       Copy it from the Foundry portal > Project > Overview page.")
    exit(1)

# ---------------------------------------------------------------
# Data file paths
# ---------------------------------------------------------------
script_dir = Path(__file__).parent
data_file_path = script_dir / "data.txt"
policy_file_path = script_dir / "expense_policy.txt"

# Show the data that will be loaded
print("\n" + "=" * 60)
print("RFP EXPENSE ANALYZER AGENT")
print("=" * 60)
print(f"\nProject Endpoint: {project_endpoint[:50]}...")
print(f"Model: {model_deployment}")

print(f"\nLoading data from: {data_file_path}")
with open(data_file_path, "r") as f:
    data_content = f.read()
print("\n--- Data Preview ---")
print(data_content[:500] + "..." if len(data_content) > 500 else data_content)
print("--- End Preview ---\n")

# ---------------------------------------------------------------
# Add references (Lab 2 + Lab 3 combined)
# ---------------------------------------------------------------

# Lab 2: AIProjectClient to connect to the Foundry project
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Lab 1 + 2: CodeInterpreterTool for data analysis
# Lab 3: FunctionTool, ToolSet for custom functions
# Lab 3: ListSortOrder, MessageRole for conversation history
from azure.ai.agents.models import (
    CodeInterpreterTool,
    FunctionTool,
    ToolSet,
    ListSortOrder,
    MessageRole,
)

# Lab 3: Import our custom functions
from user_functions import user_functions

# ---------------------------------------------------------------
# Connect to the AI Project (Lab 2)
# project_client.agents gives us an AgentsClient (Lab 3)
# ---------------------------------------------------------------
print("Connecting to Azure AI Foundry project...")

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
    ),
)

# Get the AgentsClient from the project (bridges Lab 2 + Lab 3)
agents_client = project_client.agents

# ---------------------------------------------------------------
# Upload files (Lab 2: file upload for Code Interpreter)
# ---------------------------------------------------------------
print("Uploading data file for Code Interpreter...")
data_file = agents_client.upload_file_and_poll(
    file_path=str(data_file_path),
    purpose="agents",
)
print(f"  Uploaded: {data_file.filename} (ID: {data_file.id})")

print("Uploading expense policy file...")
policy_file = agents_client.upload_file_and_poll(
    file_path=str(policy_file_path),
    purpose="agents",
)
print(f"  Uploaded: {policy_file.filename} (ID: {policy_file.id})")

# ---------------------------------------------------------------
# Create tools (Lab 1 + Lab 2 + Lab 3)
# ---------------------------------------------------------------

# Lab 1 + Lab 2: Code Interpreter with both uploaded files
code_interpreter = CodeInterpreterTool(
    file_ids=[data_file.id, policy_file.id]
)

# Lab 3: Custom function tools from user_functions.py
functions = FunctionTool(user_functions)

# Lab 3: Combine all tools into a ToolSet
toolset = ToolSet()
toolset.add(code_interpreter)
toolset.add(functions)

# Lab 3 KEY CONCEPT: Enable auto function calling
# This lets the agent automatically invoke our custom functions
agents_client.enable_auto_function_calls(toolset)

# ---------------------------------------------------------------
# Agent instructions (Lab 1: grounding with policy knowledge)
# ---------------------------------------------------------------
agent_instructions = """You are an RFP Expense Analyzer for Javista Services SAL.

You have access to two uploaded files via the Code Interpreter:
1. data.txt - RFP expense summary with consultant costs, hours, and project details
2. expense_policy.txt - Company expense policy with rate caps and approval thresholds

Your capabilities:
- Analyze RFP expense data using Python (Code Interpreter)
- Answer expense policy questions from the policy document
- Create text-based charts and visualizations
- Calculate statistics (averages, totals, standard deviations)
- Compare actual costs against policy rate caps
- Submit expense reports using submit_expense_report function
  (collect email, project name, description, and amount first)
- Flag budget overruns using flag_budget_overrun function
  (collect category, budgeted amount, actual amount, and reason first)

Always use Code Interpreter for calculations and charts.
Be concise. Reference specific policy rules when relevant.
"""

# ---------------------------------------------------------------
# Create the agent (Lab 2: create_agent with model + instructions + toolset)
# ---------------------------------------------------------------
print("\nCreating agent: rfp-expense-agent...")
agent = agents_client.create_agent(
    model=model_deployment,
    name="rfp-expense-agent",
    instructions=agent_instructions,
    toolset=toolset,
)
print(f"  Agent created: {agent.name} (ID: {agent.id})")

# ---------------------------------------------------------------
# Create a thread (Lab 2 + Lab 3: conversation thread)
# ---------------------------------------------------------------
print("Creating conversation thread...")
thread = agents_client.threads.create()
print(f"  Thread created (ID: {thread.id})")

# ---------------------------------------------------------------
# Interactive chat loop
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("Chat with the RFP Expense Analyzer Agent")
print("-" * 60)
print("Try these prompts:")
print("  'What is the highest cost category?'")
print("  'Create a bar chart of costs by consultant'")
print("  'Which consultants exceed their policy rate caps?'")
print("  'Submit an expense report'")
print("  'Flag a budget overrun for travel'")
print("Type 'quit' to exit.")
print("=" * 60 + "\n")

while True:
    user_prompt = input("You: ").strip()
    if not user_prompt:
        continue
    if user_prompt.lower() == "quit":
        print("\nEnding conversation...\n")
        break

    # -----------------------------------------------------------
    # Send a prompt to the agent (Lab 3 pattern)
    # -----------------------------------------------------------
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt,
    )

    # Lab 3 KEY CONCEPT: create_and_process handles auto function calling
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    # -----------------------------------------------------------
    # Check for failures (Lab 2 + Lab 3)
    # -----------------------------------------------------------
    if run.status == "failed":
        print(f"\n  Run failed: {run.last_error}\n")
        continue

    # -----------------------------------------------------------
    # Show response (Lab 3: get_last_message_text_by_role)
    # -----------------------------------------------------------
    last_msg = agents_client.messages.get_last_message_text_by_role(
        thread_id=thread.id,
        role=MessageRole.AGENT,
    )
    if last_msg:
        print(f"\nAgent: {last_msg.text.value}\n")

# ---------------------------------------------------------------
# Conversation history (Lab 2 + Lab 3)
# ---------------------------------------------------------------
print("=" * 60)
print("CONVERSATION LOG")
print("=" * 60 + "\n")

messages = agents_client.messages.list(
    thread_id=thread.id,
    order=ListSortOrder.ASCENDING,
)
for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        role = str(msg.role).upper()
        print(f"  [{role}]: {last_text.text.value}\n")

# ---------------------------------------------------------------
# Clean up (Lab 2 + Lab 3)
# ---------------------------------------------------------------
print("=" * 60)
print("CLEANUP")
print("=" * 60)

agents_client.delete_agent(agent.id)
print("  Agent deleted")

print("\n  All resources cleaned up successfully.")
print("  Thank you for using the RFP Expense Analyzer!\n")

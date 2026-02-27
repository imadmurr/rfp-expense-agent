"""
RFP Expense Agent - Custom Functions Only (Lab 3 Pattern)
==========================================================
Assignment: AI BootCamp 102 - Day 1

This is the STANDALONE Lab 3 implementation using AgentsClient directly.
It focuses on the custom function calling pattern.

Demonstrates:
  - AgentsClient direct connection (Lab 3)
  - FunctionTool with custom user_functions (Lab 3)
  - ToolSet with auto function calling enabled (Lab 3)
  - create_agent with toolset (Lab 3)
  - threads.create for conversation management (Lab 3)
  - messages.create + runs.create_and_process (Lab 3)
  - get_last_message_text_by_role (Lab 3)
  - Conversation history with ListSortOrder (Lab 3)
  - Grounding via instructions (Lab 1)
  - Cleanup: delete_agent (Lab 3)
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
    exit(1)

# Load policy + data content to embed in instructions (Lab 1 grounding)
script_dir = Path(__file__).parent

with open(script_dir / "expense_policy.txt", "r") as f:
    policy_content = f.read()
with open(script_dir / "data.txt", "r") as f:
    data_content = f.read()

print("\n" + "=" * 60)
print("RFP EXPENSE AGENT - Custom Functions Version")
print("=" * 60)

# ---------------------------------------------------------------
# Add references (Lab 3 pattern - AgentsClient directly)
# ---------------------------------------------------------------
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole

# Import our custom functions (Lab 3)
from user_functions import user_functions

# ---------------------------------------------------------------
# Connect to the Agent client (Lab 3 pattern)
# ---------------------------------------------------------------
print("\nConnecting to Azure AI Agent Service...")
agent_client = AgentsClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
    ),
)

# ---------------------------------------------------------------
# Define agent with custom function tools (Lab 3)
# ---------------------------------------------------------------
with agent_client:

    # Lab 3: Create FunctionTool from our custom functions
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    # Lab 3 KEY CONCEPT: Enable auto function calling
    agent_client.enable_auto_function_calls(toolset)

    # Lab 1: Embed grounding data directly in instructions
    agent_instructions = f"""You are an RFP Expense Analyzer for Javista Services SAL.

EXPENSE POLICY (reference this for policy questions):
{policy_content}

RFP DATA (reference this for data questions):
{data_content}

Your capabilities:
1. Answer questions about the RFP expense data
2. Answer questions about the expense policy
3. Compare actual costs against policy rate caps
4. Submit expense reports - collect email, project name, description, amount
   then use submit_expense_report function
5. Flag budget overruns - collect category, budgeted/actual amounts, reason
   then use flag_budget_overrun function

Be concise. Reference specific policy rules when relevant.
Show calculations clearly when doing math.
"""

    # Lab 3: Create the agent with toolset
    print("Creating agent with custom function tools...")
    agent = agent_client.create_agent(
        model=model_deployment,
        name="rfp-expense-functions-agent",
        instructions=agent_instructions,
        toolset=toolset,
    )
    print(f"  Agent created: {agent.name} (ID: {agent.id})")

    # Lab 3: Create thread
    thread = agent_client.threads.create()
    print(f"  Thread created (ID: {thread.id})")

    # -----------------------------------------------------------
    # Chat loop (Lab 3)
    # -----------------------------------------------------------
    print("\n" + "=" * 60)
    print("Chat with the RFP Expense Agent (Custom Functions)")
    print("-" * 60)
    print("Try: 'Submit an expense report'")
    print("Try: 'Flag a budget overrun for travel'")
    print("Try: 'What is the max rate for an AI Engineer?'")
    print("Type 'quit' to exit.")
    print("=" * 60 + "\n")

    while True:
        user_prompt = input("You: ").strip()
        if not user_prompt:
            continue
        if user_prompt.lower() == "quit":
            print("\nEnding conversation...\n")
            break

        # Lab 3: Send message to thread
        message = agent_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt,
        )

        # Lab 3: Run with auto function calling
        run = agent_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        # Lab 3: Check for failures
        if run.status == "failed":
            print(f"\n  Run failed: {run.last_error}\n")
            continue

        # Lab 3: Get agent response
        last_msg = agent_client.messages.get_last_message_text_by_role(
            thread_id=thread.id,
            role=MessageRole.AGENT,
        )
        if last_msg:
            print(f"\nAgent: {last_msg.text.value}\n")

    # -----------------------------------------------------------
    # Conversation history (Lab 3)
    # -----------------------------------------------------------
    print("=" * 60)
    print("CONVERSATION LOG")
    print("=" * 60 + "\n")

    messages = agent_client.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING,
    )
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            role = str(msg.role).upper()
            print(f"  [{role}]: {last_text.text.value}\n")

    # -----------------------------------------------------------
    # Clean up (Lab 3)
    # -----------------------------------------------------------
    print("=" * 60)
    print("CLEANUP")
    print("=" * 60)

    agent_client.delete_agent(agent.id)
    print("  Agent deleted")
    print("\n  All resources cleaned up successfully.\n")

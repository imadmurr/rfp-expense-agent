"""
RFP Expense Agent - Custom Functions Version
=============================================
Assignment: AI BootCamp 102 - Day 1

This is the ALTERNATIVE implementation using the AgentsClient pattern
from Lab 3 (Custom Functions). It demonstrates:

Lab 3 Concepts:
  - AgentsClient connection
  - FunctionTool with custom user_functions
  - ToolSet with auto function calling enabled
  - create_agent with toolset
  - threads.create for conversation management
  - messages.create + runs.create_and_process
  - get_last_message_text_by_role
  - Conversation history with ListSortOrder
  - Cleanup: delete_agent

Combined with Lab 1 Concepts:
  - Agent instructions for grounding behavior
  - Policy-based responses (simulates file search grounding)

Use this file when you want to demonstrate the custom function calling
pattern specifically. The main agent.py uses the Lab 2 pattern.
"""

import os
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

# Load expense policy content to embed in instructions (grounding - Lab 1)
script_dir = os.path.dirname(os.path.abspath(__file__))
policy_path = os.path.join(script_dir, "expense_policy.txt")
with open(policy_path, "r") as f:
    policy_content = f.read()

# Load data for context
data_path = os.path.join(script_dir, "data.txt")
with open(data_path, "r") as f:
    data_content = f.read()

print("\n" + "=" * 60)
print("RFP EXPENSE AGENT - Custom Functions Version")
print("=" * 60)

# ---------------------------------------------------------------
# Add references (Lab 3 pattern)
# ---------------------------------------------------------------
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole

# Import our custom functions (Lab 3 pattern)
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
# Define an agent that can use the custom functions (Lab 3)
# ---------------------------------------------------------------
with agent_client:

    # Create FunctionTool from our custom functions (Lab 3 pattern)
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    # Enable auto function calling (Lab 3 key concept)
    # This allows the agent to automatically detect and call our functions
    agent_client.enable_auto_function_calls(toolset)

    # Agent instructions include grounding data (Lab 1 concept)
    # Since we can't use file search with AgentsClient, we embed the
    # policy content directly in the instructions
    agent_instructions = f"""You are an RFP Expense Analyzer for Javista Services SAL.

You help users analyze RFP expenses and manage expense reports.

EXPENSE POLICY (use this to answer policy questions):
{policy_content}

RFP DATA (use this to answer data questions):
{data_content}

Your capabilities:
1. Answer questions about the RFP expense data (consultant costs, hours, rates, etc.)
2. Answer questions about the expense policy (rate caps, approval thresholds, travel rules)
3. Compare actual costs against policy rate caps
4. When a user wants to submit an expense report:
   - Collect their email address, project name, description, and total amount
   - Then use the submit_expense_report function
   - Tell the user the filename where the report was saved
5. When a user wants to flag a budget overrun:
   - Collect the category, budgeted amount, actual amount, and reason
   - Then use the flag_budget_overrun function
   - Tell the user the filename where the alert was saved

Be concise and reference specific policy rules when relevant.
When performing calculations, show your work clearly.
"""

    # Create the agent with the toolset (Lab 3 pattern)
    print("Creating agent with custom function tools...")
    agent = agent_client.create_agent(
        model=model_deployment,
        name="rfp-expense-functions-agent",
        instructions=agent_instructions,
        toolset=toolset,
    )
    print(f"  ✓ Agent created: {agent.name} (ID: {agent.id})")

    # Create a thread for the conversation (Lab 3 pattern)
    thread = agent_client.threads.create()
    print(f"  ✓ Thread created (ID: {thread.id})")

    # -----------------------------------------------------------
    # Interactive chat loop (Lab 3 pattern)
    # -----------------------------------------------------------
    print("\n" + "=" * 60)
    print("Chat with the RFP Expense Agent (Custom Functions)")
    print("Try: 'Submit an expense report' or 'Flag a budget overrun'")
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
        message = agent_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt,
        )

        # Run the thread with auto function calling (Lab 3 key concept)
        # create_and_process automatically handles function calls
        run = agent_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        # -----------------------------------------------------------
        # Check the run status for failures (Lab 3)
        # -----------------------------------------------------------
        if run.status == "failed":
            print(f"\n  ✗ Run failed: {run.last_error}\n")
            continue

        # -----------------------------------------------------------
        # Show the latest response from the agent (Lab 3)
        # -----------------------------------------------------------
        last_msg = agent_client.messages.get_last_message_text_by_role(
            thread_id=thread.id,
            role=MessageRole.AGENT,
        )
        if last_msg:
            print(f"\nAgent: {last_msg.text.value}\n")

    # -----------------------------------------------------------
    # Get the conversation history (Lab 3 pattern)
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
    # Clean up (Lab 3 pattern)
    # -----------------------------------------------------------
    print("=" * 60)
    print("CLEANUP")
    print("=" * 60)

    agent_client.delete_agent(agent.id)
    print("  ✓ Agent deleted")
    print("\n  All resources cleaned up successfully.\n")

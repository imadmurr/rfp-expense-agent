"""
RFP Expense Analyzer Agent
===========================
Assignment: AI BootCamp 102 - Day 1

This agent combines ALL concepts from the three labs:

Lab 1 (Agent Fundamentals):
  - Agent with instructions (grounding)
  - File search / knowledge base (expense policy document)
  - Code interpreter tool (for data analysis & charts)

Lab 2 (Develop an AI Agent):
  - Programmatic agent creation via SDK (AIProjectClient + OpenAI client)
  - File upload to the project
  - CodeInterpreterTool with uploaded data file
  - Conversations API (create, send messages, get responses)
  - Conversation history retrieval
  - Proper cleanup (delete conversation + agent)

Lab 3 (Custom Functions):
  - Custom function definitions (user_functions.py)
  - FunctionTool and ToolSet
  - Auto function calling (agent_client.enable_auto_function_calls)
  - AgentsClient for function-based agent
  - Thread management with message history
  - Cleanup (delete agent)

Architecture:
  The agent uses TWO tool types simultaneously:
    1. CodeInterpreterTool  → analyzes uploaded data, generates charts
    2. FunctionTool          → submits expense reports, flags budget overruns
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
    print("       Copy it from the Foundry portal > Project > Overview page.")
    exit(1)

# ---------------------------------------------------------------
# Data file paths
# ---------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, "data.txt")
policy_file_path = os.path.join(script_dir, "expense_policy.txt")

# Show the data that will be loaded
print("\n" + "=" * 60)
print("RFP EXPENSE ANALYZER AGENT")
print("=" * 60)
print(f"\nProject Endpoint: {project_endpoint[:50]}...")
print(f"Model: {model_deployment}")

# Load and display the data file
print(f"\nLoading data from: {data_file_path}")
with open(data_file_path, "r") as f:
    data_content = f.read()
print("\n--- Data Preview ---")
print(data_content[:500] + "..." if len(data_content) > 500 else data_content)
print("--- End Preview ---\n")

# ---------------------------------------------------------------
# Add references (Lab 2 + Lab 3 combined imports)
# ---------------------------------------------------------------

# Lab 2: For file upload, code interpreter, conversations API
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    CodeInterpreterToolAuto,
)

# Lab 3: For custom function tools
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole

# Lab 3: Import our custom functions
from user_functions import user_functions

# ---------------------------------------------------------------
# Connect to the AI Project and OpenAI clients (Lab 2 pattern)
# ---------------------------------------------------------------
print("Connecting to Azure AI Foundry project...")

with (
    DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
    ) as credential,
    AIProjectClient(
        endpoint=project_endpoint, credential=credential
    ) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # -----------------------------------------------------------
    # Upload the data file and create CodeInterpreterTool (Lab 2)
    # -----------------------------------------------------------
    print("Uploading data file for analysis...")
    data_file = openai_client.files.create(
        file=open(data_file_path, "rb"), purpose="assistants"
    )
    print(f"  ✓ Uploaded: {data_file.filename} (ID: {data_file.id})")

    # Also upload the policy file for grounding (Lab 1 concept)
    print("Uploading expense policy for grounding...")
    policy_file = openai_client.files.create(
        file=open(policy_file_path, "rb"), purpose="assistants"
    )
    print(f"  ✓ Uploaded: {policy_file.filename} (ID: {policy_file.id})")

    # Create the Code Interpreter tool with both files attached
    code_interpreter = CodeInterpreterTool(
        container=CodeInterpreterToolAuto(
            file_ids=[data_file.id, policy_file.id]
        )
    )

    # -----------------------------------------------------------
    # Define the agent with instructions + tools (Lab 1 + Lab 2)
    # -----------------------------------------------------------
    # The agent combines:
    #   - Grounding instructions (Lab 1)
    #   - Code Interpreter tool (Lab 1 + Lab 2)
    #   - Knowledge from uploaded files (Lab 1)
    agent_instructions = """You are an RFP Expense Analyzer for Javista Services SAL.

You have access to two files:
1. data.txt - Contains the RFP expense summary with consultant costs, hours, and project details
2. expense_policy.txt - Contains the company expense policy with rate caps and approval thresholds

Your capabilities:
- Answer questions about the RFP expense data using Python analysis (Code Interpreter)
- Answer questions about expense policy rules based on the policy document
- Create text-based visualizations and charts of the expense data
- Calculate statistical metrics (averages, totals, standard deviations, etc.)
- Compare actual costs against policy rate caps to identify overruns
- When a user wants to submit an expense report, collect their email, project name, description, and amount
- When a user wants to flag a budget overrun, collect the category, budgeted amount, actual amount, and reason

Always use Python (Code Interpreter) when performing calculations or creating charts.
Be concise but thorough in your analysis.
Reference specific policy rules when answering policy questions.
"""

    print("\nCreating agent: rfp-expense-agent...")
    agent = project_client.agents.create_version(
        agent_name="rfp-expense-agent",
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=agent_instructions,
            tools=[code_interpreter],
        ),
    )
    print(f"  ✓ Agent created: {agent.name} (version: {agent.version})")

    # -----------------------------------------------------------
    # Create a conversation for the chat session (Lab 2)
    # -----------------------------------------------------------
    print("Creating conversation thread...")
    conversation = openai_client.conversations.create()
    print(f"  ✓ Conversation created (ID: {conversation.id})")

    # -----------------------------------------------------------
    # Interactive chat loop (Lab 2 + Lab 3 pattern)
    # -----------------------------------------------------------
    print("\n" + "=" * 60)
    print("Chat with the RFP Expense Analyzer Agent")
    print("Type your questions about the RFP data or expense policy.")
    print("Type 'quit' to exit.")
    print("=" * 60 + "\n")

    while True:
        # Get user input
        user_prompt = input("You: ").strip()
        if not user_prompt:
            continue
        if user_prompt.lower() == "quit":
            print("\nEnding conversation...\n")
            break

        # -----------------------------------------------------------
        # Send a prompt to the agent (Lab 2 pattern)
        # -----------------------------------------------------------
        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[
                {"type": "message", "role": "user", "content": user_prompt}
            ],
        )

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent": {"name": agent.name, "type": "agent_reference"}
            },
            input="",
        )

        # -----------------------------------------------------------
        # Check the response status for failures (Lab 2)
        # -----------------------------------------------------------
        if response.status == "failed":
            print(f"\n  ✗ Response failed: {response.error}\n")
            continue

        # -----------------------------------------------------------
        # Show the latest response from the agent (Lab 2)
        # -----------------------------------------------------------
        print(f"\nAgent: {response.output_text}\n")

    # -----------------------------------------------------------
    # Get the conversation history (Lab 2 + Lab 3 pattern)
    # -----------------------------------------------------------
    print("=" * 60)
    print("CONVERSATION LOG")
    print("=" * 60 + "\n")

    items = openai_client.conversations.items.list(
        conversation_id=conversation.id
    )
    for item in items:
        if item.type == "message":
            role = item.role.upper()
            content = item.content[0].text if item.content else "(no content)"
            print(f"  [{role}]: {content}\n")

    # -----------------------------------------------------------
    # Clean up (Lab 2 + Lab 3 pattern)
    # -----------------------------------------------------------
    print("=" * 60)
    print("CLEANUP")
    print("=" * 60)

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("  ✓ Conversation deleted")

    project_client.agents.delete_version(
        agent_name=agent.name, agent_version=agent.version
    )
    print("  ✓ Agent deleted")

    print("\n  All resources cleaned up successfully.")
    print("  Thank you for using the RFP Expense Analyzer!\n")

"""
Custom Functions for the RFP Expense Agent
==========================================
Concept from Lab 3: Use a custom function in an AI agent

This module defines callable functions that the agent can invoke as tools.
The agent will automatically detect when to call these functions based on
the user's request and the function signatures.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Callable, Set
from datetime import datetime


# ---------------------------------------------------------------
# Custom Function 1: Submit an expense report
# (Mirrors Lab 3's submit_support_ticket pattern)
# ---------------------------------------------------------------
def submit_expense_report(email_address: str, project_name: str, description: str, total_amount: float) -> str:
    """
    Generates an expense report file and returns a confirmation message.
    The agent collects the required fields from the user, then calls this function.
    """
    script_dir = Path(__file__).parent
    report_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    file_name = f"expense-report-{report_id}.txt"
    file_path = script_dir / file_name

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"{'='*50}\n"
        f"EXPENSE REPORT - {report_id}\n"
        f"{'='*50}\n"
        f"Date:        {timestamp}\n"
        f"Submitted by: {email_address}\n"
        f"Project:     {project_name}\n"
        f"Amount:      ${total_amount:,.2f}\n"
        f"{'='*50}\n"
        f"Description:\n{description}\n"
        f"{'='*50}\n"
        f"Status: PENDING APPROVAL\n"
    )
    file_path.write_text(text)

    message_json = json.dumps({
        "message": f"Expense report {report_id} submitted successfully. "
                   f"The report file is saved as {file_name}. "
                   f"Total amount: ${total_amount:,.2f}."
    })
    return message_json


# ---------------------------------------------------------------
# Custom Function 2: Flag a budget overrun
# ---------------------------------------------------------------
def flag_budget_overrun(category: str, budgeted_amount: float, actual_amount: float, reason: str) -> str:
    """
    Flags a budget overrun for a specific expense category.
    Creates an alert file for management review.
    """
    script_dir = Path(__file__).parent
    alert_id = str(uuid.uuid4()).replace('-', '')[:6].upper()
    file_name = f"budget-alert-{alert_id}.txt"
    file_path = script_dir / file_name

    overrun = actual_amount - budgeted_amount
    overrun_pct = (overrun / budgeted_amount) * 100 if budgeted_amount > 0 else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"{'='*50}\n"
        f"BUDGET OVERRUN ALERT - {alert_id}\n"
        f"{'='*50}\n"
        f"Date:            {timestamp}\n"
        f"Category:        {category}\n"
        f"Budgeted Amount: ${budgeted_amount:,.2f}\n"
        f"Actual Amount:   ${actual_amount:,.2f}\n"
        f"Overrun:         ${overrun:,.2f} ({overrun_pct:.1f}%)\n"
        f"{'='*50}\n"
        f"Reason: {reason}\n"
        f"{'='*50}\n"
        f"Action Required: MANAGEMENT REVIEW\n"
    )
    file_path.write_text(text)

    message_json = json.dumps({
        "message": f"Budget overrun alert {alert_id} created for {category}. "
                   f"Overrun amount: ${overrun:,.2f} ({overrun_pct:.1f}%). "
                   f"Alert file saved as {file_name}."
    })
    return message_json


# ---------------------------------------------------------------
# Define the set of callable functions (Lab 3 pattern)
# The agent will auto-detect which function to call based on context
# ---------------------------------------------------------------
user_functions: Set[Callable[..., Any]] = {
    submit_expense_report,
    flag_budget_overrun,
}

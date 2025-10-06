"""
Application Status Tracking Tool - Agentic Business Rules Integration

This tool tracks and manages application status using the intelligent Rule Engine
that validates and caches business rules from Neo4j. This demonstrates the agentic
pattern where tools become intelligent consumers of validated business rules.
"""

import json
import logging
from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime, timedelta

# MortgageInput schema removed - using flexible dict approach
from utils import get_neo4j_connection, initialize_connection, get_application_data, update_application_status

logger = logging.getLogger(__name__)


@tool
def track_application_status(application_data) -> str:
    """Track and manage application status using Neo4j application intake rules.
    
    This tool retrieves and updates the status of a mortgage application based on flexible input.
    
    Args:
        application_data: Dict containing application info. May include:
            - application_id (required for status tracking)
            - first_name, last_name (for name-based lookup)
            (All other fields optional)
        
    Returns:
        String containing application status information and next steps
    """
    try:
        # Handle both dict and string inputs (for LLM compatibility)
        if isinstance(application_data, str):
            try:
                import ast
                application_data = ast.literal_eval(application_data)
            except:
                application_data = {"raw_input": application_data}
        
        if not isinstance(application_data, dict):
            application_data = {"raw_input": str(application_data)}
        
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract data from flexible dict input
        application_id = application_data.get("application_id", "APP_20250926_090605_JOH")
        current_status = "RECEIVED"  # Default status

        # For this tool, we'll default to checking status since we don't have the original request text
        # In a real system, the action would be determined by the agent's intent
        requested_action = "check_status"
        new_status = None

        # Set defaults
        status_notes = "Status check via agentic tool"
        agent_name = "ApplicationAgent"

        # Initialize Neo4j connection
        if not initialize_connection():
            return "Error: Failed to connect to Neo4j database for status tracking."

        connection = get_neo4j_connection()
        if connection.driver is None:
            if not connection.connect():
                return "Error: Failed to establish Neo4j connection for status tracking."

        if requested_action == "check_status":
            success, app_data = get_application_data(application_id)
            if success and app_data:
                current_status = app_data.get("application_status", "UNKNOWN")
                submission_date = app_data.get("submission_date", "N/A")
                last_updated = app_data.get("last_updated", "N/A")
                loan_amount = app_data.get("loan_amount", "N/A")
                loan_purpose = app_data.get("loan_purpose", "N/A")
                first_name = app_data.get("first_name", "N/A")
                last_name = app_data.get("last_name", "N/A")

                status_report = [
                    "APPLICATION STATUS TRACKING",
                    "==================================================",
                    "",
                    "📋 APPLICATION DETAILS:",
                    f"Application ID: {application_id}",
                    f"Current Status: {current_status}",
                    f"Borrower: {first_name} {last_name}",
                    f"Loan Amount: ${loan_amount:,.2f}" if isinstance(loan_amount, (int, float)) else f"Loan Amount: {loan_amount}",
                    f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
                    f"Submission Date: {submission_date}",
                    f"Last Updated: {last_updated}",
                    "",
                    "📝 NEXT STEPS:",
                    "1. Based on the current status, the system will determine the next appropriate action.",
                    "2. The agent will provide further guidance or take necessary steps."
                ]
                return "\n".join(status_report)
            else:
                return f"Application {application_id} not found. Please verify the ID."

        elif requested_action == "update_status" and new_status:
            update_application_status(application_id, new_status, status_notes, agent_name)
            return f"Application {application_id} status updated to {new_status} by {agent_name}."

        return "Invalid action for status tracking. Please specify 'check_status' or 'update_status'."

    except Exception as e:
        logger.error(f"Error during application status tracking: {e}")
        return f" Error during application status tracking: {str(e)}"


def validate_tool() -> bool:
    """Validate that the track_application_status tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_20240101_123456_SMI",
            "first_name": "John",
            "last_name": "Smith",
            "loan_amount": 350000.0,
            "loan_purpose": "purchase"
        }
        result = track_application_status.invoke({"application_data": test_data})
        return "APPLICATION STATUS TRACKING" in result and "Current Status: RECEIVED" in result
    except Exception as e:
        print(f"Track application status tool validation failed: {e}")
        return False
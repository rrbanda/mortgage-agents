"""
ApplicationAgent Tools Package

This package contains tools for the ApplicationAgent focused on mortgage application
data collection and management (NOT business rules enforcement).

The ApplicationAgent focuses on 5 core application management capabilities:
1. Mortgage application intake and storage
2. Application completeness verification (basic fields only)
3. Financial metrics calculation (DTI, LTV - informational only)
4. Application status tracking and retrieval
5. URLA Form 1003 generation

Currently Implemented Tools (5 operational tools):
- receive_mortgage_application: Collect and store application data in Neo4j
- check_application_completeness: Verify basic required fields are present
- perform_initial_qualification: Calculate financial metrics (DTI, LTV)
- track_application_status: Retrieve application status by ID
- generate_urla_1003_form: Generate URLA form from stored data

Business Rules:
- Application Agent does NOT enforce business rules
- For qualification decisions, use MortgageAdvisorAgent
- For business rules queries, use BusinessRulesAgent tools from shared/rules/
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import all implemented tools - 100% data-driven from Neo4j
from .receive_mortgage_application import receive_mortgage_application, validate_tool as validate_receive_mortgage_application
from .check_application_completeness import check_application_completeness, validate_tool as validate_check_application_completeness
from .perform_initial_qualification import perform_initial_qualification, validate_tool as validate_perform_initial_qualification
from .track_application_status import track_application_status, validate_tool as validate_track_application_status
from .generate_urla_1003_form import generate_urla_1003_form, validate_tool as validate_generate_urla_1003_form

# Import MCP credit check tools (shared with UnderwritingAgent)
# ApplicationAgent can fetch credit data during initial application intake
from ...underwriting_agent.tools.get_credit_score import get_credit_score
from ...underwriting_agent.tools.verify_identity import verify_identity


def get_all_application_agent_tools() -> List[BaseTool]:
    """
    Returns a list of all tools available to the ApplicationAgent.
    
    Operational Tools (7 total):
    
    Core Application Tools (5):
    - receive_mortgage_application: Store application data in MortgageApplication nodes
    - check_application_completeness: Check basic required fields are present
    - perform_initial_qualification: Calculate DTI/LTV metrics (informational only)
    - track_application_status: Retrieve application status by application_id
    - generate_urla_1003_form: Generate URLA form from stored data
    
    MCP Credit Tools (2 - for fetching missing data):
    - get_credit_score: Fetch credit score from external MCP server when not provided
    - verify_identity: Verify borrower identity via external MCP server
    
    Business Rules Tools:
    - Application Agent does NOT have business rules tools
    - For business rules, call shared/rules tools via BusinessRulesAgent
    """
    core_tools = [
        receive_mortgage_application,
        check_application_completeness,
        perform_initial_qualification,
        track_application_status,
        generate_urla_1003_form,
        # MCP tools for fetching missing borrower data
        get_credit_score,
        verify_identity
    ]
    
    return core_tools


def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        "receive_mortgage_application": "Collect and store mortgage application data in Neo4j MortgageApplication nodes",
        "check_application_completeness": "Check if basic required fields are present in application (no business rules enforcement)",
        "perform_initial_qualification": "Calculate financial metrics (DTI, LTV) for informational purposes only",
        "track_application_status": "Retrieve application status and details by application_id from Neo4j",
        "generate_urla_1003_form": "Generate URLA Form 1003 from stored application data",
        "get_credit_score": "Fetch credit score from external MCP server when not provided by borrower",
        "verify_identity": "Verify borrower identity via external MCP server"
    }


def validate_all_tools() -> Dict[str, bool]:
    """
    Runs validation tests for all individual tools and returns a dictionary of results.
    """
    results = {}
    results["receive_mortgage_application"] = validate_receive_mortgage_application()
    results["check_application_completeness"] = validate_check_application_completeness()
    results["perform_initial_qualification"] = validate_perform_initial_qualification()
    results["track_application_status"] = validate_track_application_status()
    results["generate_urla_1003_form"] = validate_generate_urla_1003_form()
    return results


__all__ = [
    # All core application tools
    "receive_mortgage_application",
    "check_application_completeness", 
    "perform_initial_qualification",
    "track_application_status",
    "generate_urla_1003_form",
    
    # Validation functions
    "validate_receive_mortgage_application",
    "validate_check_application_completeness",
    "validate_perform_initial_qualification",
    "validate_track_application_status",
    "validate_generate_urla_1003_form",
    
    # Tool management functions
    "get_all_application_agent_tools",
    "get_tool_descriptions", 
    "validate_all_tools"
]

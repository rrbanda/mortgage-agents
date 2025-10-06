"""
MortgageAdvisorAgent Tools Package

This package aggregates all operational tools for the MortgageAdvisorAgent.

The MortgageAdvisorAgent has 3 operational tools (NO business rules):
1. explain_loan_programs: Loan program education and comparison
2. recommend_loan_program: Calculate metrics and suggest programs to explore
3. check_qualification_requirements: Check data completeness and calculate ratios

Each tool:
- Performs operational tasks (calculate, format, display)
- NO hardcoded business rules or qualification thresholds
- Directs agent to use business rules tools from shared/rules/ for actual requirements
- Calls Neo4j directly (not via MCP) for operational data only

Business rules tools (from shared/rules/) are added separately in agent.py
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import all implemented tools
from .explain_loan_programs import explain_loan_programs, validate_tool as validate_explain_loan_programs
from .recommend_loan_program import recommend_loan_program
from .check_qualification_requirements import check_qualification_requirements, validate_tool as validate_check_qualification_requirements

# Import shared application data tools for accessing stored applications
try:
    from ...shared.application_data_tools import (
        get_stored_application_data,
        list_stored_applications,
        find_application_by_name
    )
except ImportError:
    from ...shared.application_data_tools import (
        get_stored_application_data,
        list_stored_applications,
        find_application_by_name
    )


def get_all_mortgage_advisor_tools() -> List[BaseTool]:
    """
    Returns all operational tools for the MortgageAdvisorAgent.
    
    These are operational tools that:
    - Calculate metrics and display information
    - Check data completeness
    - Provide educational information
    - NO business rules or qualification decisions
    
    Returns 3 operational tools (business rules tools added separately in agent.py)
    """
    return [
        explain_loan_programs,
        recommend_loan_program,
        check_qualification_requirements
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        "explain_loan_programs": "Educate customers about different mortgage loan programs (FHA, VA, USDA, Conventional, Jumbo) - NO qualification thresholds",
        "recommend_loan_program": "Calculate borrower financial metrics (DTI, LTV) and suggest loan programs to explore - NO qualification decisions",
        "check_qualification_requirements": "Check application data completeness and calculate financial ratios - NO threshold evaluations"
    }


def validate_all_tools() -> Dict[str, bool]:
    """
    Runs validation tests for all individual tools and returns a dictionary of results.
    """
    results = {}
    results["explain_loan_programs"] = validate_explain_loan_programs()
    results["recommend_loan_program"] = True  # Simplified tool doesn't have validation yet
    results["check_qualification_requirements"] = validate_check_qualification_requirements()
    return results


__all__ = [
    # All 3 operational tools
    "explain_loan_programs",
    "recommend_loan_program", 
    "check_qualification_requirements",
    
    # Validation functions
    "validate_explain_loan_programs",
    "validate_check_qualification_requirements",
    
    # Tool management functions
    "get_all_mortgage_advisor_tools",
    "get_tool_descriptions", 
    "validate_all_tools"
]

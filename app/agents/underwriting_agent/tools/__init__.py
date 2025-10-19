"""
UnderwritingAgent Tools Package

Core operational tools for mortgage underwriting.

The UnderwritingAgent has 5 core operational tools:
1. analyze_credit_risk: Credit risk analysis (NO hardcoded thresholds)
2. calculate_debt_to_income: DTI calculation (NO hardcoded limits)
3. evaluate_income_sources: Income source evaluation
4. run_aus_check: AUS system integration
5. make_underwriting_decision: Decision analysis

MCP tools are loaded separately via:
- mcp_tools_loader.get_mcp_credit_tools() for credit check via ToolHive
- neo4j_mcp_loader.get_neo4j_mcp_tools() for business rules
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import core operational tools
from .analyze_credit_risk import analyze_credit_risk, validate_tool as validate_analyze_credit_risk
from .calculate_debt_to_income import calculate_debt_to_income, validate_tool as validate_calculate_debt_to_income
from .evaluate_income_sources import evaluate_income_sources, validate_tool as validate_evaluate_income_sources
from .make_underwriting_decision import make_underwriting_decision, validate_tool as validate_make_underwriting_decision
from .run_aus_check import run_aus_check, validate_tool as validate_run_aus_check


def get_core_underwriting_tools() -> List[BaseTool]:
    """
    Get core operational tools ONLY (no MCP wrapper tools).
    
    Returns 5 core operational tools:
    - analyze_credit_risk
    - calculate_debt_to_income
    - evaluate_income_sources
    - run_aus_check
    - make_underwriting_decision
    """
    return [
        analyze_credit_risk,
        calculate_debt_to_income,
        evaluate_income_sources,
        run_aus_check,
        make_underwriting_decision,
    ]


def get_all_underwriting_agent_tools() -> List[BaseTool]:
    """
    Get all operational tools for UnderwritingAgent.
    
    Returns only core operational tools (5 tools).
    MCP tools are loaded separately via official LangGraph pattern.
    """
    return get_core_underwriting_tools()


def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        # Core underwriting tools
        "analyze_credit_risk": "Analyze credit risk - NO hardcoded thresholds, displays credit info",
        "calculate_debt_to_income": "Calculate DTI ratio - NO hardcoded limits, just math",
        "evaluate_income_sources": "Evaluate income sources - NO hardcoded qualification rules",
        "run_aus_check": "Submit to AUS system - operational integration",
        "make_underwriting_decision": "Analyze decision factors - NO hardcoded approval rules",
    }


def validate_all_tools() -> Dict[str, bool]:
    """
    Runs validation tests for all individual tools and returns a dictionary of results.
    """
    results = {}
    # Core underwriting tools
    results["analyze_credit_risk"] = validate_analyze_credit_risk()
    results["calculate_debt_to_income"] = validate_calculate_debt_to_income()
    results["evaluate_income_sources"] = validate_evaluate_income_sources()
    results["run_aus_check"] = validate_run_aus_check()
    results["make_underwriting_decision"] = validate_make_underwriting_decision()
    
    return results


__all__ = [
    # Core underwriting tools
    "analyze_credit_risk",
    "calculate_debt_to_income", 
    "evaluate_income_sources",
    "run_aus_check",
    "make_underwriting_decision",
    
    # Validation functions
    "validate_analyze_credit_risk",
    "validate_calculate_debt_to_income",
    "validate_evaluate_income_sources",
    "validate_run_aus_check",
    "validate_make_underwriting_decision",
    
    # Tool management functions
    "get_core_underwriting_tools",
    "get_all_underwriting_agent_tools",
    "get_tool_descriptions", 
    "validate_all_tools"
]

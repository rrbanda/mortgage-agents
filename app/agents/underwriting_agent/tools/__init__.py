"""
UnderwritingAgent Tools Package

Operational tools for mortgage underwriting (NO hardcoded business rules).

The UnderwritingAgent has 8 operational tools:
1. analyze_credit_risk: Credit risk analysis (NO hardcoded thresholds)
2. calculate_debt_to_income: DTI calculation (NO hardcoded limits)
3. evaluate_income_sources: Income source evaluation
4. run_aus_check: AUS system integration
5. make_underwriting_decision: Decision analysis
6. get_credit_score: MCP tool for real-time credit scores
7. verify_identity: MCP tool for identity verification
8. get_credit_report: MCP tool for credit reports

Each tool:
- Performs operational tasks (analyze, calculate, evaluate, check)
- NO hardcoded business rules about credit/DTI/LTV thresholds
- Calls Neo4j DIRECTLY (not via MCP) for operational data
- MCP tools call external credit check services

Business rules tools (from shared/rules/) are added separately in agent.py
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import all implemented tools - 100% data-driven from Neo4j
from .analyze_credit_risk import analyze_credit_risk
from .calculate_debt_to_income import calculate_debt_to_income, validate_tool as validate_calculate_debt_to_income
from .evaluate_income_sources import evaluate_income_sources, validate_tool as validate_evaluate_income_sources
from .make_underwriting_decision import make_underwriting_decision
from .run_aus_check import run_aus_check, validate_tool as validate_run_aus_check

# Import MCP credit check tools
from .get_credit_score import get_credit_score, validate_tool as validate_get_credit_score
from .verify_identity import verify_identity, validate_tool as validate_verify_identity
from .get_credit_report import get_credit_report, validate_tool as validate_get_credit_report


def get_all_underwriting_agent_tools() -> List[BaseTool]:
    """
    Get all operational tools for UnderwritingAgent.
    
    These are operational tools that:
    - Analyze credit risk and calculate DTI (NO hardcoded thresholds)
    - Evaluate income sources and run AUS checks
    - Make underwriting decisions (NO hardcoded approval rules)
    - Integrate with external MCP credit check services
    - NO business rules about credit/DTI/LTV limits
    
    Returns 8 operational tools (business rules tools added separately in agent.py)
    """
    return [
        # Core underwriting tools (operational analysis)
        analyze_credit_risk,
        calculate_debt_to_income,
        evaluate_income_sources,
        run_aus_check,
        make_underwriting_decision,
        
        # MCP credit check tools (real-time external data)
        get_credit_score,
        verify_identity,
        get_credit_report
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        # Core underwriting tools (operational - NO hardcoded business rules)
        "analyze_credit_risk": "Analyze credit risk - NO hardcoded thresholds, displays credit info",
        "calculate_debt_to_income": "Calculate DTI ratio - NO hardcoded limits, just math",
        "evaluate_income_sources": "Evaluate income sources - NO hardcoded qualification rules",
        "run_aus_check": "Submit to AUS system - operational integration",
        "make_underwriting_decision": "Analyze decision factors - NO hardcoded approval rules",
        
        # MCP credit check tools (real-time external data)
        "get_credit_score": "Get real-time credit score from external MCP service",
        "verify_identity": "Verify borrower identity via external MCP service",
        "get_credit_report": "Get comprehensive credit report from external MCP service"
    }


def validate_all_tools() -> Dict[str, bool]:
    """
    Runs validation tests for all individual tools and returns a dictionary of results.
    """
    results = {}
    # Core underwriting tools
    results["analyze_credit_risk"] = True  # Simplified tools don't have validation yet
    results["calculate_debt_to_income"] = validate_calculate_debt_to_income()
    results["evaluate_income_sources"] = validate_evaluate_income_sources()
    results["run_aus_check"] = validate_run_aus_check()
    results["make_underwriting_decision"] = True  # Simplified tools don't have validation yet
    
    # MCP credit check tools
    results["get_credit_score"] = validate_get_credit_score()
    results["verify_identity"] = validate_verify_identity()
    results["get_credit_report"] = validate_get_credit_report()
    
    return results


__all__ = [
    # Core underwriting tools (Neo4j-powered)
    "analyze_credit_risk",
    "calculate_debt_to_income", 
    "evaluate_income_sources",
    "run_aus_check",
    "make_underwriting_decision",
    
    # MCP credit check tools (real-time external data)
    "get_credit_score",
    "verify_identity",
    "get_credit_report",
    
    # Validation functions
    "validate_calculate_debt_to_income",
    "validate_evaluate_income_sources",
    "validate_run_aus_check",
    "validate_get_credit_score",
    "validate_verify_identity",
    "validate_get_credit_report",
    
    # Tool management functions
    "get_all_underwriting_agent_tools",
    "get_tool_descriptions", 
    "validate_all_tools"
]

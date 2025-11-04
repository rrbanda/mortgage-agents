"""
AppraisalAgent Tools Package

Operational tools for property appraisal (NO hardcoded business rules).

The AppraisalAgent has 6 operational tools:
1. analyze_property_value: Property valuation analysis
2. find_comparable_sales: Research comparable properties
3. assess_property_condition: Property condition assessment
4. review_appraisal_report: Review appraisal documents
5. evaluate_market_conditions: Market trend evaluation
6. schedule_appraisal: Schedule appraisal and send notifications (NEW)

Each tool:
- Performs operational tasks (analyze, research, assess, review, schedule)
- NO hardcoded business rules about LTV limits or appraisal standards
- Calls Neo4j DIRECTLY (not via MCP) for operational data

Business rules tools (from shared/rules/) are added separately in agent.py
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import all implemented tools - 100% data-driven from Neo4j
from .analyze_property_value import analyze_property_value, validate_tool as validate_analyze_property_value
from .find_comparable_sales import find_comparable_sales, validate_tool as validate_find_comparable_sales
from .assess_property_condition import assess_property_condition, validate_tool as validate_assess_property_condition
from .review_appraisal_report import review_appraisal_report, validate_tool as validate_review_appraisal_report
from .evaluate_market_conditions import evaluate_market_conditions, validate_tool as validate_evaluate_market_conditions
from .schedule_appraisal import schedule_appraisal, validate_tool as validate_schedule_appraisal


def get_all_appraisal_agent_tools() -> List[BaseTool]:
    """
    Get all operational tools for AppraisalAgent.
    
    These are operational tools that:
    - Analyze property value and market conditions
    - Research comparable sales
    - Assess property condition
    - Review appraisal reports
    - Schedule appraisals and send notifications
    - NO business rules about LTV limits or appraisal standards
    
    Returns 6 operational tools (business rules tools added separately in agent.py)
    """
    return [
        schedule_appraisal,  # NEW - Most commonly used, so prioritize first
        analyze_property_value,
        find_comparable_sales,
        assess_property_condition,
        review_appraisal_report,
        evaluate_market_conditions
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        "schedule_appraisal": "Schedule appraisal and send notifications - operational scheduling",
        "analyze_property_value": "Analyze property valuation - NO business rules, displays property info",
        "find_comparable_sales": "Research comparable sales in the area - operational analysis",
        "assess_property_condition": "Assess physical property condition - NO hardcoded standards",
        "review_appraisal_report": "Review appraisal report documents - operational review",
        "evaluate_market_conditions": "Evaluate market trends and conditions - NO threshold rules"
    }


def validate_all_tools() -> Dict[str, bool]:
    """
    Runs validation tests for all individual tools and returns a dictionary of results.
    """
    results = {}
    results["schedule_appraisal"] = validate_schedule_appraisal()
    results["analyze_property_value"] = validate_analyze_property_value()
    results["find_comparable_sales"] = validate_find_comparable_sales()
    results["assess_property_condition"] = validate_assess_property_condition()
    results["review_appraisal_report"] = validate_review_appraisal_report()
    results["evaluate_market_conditions"] = validate_evaluate_market_conditions()
    return results


__all__ = [
    # All 6 implemented tools
    "schedule_appraisal",
    "analyze_property_value",
    "find_comparable_sales",
    "assess_property_condition",
    "review_appraisal_report",
    "evaluate_market_conditions",
    
    # Validation functions
    "validate_schedule_appraisal",
    "validate_analyze_property_value",
    "validate_find_comparable_sales",
    "validate_assess_property_condition", 
    "validate_review_appraisal_report",
    "validate_evaluate_market_conditions",
    
    # Tool management functions
    "get_all_appraisal_agent_tools",
    "get_tool_descriptions", 
    "validate_all_tools"
]

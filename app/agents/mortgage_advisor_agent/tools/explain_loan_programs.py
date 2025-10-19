"""
Loan Programs Explanation Tool - Agentic Business Rules Integration

This tool explains and compares mortgage loan programs using the intelligent Rule Engine
that validates and caches business rules from Neo4j. This demonstrates the agentic
pattern where tools become intelligent consumers of validated business rules.
"""

import logging
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def explain_loan_programs(application_data: dict) -> str:
    """Explain and compare mortgage loan programs with educational guidance.
    
    This tool provides comprehensive education about mortgage loan programs,
    including general characteristics, benefits, and ideal use cases.
    For specific requirements and thresholds, agent should call Neo4j MCP tools.
    
    Args:
        application_data: Dictionary with structured borrower data (optional for this educational tool)
        
    Returns:
        String containing detailed loan program explanations and comparisons
    """
    try:
        # OPERATIONAL TOOL: Provides educational loan program overview
        # NO hardcoded business rules or specific thresholds
        # Agent should call get_loan_program_requirements MCP tool for actual requirements
        
        # Generate comprehensive loan programs educational guide
        guide = [
            "MORTGAGE LOAN PROGRAMS GUIDE",
            "==================================================",
            "",
            "📊 PROGRAM COMPARISON SUMMARY:",
            "",
            "CONVENTIONAL LOANS:",
            "• Best for: Borrowers with good credit and financial stability",
            "• Benefits: Competitive rates, flexible terms, widely available",
            "• Note: Requirements vary by lender and loan amount",
            "",
            "FHA LOANS:",
            "• Best for: First-time homebuyers and those with modest down payments",
            "• Benefits: Government-backed, more flexible qualification criteria",
            "• Note: FHA has specific requirements - use get_loan_program_requirements for details",
            "",
            "VA LOANS:",
            "• Best for: Veterans, active military, and eligible family members",
            "• Benefits: Competitive rates, government guarantee, special benefits for service members",
            "• Note: Eligibility requires military service verification",
            "",
            "USDA LOANS:",
            "• Best for: Rural and suburban homebuyers in eligible areas",
            "• Benefits: Supports homeownership in rural communities, government-backed",
            "• Note: Location and income limits apply - use get_loan_program_requirements for details",
            "",
            "📝 NEXT STEPS:",
            "1. For specific requirements (credit scores, down payments, DTI limits): Use get_loan_program_requirements tool",
            "2. For personalized recommendations based on your profile: Use recommend_loan_program tool",
            "3. For qualification criteria details: Use get_qualification_criteria tool",
            "4. Consult with a mortgage advisor for detailed guidance"
        ]

        return "\n".join(guide)

    except Exception as e:
        logger.error(f"Error during loan program explanation: {e}")
        return f" Error during loan program explanation: {str(e)}"


def validate_tool() -> bool:
    """Validate that the explain_loan_programs tool works correctly."""
    try:
        test_data = {
            "loan_purpose": "purchase",
            "credit_score": 720,
            "down_payment": 50000,
            "property_value": 250000
        }
        result = explain_loan_programs.invoke({"application_data": test_data})
        return "MORTGAGE LOAN PROGRAMS GUIDE" in result and "PROGRAM COMPARISON SUMMARY" in result
    except Exception as e:
        print(f"Explain loan programs tool validation failed: {e}")
        return False
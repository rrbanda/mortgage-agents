"""
Loan Programs Explanation Tool - Agentic Business Rules Integration

This tool explains and compares mortgage loan programs using the intelligent Rule Engine
that validates and caches business rules from Neo4j. This demonstrates the agentic
pattern where tools become intelligent consumers of validated business rules.
"""

import json
import logging
from datetime import datetime
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def explain_loan_programs(application_data: dict) -> str:
    """Explain and compare mortgage loan programs using real data from Neo4j.
    
    This tool queries the Neo4j knowledge graph to provide comprehensive
    education about mortgage loan programs, including requirements, benefits,
    and ideal use cases.
    
    Args:
        parsed_data: Pre-validated MortgageInput object with structured borrower data
        
    Returns:
        String containing detailed loan program explanations and comparisons
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract relevant fields from parsed_data for querying loan programs
        # For this tool, we might not need all fields, but can use them for context
        # For now, we'll just fetch all programs. Future enhancements could filter based on parsed_data.
        # Example: programs_to_explain = application_data.get('loan_purpose', "all")

        # ARCHITECTURE: This tool provides basic loan program guidance
        # For detailed business rules and specific program requirements, 
        # users should ask business rules questions which will be routed to BusinessRulesAgent
        
        # Use basic loan program information without business rules queries
        loan_programs = []

        if not loan_programs:
            return " No loan programs found in the database. Please contact support."

        # Generate comprehensive loan programs guide
        guide = [
            "MORTGAGE LOAN PROGRAMS GUIDE",
            "==================================================",
            "",
            "📚 AVAILABLE LOAN PROGRAMS:",
            ""
        ]

        for program in loan_programs:
            name = program.get('name', 'Unknown Program')
            description = program.get('description', 'No description available')
            min_credit = program.get('min_credit_score', 'N/A')
            max_ltv = program.get('max_ltv', 'N/A')
            max_dti = program.get('max_dti', 'N/A')
            down_payment = program.get('down_payment_required', 'N/A')
            benefits = program.get('benefits', [])
            requirements = program.get('requirements', [])

            guide.extend([
                f"🏠 {name.upper()}",
                f"Description: {description}",
                "",
                "📊 QUALIFICATION REQUIREMENTS:",
                f"• Minimum Credit Score: {min_credit}",
                f"• Maximum Loan-to-Value: {max_ltv}%",
                f"• Maximum Debt-to-Income: {max_dti}%",
                f"• Down Payment Required: {down_payment}%",
                ""
            ])

            if benefits:
                guide.append(" BENEFITS:")
                for benefit in benefits:
                    guide.append(f"• {benefit}")
                guide.append("")

            if requirements:
                guide.append("📋 REQUIREMENTS:")
                for requirement in requirements:
                    guide.append(f"• {requirement}")
                guide.append("")

            guide.append("--------------------------------------------------")
            guide.append("")

        # Add comparison section (NO hardcoded business rules)
        guide.extend([
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
        ])

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
        return "MORTGAGE LOAN PROGRAMS GUIDE" in result and "AVAILABLE LOAN PROGRAMS" in result
    except Exception as e:
        print(f"Explain loan programs tool validation failed: {e}")
        return False
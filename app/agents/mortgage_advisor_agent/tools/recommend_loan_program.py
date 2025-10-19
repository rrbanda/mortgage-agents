"""
Loan Program Recommendation Tool - Agentic Business Rules Integration

This tool provides loan program recommendations using the intelligent Rule Engine
that validates and caches business rules from Neo4j. This demonstrates the agentic
pattern where tools become intelligent consumers of validated business rules.
"""

import logging
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def recommend_loan_program(application_data: dict) -> str:
    """Provide basic loan program recommendations based on borrower profile.
    
    This tool uses structured borrower data to suggest suitable loan programs.
    
    Args:
        application_data: Dictionary with structured borrower data
        
    Returns:
        String containing loan program recommendations with explanations
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract borrower details with fallbacks from application_data
        credit_score_int = application_data.get('credit_score', 720)
        down_payment_amount = application_data.get('down_payment', 60000)
        property_value = application_data.get('property_value', 450000)
        down_payment_float = down_payment_amount / property_value if property_value > 0 else 0.15
        monthly_debts_int = application_data.get('monthly_debts', 0)
        
        # Calculate annual income from monthly if not provided directly
        monthly_income = application_data.get('monthly_income', 0)
        annual_income_int = application_data.get('annual_income', (monthly_income * 12 if monthly_income else 60000))
        
        first_time_buyer_flag = application_data.get('first_time_buyer', False)
        loan_purpose = application_data.get('loan_purpose', "purchase")
        property_type = application_data.get('property_type', "single_family_detached")

        # OPERATIONAL TOOL: Calculate borrower metrics and display profile
        # NO business logic - no qualification decisions
        # Agent should call business rules tools for actual requirements/thresholds
        
        # Calculate borrower metrics (pure math, no business rules)
        monthly_income_calc = annual_income_int / 12 if annual_income_int > 0 else 0
        dti = (monthly_debts_int / monthly_income_calc) * 100 if monthly_income_calc > 0 else 0
        ltv = (1 - down_payment_float) * 100
        loan_amount = property_value - down_payment_amount if property_value > 0 else 0

        # Generate borrower profile report (NO qualification decisions)
        report = [
            "BORROWER PROFILE & LOAN PROGRAM GUIDANCE",
            "==================================================",
            "",
            "📊 YOUR FINANCIAL PROFILE:",
            f"Credit Score: {credit_score_int}",
            f"Annual Income: ${annual_income_int:,.2f}",
            f"Monthly Income: ${monthly_income_calc:,.2f}",
            f"Monthly Debts: ${monthly_debts_int:,.2f}",
            f"Property Value: ${property_value:,.2f}",
            f"Down Payment: ${down_payment_amount:,.2f} ({down_payment_float*100:.1f}%)",
            f"Loan Amount: ${loan_amount:,.2f}",
            "",
            "📈 CALCULATED METRICS (Informational):",
            f"Loan-to-Value Ratio (LTV): {ltv:.2f}%",
            f"Debt-to-Income Ratio (DTI): {dti:.2f}%",
            f"First-Time Buyer: {'Yes' if first_time_buyer_flag else 'No'}",
            f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
            f"Property Type: {property_type.replace('_', ' ').title()}",
            "",
            "🏠 LOAN PROGRAMS TO CONSIDER:",
            "",
            "Based on your profile, here are loan programs you may want to explore:",
            "",
            "1. CONVENTIONAL LOANS",
            "   • Generally suitable for borrowers with established credit and financial stability",
            "   • Wide variety of loan options and terms available",
            "   • For specific requirements, use: get_loan_program_requirements('Conventional')",
            "",
            "2. FHA LOANS",
            "   • Government-backed option often suitable for first-time homebuyers",
            "   • May have more flexible qualification criteria",
            "   • For specific requirements, use: get_loan_program_requirements('FHA')",
            "",
            "3. VA LOANS (if eligible)",
            "   • Available for veterans and active military",
            "   • Special benefits for service members",
            "   • For specific requirements, use: get_loan_program_requirements('VA')",
            "",
            "4. USDA LOANS (if eligible)",
            "   • For rural and suburban properties in eligible areas",
            "   • Location and income restrictions apply",
            "   • For specific requirements, use: get_loan_program_requirements('USDA')",
            "",
            "📝 NEXT STEPS TO GET SPECIFIC QUALIFICATION DETAILS:",
            "",
            "1. Use get_loan_program_requirements tool to see specific requirements for each program",
            "2. Use get_qualification_criteria tool to understand what lenders look for",
            "3. Use get_underwriting_rules tool to see credit/DTI/LTV thresholds",
            "4. Use check_qualification_requirements tool to assess your specific situation",
            "",
            "⚠️ IMPORTANT:",
            "This tool provides your financial profile and suggests programs to explore.",
            "It does NOT make qualification decisions. Use business rules tools above",
            "to get actual requirements, thresholds, and eligibility criteria."
        ]

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error during loan program recommendation: {e}")
        return f" Error during loan program recommendation: {str(e)}"


def validate_tool() -> bool:
    """Validate that the recommend_loan_program tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "annual_income": 95000,
            "down_payment": 60000,
            "property_value": 450000,
            "monthly_debts": 850,
            "first_time_buyer": True,
            "loan_purpose": "purchase",
            "property_type": "single_family_detached"
        }
        result = recommend_loan_program.invoke({"application_data": test_data})
        return "BORROWER PROFILE & LOAN PROGRAM GUIDANCE" in result and "LOAN PROGRAMS TO CONSIDER" in result
    except Exception as e:
        print(f"Recommend loan program tool validation failed: {e}")
        return False
"""
Qualification Requirements Check Tool - Agentic Business Rules Integration

This tool checks qualification requirements using the intelligent Rule Engine
that validates and caches business rules from Neo4j. This demonstrates the agentic
pattern where tools become intelligent consumers of validated business rules.
"""

import logging
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def check_qualification_requirements(application_data: dict) -> str:
    """Check qualification requirements for specific loan programs based on borrower data.
    
    This tool uses structured borrower data to assess eligibility against program rules.
    
    Args:
        application_data: Dictionary with structured borrower data
        
    Returns:
        String containing detailed qualification requirements analysis
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract borrower details from flexible dict
        loan_program_name = application_data.get('loan_purpose', "Conventional")  # Default to Conventional if not specified
        credit_score = application_data.get('credit_score', 0)
        monthly_income = application_data.get('monthly_income', 0)
        annual_income = application_data.get('annual_income', (monthly_income * 12 if monthly_income else 0))
        monthly_debts = application_data.get('monthly_debts', 0)
        down_payment = application_data.get('down_payment', 0)
        property_value = application_data.get('property_value', 0)
        first_time_buyer = application_data.get('first_time_buyer', False)

        # OPERATIONAL TOOL: Check data completeness and calculate metrics
        # NO business logic - no threshold checks against requirements
        # Agent should call business rules tools for actual thresholds
        
        # Calculate borrower metrics (pure math, no business rules)
        monthly_income_calc = annual_income / 12 if annual_income > 0 else 0
        dti = (monthly_debts / monthly_income_calc) * 100 if monthly_income_calc > 0 else 0
        ltv = ((property_value - down_payment) / property_value) * 100 if property_value > 0 else 0
        down_payment_percent = (down_payment / property_value) * 100 if property_value > 0 else 0
        loan_amount = property_value - down_payment if property_value > 0 else 0

        # Check data completeness (operational, not business rules)
        data_completeness = []
        
        if credit_score > 0:
            data_completeness.append("✓ Credit Score: Provided")
        else:
            data_completeness.append("❌ Credit Score: Missing")
            
        if annual_income > 0:
            data_completeness.append("✓ Income: Provided")
        else:
            data_completeness.append("❌ Income: Missing")
            
        if property_value > 0:
            data_completeness.append("✓ Property Value: Provided")
        else:
            data_completeness.append("❌ Property Value: Missing")
            
        if down_payment > 0:
            data_completeness.append("✓ Down Payment: Provided")
        else:
            data_completeness.append("❌ Down Payment: Missing")
            
        if monthly_debts >= 0:
            data_completeness.append("✓ Monthly Debts: Provided")
        else:
            data_completeness.append("❌ Monthly Debts: Missing")
        
        complete_count = sum(1 for item in data_completeness if item.startswith("✓"))
        total_count = len(data_completeness)

        # Generate data quality and metrics report (NO qualification decisions)
        analysis = [
            "APPLICATION DATA REVIEW & METRICS",
            "==================================================",
            "",
            f"📋 LOAN PROGRAM: {loan_program_name.upper()}",
            "",
            "📊 DATA COMPLETENESS CHECK:",
            ""
        ]
        
        analysis.extend(data_completeness)
        analysis.extend([
            "",
            f"Data Completeness: {complete_count}/{total_count} fields provided ({(complete_count/total_count)*100:.0f}%)",
            "",
            "📊 BORROWER PROFILE:",
            f"Credit Score: {credit_score if credit_score > 0 else 'Not provided'}",
            f"Annual Income: ${annual_income:,.2f}" if annual_income > 0 else "Annual Income: Not provided",
            f"Monthly Income: ${monthly_income_calc:,.2f}" if monthly_income_calc > 0 else "Monthly Income: Not provided",
            f"Monthly Debts: ${monthly_debts:,.2f}" if monthly_debts >= 0 else "Monthly Debts: Not provided",
            f"Property Value: ${property_value:,.2f}" if property_value > 0 else "Property Value: Not provided",
            f"Down Payment: ${down_payment:,.2f} ({down_payment_percent:.1f}%)" if down_payment > 0 else "Down Payment: Not provided",
            f"Loan Amount: ${loan_amount:,.2f}" if loan_amount > 0 else "Loan Amount: Not calculated",
            f"First-Time Buyer: {'Yes' if first_time_buyer else 'No'}",
            "",
            "📈 CALCULATED FINANCIAL METRICS (Informational):",
            f"Debt-to-Income Ratio (DTI): {dti:.2f}%" if dti > 0 else "DTI: Cannot calculate (missing income or debts)",
            f"Loan-to-Value Ratio (LTV): {ltv:.2f}%" if ltv > 0 else "LTV: Cannot calculate (missing property value or down payment)",
            "",
            "📝 TO CHECK ACTUAL QUALIFICATION REQUIREMENTS:",
            "",
            f"1. Use get_loan_program_requirements('{loan_program_name}') to see specific requirements",
            "2. Use get_qualification_criteria tool to see what lenders evaluate",
            "3. Use get_underwriting_rules tool to see credit/DTI/LTV thresholds",
            "",
            "⚠️ IMPORTANT:",
            "This tool shows your data completeness and calculated metrics.",
            "It does NOT check against qualification thresholds or make eligibility decisions.",
            "Use business rules tools above to get actual requirements and check qualification."
        ])

        return "\n".join(analysis)

    except Exception as e:
        logger.error(f"Error during qualification requirements check: {e}")
        return f" Error during qualification requirements check: {str(e)}"


def validate_tool() -> bool:
    """Validate that the check_qualification_requirements tool works correctly."""
    try:
        test_data = {
            "loan_purpose": "FHA",
            "credit_score": 680,
            "annual_income": 70000,
            "monthly_debts": 1000,
            "down_payment": 15000,
            "property_value": 200000,
            "first_time_buyer": True
        }
        result = check_qualification_requirements.invoke({"application_data": test_data})
        return "APPLICATION DATA REVIEW & METRICS" in result and "FHA" in result
    except Exception as e:
        print(f"Check qualification requirements tool validation failed: {e}")
        return False
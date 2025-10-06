"""
Financial Metrics Calculation Tool - Application Agent

This tool calculates basic financial metrics (DTI, LTV, down payment %) from application data.
It does NOT make qualification decisions or enforce business rules - it's purely informational.
Qualification decisions are handled by MortgageAdvisorAgent and UnderwritingAgent.
"""

import logging
from langchain_core.tools import tool
from typing import Dict, Any, List, Optional

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def perform_initial_qualification(application_data) -> str:
    """Calculate basic financial metrics for mortgage application assessment.
    
    This tool calculates key financial ratios (DTI, LTV, down payment %) from application data.
    It does NOT make qualification decisions - those are handled by other agents.
    
    Args:
        application_data: Dict containing application info. May include:
            - credit_score, monthly_income, annual_income, monthly_debts
            - loan_amount, property_value, down_payment, loan_purpose
            - employment_type, years_employed, first_time_buyer
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing calculated financial metrics
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

        # Extract key parameters from flexible dict data
        credit_score = application_data.get("credit_score", 650)
        monthly_income = application_data.get("monthly_income", 0.0)
        annual_income = application_data.get("annual_income", (monthly_income * 12 if monthly_income else 0.0))
        monthly_debts = application_data.get("monthly_debts", 0.0)
        loan_amount = application_data.get("loan_amount")
        property_value = application_data.get("property_value", 0.0)
        down_payment = application_data.get("down_payment")
        loan_purpose = application_data.get("loan_purpose", "purchase")
        employment_type = application_data.get("employment_type", "w2")
        years_employed = application_data.get("years_employed")
        first_time_buyer = application_data.get("first_time_buyer", False)

        # Smart defaults: If loan_amount not provided, assume 80% LTV (typical)
        if loan_amount is None and property_value > 0:
            loan_amount = property_value * 0.8
        elif loan_amount is None:
            loan_amount = 0.0
            
        # Smart defaults: If down_payment not provided, calculate from loan_amount
        if down_payment is None and property_value > 0 and loan_amount > 0:
            down_payment = property_value - loan_amount
        elif down_payment is None:
            down_payment = 0.0

        # Calculate key ratios (pure math, no business rules)
        ltv = (loan_amount / property_value) * 100 if property_value > 0 else 0
        dti = ((monthly_debts + (loan_amount * 0.005)) / monthly_income) * 100 if monthly_income > 0 else 0  # Mock P&I
        down_payment_percent = (down_payment / property_value) * 100 if property_value > 0 else 0

        # Generate financial metrics report (NO qualification judgments)
        qualification_report = [
            "FINANCIAL METRICS CALCULATION",
            "==================================================",
            "",
            "📋 BORROWER PROFILE:",
            f"Credit Score: {credit_score}",
            f"Monthly Income: ${monthly_income:,.2f}",
            f"Annual Income: ${annual_income:,.2f}",
            f"Monthly Debts: ${monthly_debts:,.2f}",
            f"Loan Amount: ${loan_amount:,.2f}",
            f"Property Value: ${property_value:,.2f}",
            f"Down Payment: ${down_payment:,.2f} ({down_payment_percent:.1f}%)",
            f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
            f"Employment Type: {employment_type.upper()}",
            f"Years Employed: {years_employed if years_employed is not None else 'Not provided'}",
            f"First-Time Buyer: {'Yes' if first_time_buyer else 'No'}",
            "",
            "📊 CALCULATED METRICS:",
            f"Loan-to-Value (LTV): {ltv:.2f}%",
            f"Debt-to-Income (DTI): {dti:.2f}%",
            "",
            "ℹ️ NOTE:",
            "These are informational metrics only. For qualification decisions and",
            "loan program recommendations, consult with the Mortgage Advisor Agent",
            "or Business Rules Agent for specific program requirements.",
            "",
            "✅ METRICS CALCULATION COMPLETE"
        ]
        
        return "\n".join(qualification_report)
        
    except Exception as e:
        logger.error(f"Error during initial qualification: {e}")
        return f" Error during initial qualification: {str(e)}"


def validate_tool() -> bool:
    """Validate that the perform_initial_qualification tool works correctly."""
    try:
        test_data = {
            "first_name": "John",
            "last_name": "Doe",
            "credit_score": 720,
            "loan_amount": 300000.0,
            "property_value": 400000.0,
            "down_payment": 100000.0,
            "monthly_income": 5000.0,
            "monthly_debts": 1000.0,
            "loan_purpose": "purchase"
        }
        result = perform_initial_qualification.invoke({"application_data": test_data})
        return "FINANCIAL METRICS CALCULATION" in result and "CALCULATED METRICS" in result
    except Exception as e:
        print(f"Perform initial qualification tool validation failed: {e}")
        return False
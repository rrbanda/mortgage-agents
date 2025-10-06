"""
Application Completeness Check Tool - Application Agent

This tool verifies that all required fields are present in a mortgage application.
It checks basic required fields and reports what's complete vs. missing.
For loan-program-specific requirements, use get_application_intake_rules via BusinessRulesAgent.
"""

import logging
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional

# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)


@tool
def check_application_completeness(application_data) -> str:
    """Check if all basic required fields are present in mortgage application.
    
    This tool verifies that all core required fields are present. It checks:
    - Personal info, Address, Employment, Financial, Loan/Property details
    
    For loan-program-specific requirements (e.g., FHA vs. Conventional), 
    consult with BusinessRulesAgent using get_application_intake_rules().
    
    Args:
        application_data: Dict containing application info. May include:
            - application_id, loan_purpose, employment_type, property_type, occupancy_type
            - first_name, last_name, ssn, date_of_birth, phone, email
            - current_street, current_city, current_state, current_zip
            - employer_name, job_title, years_employed, monthly_income, annual_income
            - credit_score, monthly_debts, liquid_assets
            - loan_amount, property_value, down_payment, property_address
            (All fields optional - tool checks what's available)
        
    Returns:
        String containing completeness analysis and missing fields
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

        # Extract data from flexible dict input
        application_id = application_data.get("application_id", "TEMP_CHECK")
        loan_purpose = application_data.get("loan_purpose", "purchase")
        employment_type = application_data.get("employment_type", "w2")
        property_type = application_data.get("property_type", "single_family_detached")
        occupancy_type = application_data.get("occupancy_type", "primary_residence")

        # Enhanced boolean flag detection from structured data
        has_co_borrower = False  # Would need separate tracking in real system

        # Documentation status - check if required fields are present
        personal_info_complete = bool(application_data.get("first_name") and application_data.get("last_name") and
                                    application_data.get("ssn") and application_data.get("date_of_birth") and
                                    application_data.get("phone") and application_data.get("email"))
        address_info_complete = bool(application_data.get("current_street") and application_data.get("current_city") and
                                     application_data.get("current_state") and application_data.get("current_zip"))
        employment_info_complete = bool(application_data.get("employer_name") and application_data.get("job_title") and
                                       application_data.get("years_employed") is not None and
                                       (application_data.get("monthly_income") is not None or application_data.get("annual_income") is not None))
        financial_info_complete = bool(application_data.get("credit_score") is not None and
                                      application_data.get("monthly_debts") is not None and
                                      application_data.get("liquid_assets") is not None)
        loan_info_complete = bool(application_data.get("loan_amount") is not None and application_data.get("loan_purpose") and
                                 application_data.get("property_value") is not None and application_data.get("down_payment") is not None and
                                 application_data.get("property_address") and application_data.get("property_type") and
                                 application_data.get("occupancy_type"))

        # Check for missing fields based on basic completeness checks
        missing_requirements = []
        
        if not personal_info_complete:
            missing_requirements.append("• Personal Information section is incomplete")
        if not address_info_complete:
            missing_requirements.append("• Address Information section is incomplete")
        if not employment_info_complete:
            missing_requirements.append("• Employment Information section is incomplete")
        if not financial_info_complete:
            missing_requirements.append("• Financial Information section is incomplete")
        if not loan_info_complete:
            missing_requirements.append("• Loan & Property Information section is incomplete")

        # Generate completeness report
        completeness_report = [
            "APPLICATION COMPLETENESS ANALYSIS",
            "==================================================",
            "",
            "📋 APPLICATION DETAILS:",
            f"Application ID: {application_id}",
            f"Loan Purpose: {loan_purpose.title()}",
            f"Employment Type: {employment_type.upper()}",
            f"Property Type: {property_type.replace('_', ' ').title()}",
            f"Occupancy Type: {occupancy_type.replace('_', ' ').title()}",
            f"Has Co-Borrower: {'Yes' if has_co_borrower else 'No'}",
            "",
            "✅ DATA SECTIONS COMPLETENESS:",
            f"Personal Information: {'COMPLETE' if personal_info_complete else 'INCOMPLETE'}",
            f"Address Information: {'COMPLETE' if address_info_complete else 'INCOMPLETE'}",
            f"Employment Information: {'COMPLETE' if employment_info_complete else 'INCOMPLETE'}",
            f"Financial Information: {'COMPLETE' if financial_info_complete else 'INCOMPLETE'}",
            f"Loan & Property Information: {'COMPLETE' if loan_info_complete else 'INCOMPLETE'}",
            ""
        ]

        if missing_requirements:
            completeness_report.append("❌ MISSING REQUIRED INFORMATION:")
            completeness_report.extend(missing_requirements)
            completeness_report.append("\nACTION: Request the customer to provide the missing information.")
            completeness_report.append("STATUS: INCOMPLETE")
        else:
            completeness_report.append("🎉 ALL BASIC REQUIRED FIELDS ARE PRESENT!")
            completeness_report.append("STATUS: COMPLETE (BASIC FIELDS)")
        
        completeness_report.append("")
        completeness_report.append("ℹ️ NOTE:")
        completeness_report.append("This checks basic required fields only. For loan-program-specific")
        completeness_report.append("requirements (e.g., FHA vs. Conventional), consult BusinessRulesAgent")
        completeness_report.append("using get_application_intake_rules().")

        return "\n".join(completeness_report)

    except Exception as e:
        logger.error(f"Error during completeness check: {e}")
        return f" Error during completeness check: {str(e)}"


def validate_tool() -> bool:
    """Validate that the check_application_completeness tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_20240101_123456_SMI",
            "first_name": "John",
            "last_name": "Smith",
            "ssn": "123-45-6789",
            "date_of_birth": "1985-01-15",
            "phone": "555-123-4567",
            "email": "john.smith@example.com",
            "current_street": "123 Main St",
            "current_city": "Anytown",
            "current_state": "CA",
            "current_zip": "90210",
            "employer_name": "Tech Corp",
            "job_title": "Software Engineer",
            "years_employed": 4.0,
            "monthly_income": 8000.0,
            "credit_score": 720,
            "monthly_debts": 1200.0,
            "liquid_assets": 75000.0,
            "loan_amount": 400000.0,
            "loan_purpose": "purchase",
            "property_value": 500000.0,
            "down_payment": 100000.0,
            "property_address": "456 Oak Ave, Anytown, CA 90210",
            "property_type": "single_family_detached",
            "occupancy_type": "primary_residence"
        }
        result = check_application_completeness.invoke({"application_data": test_data})
        return "APPLICATION COMPLETENESS ANALYSIS" in result and "STATUS: COMPLETE" in result
    except Exception as e:
        print(f"Check application completeness tool validation failed: {e}")
        return False
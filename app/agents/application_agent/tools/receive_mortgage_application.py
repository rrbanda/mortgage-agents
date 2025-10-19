"""
Mortgage Application Intake Tool - Agentic Business Rules Integration

This tool handles the initial receipt and validation of mortgage applications
using the intelligent Rule Engine that validates and caches business rules from Neo4j.
This demonstrates the agentic pattern where tools become intelligent consumers of
validated business rules. Enhanced with agentic application storage.
"""

import logging
import re
from langchain_core.tools import tool
from datetime import datetime

# MortgageInput schema removed - using flexible dict approach
from utils import (
    get_neo4j_connection,
    initialize_connection,
    store_application_data,
    MortgageApplicationData
)

logger = logging.getLogger(__name__)


def normalize_for_api(data: dict) -> dict:
    """
    Normalize data formats for external API submission.
    Called ONLY when submitting to external systems.
    """
    normalized = {}
    
    # Phone: clean to digits only
    if phone := data.get("phone"):
        normalized["phone"] = re.sub(r'[^\d]', '', str(phone))
    
    # SSN: clean to digits only  
    if ssn := data.get("ssn"):
        normalized["ssn"] = re.sub(r'[^\d]', '', str(ssn))
    
    # Email: lowercase
    if email := data.get("email"):
        normalized["email"] = email.lower()
    
    # Date: try to standardize
    if dob := data.get("date_of_birth"):
        normalized["date_of_birth"] = standardize_date(dob)
    
    # Numbers: convert and validate
    for field in ['monthly_income', 'credit_score', 'loan_amount', 'property_value', 'down_payment', 'monthly_debts', 'liquid_assets']:
        if val := data.get(field):
            try:
                normalized[field] = float(val)
            except:
                pass
    
    # Copy other fields as-is
    for key, val in data.items():
        if key not in normalized and val:
            normalized[key] = val
    
    return normalized


def standardize_date(date_str: str) -> str:
    """Best effort date standardization to YYYY-MM-DD"""
    
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%B %d, %Y', '%b %d, %Y']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(str(date_str), fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    return str(date_str)  # Return original if can't parse


@tool
def receive_mortgage_application(application_data) -> str:
    """Process complete mortgage application with customer data.
    
    This tool should be called when you have collected comprehensive information from the customer
    to submit a complete mortgage application. The tool receives flexible application data.
    
    Args:
        application_data: Dict containing application info. May include:
            - first_name, last_name, middle_name
            - phone, email, ssn, date_of_birth
            - monthly_income, credit_score
            - loan_amount, property_value, property_address
            - employer_name, job_title
            (All fields optional - tool extracts what's available)
        
    Returns:
        String containing application processing results and next steps
    """
    try:
        # Handle both dict and string inputs (for LLM compatibility)
        if isinstance(application_data, str):
            # Try to parse string representation of dict
            try:
                import ast
                application_data = ast.literal_eval(application_data)
            except:
                # If parsing fails, create a basic dict from the string
                application_data = {"raw_input": application_data}
        
        # Ensure we have a dict
        if not isinstance(application_data, dict):
            application_data = {"raw_input": str(application_data)}
        
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract all parameters from flexible dict data
        first_name = application_data.get("first_name", "")
        last_name = application_data.get("last_name", "")
        ssn = application_data.get("ssn", "")
        date_of_birth = application_data.get("date_of_birth", "")
        phone = application_data.get("phone", "")
        email = application_data.get("email", "")
        current_street = application_data.get("current_street", "")
        current_city = application_data.get("current_city", "")
        current_state = application_data.get("current_state", "")
        current_zip = application_data.get("current_zip", "")
        years_at_address = application_data.get("years_at_address", 0.0)
        employer_name = application_data.get("employer_name", "")
        job_title = application_data.get("job_title", "")
        years_employed = application_data.get("years_employed", 0.0)
        monthly_income = application_data.get("monthly_income", 0.0)
        annual_income = application_data.get("annual_income", 0.0)
        loan_amount = application_data.get("loan_amount", 0.0)
        loan_purpose = application_data.get("loan_purpose", "purchase")
        property_address = application_data.get("property_address", "")
        property_value = application_data.get("property_value", 0.0)
        down_payment = application_data.get("down_payment", 0.0)
        middle_name = application_data.get("middle_name", "")
        credit_score = application_data.get("credit_score", 0)
        monthly_debts = application_data.get("monthly_debts", 0.0)
        first_time_buyer = application_data.get("first_time_buyer", False)
        application_id = application_data.get("application_id", f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{first_name[:3].upper()}")

        # Check for missing required information (conversational approach)
        missing = []
        if not first_name: missing.append("First name")
        if not last_name: missing.append("Last name")
        if not ssn: missing.append("Social Security Number")
        if not date_of_birth: missing.append("Date of birth")
        if not phone: missing.append("Phone number")
        if not email: missing.append("Email address")
        if not current_street: missing.append("Current street address")
        if not current_city: missing.append("Current city")
        if not current_state: missing.append("Current state")
        if not current_zip: missing.append("Current ZIP code")
        if not employer_name: missing.append("Employer name")
        if not monthly_income and not annual_income: missing.append("Monthly or annual income")
        if not loan_amount: missing.append("Loan amount")
        if not property_value: missing.append("Property value")
        if not down_payment: missing.append("Down payment")

        if missing:
            return f"I still need: {', '.join(missing)}. Could you provide those?\n\n APPLICATION INTAKE COMPLETE - AWAITING ADDITIONAL INFORMATION"

        # Calculate LTV and DTI (simplified for this tool)
        ltv = (loan_amount / property_value) * 100 if property_value > 0 else 0
        dti = ((monthly_debts + (loan_amount * 0.005)) / monthly_income) * 100 if monthly_income > 0 else 0 # Mock P&I

        # Extract property details from property_address
        property_city = ""
        property_state = ""
        property_zip = ""
        
        if property_address:
            # Parse property address to extract city, state, zip
            # Format: "789 Oak Street, Denver, CO 80202"
            address_parts = property_address.split(',')
            if len(address_parts) >= 3:
                property_city = address_parts[1].strip()
                state_zip = address_parts[2].strip().split()
                if len(state_zip) >= 2:
                    property_state = state_zip[0]
                    property_zip = state_zip[1]
        
        # Normalize data for Neo4j storage (format normalization only)
        normalize_for_api(application_data)
        
        # Store application data in Neo4j
        application_data = MortgageApplicationData(
            application_id=application_id,
            received_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            current_status="SUBMITTED",
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            ssn=ssn,
            date_of_birth=date_of_birth,
            phone=phone,
            email=email,
            current_street=current_street,
            current_city=current_city,
            current_state=current_state,
            current_zip=current_zip,
            years_at_address=years_at_address,
            employer_name=employer_name,
            job_title=job_title,
            years_employed=years_employed,
            monthly_income=monthly_income,
            annual_income=annual_income,
            loan_purpose=loan_purpose,
            requested_amount=loan_amount,  # Map loan_amount to requested_amount
            property_address=property_address,
            property_city=property_city,
            property_state=property_state,
            property_zip=property_zip,
            property_value=property_value,
            down_payment=down_payment,
            monthly_debt_payments=monthly_debts,  # Map monthly_debts to monthly_debt_payments
            credit_score=credit_score,
            first_time_buyer=first_time_buyer
        )

        store_application_data(application_data)
        logger.info(f"Application {application_id} stored successfully.")

        # Generate a comprehensive intake report
        intake_report = [
            "MORTGAGE APPLICATION INTAKE REPORT",
            "==================================================",
            "",
            "📋 APPLICATION SUMMARY:",
            f"Application ID: {application_id}",
            f"Borrower: {first_name} {last_name}",
            f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
            f"Loan Amount: ${loan_amount:,.2f}",
            f"Property Value: ${property_value:,.2f}",
            f"Down Payment: ${down_payment:,.2f} ({(down_payment/property_value*100):.1f}% of property value)" if property_value > 0 else f"Down Payment: ${down_payment:,.2f}",
            f"Credit Score: {credit_score}",
            f"Estimated LTV: {ltv:.2f}%",
            f"Estimated DTI: {dti:.2f}%",
            f"Application Status: SUBMITTED",
            "",
            "📝 NEXT STEPS:",
            "1. ✅ Application SUBMITTED successfully",
            "",
            "🎯 READY FOR DOCUMENT COLLECTION:",
            '   To continue, you can say:',
            '   • "What documents do I need?"',
            '   • "Show me the document requirements"',
            '   • "Start document collection"',
            "",
            "📍 FULL WORKFLOW:",
            "   Current: SUBMITTED ✅",
            "   Next: DOCUMENT_COLLECTION → CREDIT_REVIEW → APPRAISAL_ORDERED → UNDERWRITING"
        ]

        # Add a warning if credit score was not provided
        if credit_score == 0:
            intake_report.append("\n⚠️ NOTE: Credit score not provided. Agent may call credit check MCP tools if needed for qualification.")

        # Add completion signal to prevent ReAct agent from calling again
        intake_report.append("\n APPLICATION INTAKE COMPLETE - NO FURTHER ACTION NEEDED")
        intake_report.append("This mortgage application has been successfully received and processed.")

        return "\n".join(intake_report)

    except Exception as e:
        logger.error(f"Error during application intake: {e}")
        return f" Error during application intake: {str(e)}"


def validate_tool() -> bool:
    """Validate that the receive_mortgage_application tool works correctly."""
    try:
        test_data = {
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
            "years_at_address": 5.0,
            "employer_name": "Tech Solutions Inc.",
            "job_title": "Software Engineer",
            "years_employed": 7.0,
            "monthly_income": 8000.0,
            "annual_income": 96000.0,
            "employment_type": "w2",
            "loan_amount": 300000.0,
            "loan_purpose": "purchase",
            "property_address": "123 Main St, Anytown, CA 90210",
            "property_value": 400000.0,
            "down_payment": 100000.0,
            "property_type": "single_family_detached",
            "occupancy_type": "primary_residence",
            "credit_score": 740,
            "monthly_debts": 1000.0,
            "liquid_assets": 50000.0,
            "first_time_buyer": True
        }
        result = receive_mortgage_application.invoke({"application_data": test_data})
        return "MORTGAGE APPLICATION INTAKE REPORT" in result and "APPLICATION STATUS" in result
    except Exception as e:
        print(f"Receive mortgage application tool validation failed: {e}")
        return False
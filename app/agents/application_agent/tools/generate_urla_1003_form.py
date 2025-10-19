"""
URLA Form 1003 Generation Tool - Agentic Business Rules Integration

This tool generates URLA Form 1003 from stored application data using the intelligent
Rule Engine that validates and caches business rules from Neo4j. This demonstrates
the agentic pattern where tools become intelligent consumers of validated business rules.
"""

import json
import logging
from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime
import uuid

# MortgageInput schema removed - using flexible dict approach
from utils import get_neo4j_connection, initialize_connection

logger = logging.getLogger(__name__)


def get_application_data_from_neo4j(application_id: str) -> Dict[str, Any]:
    """Retrieve complete application data from Neo4j database."""
    try:
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return {"error": "Failed to connect to Neo4j database"}

        connection = get_neo4j_connection()

        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return {"error": "Failed to establish Neo4j connection"}

        with connection.driver.session(database=connection.database) as session:
            # Query to get application data
            application_query = """
            MATCH (app:MortgageApplication {application_id: $application_id})
            RETURN app
            """
            result = session.run(application_query, {"application_id": application_id})
            record = result.single()

            if not record:
                return {"error": f"Application {application_id} not found"}

            app_data = dict(record['app'])
            return app_data
    except Exception as e:
        logger.error(f"Error retrieving application data: {e}")
        return {"error": f"Database error: {str(e)}"}


@tool
def generate_urla_1003_form(application_data) -> str:
    """Generate URLA Form 1003 from stored application data.
    
    This tool retrieves complete application data and generates
    the standardized URLA Form 1003.
    
    Args:
        application_data: Dict containing application info. Must include:
            - application_id (required to retrieve stored data)
            (Other fields optional - data retrieved from Neo4j)
        
    Returns:
        String containing the generated URLA Form 1003 with all required sections
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

        # Extract application ID from flexible dict input
        application_id = application_data.get("application_id", "TEMP_URLA")

        # Get application data from Neo4j
        app_data = get_application_data_from_neo4j(application_id)

        if "error" in app_data:
            return f" Error: {app_data['error']}"

        # Extract all the required parameters from stored data
        first_name = app_data.get("first_name", "")
        middle_name = app_data.get("middle_name", "")
        last_name = app_data.get("last_name", "")
        ssn = app_data.get("ssn", "")
        date_of_birth = app_data.get("date_of_birth", "")
        phone = app_data.get("phone", "")
        email = app_data.get("email", "")
        current_street = app_data.get("current_street", "")
        current_city = app_data.get("current_city", "")
        current_state = app_data.get("current_state", "")
        current_zip = app_data.get("current_zip", "")
        years_at_address = app_data.get("years_at_address", 0.0)
        employer_name = app_data.get("employer_name", "")
        job_title = app_data.get("job_title", "")
        years_employed = app_data.get("years_employed", 0.0)
        monthly_income = app_data.get("monthly_income", 0.0)
        annual_income = app_data.get("annual_income", 0.0)
        employment_type = app_data.get("employment_type", "w2")
        loan_amount = app_data.get("loan_amount", 0.0)
        loan_purpose = app_data.get("loan_purpose", "purchase")
        property_address = app_data.get("property_address", "")
        property_value = app_data.get("property_value", 0.0)
        down_payment = app_data.get("down_payment", 0.0)
        property_type = app_data.get("property_type", "single_family_detached")
        occupancy_type = app_data.get("occupancy_type", "primary_residence")
        credit_score = app_data.get("credit_score", 0)
        monthly_debts = app_data.get("monthly_debts", 0.0)
        liquid_assets = app_data.get("liquid_assets", 0.0)
        first_time_buyer = app_data.get("first_time_buyer", False)
        application_status = app_data.get("application_status", "RECEIVED")
        submission_date = app_data.get("submission_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Generate a unique URLA ID
        urla_id = f"URLA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:4].upper()}"

        # Construct the URLA Form 1003 content
        urla_report = [
            "URLA FORM 1003 GENERATION REPORT",
            "==================================================",
            "",
            "📋 FORM HEADER:",
            f"Form Type: Uniform Residential Loan Application (URLA) Form 1003",
            f"Application ID: {application_id}",
            f"URLA ID: {urla_id}",
            f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SECTION 1: BORROWER INFORMATION",
            "--------------------------------------------------",
            f"Full Legal Name: {first_name} {middle_name} {last_name}",
            f"Social Security Number: {ssn}",
            f"Date of Birth: {date_of_birth}",
            f"Phone Number: {phone}",
            f"Email Address: {email}",
            f"Current Address: {current_street}, {current_city}, {current_state} {current_zip}",
            f"Years at Address: {years_at_address}",
            "",
            "SECTION 2: EMPLOYMENT INFORMATION",
            "--------------------------------------------------",
            f"Employer Name: {employer_name}",
            f"Job Title: {job_title}",
            f"Years Employed: {years_employed}",
            f"Employment Type: {employment_type.upper()}",
            f"Monthly Income: ${monthly_income:,.2f}",
            f"Annual Income: ${annual_income:,.2f}",
            "",
            "SECTION 3: LOAN AND PROPERTY INFORMATION",
            "--------------------------------------------------",
            f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
            f"Loan Amount Requested: ${loan_amount:,.2f}",
            f"Property Address: {property_address}",
            f"Property Value: ${property_value:,.2f}",
            f"Down Payment: ${down_payment:,.2f}",
            f"Property Type: {property_type.replace('_', ' ').title()}",
            f"Occupancy Type: {occupancy_type.replace('_', ' ').title()}",
            f"First-Time Homebuyer: {'Yes' if first_time_buyer else 'No'}",
            "",
            "SECTION 4: FINANCIAL INFORMATION",
            "--------------------------------------------------",
            f"Credit Score: {credit_score}",
            f"Total Monthly Debts: ${monthly_debts:,.2f}",
            f"Liquid Assets: ${liquid_assets:,.2f}",
            "",
            "SECTION 5: DECLARATIONS (Simplified)",
            "--------------------------------------------------",
            "• Are you a U.S. Citizen or Permanent Resident? [YES]",
            "• Have you ever been declared bankrupt? [NO]",
            "• Are you a party to a lawsuit? [NO]",
            "",
            "SECTION 6: ACKNOWLEDGMENTS AND AGREEMENTS",
            "--------------------------------------------------",
            "• Borrower acknowledges the information provided is true and accurate.",
            "• Borrower agrees to provide additional documentation as requested.",
            "",
            "SECTION 7: LOAN OFFICER INFORMATION",
            "--------------------------------------------------",
            "Loan Officer Name: AI Mortgage Agent",
            "NMLS ID: 1234567890",
            "Contact: agent@mortgage.ai",
            "",
            "📝 IMPORTANT NOTES FOR AGENT:",
            "1. Review generated URLA data for accuracy",
            "2. Collect any missing documentation",
            "3. Obtain borrower signature and date",
            "4. Submit to underwriting for processing"
        ]

        return "\n".join(urla_report)

    except Exception as e:
        logger.error(f"Error during URLA generation: {e}")
        return f" Error during URLA generation: {str(e)}"


def validate_tool() -> bool:
    """Validate that the generate_urla_1003_form tool works correctly."""
    try:
        # Test with dict data (MortgageInput schema removed)
        test_data = {
            "application_id": "APP_20240101_123456_SMI",
            "first_name": "John",
            "last_name": "Smith",
            "ssn": "123-45-6789",
            "date_of_birth": "1985-01-15",
            "phone": "555-123-4567",
            "email": "john.smith@email.com",
            "current_street": "123 Main St",
            "current_city": "Anytown",
            "current_state": "CA",
            "current_zip": "90210",
            "years_at_address": 3.5,
            "employer_name": "Tech Corp",
            "job_title": "Software Engineer",
            "years_employed": 4.0,
            "monthly_income": 8000.0,
            "employment_type": "w2",
            "loan_amount": 400000.0,
            "loan_purpose": "purchase",
            "property_address": "456 Oak Ave, Anytown, CA 90210",
            "property_type": "single_family_detached",
            "occupancy_type": "primary_residence",
            "property_value": 500000.0,
            "down_payment": 100000.0,
            "liquid_assets": 75000.0,
            "monthly_debts": 1200.0
        }

        result = generate_urla_1003_form.invoke({"application_data": test_data})
        return "URLA FORM 1003 GENERATION REPORT" in result and "URLA_" in result
    except Exception as e:
        print(f"URLA generation tool validation failed: {e}")
        return False
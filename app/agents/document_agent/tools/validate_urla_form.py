"""Validate URLA Form Tool - Neo4j Powered"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

# Configure logging
logger = logging.getLogger(__name__)



@tool
def validate_urla_form(application_data: dict) -> str:
    """Validate URLA Form 1003 for completeness and accuracy.
    
    This tool validates the URLA Form 1003 against business rules from Neo4j.
    
    Args:
        parsed_data: Pre-validated MortgageInput object with structured borrower data
        
    Returns:
        String containing URLA form validation results and recommendations
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract relevant data from application_data for validation
        application_id = application_data.get('application_id', "UNKNOWN_APP")
        first_name = application_data.get('first_name', '')
        last_name = application_data.get('last_name', '')
        borrower_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Unknown Borrower"

        # ARCHITECTURE: This tool provides basic document processing
        # For detailed business rules and specific document requirements, 
        # users should ask business rules questions which will be routed to BusinessRulesAgent
        
        # Use basic document processing logic without business rules queries
        validation_rules = []

        # If no rules found, use default URLA validation rules
        if not validation_rules:
            validation_rules = [
                {"section": "Borrower Information", "field": "first_name", "requirement": "required", "validation_type": "text", "description": "Borrower first name is required"},
                {"section": "Borrower Information", "field": "last_name", "requirement": "required", "validation_type": "text", "description": "Borrower last name is required"},
                {"section": "Borrower Information", "field": "ssn", "requirement": "required", "validation_type": "ssn", "description": "Social Security Number is required"},
                {"section": "Borrower Information", "field": "date_of_birth", "requirement": "required", "validation_type": "date", "description": "Date of birth is required"},
                {"section": "Employment Information", "field": "employer_name", "requirement": "required", "validation_type": "text", "description": "Employer name is required"},
                {"section": "Employment Information", "field": "monthly_income", "requirement": "required", "validation_type": "currency", "description": "Monthly income is required"},
                {"section": "Loan Information", "field": "loan_amount", "requirement": "required", "validation_type": "currency", "description": "Loan amount is required"},
                {"section": "Loan Information", "field": "property_value", "requirement": "required", "validation_type": "currency", "description": "Property value is required"},
                {"section": "Loan Information", "field": "down_payment", "requirement": "required", "validation_type": "currency", "description": "Down payment is required"}
            ]

        # Perform validation
        validation_results = []
        passed_validations = 0
        total_validations = len(validation_rules)

        for rule in validation_rules:
            section = rule.get('section', 'Unknown')
            field = rule.get('field', 'unknown')
            requirement = rule.get('requirement', 'optional')
            validation_type = rule.get('validation_type', 'text')
            description = rule.get('description', 'No description')

            # Get field value from application_data (it's a dict, not an object)
            field_value = application_data.get(field, None)

            # Perform validation based on type
            is_valid = False
            validation_message = ""

            if requirement == "required":
                if field_value is not None and (not isinstance(field_value, str) or field_value.strip()):
                    if validation_type == "ssn":
                        # SSN validation
                        if isinstance(field_value, str) and len(field_value.replace('-', '')) == 9:
                            is_valid = True
                            validation_message = "Valid SSN format"
                        else:
                            validation_message = "Invalid SSN format"
                    elif validation_type == "date":
                        # Date validation
                        if isinstance(field_value, str) and len(field_value) == 10 and field_value.count('-') == 2:
                            is_valid = True
                            validation_message = "Valid date format"
                        else:
                            validation_message = "Invalid date format (YYYY-MM-DD required)"
                    elif validation_type == "currency":
                        # Currency validation - convert to float safely
                        try:
                            amount = float(field_value) if field_value else 0.0
                            if amount > 0:
                                is_valid = True
                                validation_message = f"Valid amount: ${amount:,.2f}"
                            else:
                                validation_message = "Amount must be greater than 0"
                        except (ValueError, TypeError):
                            validation_message = "Invalid or missing amount"
                    else:
                        # Text validation
                        if isinstance(field_value, str) and len(field_value.strip()) > 0:
                            is_valid = True
                            validation_message = f"Valid: {field_value}"
                        else:
                            validation_message = "Missing or empty text"
                else:
                    validation_message = "Required field is missing"
            else:
                # Optional field
                is_valid = True
                validation_message = "Optional field - not required"

            if is_valid:
                passed_validations += 1
                status_icon = "OK"
            else:
                status_icon = "MISSING"

            validation_results.append({
                "section": section,
                "field": field,
                "status": status_icon,
                "message": validation_message,
                "description": description
            })

        # Generate validation report
        report = [
            "URLA FORM 1003 VALIDATION REPORT",
            "==================================================",
            "",
            "📋 VALIDATION DETAILS:",
            f"Application ID: {application_id}",
            f"Borrower: {borrower_name}",
            f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Validations: {total_validations}",
            f"Passed Validations: {passed_validations}",
            f"Failed Validations: {total_validations - passed_validations}",
            f"Success Rate: {(passed_validations/total_validations*100):.1f}%",
            f"Architecture: Basic document processing (for detailed business rules, ask business rules questions)",
            ""
        ]

        # Group results by section
        sections = {}
        for result in validation_results:
            section = result['section']
            if section not in sections:
                sections[section] = []
            sections[section].append(result)

        # Add validation results by section
        for section, results in sections.items():
            report.append(f"📄 {section.upper()}:")
            for result in results:
                report.append(f"  {result['status']} {result['field'].replace('_', ' ').title()}: {result['message']}")
            report.append("")

        # Add overall validation status
        if passed_validations == total_validations:
            report.extend([
                "OVERALL STATUS: VALIDATION PASSED",
                "",
                "All required fields are present and valid",
                "URLA Form 1003 is ready for submission",
                "No corrections needed",
                "",
                "NEXT STEPS:",
                "1. Form is ready for borrower signature",
                "2. Submit to underwriting for review",
                "3. Proceed with loan processing"
            ])
        else:
            failed_count = total_validations - passed_validations
            report.extend([
                f"OVERALL STATUS: VALIDATION FAILED ({failed_count} issues found)",
                "",
                "Some required fields are missing or invalid",
                "URLA Form 1003 needs corrections",
                "Form cannot be submitted in current state",
                "",
                "CORRECTIVE ACTIONS REQUIRED:",
                "1. Review failed validations above",
                "2. Collect missing information from borrower",
                "3. Correct invalid data entries",
                "4. Re-validate form after corrections",
                "5. Ensure all required fields are complete"
            ])

        # Add compliance notes
        report.extend([
            "",
            "📋 COMPLIANCE NOTES:",
            "",
            "• URLA Form 1003 must be complete and accurate per CFPB requirements",
            "• All required fields must be filled out completely",
            "• Borrower must sign and date the form",
            "• Form must be submitted within required timeframes",
            "• Any corrections must be initialed by borrower",
            "",
            "📞 SUPPORT:",
            "",
            "• Contact compliance team for validation questions",
            "• Refer to CFPB guidelines for URLA requirements",
            "• Use loan officer for borrower assistance"
        ])

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error during URLA form validation: {e}")
        return f" Error during URLA form validation: {str(e)}"


def validate_tool() -> bool:
    """Validate that the validate_urla_form tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_12345",
            "first_name": "John",
            "last_name": "Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01",
            "employer_name": "Tech Corp",
            "monthly_income": 5000.0,
            "loan_amount": 300000.0,
            "property_value": 400000.0,
            "down_payment": 100000.0
        }
        result = validate_urla_form.invoke({"application_data": test_data})
        return "URLA FORM 1003 VALIDATION REPORT" in result and "VALIDATION PASSED" in result
    except Exception as e:
        print(f"Validate URLA form tool validation failed: {e}")
        return False
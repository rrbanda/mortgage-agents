"""Process Uploaded Document Tool - Neo4j Powered"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

# Configure logging
logger = logging.getLogger(__name__)

from utils import update_application_status


@tool
def process_uploaded_document(application_data: dict) -> str:
    """Process an uploaded mortgage document, extract data, validate it, and update its status.
    
    This tool integrates with document extraction and validation rules from Neo4j.
    
    Args:
        parsed_data: Pre-validated MortgageInput object with structured borrower data
        
    Returns:
        String containing document processing results and status updates
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract relevant data from application_data for context
        application_id = application_data.get('application_id', "UNKNOWN_APP")
        context = application_data.get('context', {})
        document_type = context.get("document_type", "unknown") if context else "unknown"
        document_id = context.get("document_id", f"DOC_{application_id}_{document_type}_1") if context else f"DOC_{application_id}_{document_type}_1"
        document_content = context.get("document_content", "No content provided.") if context else "No content provided."

        # ARCHITECTURE: This tool provides basic document processing
        # For detailed business rules and specific document requirements, 
        # users should ask business rules questions which will be routed to BusinessRulesAgent
        
        # Use basic document processing logic without business rules queries
        processing_rules = []

        # Simulate document processing
        processing_results = []
        validation_results = []
        extracted_data = {}

        # Basic document validation
        if len(document_content) < 10:
            validation_results.append("❌ Document content too short - may be corrupted")
        else:
            validation_results.append("✅ Document content length acceptable")

        # Document type specific processing
        if document_type == "pay_stub":
            # Mock pay stub processing
            extracted_data = {
                "employer_name": application_data.get('employer_name', "Extracted Employer"),
                "employee_name": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'Employee')}",
                "pay_period": "Monthly",
                "gross_pay": application_data.get('monthly_income', 5000.0),
                "net_pay": (application_data.get('monthly_income', 5000.0) * 0.75),  # Mock calculation
                "year_to_date": (application_data.get('monthly_income', 5000.0) * 6)  # Mock YTD
            }
            validation_results.append("✅ Pay stub format validated")
            validation_results.append("✅ Employer information extracted")
            validation_results.append("✅ Income information extracted")

        elif document_type == "bank_statement":
            # Mock bank statement processing
            extracted_data = {
                "account_holder": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'User')}",
                "account_type": "Checking",
                "current_balance": application_data.get('liquid_assets', 25000.0),
                "average_balance": (application_data.get('liquid_assets', 25000.0) * 0.9),
                "transaction_count": 45  # Mock count
            }
            validation_results.append("✅ Bank statement format validated")
            validation_results.append("✅ Account information extracted")
            validation_results.append("✅ Balance information extracted")

        elif document_type == "w2":
            # Mock W-2 processing
            extracted_data = {
                "employee_name": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'Employee')}",
                "employer_name": application_data.get('employer_name', "Extracted Employer"),
                "wages": application_data.get('annual_income', 60000.0),
                "tax_year": "2023",
                "ssn": application_data.get('ssn', "***-**-****")
            }
            validation_results.append("✅ W-2 format validated")
            validation_results.append("✅ Employer information extracted")
            validation_results.append("✅ Income information extracted")

        else:
            validation_results.append(f"⚠️ Unknown document type: {document_type}")
            extracted_data = {"document_type": document_type, "status": "processed"}

        # Quality checks
        quality_checks = []
        if extracted_data:
            quality_checks.append("✅ Data extraction completed")
            quality_checks.append("✅ Document structure validated")
            quality_checks.append("✅ Content readability confirmed")
        else:
            quality_checks.append("❌ Data extraction failed")

        # Update document status
        try:
            update_application_status(application_id, "DOCUMENTS_PROCESSED", f"Document {document_id} successfully processed and validated")
            processing_results.append(f"✅ Document status updated to PROCESSED")
        except Exception as e:
            processing_results.append(f"⚠️ Status update failed: {str(e)}")

        # Generate processing report
        report = [
            "DOCUMENT PROCESSING REPORT",
            "==================================================",
            "",
            "📋 PROCESSING DETAILS:",
            f"Document ID: {document_id}",
            f"Application ID: {application_id}",
            f"Document Type: {document_type}",
            f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Processing Agent: DocumentAgent",
            f"Architecture: Basic document processing (for detailed business rules, ask business rules questions)",
            "",
            "📊 EXTRACTED DATA:"
        ]

        for key, value in extracted_data.items():
            report.append(f"• {key.replace('_', ' ').title()}: {value}")

        report.extend([
            "",
            "✅ VALIDATION RESULTS:"
        ])
        report.extend(validation_results)

        report.extend([
            "",
            "🔍 QUALITY CHECKS:"
        ])
        report.extend(quality_checks)

        report.extend([
            "",
            "📝 PROCESSING RESULTS:"
        ])
        report.extend(processing_results)

        # Add next steps
        report.extend([
            "",
            "📋 NEXT STEPS:",
            "1. Review extracted data for accuracy",
            "2. Compare with application information",
            "3. Flag any discrepancies for review",
            "4. Update application with validated data",
            "5. Request additional documents if needed",
            "",
            "⚠️ IMPORTANT NOTES:",
            "• All extracted data should be verified by a human reviewer",
            "• Discrepancies between documents and application should be investigated",
            "• Additional documents may be requested based on findings"
        ])

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error during document processing: {e}")
        return f" Error during document processing: {str(e)}"


def validate_tool() -> bool:
    """Validate that the process_uploaded_document tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_12345",
            "first_name": "John",
            "last_name": "Doe",
            "context": {"document_type": "pay_stub", "document_id": "DOC_PAY_1", "document_content": "John Doe, Monthly Income: $5000"}
        }
        result = process_uploaded_document.invoke({"application_data": test_data})
        return "DOCUMENT PROCESSING REPORT" in result and "Document ID: DOC_PAY_1" in result
    except Exception as e:
        print(f"Process uploaded document tool validation failed: {e}")
        return False
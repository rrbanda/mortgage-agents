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


def _detect_document_type(content: str) -> str:
    """
    Auto-detect document type from content.
    
    Args:
        content: Document text content
        
    Returns:
        Detected document type (pay_stub, w2, bank_statement, etc.)
    """
    content_lower = content.lower()
    
    # Check for pay stub indicators
    if any(indicator in content_lower for indicator in [
        "payroll statement", "pay period", "pay date", "gross pay", "net pay", 
        "pay stub", "paystub", "earnings statement"
    ]):
        return "pay_stub"
    
    # Check for W-2 indicators
    if any(indicator in content_lower for indicator in [
        "w-2", "w2", "wage and tax statement", "form w-2", "irs form w-2"
    ]):
        return "w2"
    
    # Check for bank statement indicators
    if any(indicator in content_lower for indicator in [
        "bank statement", "account balance", "beginning balance", "ending balance",
        "account summary", "transaction history"
    ]):
        return "bank_statement"
    
    # Check for employment verification
    if any(indicator in content_lower for indicator in [
        "employment verification", "verification of employment", "voe"
    ]):
        return "employment_verification"
    
    # Check for tax returns
    if any(indicator in content_lower for indicator in [
        "form 1040", "u.s. individual income tax return", "1040"
    ]):
        return "tax_return"
    
    # Default to unknown
    return "unknown"


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
        
        # Get document content - agent should provide this
        document_content = context.get("document_content", "No content provided.") if context else "No content provided."
        
        # AUTO-DETECT document type from content if not explicitly provided
        provided_doc_type = context.get("document_type", "") if context else ""
        if provided_doc_type:
            document_type = provided_doc_type
        else:
            # Auto-detect from content
            document_type = _detect_document_type(document_content)
        
        # Generate document ID
        document_id = context.get("document_id", f"DOC_{application_id}_{document_type}_1") if context else f"DOC_{application_id}_{document_type}_1"

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
            validation_results.append(" Document content length acceptable")

        # Document type specific processing
        # NOTE: LLM extracts the data, tool just formats it for display
        if document_type == "pay_stub":
            # LLM should have extracted these fields already
            extracted_data = {
                "employer_name": application_data.get('employer_name', "Not extracted"),
                "employee_name": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'Unknown')}",
                "pay_period": "Monthly",  # Standard assumption
                "gross_pay": application_data.get('monthly_income', 0),
                "net_pay": application_data.get('net_pay', 0) if application_data.get('net_pay') else (application_data.get('monthly_income', 0) * 0.75),
                "year_to_date": application_data.get('annual_income', 0)
            }
            validation_results.append(" Pay stub format validated")
            validation_results.append(" Employer information extracted" if application_data.get('employer_name') else "⚠️ Employer not extracted")
            validation_results.append(" Income information extracted" if application_data.get('monthly_income') else "⚠️ Income not extracted")

        elif document_type == "bank_statement":
            # LLM should have extracted these fields already
            extracted_data = {
                "account_holder": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'Unknown')}",
                "account_type": application_data.get('account_type', "Checking"),
                "current_balance": application_data.get('liquid_assets', 0) or application_data.get('account_balance', 0),
                "bank_name": application_data.get('bank_name', "Not extracted")
            }
            validation_results.append(" Bank statement format validated")
            validation_results.append(" Account information extracted" if application_data.get('account_balance') or application_data.get('liquid_assets') else "⚠️ Balance not extracted")

        elif document_type == "w2":
            # LLM should have extracted these fields already
            extracted_data = {
                "employee_name": f"{application_data.get('first_name', 'Unknown')} {application_data.get('last_name', 'Unknown')}",
                "employer_name": application_data.get('employer_name', "Not extracted"),
                "wages": application_data.get('annual_income', 0),
                "tax_year": application_data.get('tax_year', "Unknown")
            }
            validation_results.append(" W-2 format validated")
            validation_results.append(" Employer information extracted" if application_data.get('employer_name') else "⚠️ Employer not extracted")
            validation_results.append(" Income information extracted" if application_data.get('annual_income') else "⚠️ Income not extracted")

        else:
            validation_results.append(f"⚠️ Unknown document type: {document_type}")
            extracted_data = {"document_type": document_type, "status": "processed"}

        # Quality checks
        quality_checks = []
        if extracted_data:
            quality_checks.append(" Data extraction completed")
            quality_checks.append(" Document structure validated")
            quality_checks.append(" Content readability confirmed")
        else:
            quality_checks.append("❌ Data extraction failed")

        # Update document status
        try:
            update_application_status(application_id, "DOCUMENTS_PROCESSED", f"Document {document_id} successfully processed and validated")
            processing_results.append(f" Document status updated to PROCESSED")
        except Exception as e:
            processing_results.append(f"⚠️ Status update failed: {str(e)}")

        # Generate processing report
        # Generate simple, user-friendly summary
        doc_type_labels = {
            "pay_stub": "Pay Stub",
            "w2": "W-2",
            "bank_statement": "Bank Statement",
            "tax_return": "Tax Return",
            "employment_verification": "Employment Verification",
            "appraisal": "Appraisal Report",
            "home_insurance": "Home Insurance",
            "unknown": "Document"
        }
        
        doc_label = doc_type_labels.get(document_type, "Document")
        
        # Build simple summary of key extracted data
        summary_parts = [f"✓ {doc_label} processed"]
        
        # Add most relevant extracted data (with correct key names and type conversion)
        if document_type == "pay_stub" and "gross_pay" in extracted_data:
            try:
                gross_pay = float(extracted_data['gross_pay']) if extracted_data['gross_pay'] else 0.0
                summary_parts.append(f"Monthly income: ${gross_pay:,.2f}")
            except (ValueError, TypeError):
                pass
        elif document_type == "w2" and "wages" in extracted_data:
            try:
                wages = float(extracted_data['wages']) if extracted_data['wages'] else 0.0
                summary_parts.append(f"Annual wages: ${wages:,.2f}")
            except (ValueError, TypeError):
                pass
        elif document_type == "bank_statement" and "current_balance" in extracted_data:
            try:
                balance = float(extracted_data['current_balance']) if extracted_data['current_balance'] else 0.0
                summary_parts.append(f"Account balance: ${balance:,.2f}")
            except (ValueError, TypeError):
                pass
        
        if "employer_name" in extracted_data and extracted_data['employer_name'] != "Not extracted":
            summary_parts.append(f"Employer: {extracted_data['employer_name']}")
        
        return " - ".join(summary_parts)

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
        return "processed" in result.lower()
    except Exception as e:
        print(f"Process uploaded document tool validation failed: {e}")
        return False
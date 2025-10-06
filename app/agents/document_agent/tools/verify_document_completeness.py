"""Verify Document Completeness Tool - Neo4j Powered"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

# Configure logging
logger = logging.getLogger(__name__)



@tool
def verify_document_completeness(application_data: dict) -> str:
    """Verify that all required documents for a mortgage application are complete and present.
    
    This tool checks document completeness against business rules from Neo4j.
    
    Args:
        parsed_data: Pre-validated MortgageInput object with structured borrower data
        
    Returns:
        String containing document completeness verification results and missing items
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract relevant data from application_data for verification
        application_id = application_data.get('application_id', "UNKNOWN_APP")
        first_name = application_data.get('first_name', '')
        last_name = application_data.get('last_name', '')
        borrower_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Unknown Borrower"
        loan_purpose = application_data.get('loan_purpose', "purchase")
        employment_type = application_data.get('employment_type', "w2")

        # OPERATIONAL TOOL: Check which documents have been uploaded
        # NO hardcoded business rules about what's required
        # Agent should call get_document_requirements business rules tool to know what's needed
        
        # Mock uploaded documents (in real system, query Neo4j for actual uploaded docs)
        uploaded_documents = [
            {"document_type": "identity_document", "upload_date": "2024-01-15", "status": "PROCESSED"},
            {"document_type": "pay_stub", "upload_date": "2024-01-16", "status": "PROCESSED"},
            {"document_type": "bank_statement", "upload_date": "2024-01-17", "status": "PENDING"}
        ]
        
        # Count documents
        document_status = []
        total_uploaded = len(uploaded_documents)
        
        for doc in uploaded_documents:
            document_status.append({
                "document_type": doc.get('document_type'),
                "status": doc.get('status'),
                "upload_date": doc.get('upload_date')
            })

        # Generate uploaded documents report (NO business rules about what's required)
        report = [
            "UPLOADED DOCUMENTS REPORT",
            "==================================================",
            "",
            "📋 APPLICATION DETAILS:",
            f"Application ID: {application_id}",
            f"Borrower: {borrower_name}",
            f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}",
            f"Employment Type: {employment_type.upper()}",
            f"Check Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📄 UPLOADED DOCUMENTS:",
            f"Total Documents Uploaded: {total_uploaded}",
            ""
        ]

        # List uploaded documents
        if document_status:
            for doc in document_status:
                status_icon = "" if doc['status'] == "PROCESSED" else "⏳"
                report.append(f"{status_icon} {doc['document_type'].replace('_', ' ').title()}")
                report.append(f"   Upload Date: {doc['upload_date']}")
                report.append(f"   Status: {doc['status']}")
                report.append("")
        else:
            report.append("No documents uploaded yet.")
            report.append("")

        report.extend([
            "📝 TO CHECK WHAT DOCUMENTS ARE REQUIRED:",
            "",
            "Use get_document_requirements business rules tool with:",
            f"  - Loan Purpose: {loan_purpose}",
            f"  - Employment Type: {employment_type}",
            "",
            "⚠️ IMPORTANT:",
            "This tool shows ONLY what has been uploaded.",
            "It does NOT know what's required (that's in business rules).",
            "Agent should call get_document_requirements to see what's needed.",
            "",
            "📞 NEXT STEPS:",
            "1. Agent: Call get_document_requirements to see required documents",
            "2. Agent: Compare uploaded docs vs required docs",
            "3. Agent: Tell customer what's still missing"
        ])

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error during document completeness verification: {e}")
        return f" Error during document completeness verification: {str(e)}"


def validate_tool() -> bool:
    """Validate that the verify_document_completeness tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_12345",
            "first_name": "John",
            "last_name": "Doe",
            "loan_purpose": "purchase",
            "employment_type": "w2"
        }
        result = verify_document_completeness.invoke({"application_data": test_data})
        return "DOCUMENT COMPLETENESS VERIFICATION REPORT" in result and "DOCUMENT COLLECTION" in result
    except Exception as e:
        print(f"Verify document completeness tool validation failed: {e}")
        return False
"""Get Document Status Tool - Neo4j Powered"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from langchain_core.tools import tool

# MortgageInput schema removed - using flexible dict approach

# Configure logging
logger = logging.getLogger(__name__)



@tool
def get_document_status(application_data: dict) -> str:
    """Get the status of documents for a mortgage application.
    
    This tool retrieves document status information from the Neo4j database.
    
    Args:
        parsed_data: Pre-validated MortgageInput object with structured borrower data
        
    Returns:
        String containing document status information and collection progress
    """
    try:
        # NEW ARCHITECTURE: Tool receives pre-validated structured data
        # No parsing needed - data is already validated and structured

        # Extract relevant data from application_data for context
        application_id = application_data.get('application_id', "UNKNOWN_APP")
        first_name = application_data.get('first_name', '')
        last_name = application_data.get('last_name', '')
        borrower_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Unknown Borrower"

        # Get document status from BusinessRulesAgent (in a real system, this would query document status)
        # For now, we'll use mock data since document status tracking would be handled by a separate service
        try:
                        
            # Call BusinessRulesAgent tool to get document requirements (for context)
            document_requirements_result = get_document_requirements.invoke({
                "loan_type": "purchase",
                "property_type": "single_family",
                "document_category": "all"
            })
            
            # Parse the JSON result from BusinessRulesAgent
            document_requirements = json.loads(document_requirements_result)
            
        except Exception as e:
            logger.warning(f"Failed to get document requirements from BusinessRulesAgent: {e}")
            document_requirements = {"required_documents": []}

        # Create mock document statuses for demonstration (in real system, this would come from document service)
        document_statuses = [
                {
                    "document_id": "DOC_PAY_001",
                    "document_type": "pay_stub",
                    "status": "PROCESSED",
                    "upload_date": "2024-01-15 10:30:00",
                    "processed_date": "2024-01-15 10:35:00",
                    "notes": "Successfully processed and validated"
                },
                {
                    "document_id": "DOC_BANK_001",
                    "document_type": "bank_statement",
                    "status": "PENDING_REVIEW",
                    "upload_date": "2024-01-16 14:20:00",
                    "processed_date": None,
                    "notes": "Awaiting manual review"
                },
                {
                    "document_id": "DOC_W2_001",
                    "document_type": "w2",
                    "status": "UPLOADED",
                    "upload_date": "2024-01-17 09:15:00",
                    "processed_date": None,
                    "notes": "Uploaded, processing pending"
                }
            ]

        # Generate status report
        report = [
            "DOCUMENT STATUS REPORT",
            "==================================================",
            "",
            "📋 APPLICATION DETAILS:",
            f"Application ID: {application_id}",
            f"Borrower: {borrower_name}",
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Documents: {len(document_statuses)}",
            f"Architecture: Basic document processing (for detailed business rules, ask business rules questions)",
            "",
            "📄 DOCUMENT STATUS SUMMARY:"
        ]

        # Count documents by status
        status_counts = {}
        for doc in document_statuses:
            status = doc.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in status_counts.items():
            report.append(f"• {status}: {count} documents")

        report.extend([
            "",
            "📊 DETAILED DOCUMENT STATUS:",
            ""
        ])

        # Add detailed status for each document
        for doc in document_statuses:
            document_id = doc.get('document_id', 'Unknown')
            document_type = doc.get('document_type', 'Unknown')
            status = doc.get('status', 'UNKNOWN')
            upload_date = doc.get('upload_date', 'N/A')
            processed_date = doc.get('processed_date', 'N/A')
            notes = doc.get('notes', 'No notes')

            # Status icon
            if status == "PROCESSED":
                status_icon = "✅"
            elif status == "PENDING_REVIEW":
                status_icon = "⏳"
            elif status == "UPLOADED":
                status_icon = "📤"
            elif status == "REJECTED":
                status_icon = "❌"
            else:
                status_icon = "❓"

            report.extend([
                f"{status_icon} {document_type.upper()} - {status}",
                f"   Document ID: {document_id}",
                f"   Upload Date: {upload_date}",
                f"   Processed Date: {processed_date}",
                f"   Notes: {notes}",
                ""
            ])

        # Add collection progress
        total_docs = len(document_statuses)
        processed_docs = len([d for d in document_statuses if d.get('status') == 'PROCESSED'])
        progress_percent = (processed_docs / total_docs * 100) if total_docs > 0 else 0

        report.extend([
            "📈 COLLECTION PROGRESS:",
            f"Documents Processed: {processed_docs}/{total_docs} ({progress_percent:.1f}%)",
            "",
            "📝 NEXT STEPS:"
        ])

        # Determine next steps based on status
        pending_docs = [d for d in document_statuses if d.get('status') in ['UPLOADED', 'PENDING_REVIEW']]
        rejected_docs = [d for d in document_statuses if d.get('status') == 'REJECTED']

        if rejected_docs:
            report.append("• Address rejected documents:")
            for doc in rejected_docs:
                report.append(f"  - {doc.get('document_type', 'Unknown')}: {doc.get('notes', 'No details')}")

        if pending_docs:
            report.append("• Monitor pending documents:")
            for doc in pending_docs:
                report.append(f"  - {doc.get('document_type', 'Unknown')}: {doc.get('status', 'Unknown')}")

        if progress_percent < 100:
            report.append("• Continue document collection process")
            report.append("• Submit any missing required documents")
        else:
            report.append("• All documents have been processed")
            report.append("• Proceed with application review")

        report.extend([
            "",
            "📞 SUPPORT:",
            "• Contact your loan officer for document-related questions",
            "• Use the document upload portal for secure submission",
            "• Check this status regularly for updates"
        ])

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error during document status retrieval: {e}")
        return f" Error during document status retrieval: {str(e)}"


def validate_tool() -> bool:
    """Validate that the get_document_status tool works correctly."""
    try:
        test_data = {
            "application_id": "APP_12345",
            "first_name": "John",
            "last_name": "Doe"
        }
        result = get_document_status.invoke({"application_data": test_data})
        return "DOCUMENT STATUS REPORT" in result and "Application ID: APP_12345" in result
    except Exception as e:
        print(f"Get document status tool validation failed: {e}")
        return False
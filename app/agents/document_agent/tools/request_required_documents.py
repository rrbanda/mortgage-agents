"""
Request Required Documents Tool - Neo4j Powered

Gets document requirements from Neo4j business rules instead of hardcoded lists.
Uses Document Verification Rules to determine what documents are needed for specific loan programs.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

try:
    from utils import get_neo4j_connection, initialize_connection
except ImportError:
    from utils import get_neo4j_connection, initialize_connection


class DocumentRequestInput(BaseModel):
    """Schema for document request inputs"""
    application_id: str = Field(description="Unique identifier for the mortgage application")
    loan_program: Optional[str] = Field(description="Loan program type (FHA, VA, Conventional, etc.)", default=None)
    missing_documents: Optional[List[str]] = Field(description="Specific documents that are missing", default=None)


@tool
def request_required_documents(tool_input: str) -> str:
    """
    Generate document request for mortgage application using Neo4j business rules.
    
    Gets required documents from Document Verification Rules stored in Neo4j
    instead of using hardcoded document lists.
    
    Args:
        tool_input: Document request information in natural language format
        
    Example:
        "Application: APP_123, Loan program: FHA, Missing documents: paystub, w2, bank_statement"
    
    Returns:
        String containing document request details with submission instructions
    """
    
    try:
        # 12-FACTOR COMPLIANT: Enhanced parser only (Factor 8: Own Your Control Flow)
        from agents.shared.input_parser import parse_complete_mortgage_input
        
        # Factor 1: Natural Language → Tool Calls - comprehensive parsing
        parsed_data = parse_complete_mortgage_input(tool_input)
        input_lower = tool_input.lower()  # Keep for document extraction
        
        # Factor 4: Tools as Structured Outputs - safe parameter extraction
        application_id = parsed_data.get("application_id") or "APP_UNKNOWN"
        loan_program = parsed_data.get("loan_type")
        
        # Enhanced missing documents extraction (no regex - Factor 9: Compact Errors)
        missing_documents = None
        if 'missing documents:' in input_lower or 'missing document:' in input_lower:
            try:
                # Find the start position after "missing documents:"
                start_markers = ['missing documents:', 'missing document:']
                start_pos = -1
                for marker in start_markers:
                    if marker in input_lower:
                        start_pos = input_lower.find(marker) + len(marker)
                        break
                
                if start_pos > 0:
                    # Extract everything after the marker until end or next field
                    remaining_text = tool_input[start_pos:].strip()
                    # Split by comma and clean up
                    if ',' in remaining_text:
                        docs_part = remaining_text.split(',')[0] if remaining_text.count(',') == 1 else remaining_text
                        missing_documents = [doc.strip() for doc in docs_part.split(',') if doc.strip()]
                    else:
                        missing_documents = [remaining_text.strip()] if remaining_text.strip() else None
            except:
                missing_documents = None
        
        # Initialize database connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        # Get required documents from Neo4j business rules
        required_docs = _get_required_documents_from_rules(connection, loan_program)
        
        # Use specific missing documents if provided, otherwise use all required
        final_docs = missing_documents if missing_documents else required_docs
        
        # Generate request ID and deadline
        request_id = f"DOC_REQ_{uuid.uuid4().hex[:8].upper()}"
        deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Store document request in Neo4j
        _store_document_request(connection, application_id, request_id, final_docs, deadline)
        
        # Format response
        doc_list = "\n".join([f"   • {doc}" for doc in final_docs])
        
        return f"""
📋 **Document Request Generated - {request_id}**

**Application ID:** {application_id}
**Submission Deadline:** {deadline}
**Loan Program:** {loan_program or 'Standard'}

**Required Documents:**
{doc_list}

**Submission Options:**
1. **Online Portal:** Upload directly through your secure portal
2. **Email:** Send scanned copies to docs@mortgagelender.com
3. **Mobile App:** Use our mobile document scanner
4. **In-Person:** Visit any branch location

**Important Notes:**
• All documents must be legible and complete
• Bank statements should show complete account information
• Employment verification should be on company letterhead
• Tax returns must include all schedules and forms

**Need Help?** 
Contact your loan processor at (555) 123-4567

Your application cannot proceed until all required documents are received and verified.
"""
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating document request: {e}")
        return f"❌ Error generating document request: {str(e)}"


def _get_required_documents_from_rules(connection, loan_program: Optional[str]) -> List[str]:
    """Query Neo4j for required documents based on Document Verification Rules."""
    
    with connection.driver.session(database=connection.database) as session:
        # Query for document requirements
        if loan_program:
            # Get program-specific requirements
            query = """
            MATCH (dvr:DocumentVerificationRule)
            WHERE toLower(dvr.category) CONTAINS toLower($loan_program)
               OR dvr.document_type IS NOT NULL
            RETURN DISTINCT dvr.document_type as document_type,
                   dvr.category as category,
                   dvr.description as description
            ORDER BY dvr.document_type
            """
            result = session.run(query, loan_program=loan_program)
        else:
            # Get general requirements
            query = """
            MATCH (dvr:DocumentVerificationRule)
            WHERE dvr.document_type IS NOT NULL
            RETURN DISTINCT dvr.document_type as document_type,
                   dvr.description as description
            ORDER BY dvr.document_type
            LIMIT 15
            """
            result = session.run(query)
        
        # Process results into document list
        required_docs = []
        seen_types = set()
        # Convert to list to avoid consumption errors
        records = list(result)
        
        for record in records:
            doc_type = record.get("document_type")
            description = record.get("description")
            
            if doc_type and doc_type not in seen_types:
                # Convert technical document type to user-friendly description
                user_friendly = _convert_to_user_friendly(doc_type, description)
                required_docs.append(user_friendly)
                seen_types.add(doc_type)
        
        # If no specific rules found, get basic requirements
        if not required_docs:
            required_docs = _get_fallback_documents()
        
        return required_docs


def _convert_to_user_friendly(doc_type: str, description: str) -> str:
    """Convert technical document types to user-friendly descriptions."""
    
    # Map common document types to user-friendly names
    type_mapping = {
        "paystub": "Recent pay stubs (last 2-3 months)",
        "pay_stub": "Recent pay stubs (last 2-3 months)",
        "w2": "W-2 forms (last 2 years)",
        "w-2": "W-2 forms (last 2 years)",
        "tax_return": "Tax returns (last 2 years)",
        "bank_statement": "Bank statements (last 2-3 months)",
        "employment_verification": "Employment verification letter",
        "drivers_license": "Government-issued photo ID (driver's license or passport)",
        "passport": "Government-issued photo ID (driver's license or passport)",
        "social_security": "Social Security card or verification",
        "purchase_agreement": "Purchase agreement (if property identified)",
        "appraisal": "Property appraisal (if available)",
        "insurance": "Insurance information (homeowner's/auto)",
        "gift_letter": "Gift letter (if using gift funds for down payment)"
    }
    
    # Use mapping if available, otherwise use description or raw type
    if doc_type.lower() in type_mapping:
        return type_mapping[doc_type.lower()]
    elif description and len(description) > 10:
        return description
    else:
        # Clean up raw type
        return doc_type.replace("_", " ").title()


def _get_fallback_documents() -> List[str]:
    """Fallback document list if no rules found in Neo4j."""
    return [
        "Government-issued photo ID (driver's license or passport)",
        "Social Security card or verification", 
        "Recent pay stubs (last 2-3 months)",
        "W-2 forms (last 2 years)",
        "Tax returns (last 2 years)",
        "Bank statements (last 2-3 months)",
        "Employment verification letter"
    ]


def _store_document_request(connection, application_id: str, request_id: str, documents: List[str], deadline: str):
    """Store document request in Neo4j."""
    
    with connection.driver.session(database=connection.database) as session:
        # First, ensure application exists
        app_query = """
        MERGE (app:Application {id: $application_id})
        RETURN app.id as app_id
        """
        session.run(app_query, application_id=application_id)
        
        # Create document request
        request_query = """
        MATCH (app:Application {id: $application_id})
        CREATE (req:DocumentRequest {
            id: $request_id,
            application_id: $application_id,
            requested_documents: $documents,
            request_date: datetime(),
            deadline: date($deadline),
            status: 'SENT'
        })
        CREATE (app)-[:REQUIRES_DOCUMENTS]->(req)
        RETURN req.id as request_id
        """
        
        session.run(request_query, {
            "application_id": application_id,
            "request_id": request_id,
            "documents": json.dumps(documents),
            "deadline": deadline
        })

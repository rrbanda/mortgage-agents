"""
DocumentAgent Tools

Operational tools for document processing (NO hardcoded business rules).

The DocumentAgent has 5 operational tools:
1. process_uploaded_document - Process uploaded document content
2. extract_document_data - Extract structured data from documents
3. get_document_status - Get document upload/processing status
4. verify_document_completeness - Check uploaded docs (agent calls business rules for requirements)
5. validate_urla_form - Validate URLA form structure

Each tool:
- Performs operational tasks (process, extract, check status)
- NO hardcoded business rules about what documents are required
- Calls Neo4j DIRECTLY (not via MCP) for operational data

Business rules tools (from shared/rules/) are added separately in agent.py
"""

from .extract_document_data import extract_document_data
from .process_uploaded_document import process_uploaded_document
from .get_document_status import get_document_status
from .verify_document_completeness import verify_document_completeness
from .validate_urla_form import validate_urla_form
from .list_standard_documents import list_standard_documents


def get_all_document_agent_tools():
    """
    Get all operational tools for DocumentAgent.
    
    These are operational tools that:
    - Process and extract document data
    - Check upload status
    - Validate document structure
    - List standard documents (helpful checklist, NOT business rules)
    
    Returns 6 operational tools (business rules tools added separately in agent.py)
    """
    return [
        process_uploaded_document,
        extract_document_data,
        get_document_status,
        verify_document_completeness,
        validate_urla_form,
        list_standard_documents
    ]


__all__ = [
    "extract_document_data",
    "process_uploaded_document", 
    "get_document_status",
    "verify_document_completeness",
    "validate_urla_form",
    "list_standard_documents",
    "get_all_document_agent_tools"
]

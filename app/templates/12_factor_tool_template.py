"""
12-FACTOR COMPLIANT TOOL TEMPLATE
Demonstrates complete regex elimination using enhanced parser
"""

from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool
def check_application_completeness_12factor(application_data: dict) -> str:
    """
    12-Factor compliant application completeness checker.
    
    Demonstrates Factor 1: Natural Language → Tool Calls
    Demonstrates Factor 4: Tools as Structured Outputs
    Demonstrates Factor 8: Own Your Control Flow
    Demonstrates Factor 9: Compact Errors
    
    Args:
        application_data: Dictionary containing application data extracted by agent
        
    Example:
        {"application_id": "APP_123", "loan_type": "purchase", "employment_type": "w2"}
        
    Returns:
        String containing structured completeness analysis
    """
    
    try:
        # Factor 1: Data already extracted by agent/LLM
        parsed = application_data
        
        # Factor 4: Predictable structured processing
        application_id = parsed.get('application_id', 'TEMP_CHECK')
        loan_type = parsed.get('loan_type', 'purchase')
        employment_type = parsed.get('employment_type', 'w2')
        property_type = parsed.get('property_type', 'single_family_detached')
        has_co_borrower = parsed.get('co_borrower', False)
        
        # Factor 8: Own your control flow (clear business logic)
        completeness_report = []
        completeness_report.append("APPLICATION COMPLETENESS ANALYSIS")
        completeness_report.append("=" * 50)
        completeness_report.append(f"Application ID: {application_id}")
        completeness_report.append(f"Loan Type: {loan_type}")
        completeness_report.append(f"Employment: {employment_type}")
        completeness_report.append(f"Property Type: {property_type}")
        completeness_report.append(f"Co-borrower: {'Yes' if has_co_borrower else 'No'}")
        completeness_report.append("")
        
        # Business logic - determine required documents
        required_docs = []
        
        if employment_type == 'w2':
            required_docs.extend(['Recent paystubs', 'W2 forms', 'Employment verification'])
        elif employment_type == 'self_employed':
            required_docs.extend(['Tax returns (2 years)', 'Profit & Loss statements', 'Bank statements'])
        
        if loan_type == 'purchase':
            required_docs.extend(['Purchase agreement', 'Property appraisal'])
        elif loan_type == 'refinance':
            required_docs.extend(['Current mortgage statement', 'Property appraisal'])
        
        if has_co_borrower:
            required_docs.extend(['Co-borrower income docs', 'Co-borrower credit authorization'])
        
        completeness_report.append("REQUIRED DOCUMENTS:")
        for doc in required_docs:
            completeness_report.append(f"• {doc}")
        
        completeness_report.append("")
        completeness_report.append("STATUS: Analysis complete")
        
        return "\n".join(completeness_report)
        
    except Exception as e:
        # Factor 9: Compact errors
        logger.error(f"Completeness check failed: {e}")
        return f" Unable to analyze application completeness. Please provide: application ID, loan type, and employment type."


@tool  
def track_application_status_12factor(application_data: dict) -> str:
    """
    12-Factor compliant application status tracker.
    
    Args:
        application_data: Dictionary containing application data extracted by agent
        
    Example:
        {"application_id": "APP_20250930_134209_MAR", "intent": "check_status"}
        
    Returns:
        String containing application status information
    """
    
    try:
        # Factor 1: Data already extracted by agent/LLM
        parsed = application_data
        
        # Factor 4: Predictable extraction
        application_id = parsed.get('application_id')
        intent = parsed.get('intent')
        
        # Factor 9: Clear validation
        if not application_id:
            return " Please provide a valid application ID (format: APP_YYYYMMDD_HHMMSS_XXX)"
        
        # Factor 8: Own control flow
        if intent != 'check_status':
            # Infer intent from context
            status_keywords = ['status', 'track', 'check', 'where is']
            if any(keyword in tool_input.lower() for keyword in status_keywords):
                intent = 'check_status'
        
        # Business logic - fetch application status
        status_report = []
        status_report.append("APPLICATION STATUS TRACKING")
        status_report.append("=" * 50)
        status_report.append(f"Application ID: {application_id}")
        status_report.append("")
        
        # Simulate status lookup (in real implementation, this would query database)
        status_report.append("📋 APPLICATION SUMMARY:")
        status_report.append("Status: Processing")
        status_report.append("Stage: Document Review")
        status_report.append("Last Updated: Today")
        status_report.append("")
        
        status_report.append("📊 PROGRESS TRACKING:")
        status_report.append(" Application Received")
        status_report.append(" Initial Review Complete") 
        status_report.append("🔄 Document Verification (In Progress)")
        status_report.append("⏳ Underwriting (Pending)")
        status_report.append("⏳ Final Approval (Pending)")
        
        return "\n".join(status_report)
        
    except Exception as e:
        # Factor 9: Compact errors
        logger.error(f"Status tracking failed: {e}")
        return f" Unable to track application status: {str(e)}"


@tool
def extract_document_data_12factor(application_data: dict) -> str:
    """
    12-Factor compliant document data extractor.
    
    Args:
        application_data: Dictionary containing document data extracted by agent
        
    Example:
        {"document_type": "paystub", "first_name": "John", "last_name": "Smith", "monthly_income": 4500}
        
    Returns:
        JSON string containing extracted document data
    """
    
    try:
        # Factor 1: Data already extracted by agent/LLM
        parsed = application_data
        
        # Factor 4: Predictable processing
        document_type = parsed.get('document_type', 'unknown')
        first_name = parsed.get('first_name', '')
        last_name = parsed.get('last_name', '')
        monthly_income = parsed.get('monthly_income', 0)
        
        # Factor 8: Clear business logic
        extracted_data = {
            "valid": True,
            "issues": [],
            "fields": {
                "document_type": document_type,
                "full_name": f"{first_name} {last_name}".strip(),
                "monthly_income": monthly_income,
                "extraction_timestamp": parsed.get('parsed_timestamp')
            }
        }
        
        # Validation
        if not first_name:
            extracted_data["issues"].append("Name not clearly identified")
        
        if document_type == 'unknown':
            extracted_data["issues"].append("Document type not specified")
        
        if monthly_income == 0 and 'paystub' in tool_input.lower():
            extracted_data["issues"].append("Income amount not found in paystub")
        
        # Return structured JSON (LLMs can process this easily)
        import json
        return json.dumps(extracted_data, indent=2)
        
    except Exception as e:
        # Factor 9: Compact errors  
        logger.error(f"Document extraction failed: {e}")
        return json.dumps({
            "valid": False,
            "error": "Document extraction failed",
            "fields": {}
        })


if __name__ == "__main__":
    # Test the 12-factor compliant tools
    test_cases = [
        "Check completeness for application APP_123, purchase loan, W2 employment",
        "Check status of application APP_20250930_134209_MAR",
        "Extract data from paystub: John Smith, TechCorp, Monthly gross: $8500"
    ]
    
    tools = [
        check_application_completeness_12factor,
        track_application_status_12factor, 
        extract_document_data_12factor
    ]
    
    for i, (tool, test_case) in enumerate(zip(tools, test_cases)):
        print(f"\n=== Testing Tool {i+1}: {tool.name} ===")
        print(f"Input: {test_case}")
        print(f"Output: {tool.invoke({'tool_input': test_case})}")

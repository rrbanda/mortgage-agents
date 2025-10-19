"""
List Standard Documents Tool - Helpful Checklist (NOT business rules)

This is an operational/informational tool that provides a standard checklist
of mortgage documents. This is NOT a business rules tool - it's just a helpful
reference guide. Actual document requirements should come from Neo4j MCP when
available.
"""

import logging
from langchain_core.tools import tool
from typing import Dict, Any

logger = logging.getLogger(__name__)


@tool
def list_standard_documents(application_data: Dict[str, Any]) -> str:
    """List standard mortgage document requirements (helpful checklist).
    
    This tool provides a standard checklist of documents typically needed for
    mortgage applications. This is informational only - NOT business rules.
    
    For specific requirements based on loan type, property type, or other factors,
    the agent should query Neo4j MCP for actual business rules.
    
    Args:
        application_data: Dict containing optional context like:
            - loan_purpose (purchase, refinance, etc.)
            - loan_amount
            - property_type
            (All fields optional)
        
    Returns:
        String containing standard document checklist
    """
    try:
        # Extract optional context
        if isinstance(application_data, str):
            try:
                import ast
                application_data = ast.literal_eval(application_data)
            except:
                application_data = {}
        
        if not isinstance(application_data, dict):
            application_data = {}
        
        loan_purpose = application_data.get("loan_purpose", "purchase").lower()
        loan_amount = application_data.get("loan_amount", 0)
        
        # Build standard checklist
        checklist = [
            "STANDARD MORTGAGE DOCUMENT CHECKLIST",
            "=" * 50,
            "",
            "📋 This is a general checklist. Specific requirements may vary.",
            "   For loan-type specific rules, I can query business rules from Neo4j.",
            "",
            "📄 IDENTIFICATION & PERSONAL:",
            "   ✓ Government-issued photo ID (driver's license, passport)",
            "   ✓ Social Security card or verification",
            "   ✓ Proof of current address (utility bill, lease)",
            "",
            "💰 INCOME VERIFICATION:",
            "   ✓ Last 2 years W-2 forms",
            "   ✓ Last 2 pay stubs (showing year-to-date earnings)",
            "   ✓ Last 2 years tax returns (with all schedules)",
            "   ✓ If self-employed: Profit & Loss statements, business tax returns",
            "   ✓ Employment verification letter",
            "",
            "🏦 ASSET DOCUMENTATION:",
            "   ✓ Last 2 months bank statements (all accounts)",
            "   ✓ Last 2 months investment/retirement account statements",
            "   ✓ Gift letter (if receiving gift funds for down payment)",
            "   ✓ Proof of other assets (stocks, bonds, etc.)",
            "",
        ]
        
        # Add purchase-specific docs
        if "purchase" in loan_purpose:
            checklist.extend([
                "🏠 PROPERTY DOCUMENTS (Purchase):",
                "   ✓ Purchase agreement/sales contract",
                "   ✓ Property listing information",
                "   ✓ HOA documents (if applicable)",
                "",
            ])
        
        # Add refinance-specific docs
        if "refinance" in loan_purpose:
            checklist.extend([
                "🏠 PROPERTY DOCUMENTS (Refinance):",
                "   ✓ Current mortgage statement",
                "   ✓ Property deed",
                "   ✓ Homeowner's insurance declaration page",
                "   ✓ HOA documents (if applicable)",
                "",
            ])
        
        # Add credit/debt docs
        checklist.extend([
            "💳 CREDIT & DEBT:",
            "   ✓ List of all current debts (loans, credit cards)",
            "   ✓ Divorce decree/separation agreement (if applicable)",
            "   ✓ Bankruptcy discharge papers (if applicable)",
            "",
            "📝 OTHER:",
            "   ✓ Completed loan application (URLA Form 1003)",
            "   ✓ Authorization for credit check",
            "",
        ])
        
        # Add note about specific requirements
        checklist.extend([
            "🔍 NEED SPECIFIC REQUIREMENTS?",
            "   Ask me to check Neo4j for loan-type specific rules:",
            '   • "What documents are required for FHA loans?"',
            '   • "What are the requirements for jumbo loans?"',
            '   • "What documents needed for self-employed borrowers?"',
            "",
            f"📌 Your Application: {loan_purpose.title()}",
        ])
        
        if loan_amount > 0:
            checklist.append(f"   Loan Amount: ${loan_amount:,.2f}")
        
        return "\n".join(checklist)
    
    except Exception as e:
        logger.error(f"Error listing standard documents: {e}")
        return f"Error listing standard documents: {str(e)}"


def validate_tool() -> bool:
    """Validate that the list_standard_documents tool works correctly."""
    try:
        test_data = {
            "loan_purpose": "purchase",
            "loan_amount": 300000.0
        }
        result = list_standard_documents.invoke({"application_data": test_data})
        return "STANDARD MORTGAGE DOCUMENT CHECKLIST" in result and "INCOME VERIFICATION" in result
    except Exception as e:
        print(f"List standard documents tool validation failed: {e}")
        return False


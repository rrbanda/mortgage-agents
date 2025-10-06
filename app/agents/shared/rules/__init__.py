"""
Business Rules Agent Tools

This module provides centralized business rules tools that other agents can use.
All business rules queries go through these tools, ensuring a single source of truth.
"""

from typing import List
from langchain_core.tools import BaseTool

from .get_underwriting_rules import get_underwriting_rules
from .get_loan_program_requirements import get_loan_program_requirements
from .get_document_requirements import get_document_requirements
from .get_qualification_criteria import get_qualification_criteria
from .get_aus_rules import get_aus_rules
from .get_property_appraisal_rules import get_property_appraisal_rules
from .get_income_calculation_rules import get_income_calculation_rules
from .get_application_intake_rules import get_application_intake_rules


def get_all_business_rules_agent_tools() -> List[BaseTool]:
    """
    Returns a list of all business rules service tools.
    
    These tools provide centralized access to business rules from Neo4j,
    allowing other agents to query business rules without direct Neo4j access.
    """
    return [
        # Core business rules tools
        get_underwriting_rules,
        get_loan_program_requirements,
        get_document_requirements,
        get_qualification_criteria,
        
        # Specialized business rules tools
        get_aus_rules,
        get_property_appraisal_rules,
        get_income_calculation_rules,
        get_application_intake_rules,
    ]


def get_tool_descriptions() -> dict:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        # Core business rules tools
        "get_underwriting_rules": "Get underwriting rules for specific loan programs and credit scores",
        "get_loan_program_requirements": "Get requirements and details for specific loan programs",
        "get_document_requirements": "Get document requirements for specific loan types and property types",
        "get_qualification_criteria": "Get qualification criteria for specific programs and borrower profiles",
        
        # Specialized business rules tools
        "get_aus_rules": "Get Automated Underwriting System (AUS) rules for specific loan programs",
        "get_property_appraisal_rules": "Get property appraisal rules for specific property types and loan programs",
        "get_income_calculation_rules": "Get income calculation rules for specific employment types and loan programs",
        "get_application_intake_rules": "Get application intake rules for specific loan programs and application stages",
    }
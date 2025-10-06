"""
ApplicationAgent Implementation

This agent manages mortgage application lifecycle: data collection, storage, and basic completeness checks.

The ApplicationAgent has two types of tools (9 total):

1. Operational Tools (from application_agent/tools/) - 7 tools:
   - receive_mortgage_application: Collect & store application data
   - track_application_status: Retrieve application status by ID
   - generate_urla_1003_form: Generate URLA forms
   - perform_initial_qualification: Calculate financial metrics (DTI, LTV)
   - check_application_completeness: Check basic required fields
   - get_credit_score (MCP): Fetch credit score from external MCP server when not provided
   - verify_identity (MCP): Verify borrower identity via external MCP server

2. Business Rules Tools (from shared/rules/) - 2 tools (scoped to application needs):
   - get_application_intake_rules: Get required fields for loan programs
   - get_loan_program_requirements: Get basic loan program information

This architecture ensures:
- No hardcoded business rules in agent tools
- Agent can fetch missing borrower data (credit score) via MCP server
- Agent only has business rules tools relevant to its scope
- Clean separation: operational vs. business rules
- Other agents handle: document processing, property valuation, underwriting decisions
"""

from typing import Dict
from langgraph.prebuilt import create_react_agent
from pathlib import Path

from utils import get_llm
from utils.config import AppConfig
from .tools import get_all_application_agent_tools
from agents.shared.rules import (
    get_application_intake_rules,
    get_loan_program_requirements
)
from agents.shared.prompt_loader import load_agent_prompt


def create_application_agent():
    """
    Create ApplicationAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage application intake with:
    - 7 Operational tools (store data, track status, generate forms, fetch credit via MCP, etc.)
    - 2 Business rules tools (only what ApplicationAgent needs):
      * get_application_intake_rules - Required fields for loan programs
      * get_loan_program_requirements - Basic loan program info
    
    MCP Integration:
    - Agent can call get_credit_score to fetch credit from MCP server when user doesn't provide it
    - Agent can call verify_identity to verify borrower via MCP server
    
    Architecture:
    - Agent-specific tools: application_agent/tools/ (operational)
    - Business rules tools: Only the 2 relevant to application scope
    - No hardcoded business rules in any agent
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific)
    operational_tools = get_all_application_agent_tools()
    
    # Get only the business rules tools needed for application intake scope
    business_rules_tools = [
        get_application_intake_rules,
        get_loan_program_requirements
    ]
    
    # Combine both sets of tools (7 operational + 2 business rules = 9 total)
    all_tools = operational_tools + business_rules_tools
    
    # Load system prompt from YAML using shared prompt loader
    agent_dir = Path(__file__).parent
    system_prompt = load_agent_prompt("application_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with combined tools
    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=system_prompt
    )
    
    return agent

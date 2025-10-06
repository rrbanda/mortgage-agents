"""
MortgageAdvisorAgent Implementation

This agent provides intelligent mortgage guidance and education using specialized
tools and Neo4j knowledge graph integration for personalized recommendations.

The MortgageAdvisorAgent has 6 tools total:

Operational Tools (3 - agent-specific):
- explain_loan_programs: Educate about loan programs (NO hardcoded requirements)
- recommend_loan_program: Calculate metrics & suggest programs to explore (NO qualification decisions)
- check_qualification_requirements: Check data completeness & calculate ratios (NO threshold checks)

Business Rules Tools (3 - scoped to advisor needs):
- get_loan_program_requirements: Query specific program requirements from Neo4j via MCP
- get_qualification_criteria: Query what lenders evaluate from Neo4j via MCP
- get_underwriting_rules: Query credit/DTI/LTV thresholds from Neo4j via MCP

The agent focuses on:
- Mortgage education and loan program explanation
- Calculating borrower financial metrics (DTI, LTV)
- Guiding customers to appropriate business rules queries
- Process guidance (via prompt knowledge, not tool)
"""

from typing import Dict
from langgraph.prebuilt import create_react_agent

from utils import get_llm
from utils.config import AppConfig
from .tools import get_all_mortgage_advisor_tools
from ..shared.rules import (
    get_loan_program_requirements,
    get_qualification_criteria,
    get_underwriting_rules
)
from ..shared.prompt_loader import load_agent_prompt


def create_mortgage_advisor_agent():
    """
    Create MortgageAdvisorAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage guidance and education with:
    - 3 Operational tools (calculate metrics, educate, check data completeness)
    - 3 Business rules tools (scoped to advisor needs):
      * get_loan_program_requirements - Query specific program requirements
      * get_qualification_criteria - Query what lenders evaluate
      * get_underwriting_rules - Query credit/DTI/LTV thresholds
    
    Architecture:
    - Operational tools: NO hardcoded business rules, pure calculations/formatting
    - Business rules tools: Query Neo4j via MCP for actual requirements
    - Agent decides when to call business rules tools based on customer questions
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time guidance
    - Human-in-the-loop support for complex decisions
    - Proper error handling and validation
    - Clean separation: operational vs. business rules
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific, no business rules)
    operational_tools = get_all_mortgage_advisor_tools()
    
    # Get only the business rules tools needed for mortgage advisor scope
    business_rules_tools = [
        get_loan_program_requirements,
        get_qualification_criteria,
        get_underwriting_rules
    ]
    
    # Combine both sets of tools (3 operational + 3 business rules = 6 total)
    tools = operational_tools + business_rules_tools
    
    # Load system prompt from YAML using shared prompt loader
    # Explicitly pass the agent directory to ensure correct path detection
    from pathlib import Path
    agent_dir = Path(__file__).parent  # Current directory (mortgage_advisor_agent/)
    system_prompt = load_agent_prompt("mortgage_advisor_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with specialized configuration
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    return agent

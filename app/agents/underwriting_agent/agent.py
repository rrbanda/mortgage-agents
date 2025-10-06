"""
UnderwritingAgent Implementation

This agent provides intelligent mortgage underwriting decisions and risk assessment.

The UnderwritingAgent has 11 tools total:

Operational Tools (8 - agent-specific):
- analyze_credit_risk: Credit risk analysis
- calculate_debt_to_income: DTI calculation (NO hardcoded limits)
- evaluate_income_sources: Income source evaluation
- run_aus_check: AUS system integration
- make_underwriting_decision: Decision analysis
- get_credit_score: MCP tool for real-time credit scores
- verify_identity: MCP tool for identity verification
- get_credit_report: MCP tool for credit reports

Business Rules Tools (3 - scoped to underwriting needs):
- get_underwriting_rules: Query credit/DTI/LTV requirements from Neo4j via MCP
- get_aus_rules: Query AUS system rules from Neo4j via MCP
- get_income_calculation_rules: Query income qualification rules from Neo4j via MCP

The agent focuses on:
- Credit risk analysis and evaluation
- DTI calculations (agent calls business rules for limits)
- Income source evaluation and qualification
- Final underwriting decision making
"""

from typing import Dict
from langgraph.prebuilt import create_react_agent

from utils import get_llm
from utils.config import AppConfig
from .tools import get_all_underwriting_agent_tools
from ..shared.rules import (
    get_underwriting_rules,
    get_aus_rules,
    get_income_calculation_rules
)
from ..shared.prompt_loader import load_agent_prompt


def create_underwriting_agent():
    """
    Create UnderwritingAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage underwriting with:
    - 8 Operational tools (analyze, calculate, evaluate, check, MCP integrations)
    - 3 Business rules tools (scoped to underwriting needs):
      * get_underwriting_rules - Query credit/DTI/LTV requirements from Neo4j via MCP
      * get_aus_rules - Query AUS system rules from Neo4j via MCP
      * get_income_calculation_rules - Query income qualification from Neo4j via MCP
    
    Architecture:
    - Operational tools: NO hardcoded thresholds, just calculations and analysis
    - Business rules tools: Query Neo4j via MCP for actual requirements
    - Agent decides when to call business rules tools based on questions
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time underwriting
    - Human-in-the-loop support for complex decisions
    - Clean separation: operational vs. business rules
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific, no business rules)
    operational_tools = get_all_underwriting_agent_tools()
    
    # Get only the business rules tools needed for underwriting scope
    business_rules_tools = [
        get_underwriting_rules,
        get_aus_rules,
        get_income_calculation_rules
    ]
    
    # Combine both sets of tools (8 operational + 3 business rules = 11 total)
    tools = operational_tools + business_rules_tools
    
    # Load system prompt from YAML using shared prompt loader
    # Explicitly pass the agent directory to ensure correct path detection
    from pathlib import Path
    agent_dir = Path(__file__).parent  # Current directory (underwriting_agent/)
    system_prompt = load_agent_prompt("underwriting_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with specialized configuration
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    return agent

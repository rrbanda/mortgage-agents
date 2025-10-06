"""
AppraisalAgent Implementation

This agent provides intelligent property appraisal and valuation analysis.

The AppraisalAgent has 6 tools total:

Operational Tools (5 - agent-specific):
- analyze_property_value: Property valuation analysis
- find_comparable_sales: Research comparable properties
- assess_property_condition: Property condition assessment
- review_appraisal_report: Review appraisal documents
- evaluate_market_conditions: Market trend evaluation

Business Rules Tools (1 - scoped to appraisal needs):
- get_property_appraisal_rules: Query LTV limits, appraisal standards, condition requirements from Neo4j via MCP

The agent focuses on:
- Property value analysis and comparable sales research
- Property condition assessment for lending standards
- Appraisal report review and compliance validation
- Market conditions evaluation and impact analysis
"""

from typing import Dict
from langgraph.prebuilt import create_react_agent
from pathlib import Path

from utils import get_llm
from utils.config import AppConfig
from .tools import get_all_appraisal_agent_tools
from ..shared.rules import get_property_appraisal_rules
from ..shared.prompt_loader import load_agent_prompt


def create_appraisal_agent():
    """
    Create AppraisalAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for property appraisal with:
    - 5 Operational tools (value analysis, comparables, condition, review, market)
    - 1 Business rules tool (scoped to appraisal needs):
      * get_property_appraisal_rules - Query LTV limits, appraisal standards from Neo4j via MCP
    
    Architecture:
    - Operational tools: NO hardcoded business rules, just operational analysis
    - Business rules tool: Queries Neo4j via MCP for actual requirements
    - Agent decides when to call business rules tool based on customer questions
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time analysis
    - Human-in-the-loop support for complex valuations
    - Clean separation: operational vs. business rules
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific, no business rules)
    operational_tools = get_all_appraisal_agent_tools()
    
    # Get only the business rules tool needed for appraisal scope
    business_rules_tools = [
        get_property_appraisal_rules
    ]
    
    # Combine both sets of tools (5 operational + 1 business rules = 6 total)
    tools = operational_tools + business_rules_tools
    
    # Load system prompt from YAML using shared prompt loader
    # Explicitly pass the agent directory to ensure correct path detection
    agent_dir = Path(__file__).parent  # Current directory (appraisal_agent/)
    system_prompt = load_agent_prompt("appraisal_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with specialized configuration
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    return agent

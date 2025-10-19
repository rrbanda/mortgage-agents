"""
ApplicationAgent Implementation

This agent manages mortgage application lifecycle: data collection, storage, and basic completeness checks.

The ApplicationAgent dynamically combines three types of tools:

1. Core Operational Tools (5 tools from application_agent/tools/):
   - receive_mortgage_application: Collect & store application data
   - track_application_status: Retrieve application status by ID
   - generate_urla_1003_form: Generate URLA forms
   - perform_initial_qualification: Calculate financial metrics (DTI, LTV)
   - check_application_completeness: Check basic required fields

2. Credit Check MCP Tools (dynamically loaded via ToolHive):
   - Tools discovered at runtime from credit check MCP server
   - Examples: credit_score, verify_identity, credit_report
   - Agent decides when to call these based on prompts

3. Business Rules MCP Tools (dynamically loaded from Neo4j):
   - Tools discovered at runtime from Neo4j MCP server
   - Examples: query_underwriting_rules, query_loan_programs, etc.
   - Agent decides when to call these based on prompts

This architecture ensures:
- Official LangGraph MCP pattern: agent dynamically discovers and decides when to call MCP tools
- No hardcoded business rules in operational tools
- Clean separation: operational vs. MCP-provided tools
- Other agents handle: document processing, property valuation, underwriting decisions
"""

import logging
from langgraph.prebuilt import create_react_agent
from pathlib import Path

from utils import get_llm
from .tools import get_core_application_tools
from ..shared.prompt_loader import load_agent_prompt
from ..shared.mcp_tools_loader import get_mcp_credit_tools
from ..shared.neo4j_mcp_loader import get_neo4j_mcp_tools

logger = logging.getLogger(__name__)


def create_application_agent():
    """
    Create ApplicationAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage application intake with dynamically loaded tools:
    - 5 Core operational tools (store data, track status, generate forms, calculate metrics, check completeness)
    - N Credit check MCP tools (dynamically discovered from ToolHive at runtime)
    - M Business rules MCP tools (dynamically discovered from Neo4j MCP at runtime)
    
    Official LangGraph MCP Pattern:
    - Tools are discovered dynamically from MCP servers at agent initialization
    - Agent receives all available tools and decides when to call them based on prompts
    - No hardcoded MCP wrapper tools - agent has direct access to MCP tools
    
    Architecture:
    - Core operational tools: application_agent/tools/
    - Credit MCP tools: Loaded via mcp_tools_loader.get_mcp_credit_tools()
    - Neo4j MCP tools: Loaded via neo4j_mcp_loader.get_neo4j_mcp_tools()
    - Agent orchestrates all tools based on user intent
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get core operational tools
    core_tools = get_core_application_tools()
    logger.info(f"Loaded {len(core_tools)} core application tools")
    
    # OFFICIAL LANGGRAPH MCP PATTERN: Dynamically load MCP tools at initialization
    # Agent will receive these tools and decide when to call them based on prompts
    credit_mcp_tools = get_mcp_credit_tools()        # Credit check via ToolHive
    neo4j_mcp_tools = get_neo4j_mcp_tools()          # Business rules via Neo4j direct
    
    if credit_mcp_tools:
        logger.info(f"✓ Loaded {len(credit_mcp_tools)} credit MCP tools")
    if neo4j_mcp_tools:
        logger.info(f"✓ Loaded {len(neo4j_mcp_tools)} Neo4j MCP tools")
    
    # Combine all tools - PRIORITIZE Neo4j MCP tools by putting them FIRST
    # Tool order matters: LLMs tend to favor tools listed earlier
    # Order: Neo4j MCP (business rules) → Operational → Credit MCP
    all_tools = neo4j_mcp_tools + core_tools + credit_mcp_tools
    logger.info(f"Total tools available to agent: {len(all_tools)} (Neo4j MCP prioritized first)")
    
    # Load system prompt from YAML using shared prompt loader
    agent_dir = Path(__file__).parent
    system_prompt = load_agent_prompt("application_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with all tools (core + dynamically loaded MCP tools)
    # Agent will intelligently decide when to call MCP tools based on user prompts and context
    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=system_prompt
    )
    
    logger.info("✓ ApplicationAgent created with FULL official MCP pattern (credit + neo4j)")
    return agent

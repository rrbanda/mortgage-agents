"""
UnderwritingAgent Implementation

This agent provides intelligent mortgage underwriting decisions and risk assessment.

The UnderwritingAgent has tools in these categories:

Shared Application Data Tools (3):
- get_stored_application_data: Retrieve application by ID (gets SSN, name, DOB for credit checks)
- find_application_by_name: Find applications by applicant name
- list_stored_applications: List all applications by status

Operational Tools (5 - agent-specific):
- analyze_credit_risk: Credit risk analysis (NO hardcoded thresholds)
- calculate_debt_to_income: DTI calculation (NO hardcoded limits)
- evaluate_income_sources: Income source evaluation (NO qualification rules)
- run_aus_check: AUS system integration (operational only)
- make_underwriting_decision: Decision analysis (NO hardcoded approval rules)

MCP Tools (dynamically loaded at runtime):
- N Credit Check MCP tools: Loaded from ToolHive via get_mcp_credit_tools()
  (e.g., credit_score, verify_identity, credit_report) - AUTOMATICALLY called during underwriting
- M Neo4j MCP tools: Loaded from Neo4j MCP server via get_neo4j_mcp_tools()
  (e.g., read_neo4j_cypher for querying underwriting rules, AUS rules, income calculation rules)

Official LangGraph MCP Pattern:
- Tools are discovered dynamically from MCP servers at agent initialization
- Agent receives all available tools and decides when to call them based on prompts
- No hardcoded MCP wrapper tools - agent has direct access to MCP tools

The agent focuses on:
- Credit risk analysis and evaluation
- DTI calculations (agent calls Neo4j MCP for limits via Cypher queries)
- Income source evaluation and qualification
- Final underwriting decision making
"""

import logging
from pathlib import Path
from langgraph.prebuilt import create_react_agent

from utils import get_llm
from .tools import get_core_underwriting_tools  # Use core tools only
from ..shared.prompt_loader import load_agent_prompt
from ..shared.mcp_tools_loader import get_mcp_credit_tools  # Credit check MCP via ToolHive
from ..shared.neo4j_mcp_loader import get_neo4j_mcp_tools  # Neo4j MCP direct
from ..shared.application_data_tools import get_shared_application_tools  # Shared application data access

logger = logging.getLogger(__name__)


def create_underwriting_agent():
    """
    Create UnderwritingAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage underwriting with dynamically loaded tools:
    - 5 Core operational tools (analyze, calculate, evaluate, check, decision)
    - N Credit check MCP tools (dynamically discovered from ToolHive at runtime)
    - M Neo4j MCP tools (dynamically discovered from Neo4j MCP at runtime)
    
    Official LangGraph MCP Pattern:
    - Tools are discovered dynamically from MCP servers at agent initialization
    - Agent receives all available tools and decides when to call them based on prompts
    - No hardcoded MCP wrapper tools - agent has direct access to MCP tools
    
    Architecture:
    - Core operational tools: underwriting_agent/tools/ (NO hardcoded thresholds)
    - Credit MCP tools: Loaded via mcp_tools_loader.get_mcp_credit_tools()
    - Neo4j MCP tools: Loaded via neo4j_mcp_loader.get_neo4j_mcp_tools()
    - Agent orchestrates all tools based on user intent and conversation context
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time underwriting
    - Human-in-the-loop support for complex decisions
    - Clean separation: operational vs. external MCP services
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get core operational tools (NO MCP wrappers, NO hardcoded thresholds)
    core_tools = get_core_underwriting_tools()
    logger.info(f"Loaded {len(core_tools)} core operational tools")
    
    # Get shared application data tools (for retrieving stored application data)
    shared_tools = get_shared_application_tools()
    logger.info(f"Loaded {len(shared_tools)} shared application data tools")
    
    # OFFICIAL LANGGRAPH MCP PATTERN: Dynamically load MCP tools at initialization
    # Agent will receive these tools and decide when to call them based on prompts
    credit_mcp_tools = get_mcp_credit_tools()        # Credit check via ToolHive
    neo4j_mcp_tools = get_neo4j_mcp_tools()          # Business rules via Neo4j direct
    
    if credit_mcp_tools:
        logger.info(f"✓ Loaded {len(credit_mcp_tools)} credit MCP tools from ToolHive: {[t.name for t in credit_mcp_tools]}")
    else:
        logger.warning("⚠️  No credit MCP tools loaded - ToolHive may be unavailable")
    
    if neo4j_mcp_tools:
        logger.info(f"✓ Loaded {len(neo4j_mcp_tools)} Neo4j MCP tools: {[t.name for t in neo4j_mcp_tools]}")
    else:
        logger.warning("⚠️  No Neo4j MCP tools loaded - Neo4j MCP server may be unavailable")
    
    # Combine all tools - PRIORITIZE in order of importance
    # Tool order matters: LLMs tend to favor tools listed earlier
    # Order: Shared app data → Neo4j MCP (business rules) → Core operational → Credit MCP
    tools = shared_tools + neo4j_mcp_tools + core_tools + credit_mcp_tools
    logger.info(f"Total tools available to agent: {len(tools)} (Shared & Neo4j MCP prioritized first)")
    
    # Load system prompt from YAML using shared prompt loader
    agent_dir = Path(__file__).parent  # Current directory (underwriting_agent/)
    system_prompt = load_agent_prompt("underwriting_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with specialized configuration
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    logger.info("✓ UnderwritingAgent created with FULL official MCP pattern (credit + neo4j)")
    
    return agent

"""
MortgageAdvisorAgent Implementation

This agent provides intelligent mortgage guidance and education using specialized
tools and Neo4j knowledge graph integration for personalized recommendations.

The MortgageAdvisorAgent has tools in these categories:

Operational Tools (3 - agent-specific):
- explain_loan_programs: Educate about loan programs (NO hardcoded requirements)
- recommend_loan_program: Calculate metrics & suggest programs to explore (NO qualification decisions)
- check_qualification_requirements: Check data completeness & calculate ratios (NO threshold checks)

MCP Tools (dynamically loaded at runtime):
- N Credit Check MCP tools: Loaded from ToolHive via get_mcp_credit_tools()
- M Neo4j MCP tools: Loaded from Neo4j MCP server via get_neo4j_mcp_tools()
  (includes business rules queries for loan requirements, qualification criteria, underwriting rules)

Official LangGraph MCP Pattern:
- Tools are discovered dynamically from MCP servers at agent initialization
- Agent receives all available tools and decides when to call them based on prompts
- No hardcoded MCP wrapper tools - agent has direct access to MCP tools

The agent focuses on:
- Mortgage education and loan program explanation
- Calculating borrower financial metrics (DTI, LTV)
- Dynamically calling MCP business rules tools when needed
- Process guidance (via prompt knowledge, not tool)
"""

from langgraph.prebuilt import create_react_agent
from pathlib import Path

from utils import get_llm
from .tools import get_all_mortgage_advisor_tools
from ..shared.prompt_loader import load_agent_prompt
from ..shared.mcp_tools_loader import get_mcp_credit_tools
from ..shared.neo4j_mcp_loader import get_neo4j_mcp_tools
import logging

logger = logging.getLogger(__name__)


def create_mortgage_advisor_agent():
    """
    Create MortgageAdvisorAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for mortgage guidance and education with dynamically loaded tools:
    - 3 Operational tools (calculate metrics, educate, check data completeness)
    - N Credit check MCP tools (dynamically discovered from ToolHive at runtime)
    - M Neo4j MCP tools (dynamically discovered from Neo4j MCP at runtime)
      (includes business rules for loan requirements, qualification criteria, underwriting rules)
    
    Official LangGraph MCP Pattern:
    - Tools are discovered dynamically from MCP servers at agent initialization
    - Agent receives all available tools and decides when to call them based on prompts
    - No hardcoded MCP wrapper tools - agent has direct access to MCP tools
    
    Architecture:
    - Operational tools: mortgage_advisor_agent/tools/
    - Credit MCP tools: Loaded via mcp_tools_loader.get_mcp_credit_tools()
    - Neo4j MCP tools: Loaded via neo4j_mcp_loader.get_neo4j_mcp_tools()
    - Agent orchestrates all tools based on user intent
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time guidance
    - Human-in-the-loop support for complex decisions
    - Proper error handling and validation
    - Clean separation: operational vs. business rules
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific)
    operational_tools = get_all_mortgage_advisor_tools()
    logger.info(f"Loaded {len(operational_tools)} advisor operational tools")
    
    # OFFICIAL LANGGRAPH MCP PATTERN: Dynamically load MCP tools at initialization
    # Agent will receive these tools and decide when to call them based on prompts
    credit_mcp_tools = get_mcp_credit_tools()        # Credit check via MCP
    neo4j_mcp_tools = get_neo4j_mcp_tools()          # Business rules via Neo4j direct
    
    if credit_mcp_tools:
        logger.info(f"✓ Loaded {len(credit_mcp_tools)} credit MCP tools")
    if neo4j_mcp_tools:
        logger.info(f"✓ Loaded {len(neo4j_mcp_tools)} Neo4j MCP tools")
    
    # Combine all tools - PRIORITIZE Neo4j MCP tools by putting them FIRST
    # Tool order matters: LLMs tend to favor tools listed earlier
    # Order: Neo4j MCP (business rules) → Operational → Credit MCP
    tools = neo4j_mcp_tools + operational_tools + credit_mcp_tools
    logger.info(f"Total tools available: {len(tools)} (Neo4j MCP prioritized first)")
    
    # Load system prompt from YAML using shared prompt loader
    agent_dir = Path(__file__).parent  # Current directory (mortgage_advisor_agent/)
    system_prompt = load_agent_prompt("mortgage_advisor_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with all tools (operational + dynamically loaded MCP tools)
    # Agent will intelligently decide when to call MCP tools based on user prompts and context
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    logger.info("✓ MortgageAdvisorAgent created with FULL official MCP pattern (credit + neo4j)")
    return agent

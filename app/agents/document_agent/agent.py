"""
DocumentAgent Implementation

This agent handles mortgage document processing, validation, and workflow management.

The DocumentAgent has 6 tools total:

Operational Tools (5 - agent-specific):
- process_uploaded_document: Process document content
- extract_document_data: Extract structured data
- get_document_status: Get upload/processing status
- verify_document_completeness: Check uploaded docs (NO hardcoded requirements)
- validate_urla_form: Validate URLA form structure

Business Rules Tools (1 - scoped to document needs):
- get_document_requirements: Query required documents from Neo4j via MCP

The agent focuses on:
- Document upload and processing
- Data extraction from documents
- Status tracking
- Agent calls business rules tool to know what documents are required
"""

from langgraph.prebuilt import create_react_agent

from utils import get_llm
from .tools import get_all_document_agent_tools
from ..shared.prompt_loader import load_agent_prompt
from ..shared.mcp_tools_loader import get_mcp_credit_tools
from ..shared.neo4j_mcp_loader import get_neo4j_mcp_tools
import logging

logger = logging.getLogger(__name__)


def create_document_agent():
    """
    Create DocumentAgent using LangGraph's prebuilt create_react_agent.
    
    This creates a specialized agent for document processing with:
    - 5 Operational tools (process, extract, check status, validate)
    - 1 Business rules tool (scoped to document needs):
      * get_document_requirements - Query required documents from Neo4j via MCP
    
    Architecture:
    - Operational tools: NO hardcoded document requirements
    - Business rules tool: Queries Neo4j via MCP for actual requirements
    - Agent decides when to call business rules tool based on customer questions
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time processing
    - Human-in-the-loop support for complex document reviews
    - Clean separation: operational vs. business rules
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    # Get centralized LLM from factory
    llm = get_llm()
    
    # Get operational tools (agent-specific)
    operational_tools = get_all_document_agent_tools()
    logger.info(f"Loaded {len(operational_tools)} document operational tools")
    
    # Get MCP tools
    credit_mcp_tools = get_mcp_credit_tools()
    neo4j_mcp_tools = get_neo4j_mcp_tools()
    
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
    # Explicitly pass the agent directory to ensure correct path detection
    from pathlib import Path
    agent_dir = Path(__file__).parent  # Current directory (document_agent/)
    system_prompt = load_agent_prompt("document_agent", agent_dir)
    
    # Create the prebuilt ReAct agent with specialized configuration
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    return agent

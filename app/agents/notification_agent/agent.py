"""
NotificationAgent Implementation - MCP Integration Test

This agent demonstrates MCP (Model Context Protocol) integration with LangGraph agents,
using Twilio Alpha MCP server for SMS and communication capabilities.

The NotificationAgent focuses on:
- SMS notifications for mortgage application updates
- Customer communication management  
- Status notifications and alerts
- MCP tool integration testing

This serves as a proof-of-concept for integrating MCP servers with LangGraph agents
before rolling out to the main mortgage processing agents.
"""

from langgraph.prebuilt import create_react_agent
from pathlib import Path
import logging

from utils import get_llm
from .tools import get_all_notification_agent_tools
from ..shared.prompt_loader import load_agent_prompt
from ..shared.mcp_tools_loader import get_mcp_credit_tools
from ..shared.neo4j_mcp_loader import get_neo4j_mcp_tools

logger = logging.getLogger(__name__)

def create_notification_agent():
    """
    Create NotificationAgent using LangGraph's prebuilt create_react_agent with MCP integration.
    
    This creates a specialized agent for SMS notifications and communication management
    using LangGraph's production-ready ReAct agent with MCP-powered tool integration.
    
    Features:
    - Built-in memory and state management
    - Streaming capabilities for real-time processing
    - MCP-powered Twilio SMS tools
    - Neo4j MCP for notification rules and templates
    - Credit Check MCP for identity verification
    - Human-in-the-loop support for sensitive notifications
    - Proper error handling and validation
    - Tool isolation for clean notification functionality
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    try:
        # Get centralized LLM from factory
        llm = get_llm()
        
        # Get NotificationAgent-specific operational tools (Twilio MCP)
        operational_tools = get_all_notification_agent_tools()
        logger.info(f"Loaded {len(operational_tools)} Twilio MCP notification tools")
        
        # Load additional MCP tools
        credit_mcp_tools = get_mcp_credit_tools()
        neo4j_mcp_tools = get_neo4j_mcp_tools()
        
        if credit_mcp_tools:
            logger.info(f"✓ Loaded {len(credit_mcp_tools)} credit MCP tools")
        if neo4j_mcp_tools:
            logger.info(f"✓ Loaded {len(neo4j_mcp_tools)} Neo4j MCP tools")
        
        # Combine all tools - PRIORITIZE Neo4j MCP tools by putting them FIRST
        # Tool order matters: LLMs tend to favor tools listed earlier
        # Order: Neo4j MCP (rules) → Operational (Twilio) → Credit MCP
        tools = neo4j_mcp_tools + operational_tools + credit_mcp_tools
        logger.info(f"Total tools available: {len(tools)} (Neo4j MCP prioritized first)")
        
        # Load system prompt from YAML using shared prompt loader
        agent_dir = Path(__file__).parent  # Current directory (notification_agent/)
        system_prompt = load_agent_prompt("notification_agent", agent_dir)
        
        # Create the prebuilt ReAct agent with MCP-powered tools
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=system_prompt
        )
        
        logger.info("✓ NotificationAgent created with FULL MCP integration (Twilio + Neo4j + Credit)")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create NotificationAgent: {e}")
        raise

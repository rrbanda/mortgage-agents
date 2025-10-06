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

from typing import Dict
from langgraph.prebuilt import create_react_agent
from pathlib import Path
import logging

from utils import get_llm
from utils.config import AppConfig
from .tools import get_all_notification_agent_tools
from ..shared.prompt_loader import load_agent_prompt

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
    - Human-in-the-loop support for sensitive notifications
    - Proper error handling and validation
    - Tool isolation for clean notification functionality
    
    Returns:
        Compiled LangGraph agent ready for execution
    """
    
    try:
        # Load configuration
        config = AppConfig.load()
        
        # Get centralized LLM from factory
        llm = get_llm()
        
        # Get all NotificationAgent-specific MCP tools
        tools = get_all_notification_agent_tools()
        logger.info(f"Loaded {len(tools)} MCP-powered notification tools")
        
        # Load system prompt from YAML using shared prompt loader
        agent_dir = Path(__file__).parent  # Current directory (notification_agent/)
        system_prompt = load_agent_prompt("notification_agent", agent_dir)
        
        # Create the prebuilt ReAct agent with MCP-powered tools
        agent = create_react_agent(
            model=llm,
            tools=tools
        )
        
        logger.info("NotificationAgent created successfully with MCP integration")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create NotificationAgent: {e}")
        raise

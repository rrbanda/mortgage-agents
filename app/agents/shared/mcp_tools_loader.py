"""
MCP Tools Loader - Official LangGraph Pattern
Loads MCP tools from Credit Check MCP server for agent discovery

This module provides a clean interface for agents to load MCP tools
using the official langchain-mcp-adapters pattern.
"""

import asyncio
import logging
from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

# Global MCP client cache
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools_cache: Optional[List[BaseTool]] = None


def get_mcp_credit_tools() -> List[BaseTool]:
    """
    Get MCP credit check tools from Credit Check MCP server.
    
    This uses the official LangGraph MCP pattern where:
    - Agent discovers tools dynamically from MCP server
    - No hardcoded wrapper tools needed
    - Agent decides when to call MCP tools based on prompts
    
    Returns:
        List of BaseTool objects from MCP server (credit_score, verify_identity, credit_report)
    """
    global _mcp_tools_cache
    
    # Return cached tools if available
    if _mcp_tools_cache is not None:
        logger.info(f"Returning {len(_mcp_tools_cache)} cached MCP tools")
        return _mcp_tools_cache
    
    try:
        # Load tools from MCP server
        logger.info("Loading MCP tools from Credit Check MCP server...")
        
        # Handle both sync and async contexts
        try:
            # Try to get current event loop
            loop = asyncio.get_running_loop()
            # We're in an async context - run in thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _load_mcp_tools())
                tools = future.result(timeout=30)
        except RuntimeError:
            # No event loop running - safe to use asyncio.run()
            tools = asyncio.run(_load_mcp_tools())
        
        if tools:
            _mcp_tools_cache = tools
            logger.info(f"Loaded {len(tools)} MCP tools: {[t.name for t in tools]}")
        else:
            logger.warning("No MCP tools loaded - server may be unavailable")
            return []
        
        return tools
        
    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}")
        import traceback
        traceback.print_exc()
        return []


async def _load_mcp_tools() -> List[BaseTool]:
    """Internal async function to load MCP tools"""
    global _mcp_client
    
    # Initialize client if needed
    if _mcp_client is None:
        _mcp_client = await _initialize_mcp_client()
    
    if _mcp_client is None:
        return []
    
    # Get tools from MCP server
    try:
        tools = await _mcp_client.get_tools()
        return tools
    except Exception as e:
        logger.error(f"Error getting tools from MCP server: {e}")
        return []


async def _initialize_mcp_client() -> Optional[MultiServerMCPClient]:
    """Initialize MCP client connected to Credit Check MCP server"""
    try:
        # Import config here to avoid circular imports
        import sys
        from pathlib import Path
        
        # Add app to path if needed
        app_path = Path(__file__).parent.parent.parent
        if str(app_path) not in sys.path:
            sys.path.insert(0, str(app_path))
        
        from utils.config import AppConfig
        
        config = AppConfig.load()
        
        if not config.is_mcp_credit_check_enabled():
            logger.info("MCP credit check is disabled in config")
            return None
        
        mcp_url = config.get_mcp_credit_check_url()
        
        logger.info(f"Initializing Credit Check MCP client (streamable-http): {mcp_url}")
        
        # Configure client for streamable-http MCP server
        # URL should end with /mcp (FastMCP endpoint)
        client_config = {
            "credit_check": {
                "url": mcp_url,
                "transport": "streamable_http",
            }
        }
        
        client = MultiServerMCPClient(client_config)
        logger.info("MCP client initialized successfully")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        import traceback
        traceback.print_exc()
        return None


def clear_mcp_cache():
    """Clear MCP tools cache (useful for testing)"""
    global _mcp_tools_cache, _mcp_client
    _mcp_tools_cache = None
    _mcp_client = None
    logger.info("MCP cache cleared")


# Simple test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing MCP tools loader...")
    tools = get_mcp_credit_tools()
    
    if tools:
        print(f"\nLoaded {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
    else:
        print("\nNo tools loaded")


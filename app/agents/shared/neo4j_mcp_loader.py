"""
Neo4j MCP Tools Loader - Official LangGraph Pattern
Loads Neo4j business rules MCP tools for agent discovery

This module provides a clean interface for agents to load Neo4j MCP tools
using the official langchain-mcp-adapters pattern (direct connection, NO ToolHive).
"""

import asyncio
import logging
from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

# Global MCP client cache for Neo4j
_neo4j_mcp_client: Optional[MultiServerMCPClient] = None
_neo4j_mcp_tools_cache: Optional[List[BaseTool]] = None


def get_neo4j_mcp_tools() -> List[BaseTool]:
    """
    Get Neo4j MCP tools (business rules) from MCP server.
    
    This uses the official LangGraph MCP pattern where:
    - Agent discovers tools dynamically from MCP server
    - No hardcoded wrapper tools needed
    - Agent decides when to call Neo4j MCP tools based on prompts
    
    Returns:
        List of BaseTool objects from Neo4j MCP server (read_neo4j_cypher, etc.)
    """
    global _neo4j_mcp_tools_cache
    
    # Return cached tools if available
    if _neo4j_mcp_tools_cache is not None:
        logger.info(f"Returning {len(_neo4j_mcp_tools_cache)} cached Neo4j MCP tools")
        return _neo4j_mcp_tools_cache
    
    try:
        # Load tools from MCP server
        logger.info("Loading Neo4j MCP tools...")
        
        # Handle both sync and async contexts
        try:
            # Try to get current event loop
            loop = asyncio.get_running_loop()
            # We're in an async context - run in thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _load_neo4j_mcp_tools())
                tools = future.result(timeout=30)
        except RuntimeError:
            # No event loop running - safe to use asyncio.run()
            tools = asyncio.run(_load_neo4j_mcp_tools())
        
        if tools:
            _neo4j_mcp_tools_cache = tools
            logger.info(f"Loaded {len(tools)} Neo4j MCP tools: {[t.name for t in tools]}")
        else:
            logger.warning("No Neo4j MCP tools loaded - server may be unavailable")
            return []
        
        return tools
        
    except Exception as e:
        logger.error(f"Failed to load Neo4j MCP tools: {e}")
        import traceback
        traceback.print_exc()
        return []


async def _load_neo4j_mcp_tools() -> List[BaseTool]:
    """Internal async function to load Neo4j MCP tools"""
    global _neo4j_mcp_client
    
    # Initialize client if needed
    if _neo4j_mcp_client is None:
        _neo4j_mcp_client = await _initialize_neo4j_mcp_client()
    
    if _neo4j_mcp_client is None:
        return []
    
    # Get tools from MCP server
    try:
        tools = await _neo4j_mcp_client.get_tools()
        return tools
    except Exception as e:
        logger.error(f"Error getting tools from Neo4j MCP server: {e}")
        return []


async def _initialize_neo4j_mcp_client() -> Optional[MultiServerMCPClient]:
    """Initialize Neo4j MCP client (direct connection, NO ToolHive)"""
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
        
        # Check if mortgage rules MCP is enabled
        if not config.mcp.mortgage_rules.enabled:
            logger.info("Neo4j MCP (mortgage rules) is disabled in config")
            return None
        
        mcp_url = config.mcp.mortgage_rules.url
        
        logger.info(f"Initializing Neo4j MCP client (direct connection): {mcp_url}")
        
        # Configure client for Neo4j MCP server
        # Note: Direct connection, NOT via ToolHive
        client_config = {
            "mortgage_rules": {
                "url": mcp_url,
                "transport": "streamable_http",  # Direct HTTP, not SSE
            }
        }
        
        client = MultiServerMCPClient(client_config)
        logger.info("Neo4j MCP client initialized successfully")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j MCP client: {e}")
        import traceback
        traceback.print_exc()
        return None


def clear_neo4j_mcp_cache():
    """Clear Neo4j MCP tools cache (useful for testing)"""
    global _neo4j_mcp_tools_cache, _neo4j_mcp_client
    _neo4j_mcp_tools_cache = None
    _neo4j_mcp_client = None
    logger.info("Neo4j MCP cache cleared")


# Simple test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Neo4j MCP tools loader...")
    tools = get_neo4j_mcp_tools()
    
    if tools:
        print(f"\nLoaded {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
    else:
        print("\nNo tools loaded")


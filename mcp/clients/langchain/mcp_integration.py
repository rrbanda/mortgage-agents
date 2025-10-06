#!/usr/bin/env python3
"""
MCP Integration Module for Mortgage Agents
Direct integration with MCP servers using langchain-mcp-adapters
"""

import asyncio
import logging
from typing import List, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from app.utils.config import AppConfig

logger = logging.getLogger(__name__)

# Global MCP client instance
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools: List[BaseTool] = []
_mcp_descriptions: Dict[str, str] = {}

async def _initialize_mcp_client() -> Optional[MultiServerMCPClient]:
    """Initialize MCP client with configured servers."""
    global _mcp_client
    
    if _mcp_client is not None:
        return _mcp_client
    
    try:
        config = AppConfig.load()
        
        if not config.is_mcp_credit_check_enabled():
            logger.info("MCP credit check disabled in config")
            return None
            
        mcp_url = config.get_mcp_credit_check_url()
        
        # Configure MCP client for our deployed credit check server
        client_config = {
            "credit_check": {
                "url": mcp_url,  # Base URL for SSE transport
                "transport": "sse",  # Server-Sent Events for agentic discovery
            }
        }
        
        logger.info(f"Initializing MCP client for credit check server: {mcp_url}")
        _mcp_client = MultiServerMCPClient(client_config)
        
        return _mcp_client
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        return None

async def _load_mcp_tools() -> List[BaseTool]:
    """Load tools from MCP servers."""
    global _mcp_tools, _mcp_descriptions
    
    if _mcp_tools:
        return _mcp_tools
    
    client = await _initialize_mcp_client()
    if not client:
        return []
    
    try:
        logger.info("Loading tools from MCP servers...")
        tools = await client.get_tools()
        
        # Extract tool descriptions for our registry
        descriptions = {}
        for tool in tools:
            descriptions[tool.name] = tool.description
            
        _mcp_tools = tools
        _mcp_descriptions = descriptions
        
        logger.info(f"Successfully loaded {len(tools)} MCP tools: {[t.name for t in tools]}")
        return tools
        
    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}")
        return []

def get_mcp_tools() -> List[BaseTool]:
    """Get MCP tools synchronously."""
    try:
        # Run async function in event loop
        return asyncio.run(_load_mcp_tools())
    except Exception as e:
        logger.warning(f"Could not load MCP tools: {e}")
        return []

def get_mcp_tool_descriptions() -> Dict[str, str]:
    """Get MCP tool descriptions."""
    global _mcp_descriptions
    
    if not _mcp_descriptions:
        # Try to load tools to populate descriptions
        get_mcp_tools()
    
    return _mcp_descriptions.copy()

async def test_mcp_connection() -> bool:
    """Test MCP server connection."""
    try:
        client = await _initialize_mcp_client()
        if not client:
            return False
            
        tools = await client.get_tools()
        logger.info(f"MCP connection test successful - {len(tools)} tools available")
        return True
        
    except Exception as e:
        import traceback
        logger.error(f"MCP connection test failed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Test MCP integration
    async def main():
        print("🏦 Testing MCP Credit Check Integration...")
        
        # Test connection
        connected = await test_mcp_connection()
        print(f" MCP Connection: {'Connected' if connected else 'Failed'}")
        
        # Load tools
        tools = await _load_mcp_tools()
        print(f"🛠️  Available MCP Tools: {len(tools)}")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    
    asyncio.run(main())

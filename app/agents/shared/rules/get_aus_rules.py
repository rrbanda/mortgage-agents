"""
Get AUS Rules Tool - Business Rules Service

This tool provides centralized access to Automated Underwriting System (AUS) rules from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_aus_rules(loan_program: str, aus_system: str = "all") -> str:
    """
    Get Automated Underwriting System (AUS) rules for specific loan programs.
    
    This tool queries Neo4j for AUS rules that other agents need
    for automated underwriting decisions and AUS processing.
    
    Args:
        loan_program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        aus_system: AUS system type ('du', 'lpa', 'gses', 'all')
    
    Returns:
        JSON string containing AUS rules and requirements
    """
    
    try:
        # Import MCP tools and config
        from langchain_mcp_adapters.tools import load_mcp_tools
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        import asyncio
        import sys
        import os
        
        # Add the utils path to import config
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'utils'))
        from config import AppConfig
        
        # Load configuration
        config = AppConfig.load()
        mcp_url = config.mcp.mortgage_rules.url
        
        async def query_neo4j():
            async with streamablehttp_client(mcp_url) as (read, write, get_session_id):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await load_mcp_tools(session)
                    
                    # Find the read_neo4j_cypher tool
                    cypher_tool = None
                    for tool in mcp_tools:
                        if tool.name == "read_neo4j_cypher":
                            cypher_tool = tool
                            break
                    
                    if not cypher_tool:
                        return {"error": "Neo4j MCP tool not available"}
                    
                    # Build Cypher query
                    # AUS rules are part of general underwriting rules, not a separate category
                    query = f"""
                    MATCH (rule:UnderwritingRule) 
                    WHERE '{loan_program}' IN rule.loan_programs
                    RETURN rule
                    """
                    
                    # Execute query using MCP tool
                    result = await cypher_tool.ainvoke({"query": query})
                    return result
        
        # Run the async query
        result = asyncio.run(query_neo4j())
        
        if "error" in result:
            return json.dumps(result, indent=2)
        
        # Format the result
        formatted_result = {
            "loan_program": loan_program,
            "aus_system": aus_system,
            "aus_rules": result,
            "source": "Neo4j UnderwritingRule nodes with category='AUSRules' via MCP",
            "query_used": f"MATCH (rule:UnderwritingRule) WHERE rule.category = 'AUSRules' AND rule.loan_program = '{loan_program}' RETURN rule"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting AUS rules: {e}")
        return json.dumps({
            "error": f"Failed to get AUS rules: {str(e)}",
            "loan_program": loan_program,
            "aus_system": aus_system
        })


def validate_tool(tool_input: str) -> bool:
    """
    Validate that the tool input is properly formatted.
    
    Args:
        tool_input: The input string to validate
        
    Returns:
        bool: True if input is valid, False otherwise
    """
    try:
        # Basic validation - check if it contains expected parameters
        required_terms = ["loan_program"]
        return any(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False

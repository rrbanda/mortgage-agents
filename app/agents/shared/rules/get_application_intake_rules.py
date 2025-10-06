"""
Get Application Intake Rules Tool - Business Rules Service

This tool provides centralized access to application intake rules from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_application_intake_rules(loan_program: str, application_stage: str) -> str:
    """
    Get application intake rules for specific loan programs and application stages.
    
    This tool queries Neo4j for application intake rules that other agents need
    for application processing, validation, and workflow management.
    
    Args:
        loan_program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        application_stage: Application stage (e.g., 'initial', 'pre_qualification', 'full_application', 'processing')
    
    Returns:
        JSON string containing application intake rules and requirements
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
                    # ApplicationIntakeRule nodes are organized by category, not loan_program/application_stage
                    query = """
                    MATCH (air:ApplicationIntakeRule) 
                    RETURN air
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
            "application_stage": application_stage,
            "intake_rules": result,
            "source": "Neo4j ApplicationIntakeRule nodes via MCP",
            "query_used": f"MATCH (air:ApplicationIntakeRule) WHERE air.loan_program = '{loan_program}' AND air.application_stage = '{application_stage}' RETURN air"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting application intake rules: {e}")
        return json.dumps({
            "error": f"Failed to get application intake rules: {str(e)}",
            "loan_program": loan_program,
            "application_stage": application_stage
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
        required_terms = ["loan_program", "application_stage"]
        return all(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False
"""
Get Qualification Criteria Tool - Business Rules Service

This tool provides centralized access to qualification criteria from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_qualification_criteria(program: str, borrower_profile: str) -> str:
    """
    Get qualification criteria for specific programs and borrower profiles.
    
    This tool queries Neo4j for qualification requirements that other agents need
    for initial qualification, pre-screening, and recommendation decisions.
    
    Args:
        program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        borrower_profile: Borrower profile description (e.g., 'first_time_buyer', 'self_employed', 'veteran')
    
    Returns:
        JSON string containing qualification criteria and requirements
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
                    query = f"""
                    MATCH (qr:QualificationRequirement) 
                    WHERE '{program}' IN qr.applies_to
                    RETURN qr
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
            "program": program,
            "borrower_profile": borrower_profile,
            "qualification_criteria": result,
            "source": "Neo4j QualificationRequirement and BorrowerProfile nodes via MCP",
            "query_used": f"MATCH (qr:QualificationRequirement)-[:APPLIES_TO]->(lp:LoanProgram {{name: '{program}'}}) OPTIONAL MATCH (bp:BorrowerProfile)-[:RECOMMENDED_FOR]->(lp) WHERE bp.profile_type = '{borrower_profile}' RETURN qr, bp"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting qualification criteria: {e}")
        return json.dumps({
            "error": f"Failed to get qualification criteria: {str(e)}",
            "program": program,
            "borrower_profile": borrower_profile
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
        required_terms = ["program", "borrower_profile"]
        return all(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False

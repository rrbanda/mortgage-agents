"""
Get Loan Program Requirements Tool - Business Rules Service

This tool provides centralized access to loan program requirements from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_loan_program_requirements(program_type: str, include_qualification: bool = True) -> str:
    """
    Get general loan program information and features (NOT credit requirements).
    
    This tool queries Neo4j for general loan program information that other agents need
    for recommendations, explanations, and program features. 
    
    ⚠️  DO NOT USE THIS TOOL FOR CREDIT REQUIREMENTS - use get_underwriting_rules instead!
    
    Args:
        program_type: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda', 'jumbo') or 'all'
        include_qualification: Whether to include general qualification information (not credit-specific)
    
    Returns:
        JSON string containing loan program details and general requirements
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
                    
                    # Build Cypher query based on parameters
                    if program_type.lower() == "all":
                        query = """
                        MATCH (lp:LoanProgram)
                        OPTIONAL MATCH (lp)-[:HAS_REQUIREMENT]->(qr:QualificationRequirement)
                        RETURN lp, collect(qr) as requirements
                        """
                    else:
                        query = f"""
                        MATCH (lp:LoanProgram)
                        WHERE lp.name = '{program_type.upper()}'
                        OPTIONAL MATCH (lp)-[:HAS_REQUIREMENT]->(qr:QualificationRequirement)
                        RETURN lp, collect(qr) as requirements
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
            "program_type": program_type,
            "include_qualification": include_qualification,
            "programs": result,
            "source": "Neo4j LoanProgram and QualificationRequirement nodes via MCP",
            "query_used": f"MATCH (lp:LoanProgram) WHERE lp.name = '{program_type}' OPTIONAL MATCH (lp)-[:HAS_REQUIREMENT]->(qr:QualificationRequirement) RETURN lp, collect(qr) as requirements"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting loan program requirements: {e}")
        return json.dumps({
            "error": f"Failed to get loan program requirements: {str(e)}",
            "program_type": program_type,
            "include_qualification": include_qualification
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
        required_terms = ["program_type"]
        return any(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False

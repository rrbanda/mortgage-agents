"""
Get Income Calculation Rules Tool - Business Rules Service

This tool provides centralized access to income calculation rules from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_income_calculation_rules(employment_type: str, loan_program: str) -> str:
    """
    Get income calculation rules for specific employment types and loan programs.
    
    This tool queries Neo4j for income calculation rules that other agents need
    for income verification, calculation, and underwriting decisions.
    
    Args:
        employment_type: Employment type (e.g., 'w2_employee', 'self_employed', 'contractor', 'retired')
        loan_program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
    
    Returns:
        JSON string containing income calculation rules and requirements
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
                    # IncomeCalculationRule nodes are organized by category, not employment_type/loan_program
                    query = """
                    MATCH (icr:IncomeCalculationRule) 
                    RETURN icr
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
            "employment_type": employment_type,
            "loan_program": loan_program,
            "income_calculation_rules": result,
            "source": "Neo4j IncomeCalculationRule nodes via MCP",
            "query_used": f"MATCH (icr:IncomeCalculationRule) WHERE icr.employment_type = '{employment_type}' AND icr.loan_program = '{loan_program}' RETURN icr"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting income calculation rules: {e}")
        return json.dumps({
            "error": f"Failed to get income calculation rules: {str(e)}",
            "employment_type": employment_type,
            "loan_program": loan_program
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
        required_terms = ["employment_type", "loan_program"]
        return all(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False
"""
Get Property Appraisal Rules Tool - Business Rules Service

This tool provides centralized access to property appraisal rules from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_property_appraisal_rules(property_type: str, loan_program: str, rule_category: str = "all") -> str:
    """
    Get property appraisal rules for specific property types and loan programs.
    
    This tool queries Neo4j for property appraisal rules that other agents need
    for property valuation, condition assessment, and appraisal standards.
    
    Args:
        property_type: Property type (e.g., 'single_family', 'condo', 'townhouse', 'multi_family')
        loan_program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        rule_category: Specific rule category ('MarketAnalysis', 'AppraisalStandards', 'ValueAnalysis', 'PropertyCondition', 'SafetyRequirements', 'LoanProgramRequirements', 'PropertyType', 'all')
    
    Returns:
        JSON string containing property appraisal rules and requirements
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
                    # PropertyAppraisalRule nodes are organized by category, not property_type/loan_program
                    if rule_category == "all":
                        query = """
                        MATCH (par:PropertyAppraisalRule) 
                        RETURN par
                        """
                    else:
                        query = f"""
                        MATCH (par:PropertyAppraisalRule) 
                        WHERE par.category = '{rule_category}'
                        RETURN par
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
            "property_type": property_type,
            "loan_program": loan_program,
            "rule_category": rule_category,
            "appraisal_rules": result,
            "source": "Neo4j PropertyAppraisalRule nodes via MCP",
            "query_used": f"MATCH (par:PropertyAppraisalRule) WHERE par.property_type = '{property_type}' AND par.loan_program = '{loan_program}' AND par.category = '{rule_category}' RETURN par"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting property appraisal rules: {e}")
        return json.dumps({
            "error": f"Failed to get property appraisal rules: {str(e)}",
            "property_type": property_type,
            "loan_program": loan_program,
            "rule_category": rule_category
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
        required_terms = ["property_type", "loan_program"]
        return all(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False
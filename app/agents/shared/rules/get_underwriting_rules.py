"""
Get Underwriting Rules Tool - Business Rules Service

This tool provides centralized access to underwriting rules from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_underwriting_rules(loan_program: str, credit_score: int, rule_category: str = "all") -> str:
    """
    Get underwriting rules for specific loan programs and credit scores.
    
     USE THIS TOOL FOR CREDIT REQUIREMENTS QUESTIONS!
    
    This tool queries Neo4j for underwriting rules that other agents need
    for credit analysis, DTI calculations, and underwriting decisions.
    
    Args:
        loan_program: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        credit_score: Borrower's credit score (300-850)
        rule_category: Specific rule category ('CreditAnalysis', 'DTIAnalysis', 'DecisionMatrix', 'AUSRules', 'all')
    
    Returns:
        JSON string containing underwriting rules and requirements
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
                    if rule_category == "all":
                        query = f"""
                        MATCH (r:UnderwritingRule) 
                        WHERE '{loan_program}' IN r.loan_programs
                        RETURN r
                        """
                    else:
                        query = f"""
                        MATCH (r:UnderwritingRule) 
                        WHERE '{loan_program}' IN r.loan_programs AND r.category = '{rule_category}'
                        RETURN r
                        """
                    
                    # Execute query using MCP tool
                    result = await cypher_tool.ainvoke({"query": query})
                    return {"result": result, "query": query}
        
        # Run the async query
        query_result = asyncio.run(query_neo4j())
        
        if "error" in query_result:
            return json.dumps(query_result, indent=2)
        
        # Format the result
        formatted_result = {
            "loan_program": loan_program,
            "credit_score": credit_score,
            "rule_category": rule_category,
            "rules": query_result.get("result", []),
            "source": "Neo4j UnderwritingRule nodes via MCP",
            "query_used": query_result.get("query", "")
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting underwriting rules: {e}")
        return json.dumps({
            "error": f"Failed to get underwriting rules: {str(e)}",
            "loan_program": loan_program,
            "credit_score": credit_score,
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
        required_terms = ["loan_program", "credit_score"]
        return all(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False

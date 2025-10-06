"""
Get Document Requirements Tool - Business Rules Service

This tool provides centralized access to document requirements from Neo4j.
Other agents call this tool instead of querying Neo4j directly.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_document_requirements(loan_type: str, property_type: str = "single_family", document_category: str = "all") -> str:
    """
    Get document requirements for specific loan types and property types.
    
    This tool queries Neo4j for document verification rules that other agents need
    for document processing, validation, and completeness checks.
    
    Args:
        loan_type: Loan program type (e.g., 'conventional', 'fha', 'va', 'usda')
        property_type: Property type (e.g., 'single_family', 'condo', 'townhouse', 'multi_family')
        document_category: Document category ('URLAValidation', 'IdentityVerification', 'IncomeVerification', 'all')
    
    Returns:
        JSON string containing document requirements and verification rules
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
                    # DocumentVerificationRule nodes are organized by category, not loan_type/property_type
                    if document_category == "all":
                        query = """
                        MATCH (dvr:DocumentVerificationRule) 
                        RETURN dvr
                        """
                    else:
                        query = f"""
                        MATCH (dvr:DocumentVerificationRule) 
                        WHERE dvr.category = '{document_category}'
                        RETURN dvr
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
            "loan_type": loan_type,
            "property_type": property_type,
            "document_category": document_category,
            "required_documents": result,
            "source": "Neo4j DocumentVerificationRule nodes via MCP",
            "query_used": f"MATCH (dvr:DocumentVerificationRule) WHERE dvr.loan_type = '{loan_type}' AND dvr.property_type = '{property_type}' AND dvr.category = '{document_category}' RETURN dvr"
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting document requirements: {e}")
        return json.dumps({
            "error": f"Failed to get document requirements: {str(e)}",
            "loan_type": loan_type,
            "property_type": property_type,
            "document_category": document_category
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
        required_terms = ["loan_type"]
        return any(term in tool_input.lower() for term in required_terms)
    except Exception:
        return False

"""
Business Rules - Neo4j MCP Integration

IMPORTANT: Business rules tools are now loaded dynamically via official MCP pattern.

The agent uses neo4j_mcp_loader.get_neo4j_mcp_tools() which provides:
- get_neo4j_schema: List all nodes and relationships
- read_neo4j_cypher: Execute read Cypher queries
- write_neo4j_cypher: Execute write Cypher queries

Agent decides when to call these tools based on prompts.
No hardcoded wrapper tools needed.
"""

from typing import List
from langchain_core.tools import BaseTool


def get_all_business_rules_agent_tools() -> List[BaseTool]:
    """
    DEPRECATED: Business rules are now loaded via official MCP pattern.
    
    Use neo4j_mcp_loader.get_neo4j_mcp_tools() instead.
    
    Returns empty list for backward compatibility.
    """
    return []


def get_tool_descriptions() -> dict:
    """
    Returns descriptions for Neo4j MCP tools.
    """
    return {
        "get_neo4j_schema": "List all nodes, attributes and relationships in Neo4j database",
        "read_neo4j_cypher": "Execute read Cypher query on Neo4j for business rules",
        "write_neo4j_cypher": "Execute write Cypher query on Neo4j database",
    }


__all__ = [
    "get_all_business_rules_agent_tools",
    "get_tool_descriptions",
]

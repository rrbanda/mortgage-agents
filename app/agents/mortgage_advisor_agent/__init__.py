"""
MortgageAdvisorAgent - Intelligent Mortgage Guidance and Education

This agent provides comprehensive mortgage guidance, loan program education,
and personalized recommendations to help users navigate the mortgage process.

The MortgageAdvisorAgent specializes in:
- Mortgage education and loan program comparison
- Personalized loan selection guidance based on borrower profile
- Qualification requirements and credit guidance
- Dynamic MCP integration for business rules (Neo4j) and credit checks (ToolHive)

Structure:
- agent.py: Main agent creation and configuration
- prompts.yaml: Co-located prompt definitions specific to mortgage guidance
- tools/: Individual tool modules for focused mortgage advisory capabilities
- tests/: Comprehensive test suite for mortgage guidance functionality
- ../shared/: Reusable utilities shared across all agents (prompt loader, etc.)

Tools (3 operational + N MCP tools dynamically loaded at runtime):

Operational Tools (3):
- explain_loan_programs: Compare and explain different mortgage loan programs
- recommend_loan_program: Provide personalized loan recommendations  
- check_qualification_requirements: Analyze qualification requirements and identify gaps

MCP Tools (dynamically loaded at agent initialization):
- N Credit Check MCP tools: Loaded from ToolHive via get_mcp_credit_tools()
- M Neo4j MCP tools: Loaded from Neo4j MCP server via get_neo4j_mcp_tools()
  (includes business rules queries like loan requirements, qualification criteria, underwriting rules)

Official LangGraph MCP Pattern:
- Tools are discovered dynamically from MCP servers
- Agent receives all available tools and decides when to call them
- No hardcoded MCP wrapper tools

Benefits:
- Focused mortgage expertise with deep domain knowledge
- Dynamic business rules via Neo4j MCP integration
- Real-time credit checks via ToolHive MCP integration
- Clear separation from data collection and processing concerns
- Professional mortgage advisor experience for users
"""

from .agent import create_mortgage_advisor_agent
from .tools import (
    explain_loan_programs,
    recommend_loan_program, 
    check_qualification_requirements,
    get_all_mortgage_advisor_tools,
    validate_all_tools
)
from ..shared.prompt_loader import (
    load_agent_prompt as load_mortgage_advisor_prompt,
    get_agent_prompt_loader,
    validate_agent_prompts
)

__all__ = [
    # Main agent
    "create_mortgage_advisor_agent",
    
    # 3 operational tools (NO hardcoded business rules)
    "explain_loan_programs",
    "recommend_loan_program", 
    "check_qualification_requirements",
    
    # Tool management
    "get_all_mortgage_advisor_tools",
    "validate_all_tools",
    
    # Prompt management (shared utilities)
    "load_mortgage_advisor_prompt",
    "get_agent_prompt_loader",
    "validate_agent_prompts"
]

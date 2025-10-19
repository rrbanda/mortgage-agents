"""
UnderwritingAgent - Intelligent Mortgage Underwriting and Decision Making

This agent provides comprehensive mortgage underwriting analysis and makes lending
decisions based on risk assessment and regulatory guidelines.

The UnderwritingAgent specializes in:
- Credit risk analysis and evaluation (NO hardcoded thresholds)
- Debt-to-income calculations (pure math, NO hardcoded limits)
- Income source evaluation (NO hardcoded qualification rules)
- Final underwriting decisions (NO hardcoded approval rules)
- Dynamic MCP integration for business rules (Neo4j) and credit checks (ToolHive)

Structure:
- agent.py: Main agent creation and configuration
- prompts.yaml: Co-located prompt definitions specific to underwriting decisions
- tools/: Individual tool modules for focused underwriting capabilities (5 operational tools)
- tests/: Comprehensive test suite for underwriting functionality
- ../shared/: Reusable utilities shared across all agents (prompt loader, etc.)

Tools (5 operational + N MCP tools dynamically loaded at runtime):

Operational Tools (5):
- analyze_credit_risk: Displays credit information (NO hardcoded thresholds)
- calculate_debt_to_income: DTI calculation only (NO hardcoded limits)
- evaluate_income_sources: Displays income/employment info (NO qualification rules)
- run_aus_check: AUS submission simulation (NO hardcoded AUS rules)
- make_underwriting_decision: Analyzes decision factors (NO approval/denial rules)

MCP Tools (dynamically loaded at agent initialization):
- N Credit Check MCP tools: Loaded from ToolHive via get_mcp_credit_tools()
- M Neo4j MCP tools: Loaded from Neo4j MCP server via get_neo4j_mcp_tools()
  (includes business rules queries via read_neo4j_cypher for underwriting rules, AUS rules, income calculation rules)

Official LangGraph MCP Pattern:
- Tools are discovered dynamically from MCP servers
- Agent receives all available tools and decides when to call them
- No hardcoded MCP wrapper tools

Benefits:
- Professional underwriting expertise with clean operational tools
- Dynamic business rules via Neo4j MCP integration
- Real-time credit checks via ToolHive MCP integration
- Clear separation from application processing and customer interaction
- Automated decision making with manual review triggers for complex cases
"""

from .agent import create_underwriting_agent
from .tools import (
    analyze_credit_risk,
    calculate_debt_to_income, 
    evaluate_income_sources,
    run_aus_check,
    make_underwriting_decision,
    get_all_underwriting_agent_tools,
    validate_all_tools
)
from ..shared.prompt_loader import (
    load_agent_prompt as load_underwriting_agent_prompt,
    get_agent_prompt_loader,
    validate_agent_prompts
)

__all__ = [
    # Main agent
    "create_underwriting_agent",
    
    # All 5 operational tools (NO hardcoded business rules)
    "analyze_credit_risk",
    "calculate_debt_to_income", 
    "evaluate_income_sources",
    "run_aus_check",
    "make_underwriting_decision",
    
    # Tool management
    "get_all_underwriting_agent_tools",
    "validate_all_tools",
    
    # Prompt management (shared utilities)
    "load_underwriting_agent_prompt",
    "get_agent_prompt_loader",
    "validate_agent_prompts"
]

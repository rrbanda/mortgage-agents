"""
🎯 STANDARDIZED LANGGRAPH TOOL TEMPLATE
======================================

This template represents the OPTIMAL pattern for LangGraph tools that work reliably
with LLM agents. All tools should follow this exact pattern for consistency.

✅ PROVEN WORKING PATTERN:
- Simple @tool decorator (no complex schemas)
- Single parameter: tool_input: str
- Return type: str (not Dict[str, Any])
- Standardized input parsing
- Proper error handling
- Clear docstring with Args/Returns

❌ AVOID THESE ANTIPATTERNS:
- Multiple parameters (breaks LLM tool calling)
- Complex @tool decorators with schemas
- Returning Dict[str, Any] (LLMs need strings)
- Custom parsing in each tool (use shared parser)
- Missing or unclear docstrings
"""

from langchain_core.tools import tool
from typing import Any
import logging
from agents.shared.input_parser import parse_mortgage_application
from utils.database import initialize_connection, get_neo4j_connection

# Configure logging
logger = logging.getLogger(__name__)


@tool
def template_tool(tool_input: str) -> str:
    """
    [DESCRIPTIVE TOOL PURPOSE] - One line summary of what this tool does.
    
    [DETAILED DESCRIPTION] - 2-3 sentences explaining:
    - What business process this tool handles
    - What data sources it uses (Neo4j rules, calculations, etc.)
    - What kind of analysis/processing it provides
    
    Args:
        tool_input: [DESCRIPTION OF EXPECTED INPUT FORMAT]
        
    Example:
        "Credit: 720, Income: 95000, Loan: 390000, Property: 450000, DTI: 15.2%"
    
    Returns:
        String containing [DESCRIPTION OF OUTPUT FORMAT]
    """
    
    try:
        # 1. STANDARDIZED INPUT PARSING
        # Use shared parser for consistent data extraction
        parsed_data = parse_mortgage_application(tool_input)
        
        # 2. EXTRACT REQUIRED PARAMETERS
        # Get all needed values with proper defaults
        required_param_1 = parsed_data.get("param_1") or "default_value"
        required_param_2 = parsed_data.get("param_2") or 0.0
        
        # Optional: Additional regex parsing for tool-specific data
        import re
        specific_match = re.search(r'specific_pattern:\s*([a-z]+)', tool_input.lower())
        specific_value = specific_match.group(1) if specific_match else "default"
        
        # 3. VALIDATE ESSENTIAL INPUTS
        # Check for critical missing data
        if not required_param_1 or required_param_2 <= 0:
            return f"""
❌ **MISSING REQUIRED INFORMATION**

This tool requires:
• [List required data points]
• [Format examples]

Please provide the missing information and try again.
"""
        
        # 4. INITIALIZE NEO4J CONNECTION (if needed)
        initialize_connection()
        connection = get_neo4j_connection()
        
        # 5. QUERY NEO4J BUSINESS RULES (if applicable)
        business_rules = connection.query("""
            MATCH (r:RuleType) WHERE r.applies_to = 'tool_domain'
            RETURN r
        """)
        
        # 6. PERFORM BUSINESS LOGIC
        # Core business calculations/analysis
        result_data = _perform_core_business_logic(
            param_1=required_param_1,
            param_2=required_param_2,
            rules=business_rules
        )
        
        # 7. FORMAT STRUCTURED OUTPUT
        # Always return user-friendly string format
        report = [
            "🎯 **[TOOL NAME] RESULTS**",
            f"**Parameter 1:** {required_param_1}",
            f"**Parameter 2:** {required_param_2}",
            "",
            "📊 **ANALYSIS:**",
            f"• Key Finding 1: {result_data['finding_1']}",
            f"• Key Finding 2: {result_data['finding_2']}",
            "",
            "✅ **RECOMMENDATIONS:**",
            f"• {result_data['recommendation_1']}",
            f"• {result_data['recommendation_2']}",
            "",
            f"📅 **Generated:** {result_data['timestamp']}"
        ]
        
        return "\n".join(report)
        
    except Exception as e:
        # 8. CONSISTENT ERROR HANDLING
        logger.error(f"Error in [tool_name]: {e}")
        return f"❌ Error processing [tool_name]: {str(e)}"


def _perform_core_business_logic(param_1: Any, param_2: Any, rules: list) -> dict:
    """
    Private helper function for core business logic.
    
    Separates business logic from tool interface for better testing
    and maintainability.
    """
    from datetime import datetime
    
    # Implement actual business logic here
    result = {
        "finding_1": f"Analysis of {param_1}",
        "finding_2": f"Calculation result: {param_2 * 1.1}",
        "recommendation_1": "Based on the analysis...",
        "recommendation_2": "Consider the following...",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result


# 🧪 TESTING HELPER
def test_template_tool():
    """Test function to verify tool works correctly."""
    test_input = "param_1: test_value, param_2: 100, specific_pattern: example"
    
    try:
        result = template_tool.invoke({"tool_input": test_input})
        print(f"✅ Template tool test passed")
        print(f"📊 Output type: {type(result)}")
        print(f"📝 Output length: {len(result)} characters")
        return True
    except Exception as e:
        print(f"❌ Template tool test failed: {e}")
        return False


if __name__ == "__main__":
    test_template_tool()

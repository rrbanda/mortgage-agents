"""
List Twilio Numbers Tool - MCP Integration

This tool lists available Twilio phone numbers via MCP server,
demonstrating MCP integration for account management.
"""

import logging
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import json

logger = logging.getLogger(__name__)

class TwilioNumbersInput(BaseModel):
    """Input schema for listing Twilio numbers"""
    filter_type: Optional[str] = Field(description="Filter by number type: 'local', 'toll-free', or 'all'", default="all")

@tool  
def list_twilio_numbers(tool_input: str = "") -> str:
    """
    List active phone numbers in Twilio account via MCP server.
    
    This tool demonstrates MCP integration by querying Twilio account
    information through the MCP server instead of direct API calls.
    
    Args:
        tool_input: Optional JSON string with filter_type
        
    Returns:
        String containing list of available phone numbers or error message
    """
    try:
        # Parse input (optional)
        filter_type = "all"
        if tool_input.strip():
            try:
                input_data = json.loads(tool_input)
                filter_type = input_data.get('filter_type', 'all')
            except:
                # If input is not JSON, treat as filter type string
                filter_type = tool_input.strip()
        
        logger.info(f"Listing Twilio numbers via MCP (filter: {filter_type})")
        
        # Mock MCP response - in real implementation this would call the MCP server
        # TODO: Replace with actual MCP server call
        mock_numbers = [
            {
                "phone_number": "+1234567890",
                "friendly_name": "Main Business Line",
                "phone_number_type": "local",
                "capabilities": ["SMS", "Voice"],
                "status": "active"
            },
            {
                "phone_number": "+1800555LOAN", 
                "friendly_name": "Toll-Free Support",
                "phone_number_type": "toll-free",
                "capabilities": ["SMS", "Voice"],
                "status": "active"
            },
            {
                "phone_number": "+1555123TEST",
                "friendly_name": "Test Number",
                "phone_number_type": "local", 
                "capabilities": ["SMS"],
                "status": "active"
            }
        ]
        
        # Apply filter
        filtered_numbers = mock_numbers
        if filter_type != "all":
            filtered_numbers = [n for n in mock_numbers if n["phone_number_type"] == filter_type]
        
        if not filtered_numbers:
            return f"📱 No phone numbers found with filter '{filter_type}'"
        
        result = f"📱 **TWILIO PHONE NUMBERS** (Filter: {filter_type})\n\n"
        
        for i, number in enumerate(filtered_numbers, 1):
            capabilities = ", ".join(number["capabilities"])
            result += f"""**{i}. {number['friendly_name']}**
• Number: {number['phone_number']}
• Type: {number['phone_number_type'].title()}
• Capabilities: {capabilities}
• Status: {number['status'].upper()}

"""
        
        result += f"📊 **Total Numbers:** {len(filtered_numbers)}"
        
        if filter_type != "all":
            total_all = len(mock_numbers)
            result += f" (of {total_all} total)"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in list_twilio_numbers: {e}")
        return f" Error listing Twilio numbers: {str(e)}"

def validate_tool() -> bool:
    """Validate that the list Twilio numbers tool works correctly"""
    try:
        # Test without input
        result1 = list_twilio_numbers.invoke({"tool_input": ""})
        
        # Test with filter
        result2 = list_twilio_numbers.invoke({"tool_input": json.dumps({"filter_type": "local"})})
        
        return (isinstance(result1, str) and "TWILIO PHONE NUMBERS" in result1 and
                isinstance(result2, str) and "TWILIO PHONE NUMBERS" in result2)
        
    except Exception as e:
        logger.error(f"List Twilio numbers tool validation failed: {e}")
        return False

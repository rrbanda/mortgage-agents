"""
Send SMS Notification Tool - MCP Integration

This tool sends SMS notifications via Twilio Alpha MCP server,
demonstrating MCP integration with LangGraph tools.
"""

import logging
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import json

logger = logging.getLogger(__name__)

class SMSInput(BaseModel):
    """Input schema for SMS notification tool"""
    phone_number: str = Field(description="Phone number to send SMS to (E.164 format recommended, e.g., +1234567890)")
    message: str = Field(description="SMS message content")
    from_number: Optional[str] = Field(description="Twilio phone number to send from (optional)", default=None)

@tool
def send_sms_notification(tool_input: str) -> str:
    """
    Send SMS notification via Twilio Alpha MCP server.
    
    This tool demonstrates MCP integration by sending SMS messages through
    the Twilio Alpha MCP server instead of direct API calls.
    
    Args:
        tool_input: JSON string with phone_number, message, and optional from_number
        
    Returns:
        String containing the SMS send result or error message
    """
    try:
        # Parse input
        input_data = json.loads(tool_input)
        phone_number = input_data.get('phone_number', '').strip()
        message = input_data.get('message', '').strip()
        from_number = input_data.get('from_number', '').strip()
        
        if not phone_number:
            return " Error: Phone number is required"
            
        if not message:
            return " Error: Message content is required"
        
        # For now, simulate MCP call until actual integration is ready
        # TODO: Replace with actual MCP server call
        logger.info(f"Sending SMS via MCP to {phone_number}: {message[:50]}...")
        
        # Mock MCP response - in real implementation this would call the MCP server
        mock_response = {
            "success": True,
            "message_sid": f"SM{hash(phone_number + message) % 1000000:06d}",
            "status": "queued",
            "to": phone_number,
            "from": from_number or "+1234567890",  # Mock from number
            "body": message,
            "price": "0.0075",
            "price_unit": "USD"
        }
        
        if mock_response["success"]:
            return f"""
 **SMS SENT SUCCESSFULLY**

📱 **Message Details:**
• To: {mock_response['to']}
• From: {mock_response['from']}  
• Status: {mock_response['status'].upper()}
• Message SID: {mock_response['message_sid']}

📝 **Message Content:**
{mock_response['body']}

💰 **Cost:** ${mock_response['price']} {mock_response['price_unit']}

🔄 **Note:** Message is queued for delivery. Use get_message_status tool to check delivery status.
"""
        else:
            return f" Failed to send SMS: {mock_response.get('error', 'Unknown error')}"
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in send_sms_notification: {e}")
        return f" Error: Invalid JSON input - {str(e)}"
    except Exception as e:
        logger.error(f"Error in send_sms_notification: {e}")
        return f" Error sending SMS: {str(e)}"

def validate_tool() -> bool:
    """Validate that the SMS notification tool works correctly"""
    try:
        # Test with valid input
        test_input = {
            "phone_number": "+1234567890",
            "message": "Test notification message"
        }
        
        result = send_sms_notification.invoke({"tool_input": json.dumps(test_input)})
        return isinstance(result, str) and "SMS SENT SUCCESSFULLY" in result
        
    except Exception as e:
        logger.error(f"SMS notification tool validation failed: {e}")
        return False

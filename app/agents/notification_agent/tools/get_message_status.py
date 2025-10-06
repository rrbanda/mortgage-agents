"""
Get Message Status Tool - MCP Integration

This tool checks SMS message delivery status via Twilio Alpha MCP server,
demonstrating MCP integration for message tracking.
"""

import logging
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import json
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MessageStatusInput(BaseModel):
    """Input schema for message status check"""
    message_sid: str = Field(description="Twilio message SID to check status for")

@tool
def get_message_status(tool_input: str) -> str:
    """
    Check SMS message delivery status via Twilio Alpha MCP server.
    
    This tool demonstrates MCP integration by querying message status
    through the MCP server instead of direct API calls.
    
    Args:
        tool_input: JSON string with message_sid
        
    Returns:
        String containing message status details or error message
    """
    try:
        # Parse input
        input_data = json.loads(tool_input)
        message_sid = input_data.get('message_sid', '').strip()
        
        if not message_sid:
            return " Error: Message SID is required"
        
        if not message_sid.startswith('SM'):
            return " Error: Invalid message SID format (should start with 'SM')"
        
        logger.info(f"Checking message status via MCP for SID: {message_sid}")
        
        # Mock MCP response - in real implementation this would call the MCP server
        # TODO: Replace with actual MCP server call
        
        # Generate realistic mock status based on SID
        possible_statuses = ["delivered", "sent", "received", "failed", "undelivered"]
        weights = [0.7, 0.15, 0.05, 0.05, 0.05]  # Most messages are delivered
        status = random.choices(possible_statuses, weights=weights)[0]
        
        # Mock timestamp (recent)
        sent_time = datetime.now() - timedelta(minutes=random.randint(1, 60))
        updated_time = sent_time + timedelta(seconds=random.randint(1, 300))
        
        mock_response = {
            "message_sid": message_sid,
            "status": status,
            "to": "+1234567890",  # Mock phone number
            "from": "+1800555LOAN",  # Mock from number
            "body": "Your mortgage application has been received...",
            "date_created": sent_time.isoformat(),
            "date_updated": updated_time.isoformat(),
            "date_sent": sent_time.isoformat() if status != "failed" else None,
            "price": "0.0075",
            "price_unit": "USD",
            "error_code": "30007" if status == "failed" else None,
            "error_message": "Message blocked by carrier" if status == "failed" else None
        }
        
        # Format response based on status
        status_emoji = {
            "delivered": "",
            "sent": "📤", 
            "received": "📨",
            "failed": "",
            "undelivered": "⚠️"
        }
        
        result = f"""
{status_emoji.get(status, '📱')} **MESSAGE STATUS: {status.upper()}**

📱 **Message Details:**
• SID: {mock_response['message_sid']}
• To: {mock_response['to']}
• From: {mock_response['from']}
• Status: {mock_response['status'].upper()}

📝 **Message Content:**
{mock_response['body'][:100]}{'...' if len(mock_response['body']) > 100 else ''}

⏰ **Timestamps:**
• Created: {sent_time.strftime('%Y-%m-%d %H:%M:%S')}
• Updated: {updated_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if mock_response.get('date_sent'):
            sent_dt = datetime.fromisoformat(mock_response['date_sent'])
            result += f"• Sent: {sent_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        result += f"\n💰 **Cost:** ${mock_response['price']} {mock_response['price_unit']}\n"
        
        # Add error details if failed
        if status == "failed" and mock_response.get('error_code'):
            result += f"""
 **Error Details:**
• Error Code: {mock_response['error_code']}
• Error Message: {mock_response['error_message']}
"""
        
        # Add status-specific info
        if status == "delivered":
            result += "\n🎯 **Result:** Message successfully delivered to recipient"
        elif status == "sent":
            result += "\n🚀 **Result:** Message sent to carrier, awaiting delivery confirmation"
        elif status == "failed":
            result += "\n💥 **Result:** Message delivery failed - please check phone number and try again"
        elif status == "undelivered":
            result += "\n⚠️  **Result:** Message could not be delivered - recipient may be unreachable"
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in get_message_status: {e}")
        return f" Error: Invalid JSON input - {str(e)}"
    except Exception as e:
        logger.error(f"Error in get_message_status: {e}")
        return f" Error checking message status: {str(e)}"

def validate_tool() -> bool:
    """Validate that the message status tool works correctly"""
    try:
        # Test with valid message SID
        test_input = {"message_sid": "SM123456789"}
        
        result = get_message_status.invoke({"tool_input": json.dumps(test_input)})
        return isinstance(result, str) and "MESSAGE STATUS:" in result
        
    except Exception as e:
        logger.error(f"Message status tool validation failed: {e}")
        return False

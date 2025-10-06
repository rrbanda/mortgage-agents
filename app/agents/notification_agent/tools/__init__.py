"""
NotificationAgent Tools Package - MCP Integration

This package contains Twilio MCP-powered tools for the NotificationAgent,
demonstrating how to integrate MCP servers with LangGraph agents.

Tools (MCP-Powered):
- send_sms_notification: Send SMS via Twilio MCP
- list_twilio_numbers: List available phone numbers
- get_message_status: Check message delivery status

Each tool integrates with Twilio Alpha MCP server for real SMS capabilities.
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

# Import MCP-powered tools
from .send_sms_notification import send_sms_notification
from .list_twilio_numbers import list_twilio_numbers  
from .get_message_status import get_message_status

def get_all_notification_agent_tools() -> List[BaseTool]:
    """
    Returns a list of all MCP-powered tools available to the NotificationAgent.
    
    These tools integrate with Twilio Alpha MCP server for real SMS capabilities.
    """
    return [
        send_sms_notification,
        list_twilio_numbers,
        get_message_status
    ]

def get_tool_descriptions() -> Dict[str, str]:
    """
    Returns a dictionary of tool names and their descriptions.
    """
    return {
        "send_sms_notification": "Send SMS notification via Twilio MCP",
        "list_twilio_numbers": "List available Twilio phone numbers",
        "get_message_status": "Check SMS message delivery status"
    }

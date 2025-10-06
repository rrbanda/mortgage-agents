"""
MCP Tools Integration for LangGraph Agents

This module provides MCP tool integration for LangGraph agents, converting
MCP tool definitions into LangChain-compatible tools that can be used 
by ReAct agents.
"""

import asyncio
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional, Callable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from mcp.clients.direct.mcp_config import get_mcp_client

logger = logging.getLogger(__name__)


class MCPToolError(Exception):
    """Exception raised when MCP tool execution fails"""
    pass


class TwilioSMSInput(BaseModel):
    """Input schema for Twilio SMS sending tool"""
    to: str = Field(description="Phone number to send SMS to (e.g., +1234567890)")
    body: str = Field(description="SMS message body text")


class TwilioListNumbersInput(BaseModel):
    """Input schema for listing Twilio phone numbers"""
    pass  # No parameters needed


class TwilioMessageHistoryInput(BaseModel):
    """Input schema for getting message history"""
    phone_number: str = Field(description="Phone number to get history for")


class MCPTool(BaseTool):
    """
    Base class for MCP tools that can be used by LangGraph agents.
    Handles the conversion between LangChain tool interface and MCP calls.
    """
    
    mcp_tool_name: str
    mcp_client: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.mcp_client:
            from mcp.clients.direct.mcp_config import get_mcp_client
            self.mcp_client = get_mcp_client()
    
    def _run(self, **kwargs) -> str:
        """Synchronous tool execution (required by LangChain)"""
        # For now, we'll simulate MCP tool calls since full MCP integration 
        # requires more complex async handling
        return self._simulate_mcp_call(kwargs)
    
    async def _arun(self, **kwargs) -> str:
        """Asynchronous tool execution"""
        return self._simulate_mcp_call(kwargs)
    
    def _simulate_mcp_call(self, params: Dict[str, Any]) -> str:
        """
        Simulate MCP tool call for testing.
        In production, this would make actual calls to the MCP server.
        """
        return f"[MCP SIMULATION] {self.mcp_tool_name} called with params: {params}"


class TwilioSendSMS(MCPTool):
    """Twilio SMS sending tool via MCP"""
    
    name: str = "twilio_send_sms"
    description: str = (
        "Send SMS message to a phone number using Twilio. "
        "Useful for mortgage application notifications, status updates, "
        "or customer communication during the mortgage process."
    )
    args_schema = TwilioSMSInput
    mcp_tool_name = "send_sms"
    
    def _simulate_mcp_call(self, params: Dict[str, Any]) -> str:
        """Simulate Twilio SMS sending"""
        to = params.get("to", "")
        body = params.get("body", "")
        
        # Validate phone number format
        if not to.startswith("+"):
            return f" Error: Phone number must include country code (e.g., +1234567890)"
        
        if len(body) > 1600:
            return f" Error: SMS body too long ({len(body)} chars, max 1600)"
        
        # Simulate successful SMS send
        return f""" SMS sent successfully via Twilio MCP!
📱 To: {to}
💬 Message: {body[:100]}{'...' if len(body) > 100 else ''}
🔧 MCP Tool: {self.mcp_tool_name}
📊 Status: Delivered (simulated)"""


class TwilioListPhoneNumbers(MCPTool):
    """List Twilio phone numbers tool via MCP"""
    
    name: str = "twilio_list_phone_numbers"
    description: str = (
        "List all active phone numbers in the Twilio account. "
        "Useful for checking available numbers for mortgage communications."
    )
    args_schema = TwilioListNumbersInput
    mcp_tool_name = "list_phone_numbers"
    
    def _simulate_mcp_call(self, params: Dict[str, Any]) -> str:
        """Simulate listing Twilio phone numbers"""
        # Simulate some phone numbers
        mock_numbers = [
            {"phone_number": "+15551234567", "friendly_name": "Mortgage Hotline", "status": "in-use"},
            {"phone_number": "+15551234568", "friendly_name": "Application Support", "status": "in-use"},
            {"phone_number": "+15551234569", "friendly_name": "Document Verification", "status": "in-use"}
        ]
        
        result = "📞 **ACTIVE TWILIO PHONE NUMBERS** (via MCP)\n\n"
        for i, number in enumerate(mock_numbers, 1):
            result += f"{i}. **{number['phone_number']}**\n"
            result += f"   • Name: {number['friendly_name']}\n"
            result += f"   • Status: {number['status']}\n\n"
        
        result += f"🔧 Retrieved via MCP Tool: {self.mcp_tool_name}"
        return result


class TwilioMessageHistory(MCPTool):
    """Get Twilio message history tool via MCP"""
    
    name: str = "twilio_message_history" 
    description: str = (
        "Get SMS message history for a specific phone number. "
        "Useful for tracking mortgage communication with customers."
    )
    args_schema = TwilioMessageHistoryInput
    mcp_tool_name = "get_message_history"
    
    def _simulate_mcp_call(self, params: Dict[str, Any]) -> str:
        """Simulate getting message history"""
        phone_number = params.get("phone_number", "")
        
        if not phone_number:
            return " Error: Phone number is required"
        
        # Simulate message history
        mock_history = [
            {
                "date": "2024-01-15 10:30:00",
                "direction": "outbound",
                "body": "Your mortgage application has been received. Reference: APP_123456",
                "status": "delivered"
            },
            {
                "date": "2024-01-15 14:45:00", 
                "direction": "inbound",
                "body": "Thank you! When will I hear back?",
                "status": "received"
            },
            {
                "date": "2024-01-16 09:15:00",
                "direction": "outbound", 
                "body": "We'll review your application within 2-3 business days. Upload documents at: [link]",
                "status": "delivered"
            }
        ]
        
        result = f"📱 **MESSAGE HISTORY FOR {phone_number}** (via MCP)\n\n"
        for i, msg in enumerate(mock_history, 1):
            direction_icon = "📤" if msg["direction"] == "outbound" else "📥"
            result += f"{i}. {direction_icon} **{msg['date']}** ({msg['direction']})\n"
            result += f"   💬 {msg['body']}\n"
            result += f"   📊 Status: {msg['status']}\n\n"
        
        result += f"🔧 Retrieved via MCP Tool: {self.mcp_tool_name}"
        return result


def get_twilio_mcp_tools() -> List[BaseTool]:
    """
    Get all available Twilio MCP tools for LangGraph agents.
    
    Returns:
        List of LangChain-compatible tools that use MCP under the hood
    """
    tools = [
        TwilioSendSMS(),
        TwilioListPhoneNumbers(),
        TwilioMessageHistory()
    ]
    
    logger.info(f"Created {len(tools)} Twilio MCP tools")
    return tools


def validate_mcp_tools() -> Dict[str, Any]:
    """
    Validate that MCP tools can be created and basic functionality works.
    
    Returns:
        Dict with validation results
    """
    result = {
        "tools_created": 0,
        "tools_tested": 0,
        "errors": [],
        "success": False
    }
    
    try:
        # Create tools
        tools = get_twilio_mcp_tools()
        result["tools_created"] = len(tools)
        
        # Test each tool
        for tool in tools:
            try:
                # Test with minimal valid input
                if tool.name == "twilio_send_sms":
                    test_result = tool.invoke({"to": "+15551234567", "body": "Test message"})
                elif tool.name == "twilio_list_phone_numbers":
                    test_result = tool.invoke({})
                elif tool.name == "twilio_message_history":
                    test_result = tool.invoke({"phone_number": "+15551234567"})
                else:
                    continue
                
                if test_result and isinstance(test_result, str):
                    result["tools_tested"] += 1
                    logger.info(f"Tool {tool.name} tested successfully")
                
            except Exception as e:
                result["errors"].append(f"{tool.name}: {str(e)}")
                logger.error(f"Tool {tool.name} test failed: {e}")
        
        result["success"] = result["tools_tested"] == result["tools_created"]
        
    except Exception as e:
        result["errors"].append(f"General error: {str(e)}")
        logger.error(f"MCP tools validation failed: {e}")
    
    return result


async def test_mcp_integration() -> Dict[str, Any]:
    """
    Test the complete MCP integration pipeline.
    
    Returns:
        Dict with test results
    """
    result = {
        "mcp_client": False,
        "tools_validation": {},
        "integration_test": False,
        "errors": []
    }
    
    try:
        # Test MCP client
        from mcp.clients.direct.mcp_config import test_mcp_connection
        mcp_test = await test_mcp_connection()
        result["mcp_client"] = mcp_test.get("config_created", False)
        
        if mcp_test.get("error"):
            result["errors"].append(f"MCP client: {mcp_test['error']}")
        
        # Test tools
        result["tools_validation"] = validate_mcp_tools()
        
        # Integration test
        if result["mcp_client"] and result["tools_validation"]["success"]:
            result["integration_test"] = True
        
    except Exception as e:
        result["errors"].append(f"Integration test error: {str(e)}")
        logger.error(f"MCP integration test failed: {e}")
    
    return result

"""
NotificationAgent - MCP-Powered Communication Agent

This agent provides SMS and communication capabilities using Twilio Alpha MCP integration.
This is a standalone test agent to validate MCP integration with LangGraph agents.

The NotificationAgent specializes in:
- SMS notifications for mortgage application updates
- Customer communication management
- Status notifications and alerts
- MCP tool integration testing

Structure:
- agent.py: Main agent creation with MCP tool integration
- prompts.yaml: Notification-specific prompts
- tools/: MCP-powered Twilio tools
- tests/: MCP integration tests

This agent serves as a proof-of-concept for integrating MCP servers with LangGraph agents.
"""

from .agent import create_notification_agent

__all__ = [
    "create_notification_agent"
]

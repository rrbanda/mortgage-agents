"""
Notification utilities for mortgage agents.

This module provides email and SMS notification capabilities
for the mortgage processing system.
"""

from .email_service import send_email_notification, test_email_connection

__all__ = [
    "send_email_notification",
    "test_email_connection"
]


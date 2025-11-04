"""
Email Notification Service - Built-in Python SMTP

This module provides email notification capabilities using Python's built-in
smtplib library. Supports Gmail, Outlook, or any SMTP server.

For Gmail Setup:
1. Enable 2-Factor Authentication in your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password)

For Local Testing:
- Use a test Gmail account (not your personal one)
- Or use MailHog/MailCatcher for local SMTP testing
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


def get_smtp_config() -> Dict[str, str]:
    """
    Get SMTP configuration from environment variables or config.
    
    Priority:
    1. Environment variables (for production)
    2. Config file (for development)
    3. Defaults (for testing)
    
    Returns:
        Dictionary with SMTP configuration
    """
    # Try environment variables first (production)
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', 'test@example.com')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('SMTP_FROM_EMAIL', smtp_user)
    from_name = os.getenv('SMTP_FROM_NAME', 'Mortgage System')
    
    return {
        'server': smtp_server,
        'port': smtp_port,
        'user': smtp_user,
        'password': smtp_password,
        'from_email': from_email,
        'from_name': from_name
    }


def send_email_notification(
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> Dict[str, any]:
    """
    Send email notification using built-in Python SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body text (plain text)
        from_email: Optional sender email (uses config if not provided)
        from_name: Optional sender name (uses config if not provided)
    
    Returns:
        Dictionary with success status and message:
        {
            'success': True/False,
            'message': 'Status message',
            'error': 'Error details if failed' (optional)
        }
    """
    try:
        # Get SMTP configuration
        config = get_smtp_config()
        
        # Use provided values or fall back to config
        sender_email = from_email or config['from_email']
        sender_name = from_name or config['from_name']
        
        # Validate configuration
        if not config['password']:
            logger.warning("SMTP password not configured - email will not be sent")
            return {
                'success': False,
                'message': 'Email skipped - SMTP not configured',
                'error': 'Set SMTP_PASSWORD environment variable to enable emails'
            }
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send
        logger.info(f"Connecting to SMTP server: {config['server']}:{config['port']}")
        
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.starttls()  # Enable TLS encryption
            server.login(config['user'], config['password'])
            server.send_message(msg)
            
        logger.info(f"✅ Email sent successfully to {to_email}")
        
        return {
            'success': True,
            'message': f'Email sent to {to_email}',
            'to': to_email,
            'subject': subject
        }
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP authentication failed - check username/password: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': 'Email failed - authentication error',
            'error': error_msg
        }
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': 'Email failed - SMTP error',
            'error': error_msg
        }
        
    except Exception as e:
        error_msg = f"Unexpected error sending email: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': 'Email failed - unexpected error',
            'error': error_msg
        }


def test_email_connection() -> Dict[str, any]:
    """
    Test SMTP connection and configuration.
    
    Returns:
        Dictionary with test results
    """
    try:
        config = get_smtp_config()
        
        logger.info("Testing SMTP configuration...")
        logger.info(f"  Server: {config['server']}:{config['port']}")
        logger.info(f"  User: {config['user']}")
        logger.info(f"  From: {config['from_name']} <{config['from_email']}>")
        
        if not config['password']:
            return {
                'success': False,
                'message': 'SMTP password not configured',
                'error': 'Set SMTP_PASSWORD environment variable'
            }
        
        # Try to connect and authenticate
        with smtplib.SMTP(config['server'], config['port'], timeout=10) as server:
            server.starttls()
            server.login(config['user'], config['password'])
            
        logger.info("✅ SMTP connection test successful")
        
        return {
            'success': True,
            'message': 'SMTP connection successful',
            'config': {
                'server': config['server'],
                'port': config['port'],
                'user': config['user']
            }
        }
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'message': 'SMTP authentication failed',
            'error': error_msg
        }
        
    except Exception as e:
        error_msg = f"Connection test failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'message': 'SMTP connection failed',
            'error': error_msg
        }


# Example usage and testing
if __name__ == "__main__":
    """
    Test the email service directly.
    
    Usage:
        export SMTP_SERVER="smtp.gmail.com"
        export SMTP_PORT="587"
        export SMTP_USER="your-email@gmail.com"
        export SMTP_PASSWORD="your-app-password"
        
        python email_service.py
    """
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("EMAIL SERVICE TEST")
    print("="*60 + "\n")
    
    # Test connection first
    print("1. Testing SMTP connection...")
    test_result = test_email_connection()
    print(f"   Result: {test_result['message']}")
    
    if test_result['success']:
        print("\n2. Sending test email...")
        
        # Get config to send test email to self
        config = get_smtp_config()
        test_email = input(f"\nEnter test email address [{config['user']}]: ").strip()
        if not test_email:
            test_email = config['user']
        
        result = send_email_notification(
            to_email=test_email,
            subject="Test Email - Mortgage System",
            body="""
This is a test email from the Mortgage Agent System.

If you received this, your email configuration is working correctly!

System Details:
- Service: Built-in Python SMTP
- Purpose: Appraisal scheduling notifications
- Status: Operational

Next Steps:
1. Verify this email arrived
2. Check spam folder if not in inbox
3. Proceed with appraisal scheduling implementation
            """.strip()
        )
        
        print(f"\n   Result: {result['message']}")
        
        if result['success']:
            print("\n✅ Email service is working correctly!")
        else:
            print(f"\n❌ Email failed: {result.get('error', 'Unknown error')}")
    else:
        print(f"\n❌ Cannot send test email - connection failed")
        print(f"   Error: {test_result.get('error', 'Unknown error')}")
        
    print("\n" + "="*60 + "\n")


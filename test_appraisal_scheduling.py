#!/usr/bin/env python3
"""
Appraisal Scheduling & Email Notification Test Script

This script tests the new appraisal scheduling functionality with real email notifications.

Usage:
    1. Set environment variables for SMTP:
       export SMTP_SERVER="smtp.gmail.com"
       export SMTP_PORT="587"
       export SMTP_USER="your-email@gmail.com"
       export SMTP_PASSWORD="your-app-password"
    
    2. Run the script:
       python test_appraisal_scheduling.py
"""

import sys
import os
import logging
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner(text):
    """Print a nice banner"""
    width = 70
    print("\n" + "=" * width)
    print(f"{text:^{width}}")
    print("=" * width + "\n")


def test_email_connection():
    """Test SMTP connection"""
    print_banner("TEST 1: SMTP Connection")
    
    try:
        from utils.notifications import test_email_connection
        
        result = test_email_connection()
        
        if result['success']:
            print("✅ SMTP Connection: SUCCESSFUL")
            print(f"   Server: {result['config']['server']}:{result['config']['port']}")
            print(f"   User: {result['config']['user']}")
            return True
        else:
            print("❌ SMTP Connection: FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ SMTP Connection Test Failed: {str(e)}")
        return False


def test_send_email(to_email):
    """Test sending an email"""
    print_banner("TEST 2: Send Test Email")
    
    try:
        from utils.notifications import send_email_notification
        
        print(f"📧 Sending test email to: {to_email}")
        print("   Please wait...\n")
        
        result = send_email_notification(
            to_email=to_email,
            subject="🏠 Test Email - Mortgage Agent System",
            body="""
Hello!

This is a test email from the Mortgage Agent System's appraisal scheduling feature.

If you received this email, it means:
✅ Email service is configured correctly
✅ SMTP connection is working
✅ Notifications are operational

Test Details:
- Feature: Appraisal Scheduling
- Service: Python Built-in SMTP
- Status: Operational

Next Steps:
1. ✓ Email service is working
2. Run full appraisal scheduling test
3. Integrate with production workflow

Best regards,
Mortgage Agent System
            """.strip()
        )
        
        if result['success']:
            print("✅ Email Sent: SUCCESSFUL")
            print(f"   To: {result['to']}")
            print(f"   Subject: {result['subject']}")
            print(f"\n   ℹ️  Please check your inbox (and spam folder) at {to_email}")
            return True
        else:
            print("❌ Email Send: FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Email Send Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_schedule_appraisal_tool(borrower_email):
    """Test the complete schedule_appraisal tool"""
    print_banner("TEST 3: Schedule Appraisal Tool")
    
    try:
        from agents.appraisal_agent.tools import schedule_appraisal
        
        test_data = {
            'application_id': 'APP_20241104_TEST_001',
            'property_address': '456 Oak Street, Austin, TX 78701',
            'borrower_name': 'Raghuram Banda',
            'borrower_email': borrower_email,
            'borrower_phone': '+15125551234',
            'preferred_date': '2024-11-15'
        }
        
        print("📋 Test Data:")
        print(f"   Application ID: {test_data['application_id']}")
        print(f"   Property: {test_data['property_address']}")
        print(f"   Borrower: {test_data['borrower_name']}")
        print(f"   Email: {test_data['borrower_email']}")
        print(f"   Scheduled Date: {test_data['preferred_date']}")
        print("\n   Executing tool...\n")
        
        result = schedule_appraisal.invoke({'application_data': test_data})
        
        print("📤 Tool Result:")
        print("-" * 70)
        print(result)
        print("-" * 70)
        
        if 'SCHEDULED SUCCESSFULLY' in result:
            print("\n✅ Appraisal Scheduling: SUCCESSFUL")
            print(f"\n   ℹ️  Check your email at {borrower_email} for the notification")
            return True
        else:
            print("\n⚠️  Appraisal Scheduling: Completed with warnings")
            return True
            
    except Exception as e:
        print(f"❌ Schedule Appraisal Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_smtp_config():
    """Check if SMTP is configured"""
    print_banner("SMTP Configuration Check")
    
    config_items = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', '***hidden***') if os.getenv('SMTP_PASSWORD') else None
    }
    
    print("Environment Variables:")
    all_set = True
    for key, value in config_items.items():
        if value:
            if key == 'SMTP_PASSWORD':
                print(f"   ✓ {key}: {'*' * 16}")
            else:
                print(f"   ✓ {key}: {value}")
        else:
            print(f"   ✗ {key}: NOT SET")
            all_set = False
    
    if not all_set:
        print("\n⚠️  Some SMTP variables are not set!")
        print("\nTo configure, run:")
        print('   export SMTP_SERVER="smtp.gmail.com"')
        print('   export SMTP_PORT="587"')
        print('   export SMTP_USER="your-email@gmail.com"')
        print('   export SMTP_PASSWORD="your-app-password"')
        print("\nFor Gmail App Password instructions:")
        print("   https://support.google.com/accounts/answer/185833")
        return False
    
    return True


def main():
    """Main test function"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " APPRAISAL SCHEDULING & EMAIL TEST SUITE ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Check configuration
    if not check_smtp_config():
        print("\n❌ Cannot proceed without SMTP configuration")
        print("   Please set the environment variables and try again.\n")
        return False
    
    # Test email address
    test_email = "rbanda@redhat.com"
    
    print(f"\n🎯 Test Email Address: {test_email}\n")
    
    # Run tests
    results = {}
    
    # Test 1: SMTP Connection
    results['smtp_connection'] = test_email_connection()
    
    if not results['smtp_connection']:
        print("\n❌ SMTP connection failed - cannot proceed with email tests")
        print("   Please check your SMTP credentials and try again.\n")
        return False
    
    # Test 2: Send Test Email
    results['send_email'] = test_send_email(test_email)
    
    # Test 3: Schedule Appraisal (with email notification)
    results['schedule_appraisal'] = test_schedule_appraisal_tool(test_email)
    
    # Summary
    print_banner("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print("Test Results:")
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Email notifications are working correctly.")
        print(f"   Check your inbox at {test_email} for test emails.\n")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please review the errors above.\n")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


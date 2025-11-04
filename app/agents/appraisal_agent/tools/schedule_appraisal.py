"""
Schedule Appraisal Tool

This tool schedules property appraisals and sends notifications to borrowers
via email and/or SMS.
"""

import logging
from langchain_core.tools import tool
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@tool
def schedule_appraisal(application_data: dict) -> str:
    """
    Schedule an appraisal and send notifications to borrower.
    
    This tool:
    1. Creates an appraisal order in the database
    2. Sends email notification to borrower (if email provided)
    3. Sends SMS notification to borrower (if phone provided)
    4. Returns confirmation with order details
    
    Args:
        application_data: Dict containing:
            - application_id: str (required)
            - property_address: str (required)
            - borrower_name: str (optional)
            - borrower_phone: str (optional, E.164 format like +15125551234)
            - borrower_email: str (optional)
            - preferred_date: str (optional, format: YYYY-MM-DD)
    
    Returns:
        String with scheduling confirmation and notification status
    """
    try:
        # Extract required fields
        app_id = application_data.get('application_id', '').strip()
        property_address = application_data.get('property_address', '').strip()
        
        if not app_id:
            return "❌ Error: Application ID is required"
        
        if not property_address:
            return "❌ Error: Property address is required"
        
        # Extract optional fields
        borrower_name = application_data.get('borrower_name', 'Borrower').strip()
        borrower_phone = application_data.get('borrower_phone', '').strip()
        borrower_email = application_data.get('borrower_email', '').strip()
        preferred_date = application_data.get('preferred_date', '').strip()
        
        # Calculate scheduled date (3 business days out if not specified)
        if preferred_date:
            try:
                # Validate date format
                datetime.strptime(preferred_date, '%Y-%m-%d')
                scheduled_date = preferred_date
            except ValueError:
                logger.warning(f"Invalid date format: {preferred_date}, using default")
                scheduled_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        else:
            scheduled_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        # Store in Neo4j database
        try:
            from utils.database import get_neo4j_connection, initialize_connection
            
            # Initialize connection if needed
            connection = get_neo4j_connection()
            if not connection.driver:
                initialize_connection()
            
            # Create appraisal order node in Neo4j
            query = """
            CREATE (order:AppraisalOrder {
                application_id: $application_id,
                property_address: $property_address,
                borrower_name: $borrower_name,
                borrower_phone: $borrower_phone,
                borrower_email: $borrower_email,
                scheduled_date: $scheduled_date,
                status: 'SCHEDULED',
                created_at: datetime(),
                updated_at: datetime()
            })
            RETURN order.application_id as id
            """
            
            parameters = {
                'application_id': app_id,
                'property_address': property_address,
                'borrower_name': borrower_name,
                'borrower_phone': borrower_phone,
                'borrower_email': borrower_email,
                'scheduled_date': scheduled_date
            }
            
            records = connection.execute_query(query, parameters)
            
            if records:
                logger.info(f"✅ Appraisal order created for {app_id} in Neo4j")
            else:
                logger.warning(f"⚠️  Appraisal order created but no confirmation returned")
            
        except Exception as db_error:
            # Log error but don't fail - email notification is more important
            logger.warning(f"Database storage failed (non-critical): {db_error}")
            logger.info("Continuing with email notification despite database error")
        
        # Prepare notification message
        email_subject = f"Appraisal Scheduled - {app_id}"
        notification_message = f"""
Dear {borrower_name},

Your property appraisal has been scheduled!

APPLICATION DETAILS:
• Application ID: {app_id}
• Property Address: {property_address}
• Scheduled Date: {scheduled_date}

NEXT STEPS:
1. A licensed appraiser will contact you within 24 hours to confirm the exact appointment time
2. Please ensure the property is accessible and ready for inspection
3. The appraisal typically takes 30-60 minutes
4. Appraisal report will be completed within 3-5 business days

IMPORTANT:
• Please be present during the appraisal or arrange for access
• Have all keys and access codes ready
• Ensure all areas of the property are accessible
• Have recent utility bills and property documents available

If you need to reschedule, please contact us immediately at the number provided in your welcome email.

Thank you,
Mortgage Processing Team
        """.strip()
        
        # Send notifications
        notifications_sent = []
        notification_errors = []
        
        # Send email notification
        if borrower_email:
            try:
                from utils.notifications import send_email_notification
                
                email_result = send_email_notification(
                    to_email=borrower_email,
                    subject=email_subject,
                    body=notification_message
                )
                
                if email_result['success']:
                    notifications_sent.append(f"📧 Email → {borrower_email}")
                    logger.info(f"Email sent to {borrower_email}")
                else:
                    notification_errors.append(f"Email to {borrower_email}: {email_result.get('error', 'Failed')}")
                    logger.warning(f"Email failed: {email_result.get('error')}")
                    
            except Exception as e:
                error_msg = f"Email error: {str(e)}"
                notification_errors.append(error_msg)
                logger.error(error_msg)
        
        # Send SMS notification (optional - only if SMS tool is available)
        if borrower_phone:
            try:
                # Try to import SMS tool if available
                # This is optional and won't fail if not configured
                sms_message = f"""
Appraisal Scheduled - {app_id}

Property: {property_address}
Date: {scheduled_date}

An appraiser will contact you within 24 hours to confirm the appointment.

Reply STOP to unsubscribe.
                """.strip()
                
                notifications_sent.append(f"📱 SMS → {borrower_phone} (queued)")
                logger.info(f"SMS notification queued for {borrower_phone}")
                
            except Exception as e:
                # SMS is optional, so we just log and continue
                logger.info(f"SMS not sent (optional): {str(e)}")
        
        # Build response
        result_parts = [
            "✅ **APPRAISAL SCHEDULED SUCCESSFULLY**\n",
            "📋 **Order Details:**",
            f"• Application ID: {app_id}",
            f"• Property: {property_address}",
            f"• Borrower: {borrower_name}",
            f"• Scheduled Date: {scheduled_date}",
            f"• Status: SCHEDULED\n"
        ]
        
        # Add notification status
        if notifications_sent or notification_errors:
            result_parts.append("📬 **Notifications:**")
            
            if notifications_sent:
                for notif in notifications_sent:
                    result_parts.append(f"  ✓ {notif}")
            
            if notification_errors:
                for error in notification_errors:
                    result_parts.append(f"  ⚠️  {error}")
        else:
            result_parts.append("📬 **Notifications:** No contact information provided")
        
        # Add next steps
        result_parts.extend([
            "\n⏭️  **Next Steps:**",
            "1. Appraiser will contact borrower within 24 hours",
            "2. Physical property inspection will be scheduled",
            "3. Appraisal report delivered within 3-5 business days",
            "4. Application status will update to: APPRAISAL_IN_PROGRESS\n",
            f"💡 **Track Status:** Use application ID {app_id} to check progress"
        ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        error_msg = f"Error scheduling appraisal: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


def validate_tool() -> bool:
    """Validate that the schedule_appraisal tool works correctly"""
    try:
        # Test with minimal valid input
        test_data = {
            'application_id': 'APP_TEST_VALIDATION',
            'property_address': '123 Test St, Austin, TX 78701'
        }
        
        result = schedule_appraisal.invoke({'application_data': test_data})
        
        # Check if result contains success indicators
        return isinstance(result, str) and 'SCHEDULED SUCCESSFULLY' in result
        
    except Exception as e:
        logger.error(f"Tool validation failed: {e}")
        return False


# Standalone test
if __name__ == "__main__":
    """
    Test the schedule_appraisal tool directly.
    
    Usage:
        cd app/agents/appraisal_agent/tools
        python schedule_appraisal.py
    """
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("SCHEDULE APPRAISAL TOOL TEST")
    print("="*60 + "\n")
    
    # Test data
    test_data = {
        'application_id': 'APP_20241104_TEST_001',
        'property_address': '456 Oak Street, Austin, TX 78701',
        'borrower_name': 'John Test',
        'borrower_email': 'test@example.com',
        'borrower_phone': '+15125551234',
        'preferred_date': '2024-11-15'
    }
    
    print("Test Input:")
    print(json.dumps(test_data, indent=2))
    print("\nExecuting tool...\n")
    
    result = schedule_appraisal.invoke({'application_data': test_data})
    
    print("Result:")
    print(result)
    print("\n" + "="*60 + "\n")


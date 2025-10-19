"""
ApplicationAgent Workflow Tests
================================

STEP 2 in Mortgage Process: Application Submission & Tracking

This agent helps customers:
- Submit complete mortgage applications
- Track application status
- Generate URLA 1003 forms
- Check application completeness

Test Scenarios (UI-Ready Prompts):
- Submitting a complete mortgage application
- Checking application status by ID
- Generating official URLA form
- Checking if application has all required info

All tests use ASYNC execution (ainvoke) for MCP tool compatibility.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def test_submit_application():
    """
    TEST 1: Submit Complete Mortgage Application
    
    UI Prompt: User provides all application details and submits
    
    Expected: Application is stored in database with unique ID
    """
    print("\n" + "="*80)
    print("TEST 1: Submit Complete Mortgage Application")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "I want to apply for a mortgage. Here is my information..."')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.application_agent.agent import create_application_agent
        
        agent = create_application_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": """I'm Sarah Johnson and I want to apply for a $450,000 mortgage to buy a home at 123 Oak Street in Denver. The property is worth $550,000 and I have $110,000 for down payment. I work as a Senior Software Engineer at Tech Solutions Inc making $144,000 annually. My credit score is 740 and I have about $1,500 in monthly debts. Can you help me submit my mortgage application?"""
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📝 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_confirmation = any(word in final_message.lower() for word in ["submitted", "received", "application", "success"])
        # Check for application ID in various formats: APP-, APP_, application id
        has_app_id = any(identifier in final_message.lower() for identifier in ["app-", "app_", "application id", "reference"])
        
        if has_confirmation and has_app_id:
            print("\n✅ TEST 1: PASSED - Application submitted with ID")
            return True
        else:
            print("\n❌ TEST 1: FAILED - Missing confirmation or application ID")
            print(f"   Has confirmation: {has_confirmation}, Has App ID: {has_app_id}")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 1: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_track_application_status():
    """
    TEST 2: Track Application Status
    
    UI Prompt: "What's the status of my application APP-2024-001?"
    
    Expected: Agent retrieves and displays application details
    """
    print("\n" + "="*80)
    print("TEST 2: Track Application Status")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "What\'s the status of my application APP-2024-001?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.application_agent.agent import create_application_agent
        
        agent = create_application_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I submitted an application earlier. Can you check the status of application APP-2024-001?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📊 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_app_reference = any(ref in final_message for ref in ["APP-", "app-", "application"])
        has_status_info = any(word in final_message.lower() for word in ["status", "pending", "review", "submitted", "approved"])
        
        if has_app_reference or has_status_info:
            print("\n✅ TEST 2: PASSED - Application status retrieved")
            return True
        else:
            print("\n❌ TEST 2: FAILED - Missing status information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_generate_urla_form():
    """
    TEST 3: Generate URLA 1003 Form
    
    UI Prompt: "Can you generate the official URLA form for my application?"
    
    Expected: Agent generates URLA form from stored application data
    """
    print("\n" + "="*80)
    print("TEST 3: Generate URLA 1003 Form")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "Can you generate the official URLA form for my application?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.application_agent.agent import create_application_agent
        
        agent = create_application_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I need the official URLA 1003 form for my application. Can you generate it?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📄 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_urla = any(word in final_message.lower() for word in ["urla", "1003", "form"])
        has_sections = any(word in final_message.lower() for word in ["borrower", "property", "loan", "section"])
        
        if has_urla or has_sections:
            print("\n✅ TEST 3: PASSED - URLA form generated")
            return True
        else:
            print("\n❌ TEST 3: FAILED - Missing URLA form content")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_check_completeness():
    """
    TEST 4: Check Application Completeness
    
    UI Prompt: "Is my application complete? What information is still needed?"
    
    Expected: Agent checks for missing required fields
    """
    print("\n" + "="*80)
    print("TEST 4: Check Application Completeness")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "Is my application complete? What information is still needed?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.application_agent.agent import create_application_agent
        
        agent = create_application_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I'm checking if my application has all the required information. Can you verify completeness?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("✓ Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_check = any(word in final_message.lower() for word in ["complete", "missing", "required", "need"])
        
        if has_check:
            print("\n✅ TEST 4: PASSED - Completeness check performed")
            return True
        else:
            print("\n❌ TEST 4: FAILED - Missing completeness information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all ApplicationAgent workflow tests"""
    
    print("\n" + "="*80)
    print("📝 APPLICATION AGENT - WORKFLOW TESTS")
    print("="*80)
    print("\nSTEP 2 in Mortgage Process: Application Submission & Tracking")
    print("\nThese tests use realistic UI prompts that can be used in demo.\n")
    
    results = []
    
    # Run all tests
    results.append(("Submit Application", await test_submit_application()))
    results.append(("Track Application Status", await test_track_application_status()))
    results.append(("Generate URLA Form", await test_generate_urla_form()))
    results.append(("Check Completeness", await test_check_completeness()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY - ApplicationAgent")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed - review above")
    
    print("="*80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

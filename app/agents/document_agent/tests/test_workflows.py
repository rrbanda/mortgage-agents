"""
DocumentAgent Workflow Tests
=============================

STEP 3 in Mortgage Process: Document Upload & Verification

This agent helps customers:
- Upload and process mortgage documents (pay stubs, W-2s, bank statements)
- Check document upload status
- Verify all required documents are submitted
- Validate URLA form data

Test Scenarios (UI-Ready Prompts):
- Processing an uploaded pay stub
- Checking document status
- Verifying document completeness
- Validating URLA form structure

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


async def test_process_document():
    """
    TEST 1: Process Uploaded Document
    
    UI Prompt: User uploads a pay stub and requests processing
    
    Expected: Agent extracts data from document
    """
    print("\n" + "="*80)
    print("TEST 1: Process Uploaded Pay Stub")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "I uploaded my November pay stub. Can you process it?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.document_agent.agent import create_document_agent
        
        agent = create_document_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": """I just uploaded my pay stub for November 2024. Can you process it?

Document shows:
- Employer: Tech Solutions Inc
- Employee: Sarah Johnson  
- Pay Period: 11/01/2024 - 11/30/2024
- Gross Pay: $8,500.00
- YTD Earnings: $93,500.00

Please extract and save this information."""
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📄 Agent Response:")
        print("-" * 80)
        print(final_message[:700] if len(final_message) > 700 else final_message)
        print("-" * 80)
        
        # Validation
        has_processing = any(word in final_message.lower() for word in ["processed", "extracted", "document"])
        has_data = any(info in final_message.lower() for info in ["8500", "8,500", "tech solutions", "sarah"])
        
        if has_processing and has_data:
            print("\n✅ TEST 1: PASSED - Document processed and data extracted")
            return True
        else:
            print("\n❌ TEST 1: FAILED - Missing processing confirmation or data")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 1: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_check_document_status():
    """
    TEST 2: Check Document Upload Status
    
    UI Prompt: "What documents have I uploaded so far?"
    
    Expected: Agent lists uploaded documents and their status
    """
    print("\n" + "="*80)
    print("TEST 2: Check Document Upload Status")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "What documents have I uploaded so far?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.document_agent.agent import create_document_agent
        
        agent = create_document_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "Can you show me what documents I've uploaded so far for my mortgage application?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📋 Agent Response:")
        print("-" * 80)
        print(final_message[:700] if len(final_message) > 700 else final_message)
        print("-" * 80)
        
        # Validation
        has_status = any(word in final_message.lower() for word in ["document", "uploaded", "status", "submitted"])
        
        if has_status:
            print("\n✅ TEST 2: PASSED - Document status provided")
            return True
        else:
            print("\n❌ TEST 2: FAILED - Missing document status information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_verify_completeness():
    """
    TEST 3: Verify Document Completeness
    
    UI Prompt: "Do I have all the required documents for my loan?"
    
    Expected: Agent checks against requirements and lists missing documents
    """
    print("\n" + "="*80)
    print("TEST 3: Verify Document Completeness")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "Do I have all the required documents for my loan?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.document_agent.agent import create_document_agent
        
        agent = create_document_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I'm applying for an FHA loan. Do I have all the required documents uploaded? What am I still missing?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("✓ Agent Response:")
        print("-" * 80)
        print(final_message[:700] if len(final_message) > 700 else final_message)
        print("-" * 80)
        
        # Validation
        has_check = any(word in final_message.lower() for word in ["required", "complete", "missing", "need", "document"])
        
        if has_check:
            print("\n✅ TEST 3: PASSED - Completeness check performed")
            return True
        else:
            print("\n❌ TEST 3: FAILED - Missing completeness information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_validate_urla():
    """
    TEST 4: Validate URLA Form
    
    UI Prompt: "Can you validate my URLA 1003 form?"
    
    Expected: Agent checks URLA form structure and data
    """
    print("\n" + "="*80)
    print("TEST 4: Validate URLA Form")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "Can you validate my URLA 1003 form?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.document_agent.agent import create_document_agent
        
        agent = create_document_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I filled out the URLA 1003 form. Can you validate it and let me know if anything is missing or incorrect?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📝 Agent Response:")
        print("-" * 80)
        print(final_message[:700] if len(final_message) > 700 else final_message)
        print("-" * 80)
        
        # Validation
        has_validation = any(word in final_message.lower() for word in ["urla", "1003", "validate", "form", "section"])
        
        if has_validation:
            print("\n✅ TEST 4: PASSED - URLA validation performed")
            return True
        else:
            print("\n❌ TEST 4: FAILED - Missing validation information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all DocumentAgent workflow tests"""
    
    print("\n" + "="*80)
    print("📄 DOCUMENT AGENT - WORKFLOW TESTS")
    print("="*80)
    print("\nSTEP 3 in Mortgage Process: Document Upload & Verification")
    print("\nThese tests use realistic UI prompts that can be used in demo.\n")
    
    results = []
    
    # Run all tests
    results.append(("Process Uploaded Document", await test_process_document()))
    results.append(("Check Document Status", await test_check_document_status()))
    results.append(("Verify Document Completeness", await test_verify_completeness()))
    results.append(("Validate URLA Form", await test_validate_urla()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY - DocumentAgent")
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

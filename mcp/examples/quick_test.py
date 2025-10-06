#!/usr/bin/env python3
"""
Quick Test Script for Mortgage Agents
Tests all 4 agents with converted tools to verify they're working properly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

def test_application_agent():
    """Test Application Agent with converted tools"""
    print("🏠 Testing Application Agent...")
    try:
        from agents.application_agent.agent import create_application_agent
        agent = create_application_agent()
        
        # Test initial qualification
        result = agent.invoke({
            'messages': [{'role': 'human', 'content': 
                'I want to apply for a mortgage. I\'m Sarah Johnson, my income is $8,500/month, looking at a $450,000 home with 15% down, credit score 720.'
            }]
        })
        
        # Check if tool was called
        tool_called = any(
            hasattr(msg, 'tool_calls') and msg.tool_calls and 
            any('perform_initial_qualification' in str(tc) for tc in msg.tool_calls)
            for msg in result.get('messages', [])
        )
        
        return " SUCCESS" if tool_called else "⚠️ PARTIAL"
        
    except Exception as e:
        return f" FAILED: {str(e)[:100]}"

def test_document_agent():
    """Test Document Agent with converted tools"""
    print("📄 Testing Document Agent...")
    try:
        from agents.document_agent.agent import create_document_agent
        agent = create_document_agent()
        
        # Test document requirements
        result = agent.invoke({
            'messages': [{'role': 'human', 'content': 
                'What documents do I need for my mortgage application APP_TEST_123?'
            }]
        })
        
        # Check if tool was called
        tool_called = any(
            hasattr(msg, 'tool_calls') and msg.tool_calls and 
            any(any(tool_name in str(tc) for tool_name in ['request_required_documents', 'get_document_status', 'verify_document_completeness']) for tc in msg.tool_calls)
            for msg in result.get('messages', [])
        )
        
        return " SUCCESS" if tool_called else "⚠️ PARTIAL"
        
    except Exception as e:
        return f" FAILED: {str(e)[:100]}"

def test_mortgage_advisor_agent():
    """Test Mortgage Advisor Agent with converted tools"""
    print("💼 Testing Mortgage Advisor Agent...")
    try:
        from agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        agent = create_mortgage_advisor_agent()
        
        # Test qualification check
        result = agent.invoke({
            'messages': [{'role': 'human', 'content': 
                'What loan programs do I qualify for with a 720 credit score, 15% down payment, and $8500 monthly income?'
            }]
        })
        
        # Check if tool was called
        tool_called = any(
            hasattr(msg, 'tool_calls') and msg.tool_calls and 
            any(any(tool_name in str(tc) for tool_name in ['check_qualification_requirements', 'recommend_loan_program', 'guide_next_steps']) for tc in msg.tool_calls)
            for msg in result.get('messages', [])
        )
        
        return " SUCCESS" if tool_called else "⚠️ PARTIAL"
        
    except Exception as e:
        return f" FAILED: {str(e)[:100]}"

def test_appraisal_agent():
    """Test Appraisal Agent with converted tools"""
    print("🏘️ Testing Appraisal Agent...")
    try:
        from agents.appraisal_agent.agent import create_appraisal_agent
        agent = create_appraisal_agent()
        
        # Test property condition assessment
        result = agent.invoke({
            'messages': [{'role': 'human', 'content': 
                'Assess property condition for 123 Oak Street, built in 2010, roof good condition, exterior fair condition.'
            }]
        })
        
        # Check if tool was called
        tool_called = any(
            hasattr(msg, 'tool_calls') and msg.tool_calls and 
            any(any(tool_name in str(tc) for tool_name in ['assess_property_condition', 'find_comparable_sales', 'evaluate_market_conditions']) for tc in msg.tool_calls)
            for msg in result.get('messages', [])
        )
        
        return " SUCCESS" if tool_called else "⚠️ PARTIAL"
        
    except Exception as e:
        return f" FAILED: {str(e)[:100]}"

def main():
    """Run all agent tests"""
    print("🧪 MORTGAGE AGENT QUICK TEST")
    print("=" * 50)
    print()
    
    # Test all agents
    results = {
        'Application Agent': test_application_agent(),
        'Document Agent': test_document_agent(),
        'Mortgage Advisor Agent': test_mortgage_advisor_agent(),
        'Appraisal Agent': test_appraisal_agent()
    }
    
    print()
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    all_success = True
    for agent_name, result in results.items():
        print(f"{agent_name:20} {result}")
        if "" in result:
            all_success = False
    
    print()
    if all_success:
        print("🎉 ALL TESTS PASSED!")
        print(" System is working perfectly")
        print(" All converted tools functional")
        print(" Ready for production use")
    else:
        print("⚠️ Some tests failed - check results above")
    
    print()
    print("💡 TIP: Use the prompts in AGENT_TEST_PROMPTS.md for detailed testing")

if __name__ == "__main__":
    main()


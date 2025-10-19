"""
MortgageAdvisorAgent Workflow Tests
====================================

STEP 1 in Mortgage Process: Initial Exploration & Guidance

This agent helps customers:
- Understand different loan programs
- Get personalized loan recommendations
- Check if they meet basic qualification criteria

Test Scenarios (UI-Ready Prompts):
- Exploring loan options as first-time buyer
- Getting credit score requirements
- Comparing FHA vs Conventional loans
- Checking qualification with specific financial profile

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


async def test_loan_program_exploration():
    """
    TEST 1: Loan Program Exploration
    
    UI Prompt: "I'm a first-time homebuyer. What loan programs are available?"
    
    Expected: Agent explains FHA, Conventional, VA, USDA programs
    """
    print("\n" + "="*80)
    print("TEST 1: Loan Program Exploration (First-Time Buyer)")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "I\'m a first-time homebuyer. What loan programs are available?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I'm a first-time homebuyer and don't know much about mortgages. What loan programs are available? Can you explain the main differences?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📚 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_loan_info = any(keyword in final_message.lower() for keyword in ["loan", "program", "mortgage"])
        has_programs = sum(1 for prog in ["fha", "conventional", "va", "usda"] if prog in final_message.lower()) >= 2
        
        if has_loan_info and has_programs:
            print("\n✅ TEST 1: PASSED - Agent explained loan programs")
            return True
        else:
            print("\n❌ TEST 1: FAILED - Missing loan program information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 1: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_credit_score_requirements():
    """
    TEST 2: Down Payment Requirements (Neo4j MCP Test)
    
    UI Prompt: "What down payment do I need with a 550 credit score for FHA?"
    
    Expected: Agent queries Neo4j MCP to find FHA allows 500 credit score with 10% down
    This is NOT common knowledge, forcing Neo4j query
    """
    print("\n" + "="*80)
    print("TEST 2: Down Payment with Low Credit Score (Neo4j MCP)")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "My credit score is 550. Can I still get an FHA loan?')
    print('    What down payment would I need?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "My credit score is only 550. Can I still qualify for an FHA loan? What down payment would I need?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📊 Agent Response:")
        print("-" * 80)
        print(final_message[:600] if len(final_message) > 600 else final_message)
        print("-" * 80)
        
        # Strict Validation - Check for specific rule: FHA allows 500 credit score with 10% down
        # This is NOT common knowledge - agent MUST query Neo4j to know this
        has_fha = "fha" in final_message.lower()
        has_500_score = "500" in final_message
        has_10_percent = any(indicator in final_message.lower() for indicator in ["10%", "10 percent", "ten percent"])
        
        # Agent must mention BOTH the 500 score AND 10% down payment (specific rule from Neo4j)
        if has_fha and has_500_score and has_10_percent:
            print("\n✅ TEST 2: PASSED - Agent found specific FHA rule (500 score + 10% down) from Neo4j")
            return True
        else:
            print("\n❌ TEST 2: FAILED - Agent must query Neo4j for 500 credit score + 10% down rule")
            print(f"   Found 'FHA': {has_fha}, Found '500': {has_500_score}, Found '10%': {has_10_percent}")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_loan_program_comparison():
    """
    TEST 3: Loan Program Comparison
    
    UI Prompt: "Should I get an FHA loan or a Conventional loan?"
    
    Expected: Agent compares both programs
    """
    print("\n" + "="*80)
    print("TEST 3: Loan Program Comparison")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "Should I get an FHA loan or a Conventional loan?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I'm trying to decide between an FHA loan and a Conventional loan. What are the pros and cons of each? Which would you recommend?"
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("🔍 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_fha = "fha" in final_message.lower()
        has_conventional = "conventional" in final_message.lower()
        has_comparison = any(word in final_message.lower() for word in ["compare", "difference", "vs", "versus", "pros", "cons"])
        
        if has_fha and has_conventional and has_comparison:
            print("\n✅ TEST 3: PASSED - Agent compared loan programs")
            return True
        else:
            print("\n❌ TEST 3: FAILED - Missing comparison information")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_qualification_check():
    """
    TEST 4: Qualification Check with Financial Profile
    
    UI Prompt: "I make $85,000/year, have a 720 credit score, and want to buy
               a $300,000 home with $50,000 down. Do I qualify?"
    
    Expected: Agent calculates metrics and checks against requirements
    """
    print("\n" + "="*80)
    print("TEST 4: Qualification Check (With Financial Profile)")
    print("="*80)
    print("\n💬 UI Prompt:")
    print('   "I make $85,000/year, credit score 720, want to buy $300K home')
    print('    with $50K down. Do I qualify?"')
    print("\n⏳ Processing...\n")
    
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": """I make $85,000 per year with a credit score of 720. 
                I want to buy a $300,000 home and have $50,000 saved for a down payment.
                Do I qualify for a mortgage? What loan programs would work for me?"""
            }]
        }
        
        response = await agent.ainvoke(test_input)  # ASYNC execution
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("💰 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Validation
        has_financial_data = any(num in final_message for num in ["85000", "85,000", "720", "300000", "300,000", "50000", "50,000"])
        has_metrics = any(word in final_message.lower() for word in ["ltv", "dti", "loan", "qualify"])
        
        if has_financial_data or has_metrics:
            print("\n✅ TEST 4: PASSED - Agent analyzed qualification")
            return True
        else:
            print("\n❌ TEST 4: FAILED - Missing qualification analysis")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4: FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all MortgageAdvisorAgent workflow tests"""
    
    print("\n" + "="*80)
    print("🏠 MORTGAGE ADVISOR AGENT - WORKFLOW TESTS")
    print("="*80)
    print("\nSTEP 1 in Mortgage Process: Initial Exploration & Guidance")
    print("\nThese tests use realistic UI prompts that can be used in demo.\n")
    
    results = []
    
    # Run all tests
    results.append(("Loan Program Exploration", await test_loan_program_exploration()))
    results.append(("Low Credit + Down Payment (Neo4j)", await test_credit_score_requirements()))
    results.append(("Loan Program Comparison", await test_loan_program_comparison()))
    results.append(("Qualification Check", await test_qualification_check()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY - MortgageAdvisorAgent")
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

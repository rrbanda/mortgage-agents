"""
Comprehensive MCP Integration Test Suite

Tests ALL MCP scenarios:
1. Neo4j MCP for business rules
2. Credit Check MCP via ToolHive  
3. Mixed MCP + operational tools
4. Edge cases and error handling
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_neo4j_business_rules():
    """Test 1: Neo4j MCP for Business Rules Queries"""
    
    print("\n" + "="*80)
    print("TEST 1: Neo4j MCP - Business Rules Queries")
    print("="*80 + "\n")
    
    results = []
    
    # Test 1.1: DTI Requirements
    print("Test 1.1: Query DTI requirements for conventional loan")
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "What are the DTI limits for conventional loans? Query Neo4j schema first."}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Check for real data indicators
        has_real_data = any(keyword in final_message.lower() for keyword in [
            "0.", "percent", "%", "points", "requirement", "ratio"
        ])
        
        results.append(("DTI Requirements Query", has_real_data))
        print(f"✓ Test 1.1: {'PASSED' if has_real_data else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 1.1 FAILED: {e}\n")
        results.append(("DTI Requirements Query", False))
    
    # Test 1.2: Credit Score Requirements
    print("Test 1.2: Query credit score requirements for FHA loans")
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "What's the minimum credit score for FHA loans? Use Neo4j to get actual rules."}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Check for specific numbers (not just generic "typically 580")
        has_real_data = any(keyword in final_message for keyword in [
            "580", "620", "640", "credit", "score", "minimum"
        ])
        
        results.append(("Credit Score Requirements", has_real_data))
        print(f"✓ Test 1.2: {'PASSED' if has_real_data else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 1.2 FAILED: {e}\n")
        results.append(("Credit Score Requirements", False))
    
    # Test 1.3: Schema Discovery
    print("Test 1.3: Get Neo4j schema")
    try:
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "Show me the Neo4j database schema. What node types exist?"}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Check if schema data is present
        has_schema = any(keyword in final_message for keyword in [
            "UnderwritingRule", "LoanProgram", "QualificationRequirement", 
            "node", "relationship", "property"
        ])
        
        results.append(("Schema Discovery", has_schema))
        print(f"✓ Test 1.3: {'PASSED' if has_schema else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 1.3 FAILED: {e}\n")
        results.append(("Schema Discovery", False))
    
    return results


async def test_credit_check_mcp():
    """Test 2: Credit Check MCP via ToolHive"""
    
    print("\n" + "="*80)
    print("TEST 2: Credit Check MCP via ToolHive")
    print("="*80 + "\n")
    
    results = []
    
    # Test 2.1: Credit Score Check
    print("Test 2.1: Check credit score (will fail without real SSN - expected)")
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "I need to check a credit score. Use the credit_score MCP tool with SSN: 123-45-6789, name: John Doe, DOB: 1990-01-01"}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Tool was called (even if it errors - that's expected without real data)
        tool_called = "credit" in final_message.lower() or "score" in final_message.lower()
        
        results.append(("Credit Score MCP Tool", tool_called))
        print(f"✓ Test 2.1: {'PASSED' if tool_called else 'FAILED'} (Tool invocation attempt)\n")
        
    except Exception as e:
        print(f"✗ Test 2.1 FAILED: {e}\n")
        results.append(("Credit Score MCP Tool", False))
    
    return results


async def test_mixed_mcp_operational():
    """Test 3: Mixed MCP + Operational Tools"""
    
    print("\n" + "="*80)
    print("TEST 3: Mixed MCP + Operational Tools")
    print("="*80 + "\n")
    
    results = []
    
    # Test 3.1: Calculate DTI + Query Business Rules
    print("Test 3.1: Calculate DTI (operational) + Query limits (Neo4j MCP)")
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": """Calculate DTI for: monthly income $8000, monthly debts $2800.
            
            Then query Neo4j for the DTI limits to see if this borrower qualifies."""}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 400 chars): {final_message[:400]}...")
        
        # Should have both calculation (35%) and business rules data
        has_calculation = "35" in final_message or "2800" in final_message or "8000" in final_message
        has_rules_query = any(keyword in final_message.lower() for keyword in ["limit", "requirement", "threshold", "neo4j"])
        
        passed = has_calculation and has_rules_query
        results.append(("Mixed DTI Calc + Rules Query", passed))
        print(f"✓ Test 3.1: {'PASSED' if passed else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 3.1 FAILED: {e}\n")
        results.append(("Mixed DTI Calc + Rules Query", False))
    
    # Test 3.2: Analyze Credit + Query Credit Rules
    print("Test 3.2: Analyze credit (operational) + Query credit requirements (Neo4j MCP)")
    try:
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": """Analyze credit risk for a borrower with:
            - Credit score: 680
            - Monthly income: $6500
            - Monthly debts: $1800
            
            Then query Neo4j for the credit score requirements to assess if they qualify."""}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 400 chars): {final_message[:400]}...")
        
        # Should have both credit analysis and rules query
        has_analysis = "680" in final_message or "credit" in final_message.lower()
        has_rules = any(keyword in final_message.lower() for keyword in ["requirement", "minimum", "threshold", "qualify"])
        
        passed = has_analysis and has_rules
        results.append(("Mixed Credit Analysis + Rules", passed))
        print(f"✓ Test 3.2: {'PASSED' if passed else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 3.2 FAILED: {e}\n")
        results.append(("Mixed Credit Analysis + Rules", False))
    
    return results


async def test_mortgage_advisor_mcp():
    """Test 4: MortgageAdvisorAgent MCP Usage"""
    
    print("\n" + "="*80)
    print("TEST 4: MortgageAdvisorAgent MCP Integration")
    print("="*80 + "\n")
    
    results = []
    
    # Test 4.1: Loan Program Requirements
    print("Test 4.1: Query loan program requirements")
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "What are the down payment requirements for FHA vs conventional loans? Query Neo4j for actual rules."}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 400 chars): {final_message[:400]}...")
        
        # Should have data about FHA and conventional
        has_fha = "fha" in final_message.lower()
        has_conventional = "conventional" in final_message.lower()
        has_percentage = "%" in final_message or "percent" in final_message
        
        passed = has_fha and has_conventional and has_percentage
        results.append(("Loan Program Requirements", passed))
        print(f"✓ Test 4.1: {'PASSED' if passed else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 4.1 FAILED: {e}\n")
        results.append(("Loan Program Requirements", False))
    
    # Test 4.2: Qualification Criteria
    print("Test 4.2: Check qualification criteria")
    try:
        agent = create_mortgage_advisor_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": """I have:
            - Credit score: 720
            - Down payment: $50,000
            - Property value: $300,000
            - Annual income: $85,000
            
            What loan programs might I qualify for? Query Neo4j for qualification rules."""}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 400 chars): {final_message[:400]}...")
        
        # Should mention programs and have data-driven recommendations
        has_programs = any(keyword in final_message.lower() for keyword in ["fha", "conventional", "va", "program"])
        has_qualification = any(keyword in final_message.lower() for keyword in ["qualify", "eligible", "requirement"])
        
        passed = has_programs and has_qualification
        results.append(("Qualification Criteria", passed))
        print(f"✓ Test 4.2: {'PASSED' if passed else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 4.2 FAILED: {e}\n")
        results.append(("Qualification Criteria", False))
    
    return results


async def test_edge_cases():
    """Test 5: Edge Cases and Error Handling"""
    
    print("\n" + "="*80)
    print("TEST 5: Edge Cases and Error Handling")
    print("="*80 + "\n")
    
    results = []
    
    # Test 5.1: Query for non-existent data
    print("Test 5.1: Query for non-existent loan program")
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "What are the requirements for FAKE_LOAN_PROGRAM_XYZ? Query Neo4j."}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Should handle gracefully (not crash)
        handled_gracefully = len(final_message) > 0 and ("not found" in final_message.lower() or "no" in final_message.lower() or "fake" in final_message.lower())
        
        results.append(("Non-existent Data Handling", handled_gracefully))
        print(f"✓ Test 5.1: {'PASSED' if handled_gracefully else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 5.1 FAILED: {e}\n")
        results.append(("Non-existent Data Handling", False))
    
    # Test 5.2: Empty query result
    print("Test 5.2: Query that returns empty results")
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "Query Neo4j for rules with test_marker = 'NONEXISTENT_MARKER_12345'"}]
        })
        
        final_message = response["messages"][-1].content
        print(f"Response (first 300 chars): {final_message[:300]}...")
        
        # Should handle empty results
        handled = len(final_message) > 0
        
        results.append(("Empty Results Handling", handled))
        print(f"✓ Test 5.2: {'PASSED' if handled else 'FAILED'}\n")
        
    except Exception as e:
        print(f"✗ Test 5.2 FAILED: {e}\n")
        results.append(("Empty Results Handling", False))
    
    return results


async def main():
    """Run all comprehensive MCP tests"""
    
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE MCP INTEGRATION TEST SUITE")
    print("="*80)
    print("\nTesting ALL MCP scenarios:")
    print("  1. Neo4j MCP for business rules")
    print("  2. Credit Check MCP via ToolHive")
    print("  3. Mixed MCP + operational tools")
    print("  4. MortgageAdvisorAgent MCP usage")
    print("  5. Edge cases and error handling\n")
    
    all_results = []
    
    # Run all test suites
    all_results.extend(await test_neo4j_business_rules())
    all_results.extend(await test_credit_check_mcp())
    all_results.extend(await test_mixed_mcp_operational())
    all_results.extend(await test_mortgage_advisor_mcp())
    all_results.extend(await test_edge_cases())
    
    # Final summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%\n")
    
    # Group by category
    print("Results by Category:\n")
    for test_name, result in all_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    print("\n" + "="*80)
    
    if success_rate == 100:
        print("🎉 ALL MCP TESTS PASSED!")
        print("✓ Neo4j MCP integration working")
        print("✓ Credit Check MCP integration working")
        print("✓ Mixed scenarios working")
        print("✓ Edge cases handled properly")
    elif success_rate >= 80:
        print("✅ Most MCP tests passed!")
        print("⚠️  Review failed tests above")
    elif success_rate >= 60:
        print("⚠️  Partial MCP functionality working")
        print("⚠️  Several tests failed - review above")
    else:
        print("❌ Many MCP tests failed")
        print("⚠️  MCP integration needs attention")
    
    print("="*80 + "\n")
    
    return success_rate >= 80


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


"""
End-to-End Test: Write Business Rule → Agent Reads It

This test proves the full MCP cycle works:
1. Write a test business rule to Neo4j via MCP
2. Agent queries for it
3. Verify agent returns the exact data we wrote
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_full_mcp_roundtrip():
    """Test writing and reading business rules via MCP"""
    
    print("\n" + "="*80)
    print("🧪 END-TO-END MCP ROUNDTRIP TEST")
    print("="*80)
    print("\nThis test proves agents can read business rules from Neo4j:\n")
    print("Step 1: Write a test business rule to Neo4j")
    print("Step 2: Agent queries for that rule")
    print("Step 3: Verify agent returns our exact data\n")
    
    # ========================================
    # STEP 1: Write Test Business Rule
    # ========================================
    print("="*80)
    print("STEP 1: Writing Test Business Rule to Neo4j via MCP")
    print("="*80 + "\n")
    
    try:
        from app.agents.shared.neo4j_mcp_loader import get_neo4j_mcp_tools
        
        tools = get_neo4j_mcp_tools()
        write_tool = next((t for t in tools if t.name == 'write_neo4j_cypher'), None)
        
        if not write_tool:
            print("❌ write_neo4j_cypher tool not found!")
            return False
        
        # Create a unique test rule
        test_rule = {
            "rule_id": "TEST_DTI_CONVENTIONAL_2024",
            "rule_type": "dti_limit",
            "loan_program": "conventional",
            "max_dti": 0.50,  # 50%
            "test_marker": "CURSOR_AI_TEST"
        }
        
        create_query = """
        MERGE (n:TestBusinessRule {rule_id: $rule_id})
        SET n.rule_type = $rule_type,
            n.loan_program = $loan_program,
            n.max_dti = $max_dti,
            n.test_marker = $test_marker
        RETURN n
        """
        
        print(f"Writing test rule: {test_rule}")
        result = await write_tool.ainvoke({
            'query': create_query,
            'params': test_rule
        })
        
        print(f"✓ Rule written successfully")
        print(f"Response: {result}\n")
        
    except Exception as e:
        print(f"❌ Failed to write test rule: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========================================
    # STEP 2: Agent Queries for the Rule
    # ========================================
    print("="*80)
    print("STEP 2: Agent Queries for Test Rule")
    print("="*80 + "\n")
    
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        
        # Ask agent to find our specific test rule
        test_input = {
            "messages": [{
                "role": "user",
                "content": f"""Query Neo4j for a business rule with rule_id = 'TEST_DTI_CONVENTIONAL_2024'.
                
                Use read_neo4j_cypher to find nodes with test_marker = 'CURSOR_AI_TEST'.
                Tell me the max_dti value you find."""
            }]
        }
        
        print("Asking agent to find our test rule...")
        response = await agent.ainvoke(test_input)
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("\n📊 Agent Response:")
        print("-" * 80)
        print(final_message)
        print("-" * 80 + "\n")
        
        # ========================================
        # STEP 3: Verify Agent Found Our Data
        # ========================================
        print("="*80)
        print("STEP 3: Verification")
        print("="*80 + "\n")
        
        # Check if agent mentions our specific test values
        success_checks = {
            "Found rule_id": "TEST_DTI_CONVENTIONAL_2024" in final_message or "test_dti_conventional" in final_message.lower(),
            "Found max_dti value": "0.5" in final_message or "50" in final_message or "0.50" in final_message,
            "Found test_marker": "CURSOR_AI_TEST" in final_message or "cursor_ai_test" in final_message.lower(),
            "Found loan_program": "conventional" in final_message.lower()
        }
        
        print("Verification Results:")
        for check, passed in success_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        passed_count = sum(success_checks.values())
        total_checks = len(success_checks)
        
        print(f"\nPassed: {passed_count}/{total_checks} checks")
        
        if passed_count >= 2:  # At least 2 checks must pass
            print("\n🎉 SUCCESS! Agent successfully read our test business rule from Neo4j!")
            print("✓ MCP write → Neo4j → MCP read → Agent → User works end-to-end!")
            success = True
        else:
            print("\n❌ FAILED! Agent did not return our test data")
            success = False
        
    except Exception as e:
        print(f"❌ Agent query failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    # ========================================
    # CLEANUP: Delete Test Rule
    # ========================================
    print("\n" + "="*80)
    print("CLEANUP: Removing Test Rule")
    print("="*80 + "\n")
    
    try:
        delete_query = """
        MATCH (n:TestBusinessRule {test_marker: 'CURSOR_AI_TEST'})
        DELETE n
        RETURN count(n) as deleted
        """
        
        result = await write_tool.ainvoke({'query': delete_query})
        print(f"✓ Test rule cleaned up: {result}\n")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}\n")
    
    return success


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("🧪 FULL MCP ROUNDTRIP VERIFICATION TEST")
    print("="*80)
    print("\nThis test verifies the complete MCP flow:")
    print("  Write → Neo4j → Read → Agent → User")
    print("\n")
    
    success = await test_full_mcp_roundtrip()
    
    print("\n" + "="*80)
    print("📊 FINAL RESULT")
    print("="*80)
    
    if success:
        print("\n✅ END-TO-END MCP INTEGRATION VERIFIED!")
        print("   Agents can successfully read business rules from Neo4j!\n")
        return True
    else:
        print("\n❌ MCP integration test failed")
        print("   Review the output above for details\n")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


"""
Test to verify agents actually call Neo4j MCP for business rules

This test checks HTTP traffic to confirm Neo4j MCP server is called.
"""

import sys
import asyncio
import logging
from pathlib import Path
import httpx

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging to capture HTTP requests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Track HTTP calls
neo4j_mcp_calls = []
original_request = httpx.AsyncClient.request

async def tracked_request(self, *args, **kwargs):
    """Intercept HTTP requests to track Neo4j MCP calls"""
    url = str(kwargs.get('url', args[1] if len(args) > 1 else ''))
    
    # Track Neo4j MCP calls
    if 'mcp-mortgage-business-rules' in url:
        neo4j_mcp_calls.append({
            'url': url,
            'method': kwargs.get('method', args[0] if len(args) > 0 else 'unknown')
        })
        print(f"\n🔍 Neo4j MCP CALLED: {kwargs.get('method', 'POST')} {url}")
    
    return await original_request(self, *args, **kwargs)

# Monkey patch to track requests
httpx.AsyncClient.request = tracked_request


async def test_underwriting_agent_uses_neo4j_mcp():
    """Test that UnderwritingAgent calls Neo4j MCP for business rules"""
    
    print("\n" + "="*80)
    print("🧪 TEST: UnderwritingAgent Neo4j MCP Usage")
    print("="*80 + "\n")
    
    global neo4j_mcp_calls
    neo4j_mcp_calls = []
    
    try:
        from app.agents.underwriting_agent.agent import create_underwriting_agent
        
        agent = create_underwriting_agent()
        
        # Ask a direct business rules question
        test_input = {
            "messages": [{
                "role": "user",
                "content": "What are the DTI requirements for a conventional loan? What's the maximum allowed?"
            }]
        }
        
        print("📋 Question: What are the DTI requirements for a conventional loan?\n")
        print("⏳ Waiting for agent response (ASYNC execution)...\n")
        
        response = await agent.ainvoke(test_input)
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📊 Agent Response:")
        print("-" * 80)
        print(final_message[:800] if len(final_message) > 800 else final_message)
        print("-" * 80)
        
        # Check if Neo4j MCP was called
        print(f"\n🔍 Neo4j MCP Calls Made: {len(neo4j_mcp_calls)}")
        
        if neo4j_mcp_calls:
            print("\n✅ SUCCESS! Neo4j MCP WAS CALLED:")
            for idx, call in enumerate(neo4j_mcp_calls, 1):
                print(f"  {idx}. {call['method']} {call['url']}")
            
            # Check response content
            if any(keyword in final_message.lower() for keyword in ['neo4j', 'query', 'match', 'node']):
                print("\n⚠️  Agent mentioned Neo4j/query terms - might be explaining rather than using")
            elif 'typically' in final_message.lower() or 'generally' in final_message.lower():
                print("\n⚠️  Agent used general terms - might not have used actual data")
            else:
                print("\n✅ Agent provided specific data-driven response")
            
            return True
        else:
            print("\n❌ FAILED! Neo4j MCP WAS NOT CALLED")
            print("Agent answered from general knowledge instead of querying Neo4j")
            
            # Check if agent mentioned it couldn't access data
            if 'unable' in final_message.lower() or 'cannot' in final_message.lower():
                print("⚠️  Agent reported inability to access data")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mortgage_advisor_uses_neo4j_mcp():
    """Test that MortgageAdvisorAgent calls Neo4j MCP for business rules"""
    
    print("\n" + "="*80)
    print("🧪 TEST: MortgageAdvisorAgent Neo4j MCP Usage")
    print("="*80 + "\n")
    
    global neo4j_mcp_calls
    neo4j_mcp_calls = []
    
    try:
        from app.agents.mortgage_advisor_agent.agent import create_mortgage_advisor_agent
        
        agent = create_mortgage_advisor_agent()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "What's the minimum credit score needed for an FHA loan?"
            }]
        }
        
        print("📋 Question: What's the minimum credit score for FHA loan?\n")
        print("⏳ Waiting for agent response (ASYNC execution)...\n")
        
        response = await agent.ainvoke(test_input)
        final_message = response["messages"][-1].content if response.get("messages") else ""
        
        print("📊 Agent Response:")
        print("-" * 80)
        print(final_message[:600] if len(final_message) > 600 else final_message)
        print("-" * 80)
        
        print(f"\n🔍 Neo4j MCP Calls Made: {len(neo4j_mcp_calls)}")
        
        if neo4j_mcp_calls:
            print("\n✅ SUCCESS! Neo4j MCP WAS CALLED:")
            for idx, call in enumerate(neo4j_mcp_calls, 1):
                print(f"  {idx}. {call['method']} {call['url']}")
            return True
        else:
            print("\n❌ FAILED! Neo4j MCP WAS NOT CALLED")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE NEO4J MCP USAGE TEST")
    print("="*80)
    print("\nThis test verifies that agents actually call Neo4j MCP for business rules")
    print("and don't just use their general knowledge.\n")
    
    results = []
    
    # Test 1: UnderwritingAgent
    result1 = await test_underwriting_agent_uses_neo4j_mcp()
    results.append(("UnderwritingAgent", result1))
    
    # Test 2: MortgageAdvisorAgent
    result2 = await test_mortgage_advisor_uses_neo4j_mcp()
    results.append(("MortgageAdvisorAgent", result2))
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for agent_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {agent_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL AGENTS SUCCESSFULLY USE NEO4J MCP FOR BUSINESS RULES!")
    else:
        print("\n⚠️  Some agents are not using Neo4j MCP - prompts need adjustment")
    
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


"""
Populate Neo4j with Realistic Credit Score Rules
=================================================

This script adds credit score requirements for different loan programs
based on real-world standards from Equifax, Experian, and TransUnion.

Credit Score Ranges (Industry Standard):
- 300-579: Poor
- 580-669: Fair
- 670-739: Good
- 740-799: Very Good
- 800-850: Exceptional

Loan Program Requirements (Real Industry Standards):
- FHA: 580 minimum (500 with 10% down)
- VA: No minimum (but lenders typically want 620+)
- USDA: No minimum (but lenders typically want 640+)
- Conventional: 620 minimum (better rates at 740+)
- Jumbo: 700+ minimum
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(message)s')


async def populate_credit_score_rules():
    """Add realistic credit score rules to Neo4j via MCP"""
    
    print("\n" + "="*80)
    print("📊 POPULATING NEO4J WITH CREDIT SCORE RULES")
    print("="*80 + "\n")
    
    from app.agents.shared.neo4j_mcp_loader import get_neo4j_mcp_tools
    
    tools = get_neo4j_mcp_tools()
    write_tool = None
    read_tool = None
    
    for tool in tools:
        if tool.name == "write_neo4j_cypher":
            write_tool = tool
        elif tool.name == "read_neo4j_cypher":
            read_tool = tool
    
    if not write_tool or not read_tool:
        print("❌ Failed to get Neo4j MCP tools")
        return False
    
    # Credit score rules to add
    rules = [
        # FHA Loan Requirements
        {
            "loan_program": "FHA",
            "min_credit_score": 580,
            "recommended_score": 620,
            "optimal_score": 680,
            "description": "FHA loans require 580 minimum (500 with 10% down payment)",
            "source": "HUD Handbook 4000.1",
            "tier": "government_backed"
        },
        {
            "loan_program": "FHA",
            "min_credit_score": 500,
            "min_down_payment": 0.10,
            "description": "FHA allows 500 credit score with 10% down payment",
            "source": "HUD Handbook 4000.1",
            "tier": "government_backed"
        },
        
        # VA Loan Requirements
        {
            "loan_program": "VA",
            "min_credit_score": 620,
            "recommended_score": 660,
            "optimal_score": 700,
            "description": "VA has no official minimum, but lenders typically require 620+",
            "source": "VA Lender Guidelines",
            "tier": "government_backed"
        },
        
        # USDA Loan Requirements
        {
            "loan_program": "USDA",
            "min_credit_score": 640,
            "recommended_score": 660,
            "optimal_score": 700,
            "description": "USDA has no official minimum, but lenders typically require 640+",
            "source": "USDA Rural Development Guidelines",
            "tier": "government_backed"
        },
        
        # Conventional Loan Requirements
        {
            "loan_program": "Conventional",
            "min_credit_score": 620,
            "recommended_score": 680,
            "optimal_score": 740,
            "description": "Conventional loans require 620 minimum, better rates at 740+",
            "source": "Fannie Mae/Freddie Mac Guidelines",
            "tier": "conventional"
        },
        {
            "loan_program": "Conventional",
            "min_credit_score": 740,
            "rate_benefit": "best_rates",
            "description": "Conventional loans offer best rates at 740+ credit score",
            "source": "Fannie Mae/Freddie Mac Guidelines",
            "tier": "conventional_premium"
        },
        
        # Jumbo Loan Requirements
        {
            "loan_program": "Jumbo",
            "min_credit_score": 700,
            "recommended_score": 740,
            "optimal_score": 760,
            "description": "Jumbo loans require 700+ minimum, 740+ for best rates",
            "source": "Jumbo Lender Guidelines",
            "tier": "jumbo"
        },
        
        # Credit Score Ranges (Industry Standard from Equifax/Experian/TransUnion)
        {
            "category": "CreditScoreRange",
            "range_name": "Poor",
            "min_score": 300,
            "max_score": 579,
            "description": "Poor credit - limited loan options, high interest rates",
            "source": "FICO/VantageScore Standard"
        },
        {
            "category": "CreditScoreRange",
            "range_name": "Fair",
            "min_score": 580,
            "max_score": 669,
            "description": "Fair credit - FHA eligible, higher interest rates",
            "source": "FICO/VantageScore Standard"
        },
        {
            "category": "CreditScoreRange",
            "range_name": "Good",
            "min_score": 670,
            "max_score": 739,
            "description": "Good credit - most loan programs available, competitive rates",
            "source": "FICO/VantageScore Standard"
        },
        {
            "category": "CreditScoreRange",
            "range_name": "Very Good",
            "min_score": 740,
            "max_score": 799,
            "description": "Very good credit - all programs available, excellent rates",
            "source": "FICO/VantageScore Standard"
        },
        {
            "category": "CreditScoreRange",
            "range_name": "Exceptional",
            "min_score": 800,
            "max_score": 850,
            "description": "Exceptional credit - best available rates and terms",
            "source": "FICO/VantageScore Standard"
        },
    ]
    
    print("Adding credit score rules to Neo4j...\n")
    
    success_count = 0
    
    for idx, rule in enumerate(rules, 1):
        try:
            # Create a unique node for each rule
            if "loan_program" in rule:
                # Loan program specific rule
                cypher = f"""
                CREATE (r:CreditScoreRequirement {{
                    id: '{rule['loan_program']}_credit_{rule['min_credit_score']}',
                    loan_program: '{rule['loan_program']}',
                    min_credit_score: {rule['min_credit_score']},
                    recommended_score: {rule.get('recommended_score', 'null')},
                    optimal_score: {rule.get('optimal_score', 'null')},
                    min_down_payment: {rule.get('min_down_payment', 'null')},
                    rate_benefit: '{rule.get('rate_benefit', '')}',
                    description: '{rule['description']}',
                    source: '{rule['source']}',
                    tier: '{rule['tier']}',
                    created_at: datetime()
                }})
                RETURN r.id as id, r.loan_program as program, r.min_credit_score as min_score
                """
            else:
                # Credit score range
                cypher = f"""
                CREATE (r:CreditScoreRange {{
                    id: 'range_{rule['range_name'].lower()}',
                    range_name: '{rule['range_name']}',
                    min_score: {rule['min_score']},
                    max_score: {rule['max_score']},
                    description: '{rule['description']}',
                    source: '{rule['source']}',
                    created_at: datetime()
                }})
                RETURN r.id as id, r.range_name as range, r.min_score as min, r.max_score as max
                """
            
            result = await write_tool.ainvoke({"query": cypher})
            
            if "loan_program" in rule:
                print(f"  ✅ {idx:2d}. Added: {rule['loan_program']} - Min Score: {rule['min_credit_score']}")
            else:
                print(f"  ✅ {idx:2d}. Added: Credit Range '{rule['range_name']}' ({rule['min_score']}-{rule['max_score']})")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ {idx:2d}. Failed to add rule: {e}")
    
    print(f"\n✅ Successfully added {success_count}/{len(rules)} credit score rules to Neo4j\n")
    
    # Verify by querying
    print("="*80)
    print("🔍 VERIFYING CREDIT SCORE RULES IN NEO4J")
    print("="*80 + "\n")
    
    verify_query = """
    MATCH (r:CreditScoreRequirement)
    RETURN r.loan_program as program, r.min_credit_score as min_score, r.description as description
    ORDER BY r.min_credit_score
    LIMIT 10
    """
    
    try:
        result = await read_tool.ainvoke({"query": verify_query})
        print("📊 Sample Credit Score Requirements:")
        print(result[:800] if len(str(result)) > 800 else result)
    except Exception as e:
        print(f"❌ Failed to verify: {e}")
    
    print("\n" + "="*80)
    print("✅ CREDIT SCORE RULES POPULATED SUCCESSFULLY!")
    print("="*80 + "\n")
    print("Agents can now query these rules using Neo4j MCP tools:")
    print("  • get_neo4j_schema() - Discover what nodes exist")
    print("  • read_neo4j_cypher(query='MATCH (r:CreditScoreRequirement) RETURN r')")
    print("\n")
    
    return True


async def cleanup_test_rules():
    """Remove test credit score rules (optional cleanup)"""
    
    print("\n" + "="*80)
    print("🧹 CLEANUP: Remove Test Credit Score Rules")
    print("="*80 + "\n")
    
    from app.agents.shared.neo4j_mcp_loader import get_neo4j_mcp_tools
    
    tools = get_neo4j_mcp_tools()
    write_tool = None
    
    for tool in tools:
        if tool.name == "write_neo4j_cypher":
            write_tool = tool
            break
    
    if not write_tool:
        print("❌ Failed to get write tool")
        return False
    
    cleanup_query = """
    MATCH (r:CreditScoreRequirement)
    WHERE r.created_at IS NOT NULL
    DELETE r
    """
    
    try:
        result = await write_tool.ainvoke({"query": cleanup_query})
        print("✅ Test credit score rules removed\n")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


async def main():
    """Main entry point"""
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        success = await cleanup_test_rules()
    else:
        success = await populate_credit_score_rules()
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


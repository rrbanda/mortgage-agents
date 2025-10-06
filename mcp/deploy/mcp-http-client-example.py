#!/usr/bin/env python3
"""
MCP HTTP Client Example for Mortgage Business Rules Server
This shows how agents can interact with the MCP server via HTTP
"""

import requests
import json
from typing import Dict, Any, List

class MCPMortgageClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        if params:
            payload["params"] = params
        
        response = requests.post(
            f"{self.base_url}/mcp/",
            headers=self.headers,
            json=payload,
            verify=False  # For self-signed certificates
        )
        
        # Parse Server-Sent Events response
        if response.headers.get('content-type', '').startswith('text/event-stream'):
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    return json.loads(data)
        
        return response.json()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        result = self._make_request("tools/list")
        return result.get("result", {}).get("tools", [])
    
    def get_neo4j_schema(self) -> Dict[str, Any]:
        """Get the Neo4j database schema"""
        result = self._make_request("tools/call", {
            "name": "get_neo4j_schema",
            "arguments": {}
        })
        return result.get("result", {})
    
    def query_neo4j(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a read-only Cypher query"""
        if params is None:
            params = {}
        
        result = self._make_request("tools/call", {
            "name": "read_neo4j_cypher",
            "arguments": {
                "query": query,
                "params": params
            }
        })
        
        content = result.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        return []
    
    def get_compliance_rules(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get compliance rules from the database"""
        query = f"MATCH (n:ComplianceRule) RETURN n.rule_id, n.category, n.description LIMIT {limit}"
        return self.query_neo4j(query)
    
    def get_applications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get mortgage applications from the database"""
        query = f"MATCH (a:Application) RETURN a.application_id, a.borrower_name, a.loan_amount, a.status LIMIT {limit}"
        return self.query_neo4j(query)
    
    def search_business_rules(self, rule_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for specific business rule types"""
        query = f"MATCH (n:{rule_type}) RETURN n LIMIT {limit}"
        return self.query_neo4j(query)

def main():
    """Example usage of the MCP client"""
    # Initialize client
    client = MCPMortgageClient("https://mcp-mortgage-business-rules-route-rh12026.apps.prod.rhoai.rh-aiservices-bu.com")
    
    print("🔧 Available MCP Tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n📊 Compliance Rules:")
    rules = client.get_compliance_rules(3)
    for rule in rules:
        print(f"  - {rule['n.rule_id']}: {rule['n.description']}")
    
    print("\n📋 Recent Applications:")
    apps = client.get_applications(3)
    for app in apps:
        print(f"  - {app['a.application_id']}: ${app['a.loan_amount']:,} - {app['a.status']}")
    
    print("\n🏠 Property Appraisal Rules:")
    appraisal_rules = client.search_business_rules("PropertyAppraisalRule", 2)
    for rule in appraisal_rules:
        print(f"  - {rule['n'].get('rule_id', 'N/A')}: {rule['n'].get('description', 'N/A')}")

if __name__ == "__main__":
    main()

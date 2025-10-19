#!/usr/bin/env python3
"""
Mock Credit Bureau API for Mortgage Processing
Simple HTTP server that provides realistic credit data for MCP integration

This is a SEPARATE service that doesn't modify existing mortgage agents.
Purpose: Provide credit check capability via MCP for Application Agent.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import random
import re

app = Flask(__name__)

# Mock database of credit profiles for testing
MOCK_CREDIT_PROFILES = {
    "987-65-4321": {
        "ssn": "987-65-4321",
        "first_name": "Sarah", 
        "last_name": "Johnson",
        "date_of_birth": "1990-05-20",
        "credit_score": 742,
        "credit_scores": {
            "experian": 745,
            "equifax": 742, 
            "transunion": 739
        },
        "credit_history_months": 156,  # 13 years
        "total_accounts": 12,
        "open_accounts": 8,
        "payment_history": {
            "on_time_percentage": 96.5,
            "late_30_days": 2,
            "late_60_days": 0,
            "late_90_days": 0
        },
        "derogatory_marks": {
            "bankruptcies": 0,
            "foreclosures": 0,
            "collections": 0,
            "charge_offs": 0
        },
        "total_debt": 45800,
        "available_credit": 87500,
        "credit_utilization": 15.2,
        "identity_verified": True,
        "fraud_alerts": []
    },
    "123-45-6789": {
        "ssn": "123-45-6789",
        "first_name": "Michael",
        "last_name": "Chen", 
        "date_of_birth": "1978-03-22",
        "credit_score": 680,
        "credit_scores": {
            "experian": 685,
            "equifax": 680,
            "transunion": 675
        },
        "credit_history_months": 220,  # 18+ years
        "total_accounts": 15,
        "open_accounts": 10,
        "payment_history": {
            "on_time_percentage": 88.3,
            "late_30_days": 5,
            "late_60_days": 1,
            "late_90_days": 0
        },
        "derogatory_marks": {
            "bankruptcies": 0,
            "foreclosures": 0,
            "collections": 1,
            "charge_offs": 1
        },
        "total_debt": 78500,
        "available_credit": 125000,
        "credit_utilization": 35.8,
        "identity_verified": True,
        "fraud_alerts": []
    }
}

def validate_ssn(ssn):
    """Validate SSN format"""
    ssn_pattern = r'^\d{3}-\d{2}-\d{4}$'
    return bool(re.match(ssn_pattern, ssn))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "mock-credit-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/credit-score', methods=['POST'])
def get_credit_score():
    """
    Pull tri-bureau credit scores for mortgage qualification
    
    Request: {"ssn": "123-45-6789", "first_name": "Sarah", "last_name": "Johnson"}
    Response: Credit scores and basic qualification data
    """
    try:
        data = request.get_json()
        
        if not data or 'ssn' not in data:
            return jsonify({"error": "SSN required"}), 400
            
        ssn = data['ssn']
        
        if not validate_ssn(ssn):
            return jsonify({"error": "Invalid SSN format. Use XXX-XX-XXXX"}), 400
        
        # Check if we have mock data for this SSN
        if ssn not in MOCK_CREDIT_PROFILES:
            # Generate random but realistic credit data
            profile = generate_random_credit_profile(ssn, data.get('first_name', 'John'), data.get('last_name', 'Doe'))
        else:
            profile = MOCK_CREDIT_PROFILES[ssn]
        
        # Return credit score response optimized for mortgage qualification
        response = {
            "ssn": profile["ssn"],
            "identity_match": True,
            "credit_score": profile["credit_score"],
            "tri_bureau_scores": profile["credit_scores"],
            "credit_score_date": datetime.now().strftime("%Y-%m-%d"),
            "mortgage_qualification": {
                "conventional_eligible": profile["credit_score"] >= 620,
                "fha_eligible": profile["credit_score"] >= 580,
                "va_eligible": profile["credit_score"] >= 620,
                "jumbo_eligible": profile["credit_score"] >= 700
            },
            "risk_factors": {
                "credit_utilization": profile["credit_utilization"],
                "payment_history_score": profile["payment_history"]["on_time_percentage"],
                "derogatory_marks": profile["derogatory_marks"]["bankruptcies"] + profile["derogatory_marks"]["collections"]
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Credit score lookup failed: {str(e)}"}), 500

def normalize_date(date_str):
    """
    Normalize date to YYYY-MM-DD format
    Accepts: YYYY-MM-DD, MM/DD/YYYY, or M/D/YYYY
    """
    from datetime import datetime
    
    # Try ISO format first (YYYY-MM-DD)
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Try US format (MM/DD/YYYY or M/D/YYYY)
    try:
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Return as-is if can't parse
    return date_str

@app.route('/verify-identity', methods=['POST'])  
def verify_identity():
    """
    Cross-reference personal info with credit file for identity verification
    
    Request: {"ssn": "123-45-6789", "first_name": "Sarah", "last_name": "Johnson", "date_of_birth": "1985-06-15"}
    Response: Identity verification status and confidence score
    """
    try:
        data = request.get_json()
        
        required_fields = ['ssn', 'first_name', 'last_name', 'date_of_birth']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"{field} required for identity verification"}), 400
        
        ssn = data['ssn']
        
        if not validate_ssn(ssn):
            return jsonify({"error": "Invalid SSN format"}), 400
            
        # Check mock profiles for identity match
        if ssn in MOCK_CREDIT_PROFILES:
            profile = MOCK_CREDIT_PROFILES[ssn]
            
            name_match = (data['first_name'].lower() == profile['first_name'].lower() and 
                         data['last_name'].lower() == profile['last_name'].lower())
            # Normalize both dates for comparison
            dob_match = normalize_date(data['date_of_birth']) == normalize_date(profile['date_of_birth'])
            
            confidence_score = 0
            if name_match: confidence_score += 60
            if dob_match: confidence_score += 40
            
        else:
            # For unknown SSNs, simulate moderate confidence
            name_match = True  # Assume reasonable match
            dob_match = True
            confidence_score = 85
        
        response = {
            "ssn": ssn,
            "identity_verified": confidence_score >= 80,
            "confidence_score": confidence_score,
            "match_details": {
                "name_match": name_match,
                "date_of_birth_match": dob_match,
                "address_on_file": True  # Simplified for demo
            },
            "fraud_indicators": {
                "alerts_found": len(MOCK_CREDIT_PROFILES.get(ssn, {}).get("fraud_alerts", [])),
                "identity_theft_flag": False,
                "deceased_flag": False
            },
            "verification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Identity verification failed: {str(e)}"}), 500

@app.route('/credit-report', methods=['POST'])
def get_credit_report():
    """
    Get detailed credit report with trade lines and payment history
    
    Request: {"ssn": "123-45-6789"}
    Response: Comprehensive credit report data for underwriting analysis
    """
    try:
        data = request.get_json()
        
        if not data or 'ssn' not in data:
            return jsonify({"error": "SSN required"}), 400
            
        ssn = data['ssn']
        
        if not validate_ssn(ssn):
            return jsonify({"error": "Invalid SSN format"}), 400
        
        # Get or generate credit profile
        if ssn in MOCK_CREDIT_PROFILES:
            profile = MOCK_CREDIT_PROFILES[ssn]
        else:
            profile = generate_random_credit_profile(ssn, "Unknown", "Borrower")
        
        # Generate realistic trade lines
        trade_lines = generate_trade_lines(profile)
        
        response = {
            "ssn": profile["ssn"],
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "credit_summary": {
                "credit_score": profile["credit_score"],
                "tri_bureau_scores": profile["credit_scores"],
                "credit_history_length_months": profile["credit_history_months"],
                "total_accounts": profile["total_accounts"],
                "open_accounts": profile["open_accounts"],
                "credit_utilization_percent": profile["credit_utilization"]
            },
            "payment_history": profile["payment_history"],
            "derogatory_marks": profile["derogatory_marks"],
            "trade_lines": trade_lines,
            "inquiries": {
                "hard_inquiries_12_months": random.randint(0, 3),
                "soft_inquiries_12_months": random.randint(2, 8)
            },
            "underwriting_flags": {
                "recent_late_payments": profile["payment_history"]["late_30_days"] > 2,
                "high_utilization": profile["credit_utilization"] > 30,
                "short_credit_history": profile["credit_history_months"] < 24,
                "derogatory_present": sum(profile["derogatory_marks"].values()) > 0
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Credit report lookup failed: {str(e)}"}), 500

def generate_random_credit_profile(ssn, first_name, last_name):
    """Generate realistic random credit profile for unknown SSNs"""
    credit_score = random.randint(580, 800)
    
    return {
        "ssn": ssn,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": f"{random.randint(1970, 1995)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "credit_score": credit_score,
        "credit_scores": {
            "experian": credit_score + random.randint(-15, 15),
            "equifax": credit_score + random.randint(-10, 10), 
            "transunion": credit_score + random.randint(-12, 12)
        },
        "credit_history_months": random.randint(24, 240),
        "total_accounts": random.randint(5, 20),
        "open_accounts": random.randint(3, 12),
        "payment_history": {
            "on_time_percentage": random.uniform(75, 99),
            "late_30_days": random.randint(0, 8),
            "late_60_days": random.randint(0, 3),
            "late_90_days": random.randint(0, 1)
        },
        "derogatory_marks": {
            "bankruptcies": random.choice([0, 0, 0, 0, 1]) if credit_score < 650 else 0,
            "foreclosures": random.choice([0, 0, 0, 1]) if credit_score < 600 else 0,
            "collections": random.randint(0, 3) if credit_score < 700 else 0,
            "charge_offs": random.randint(0, 2) if credit_score < 650 else 0
        },
        "total_debt": random.randint(5000, 150000),
        "available_credit": random.randint(10000, 200000),
        "credit_utilization": random.uniform(5, 75),
        "identity_verified": True,
        "fraud_alerts": []
    }

def generate_trade_lines(profile):
    """Generate realistic trade lines for credit report"""
    trade_lines = []
    
    # Add some credit cards
    for i in range(random.randint(2, 6)):
        trade_lines.append({
            "account_type": "credit_card",
            "creditor_name": random.choice(["Chase", "Capital One", "Discover", "American Express", "Citi"]),
            "account_status": "open",
            "credit_limit": random.randint(1000, 25000),
            "current_balance": random.randint(0, 15000),
            "payment_status": "current" if random.random() > 0.1 else "30_days_late",
            "opened_date": (datetime.now() - timedelta(days=random.randint(365, 2555))).strftime("%Y-%m-%d")
        })
    
    # Add installment loans
    if random.random() > 0.3:  # 70% chance of having installment loans
        trade_lines.append({
            "account_type": "auto_loan",
            "creditor_name": random.choice(["Toyota Financial", "Ford Credit", "Wells Fargo Auto"]),
            "account_status": "open",
            "original_amount": random.randint(15000, 45000),
            "current_balance": random.randint(5000, 35000),
            "payment_status": "current",
            "opened_date": (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime("%Y-%m-%d")
        })
    
    return trade_lines

# OpenAPI specification endpoint
@app.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """OpenAPI specification for gen-mcp conversion"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Mock Credit Bureau API",
            "version": "1.0.0",
            "description": "Mock credit bureau API for mortgage processing MCP integration"
        },
        "servers": [
            {"url": "http://localhost:8080", "description": "Development server"}
        ],
        "paths": {
            "/credit-score": {
                "post": {
                    "summary": "Get credit scores for mortgage qualification",
                    "description": "Pull tri-bureau credit scores and mortgage eligibility data",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["ssn"],
                                    "properties": {
                                        "ssn": {"type": "string", "pattern": "^\\d{3}-\\d{2}-\\d{4}$"},
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Credit score data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "credit_score": {"type": "integer"},
                                            "tri_bureau_scores": {"type": "object"},
                                            "mortgage_qualification": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/verify-identity": {
                "post": {
                    "summary": "Verify borrower identity against credit file",
                    "description": "Cross-reference personal information with credit bureau records",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["ssn", "first_name", "last_name", "date_of_birth"],
                                    "properties": {
                                        "ssn": {"type": "string"},
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"},
                                        "date_of_birth": {"type": "string", "format": "date"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Identity verification result",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "identity_verified": {"type": "boolean"},
                                            "confidence_score": {"type": "integer"},
                                            "fraud_indicators": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/credit-report": {
                "post": {
                    "summary": "Get detailed credit report",
                    "description": "Comprehensive credit report with trade lines and payment history",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["ssn"],
                                    "properties": {
                                        "ssn": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Detailed credit report",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "credit_summary": {"type": "object"},
                                            "trade_lines": {"type": "array"},
                                            "underwriting_flags": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return jsonify(spec)

if __name__ == '__main__':
    print("🏦 Starting Mock Credit Bureau API...")
    print("📊 Available endpoints:")
    print("  POST /credit-score - Get credit scores for mortgage qualification")  
    print("  POST /verify-identity - Verify borrower identity")
    print("  POST /credit-report - Get detailed credit report")
    print("  GET /openapi.json - OpenAPI specification for gen-mcp")
    print("  GET /health - Health check")
    print("\n🔗 OpenAPI spec: http://localhost:8080/openapi.json")
    print("🚀 Ready for gen-mcp conversion!")
    
    # Use environment variable for port (OpenShift compatibility)
    import os
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)

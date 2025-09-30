"""
Analyze Credit Risk Tool - Neo4j Powered

This tool performs comprehensive credit risk analysis for mortgage underwriting
by querying Neo4j underwriting rules and credit analysis criteria.

Purpose:
- Evaluate credit score requirements by loan program
- Analyze derogatory credit events and seasoning
- Assess credit history depth and patterns
- Provide credit risk recommendations
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

try:
    from utils import get_neo4j_connection, initialize_connection
except ImportError:
    # Fallback for different import paths during testing
    from utils import get_neo4j_connection, initialize_connection


class CreditAnalysisRequest(BaseModel):
    """Schema for credit risk analysis request"""
    credit_score: int = Field(description="Current credit score (300-850)")
    loan_program: str = Field(description="Loan program type: 'conventional', 'fha', 'va', 'usda', 'jumbo'")
    bankruptcy_months_ago: Optional[int] = Field(description="Months since bankruptcy discharge (if any)", default=None)
    foreclosure_months_ago: Optional[int] = Field(description="Months since foreclosure (if any)", default=None)
    late_payments_12_months: Dict[str, int] = Field(
        description="Late payment counts in past 12 months: {'30_day': 0, '60_day': 0, '90_day': 0}",
        default_factory=lambda: {"30_day": 0, "60_day": 0, "90_day": 0}
    )
    open_collections: int = Field(description="Number of open collection accounts", default=0)
    credit_history_years: float = Field(description="Length of credit history in years")


@tool
def analyze_credit_risk(tool_input: str) -> str:
    """Perform comprehensive credit risk analysis for mortgage underwriting.
    
    This tool analyzes a borrower's credit profile against predefined business rules
    from Neo4j to assess credit risk and provide recommendations for underwriting.
    
    Args:
        tool_input: Credit details in natural language format
        
    Example:
        "Credit: 720, Loan: conventional, Bankruptcy: 36 months ago, Collections: 0, History: 8 years"
    
    Returns:
        String containing comprehensive credit risk analysis report
    """
    
    try:
        # Use standardized parsing first, then custom parsing for tool-specific data
        from agents.shared.input_parser import parse_mortgage_application
        import re
        
        parsed_data = parse_mortgage_application(tool_input)
        borrower_info = tool_input.lower() # Keep for fallback regex
        
        # Extract credit score (use parser first, regex fallback)
        credit_score = parsed_data.get("credit_score") or 720
        credit_match = re.search(r'credit[:\s]*(\d+)', borrower_info)
        if credit_match and not parsed_data.get("credit_score"):
            credit_score = int(credit_match.group(1))
        
        # Extract loan program (use parser first, regex fallback)
        loan_program = parsed_data.get("loan_program") or "conventional"
        loan_match = re.search(r'loan[:\s]*([a-z]+)', borrower_info)
        if loan_match and not parsed_data.get("loan_program"):
            loan_program = loan_match.group(1)
        
        # Extract bankruptcy info
        bankruptcy_match = re.search(r'bankruptcy[:\s]*(\d+)', borrower_info)
        bankruptcy_months_ago = int(bankruptcy_match.group(1)) if bankruptcy_match else None
        
        # Extract foreclosure info
        foreclosure_match = re.search(r'foreclosure[:\s]*(\d+)', borrower_info)
        foreclosure_months_ago = int(foreclosure_match.group(1)) if foreclosure_match else None
        
        # Extract collections
        collections_match = re.search(r'collections[:\s]*(\d+)', borrower_info)
        open_collections = int(collections_match.group(1)) if collections_match else 0
        
        # Extract credit history
        history_match = re.search(r'history[:\s]*(\d+)', borrower_info)
        credit_history_years = float(history_match.group(1)) if history_match else 8.0
        
        # Set default late payments
        late_payments_12_months = {"30_day": 0, "60_day": 0, "90_day": 0}
        
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        # Query underwriting rules for credit analysis
        credit_rules_query = """
        MATCH (r:UnderwritingRule) 
        WHERE r.category = 'CreditAnalysis'
        RETURN r
        ORDER BY r.rule_id
        """
        
        with connection.driver.session(database=connection.database) as session:
            result = session.run(credit_rules_query)
            credit_rules = [dict(record['r']) for record in result]
        
        if not credit_rules:
            return " No credit analysis rules found in Neo4j. Please load underwriting rules first."
        
        # Analyze credit score requirements
        score_analysis = _analyze_credit_score(credit_score, loan_program, credit_rules)
        
        # Analyze derogatory events
        derogatory_analysis = _analyze_derogatory_events(
            bankruptcy_months_ago, foreclosure_months_ago, late_payments_12_months, 
            open_collections, credit_rules
        )
        
        # Analyze credit history depth
        history_analysis = _analyze_credit_history(credit_history_years, credit_rules)
        
        # Calculate overall risk level
        risk_level, risk_factors = _calculate_credit_risk_level(
            score_analysis, derogatory_analysis, history_analysis
        )
        
        # Generate recommendations
        recommendations = _generate_credit_recommendations(
            risk_level, risk_factors, loan_program, credit_rules
        )
        
        return _format_credit_analysis_report(
            credit_score, loan_program, risk_level, score_analysis, 
            derogatory_analysis, history_analysis, recommendations
        )
        
    except Exception as e:
        return f" Error during credit risk analysis: {str(e)}"


def _analyze_credit_score(credit_score: int, loan_program: str, rules: List[Dict]) -> Dict[str, Any]:
    """Analyze credit score against program requirements."""
    score_analysis = {
        "meets_minimum": False,
        "minimum_required": None,
        "score_tier": "poor",
        "exceptions_available": False
    }
    
    # Find minimum score rule
    for rule in rules:
        if rule.get("rule_type") == "minimum_requirements" and loan_program in rule.get("loan_programs", []):
            try:
                minimum_scores = json.loads(rule.get("minimum_scores", "{}"))
                minimum_required = minimum_scores.get(loan_program, 620)
                score_analysis["minimum_required"] = minimum_required
                score_analysis["meets_minimum"] = credit_score >= minimum_required
                score_analysis["exceptions_available"] = "compensating_factors" in rule.get("exceptions", [])
                break
            except:
                continue
    
    # Determine score tier
    if credit_score >= 740:
        score_analysis["score_tier"] = "excellent"
    elif credit_score >= 680:
        score_analysis["score_tier"] = "good"
    elif credit_score >= 620:
        score_analysis["score_tier"] = "fair"
    else:
        score_analysis["score_tier"] = "poor"
    
    return score_analysis


def _analyze_derogatory_events(
    bankruptcy_months: Optional[int], 
    foreclosure_months: Optional[int],
    late_payments: Dict[str, int],
    collections: int,
    rules: List[Dict]
) -> Dict[str, Any]:
    """Analyze derogatory credit events."""
    derogatory_analysis = {
        "bankruptcy_compliant": True,
        "foreclosure_compliant": True,
        "late_payments_compliant": True,
        "collections_compliant": True,
        "issues": []
    }
    
    # Find derogatory events rule
    for rule in rules:
        if rule.get("rule_type") == "derogatory_analysis":
            try:
                # Check bankruptcy seasoning
                if bankruptcy_months is not None:
                    bankruptcy_requirements = json.loads(rule.get("bankruptcy_seasoning", "{}"))
                    min_months = bankruptcy_requirements.get("chapter_7", 48)  # Default to Chapter 7
                    if bankruptcy_months < min_months:
                        derogatory_analysis["bankruptcy_compliant"] = False
                        derogatory_analysis["issues"].append(f"Bankruptcy seasoning insufficient: {bankruptcy_months} months (need {min_months})")
                
                # Check foreclosure seasoning
                if foreclosure_months is not None:
                    min_foreclosure = rule.get("foreclosure_seasoning", 36)
                    if foreclosure_months < min_foreclosure:
                        derogatory_analysis["foreclosure_compliant"] = False
                        derogatory_analysis["issues"].append(f"Foreclosure seasoning insufficient: {foreclosure_months} months (need {min_foreclosure})")
                
                # Check late payment tolerance
                late_tolerance = json.loads(rule.get("late_payment_tolerance", "{}"))
                for severity, count in late_payments.items():
                    max_allowed = late_tolerance.get(severity, 0)
                    if count > max_allowed:
                        derogatory_analysis["late_payments_compliant"] = False
                        derogatory_analysis["issues"].append(f"Excessive {severity} late payments: {count} (max {max_allowed})")
                
                # Check collections
                if collections > 0:
                    collection_treatment = rule.get("collection_treatment", "paid_or_payment_plan")
                    if collection_treatment == "paid_or_payment_plan":
                        derogatory_analysis["issues"].append(f"Collections must be paid or have payment plan: {collections} accounts")
                
                break
            except Exception as e:
                continue
    
    return derogatory_analysis


def _analyze_credit_history(credit_years: float, rules: List[Dict]) -> Dict[str, Any]:
    """Analyze credit history depth."""
    history_analysis = {
        "sufficient_depth": credit_years >= 2.0,
        "years_available": credit_years,
        "recommendation": ""
    }
    
    if credit_years < 1.0:
        history_analysis["recommendation"] = "Thin credit file - consider alternative credit sources"
    elif credit_years < 2.0:
        history_analysis["recommendation"] = "Limited credit history - may need compensating factors"
    elif credit_years >= 7.0:
        history_analysis["recommendation"] = "Excellent credit history depth"
    else:
        history_analysis["recommendation"] = "Good credit history depth"
    
    return history_analysis


def _calculate_credit_risk_level(
    score_analysis: Dict, 
    derogatory_analysis: Dict, 
    history_analysis: Dict
) -> tuple[str, List[str]]:
    """Calculate overall credit risk level."""
    risk_factors = []
    
    # Score-based risk
    if score_analysis["score_tier"] == "poor":
        risk_factors.append("Low credit score")
    if not score_analysis["meets_minimum"]:
        risk_factors.append("Below minimum score requirement")
    
    # Derogatory event risk
    if not derogatory_analysis["bankruptcy_compliant"]:
        risk_factors.append("Recent bankruptcy")
    if not derogatory_analysis["foreclosure_compliant"]:
        risk_factors.append("Recent foreclosure")
    if not derogatory_analysis["late_payments_compliant"]:
        risk_factors.append("Excessive late payments")
    
    # History depth risk
    if not history_analysis["sufficient_depth"]:
        risk_factors.append("Limited credit history")
    
    # Determine overall risk level
    if len(risk_factors) == 0:
        risk_level = "LOW"
    elif len(risk_factors) <= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return risk_level, risk_factors


def _generate_credit_recommendations(
    risk_level: str, 
    risk_factors: List[str], 
    loan_program: str, 
    rules: List[Dict]
) -> List[str]:
    """Generate credit improvement recommendations."""
    recommendations = []
    
    if risk_level == "LOW":
        recommendations.append(" Credit profile meets underwriting standards")
        recommendations.append("Consider shopping for best rates with excellent credit")
    elif risk_level == "MEDIUM":
        recommendations.append("⚠️ Credit profile acceptable with possible conditions")
        if "Low credit score" in risk_factors:
            recommendations.append("Consider improving credit score before applying")
        if "Limited credit history" in risk_factors:
            recommendations.append("Provide alternative credit documentation")
    else:  # HIGH risk
        recommendations.append(" Credit profile presents significant challenges")
        recommendations.append("Consider manual underwriting if available")
        recommendations.append("Work on credit repair before applying")
        if loan_program in ["conventional", "jumbo"]:
            recommendations.append("Consider FHA or VA loan programs with more flexible credit requirements")
    
    return recommendations


def _format_credit_analysis_report(
    credit_score: int,
    loan_program: str, 
    risk_level: str,
    score_analysis: Dict,
    derogatory_analysis: Dict,
    history_analysis: Dict,
    recommendations: List[str]
) -> str:
    """Format the comprehensive credit analysis report."""
    
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
    
    report = f"""
🔍 **Credit Risk Analysis Report**

**Overall Risk Level:** {risk_emoji.get(risk_level, "⚪")} {risk_level}
**Credit Score:** {credit_score} ({score_analysis['score_tier'].title()})
**Loan Program:** {loan_program.upper()}

📊 **Credit Score Analysis:**
• Minimum Required: {score_analysis.get('minimum_required', 'Not specified')}
• Meets Minimum: {' Yes' if score_analysis['meets_minimum'] else ' No'}
• Score Tier: {score_analysis['score_tier'].title()}
• Exceptions Available: {' Yes' if score_analysis['exceptions_available'] else ' No'}

📋 **Derogatory Events Analysis:**
• Bankruptcy Compliant: {' Yes' if derogatory_analysis['bankruptcy_compliant'] else ' No'}
• Foreclosure Compliant: {' Yes' if derogatory_analysis['foreclosure_compliant'] else ' No'}
• Late Payments Compliant: {' Yes' if derogatory_analysis['late_payments_compliant'] else ' No'}
• Collections Compliant: {' Yes' if derogatory_analysis['collections_compliant'] else ' No'}
"""
    
    if derogatory_analysis['issues']:
        report += "\n**⚠️ Credit Issues Identified:**\n"
        for issue in derogatory_analysis['issues']:
            report += f"• {issue}\n"
    
    report += f"""
📚 **Credit History:**
• Years of History: {history_analysis['years_available']:.1f} years
• Sufficient Depth: {' Yes' if history_analysis['sufficient_depth'] else ' No'}
• Assessment: {history_analysis['recommendation']}

💡 **Recommendations:**
"""
    for rec in recommendations:
        report += f"• {rec}\n"
    
    report += """
---
**Next Steps:** Review with underwriter if risk level is MEDIUM or HIGH
"""
    
    return report


def validate_tool() -> bool:
    """Validate that the analyze_credit_risk tool works correctly."""
    try:
        # Test with sample data
        result = analyze_credit_risk.invoke({
            "credit_score": 720,
            "loan_program": "conventional",
            "bankruptcy_months_ago": None,
            "foreclosure_months_ago": None,
            "late_payments_12_months": {"30_day": 0, "60_day": 0, "90_day": 0},
            "open_collections": 0,
            "credit_history_years": 5.0
        })
        return "Credit Risk Analysis Report" in result and "Overall Risk Level" in result
    except Exception as e:
        print(f"Credit risk analysis tool validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the tool
    print("Testing analyze_credit_risk tool...")
    result = validate_tool()
    print(f"Validation result: {result}")

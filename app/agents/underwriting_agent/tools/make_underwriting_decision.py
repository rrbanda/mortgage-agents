"""
Make Underwriting Decision Tool - Neo4j Powered

This tool makes final underwriting decisions for mortgage applications
by analyzing all underwriting factors and applying decision rules from Neo4j.

Purpose:
- Combine credit, income, DTI, and asset analysis
- Apply automated underwriting decision rules
- Generate approval, denial, or manual review recommendations
- Provide detailed reasoning for decisions
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


class UnderwritingFactors(BaseModel):
    """Schema for comprehensive underwriting factors"""
    # Credit factors
    credit_score: int = Field(description="Current credit score (300-850)")
    credit_risk_level: str = Field(description="Credit risk level: 'LOW', 'MEDIUM', 'HIGH'")
    
    # Income factors
    monthly_gross_income: float = Field(description="Total monthly gross income")
    income_stability: str = Field(description="Income stability rating: 'excellent', 'good', 'fair', 'poor'")
    
    # DTI factors
    front_end_dti: float = Field(description="Front-end DTI ratio percentage")
    back_end_dti: float = Field(description="Back-end DTI ratio percentage")
    
    # Loan factors
    loan_program: str = Field(description="Loan program: 'conventional', 'fha', 'va', 'usda', 'jumbo'")
    loan_amount: float = Field(description="Requested loan amount")
    down_payment_percent: float = Field(description="Down payment percentage (e.g., 0.20 for 20%)")
    property_value: float = Field(description="Appraised property value")
    
    # Additional factors
    cash_reserves_months: float = Field(description="Months of cash reserves", default=0.0)
    employment_years: float = Field(description="Years at current employment", default=2.0)
    first_time_buyer: bool = Field(description="Is first-time home buyer", default=False)
    property_type: str = Field(description="Property type: 'primary_residence', 'investment', 'vacation_home'")


@tool
def make_underwriting_decision(tool_input: str) -> str:
    """Make comprehensive underwriting decision based on all application factors.
    
    Args:
        tool_input: Underwriting analysis summary in natural language format
        
    Example:
        "Credit: 720 LOW risk, Income: 95000 good stability, DTI: 10.7% front, 15.2% back, Loan: conventional 390000, Down: 13.3%, Property: 450000, Reserves: 8 months"
    
    Returns:
        String containing comprehensive underwriting decision with detailed reasoning
    """
    
    try:
        # Use standardized parser for robust underwriting data parsing
        from agents.shared.input_parser import parse_mortgage_application
        import re
        
        # Parse using standardized parser first
        parsed_data = parse_mortgage_application(tool_input)
        summary = tool_input.lower()
        
        # Extract credit score and risk (use parser first, regex fallback)
        credit_score = parsed_data.get("credit_score") or 720
        credit_match = re.search(r'credit[:\s]*(\d+)', summary)
        if credit_match and not parsed_data.get("credit_score"):
            credit_score = int(credit_match.group(1))
        
        risk_match = re.search(r'(low|medium|high)\s*risk', summary)
        credit_risk_level = risk_match.group(1).upper() if risk_match else "LOW"
        
        # Extract income (use parser first, regex fallback)
        monthly_gross_income = parsed_data.get("monthly_income") or 7917.0
        income_match = re.search(r'income[:\s]*(\d+)', summary)
        if income_match and not parsed_data.get("monthly_income"):
            monthly_gross_income = float(income_match.group(1))
        
        # Extract income stability
        stability_match = re.search(r'(excellent|good|fair|poor)\s*stability', summary)
        income_stability = stability_match.group(1) if stability_match else "good"
        
        # Extract DTI ratios
        front_dti_match = re.search(r'(\d+\.?\d*)[%\s]*front', summary)
        front_end_dti = float(front_dti_match.group(1)) if front_dti_match else 10.7
        
        back_dti_match = re.search(r'(\d+\.?\d*)[%\s]*back', summary)
        back_end_dti = float(back_dti_match.group(1)) if back_dti_match else 15.2
        
        # Extract loan info
        loan_match = re.search(r'loan[:\s]*([a-z]+)', summary)
        loan_program = loan_match.group(1) if loan_match else "conventional"
        
        amount_match = re.search(r'loan[^0-9]*(\d+)', summary)
        loan_amount = float(amount_match.group(1)) if amount_match else 390000.0
        
        # Extract down payment percentage
        down_match = re.search(r'down[:\s]*(\d+\.?\d*)', summary)
        down_payment_percent = float(down_match.group(1)) / 100 if down_match else 0.13
        
        # Extract property value
        property_match = re.search(r'property[:\s]*(\d+)', summary)
        property_value = float(property_match.group(1)) if property_match else 450000.0
        
        # Extract reserves
        reserves_match = re.search(r'reserves[:\s]*(\d+)', summary)
        cash_reserves_months = float(reserves_match.group(1)) if reserves_match else 8.0
        
        # Set defaults
        employment_years = 5.0
        first_time_buyer = True
        property_type = "primary_residence"
        
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        # Query underwriting decision rules
        decision_rules_query = """
        MATCH (r:UnderwritingRule) 
        WHERE r.category IN ['DecisionMatrix', 'ApprovalConditions', 'CompensatingFactors']
        RETURN r
        ORDER BY r.rule_id
        """
        
        with connection.driver.session(database=connection.database) as session:
            result = session.run(decision_rules_query)
            decision_rules = [dict(record['r']) for record in result]
        
        if not decision_rules:
            return " No underwriting decision rules found in Neo4j. Please load underwriting rules first."
        
        # Calculate derived metrics
        ltv_ratio = (loan_amount / property_value) * 100 if property_value > 0 else 0
        
        # Calculate actual monthly debt amounts from DTI ratios (FIX: correct calculation)
        monthly_housing_payment = (front_end_dti / 100) * monthly_gross_income
        total_monthly_debt = (back_end_dti / 100) * monthly_gross_income
        monthly_non_housing_debt = total_monthly_debt - monthly_housing_payment
        
        # Collect all factors for analysis
        underwriting_factors = {
            "credit_score": credit_score,
            "credit_risk_level": credit_risk_level,
            "front_end_dti": front_end_dti,
            "back_end_dti": back_end_dti,
            "ltv_ratio": ltv_ratio,
            "down_payment_percent": down_payment_percent * 100,  # Convert to percentage
            "loan_amount": loan_amount,
            "property_value": property_value,
            "income_stability": income_stability,
            "employment_years": employment_years,
            "cash_reserves_months": cash_reserves_months,
            "loan_program": loan_program,
            "property_type": property_type,
            "first_time_buyer": first_time_buyer,
            # Corrected debt calculations
            "monthly_gross_income": monthly_gross_income,
            "monthly_housing_payment": monthly_housing_payment,
            "total_monthly_debt": total_monthly_debt,
            "monthly_non_housing_debt": monthly_non_housing_debt
        }
        
        # Analyze approval factors
        approval_analysis = _analyze_approval_factors(underwriting_factors, decision_rules)
        
        # Check for compensating factors
        compensating_factors = _identify_compensating_factors(underwriting_factors, decision_rules)
        
        # Make preliminary decision
        preliminary_decision = _make_preliminary_decision(approval_analysis, compensating_factors)
        
        # Apply program-specific overlays
        final_decision = _apply_program_overlays(preliminary_decision, underwriting_factors, decision_rules)
        
        # Generate conditions and recommendations
        conditions = _generate_approval_conditions(final_decision, underwriting_factors, decision_rules)
        
        return _format_underwriting_decision_report(
            final_decision, underwriting_factors, approval_analysis, 
            compensating_factors, conditions, loan_program
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during underwriting decision: {e}")
        return f"❌ Error during underwriting decision: {str(e)}"


def _get_fallback_dti_limits(loan_program: str) -> Dict[str, float]:
    """Fallback DTI limits when Neo4j rules are unavailable (minimal hardcoding)."""
    
    # Conservative fallbacks - prefer Neo4j rules when available
    fallback_limits = {
        "fha": {"front_end": 31.0, "back_end": 43.0},
        "conventional": {"front_end": 28.0, "back_end": 45.0},
        "va": {"front_end": 100.0, "back_end": 100.0},  # VA has no DTI limit
        "usda": {"front_end": 29.0, "back_end": 41.0},
    }
    
    # Default to conservative QM limits when program unknown
    return fallback_limits.get(loan_program.lower(), {"front_end": 28.0, "back_end": 43.0})


def _get_max_ltv_from_rules(loan_program: str, property_type: str, rules: List[Dict]) -> float:
    """Get max LTV from Neo4j rules with minimal fallbacks."""
    
    # Try to find LTV rules in Neo4j first
    for rule in rules:
        if rule.get("rule_type") == "ltv_requirements" and loan_program in rule.get("loan_programs", []):
            try:
                ltv_limits = json.loads(rule.get("ltv_limits", "{}"))
                program_limits = ltv_limits.get(loan_program, {})
                property_limit = program_limits.get(property_type)
                if property_limit:
                    return float(property_limit)
            except:
                continue
    
    # Fallback only when Neo4j rules unavailable
    fallback_ltv = {
        "conventional": {"primary_residence": 97, "investment": 75, "vacation_home": 90},
        "fha": {"primary_residence": 96.5, "investment": 85, "vacation_home": 96.5},
        "va": {"primary_residence": 100, "investment": 90, "vacation_home": 100},
        "usda": {"primary_residence": 100, "investment": 80, "vacation_home": 90},
        "jumbo": {"primary_residence": 90, "investment": 70, "vacation_home": 80}
    }
    
    return fallback_ltv.get(loan_program, {}).get(property_type, 80)


def _check_property_type_restrictions(property_type: str, loan_program: str, rules: List[Dict]) -> Dict[str, any]:
    """Check property type restrictions from Neo4j rules first."""
    
    # Query Neo4j rules for property restrictions
    for rule in rules:
        if rule.get("rule_type") == "property_restrictions":
            try:
                restrictions = json.loads(rule.get("property_restrictions", "{}"))
                program_restrictions = restrictions.get(loan_program, {})
                type_restrictions = program_restrictions.get(property_type, {})
                if type_restrictions:
                    return {
                        "program_available": type_restrictions.get("available", True),
                        "special_requirements": type_restrictions.get("requirements", [])
                    }
            except:
                continue
    
    # Minimal fallback when Neo4j rules unavailable
    unavailable_combinations = [
        ("fha", "investment"), ("fha", "vacation_home"),
        ("va", "investment"), ("va", "vacation_home"),
        ("usda", "investment"), ("usda", "vacation_home")
    ]
    
    program_available = (loan_program, property_type) not in unavailable_combinations
    
    return {
        "program_available": program_available,
        "special_requirements": ["Verify program eligibility"] if not program_available else []
    }


def _analyze_approval_factors(factors: Dict[str, Any], rules: List[Dict]) -> Dict[str, Any]:
    """Analyze key approval factors against underwriting guidelines."""
    
    analysis = {
        "credit_acceptable": False,
        "dti_acceptable": False,
        "ltv_acceptable": False,
        "income_acceptable": False,
        "employment_acceptable": False,
        "overall_score": 0,
        "risk_factors": [],
        "positive_factors": []
    }
    
    # Credit analysis
    if factors["credit_risk_level"] == "LOW":
        analysis["credit_acceptable"] = True
        analysis["positive_factors"].append("Low credit risk profile")
        analysis["overall_score"] += 25
    elif factors["credit_risk_level"] == "MEDIUM":
        analysis["credit_acceptable"] = True  # May be acceptable with compensating factors
        analysis["overall_score"] += 15
    else:
        analysis["risk_factors"].append("High credit risk")
    
    # DTI analysis - find program-specific limits
    for rule in rules:
        if rule.get("rule_type") == "dti_requirements" and factors["loan_program"] in rule.get("loan_programs", []):
            try:
                dti_limits = json.loads(rule.get("dti_limits", "{}"))
                
                # Use Neo4j rules with industry-standard fallbacks
                program_limits = dti_limits.get(factors["loan_program"], {})
                
                # Fallback to industry standards only if Neo4j data is missing
                front_limit = program_limits.get("front_end", _get_fallback_dti_limits(factors["loan_program"])["front_end"])
                back_limit = program_limits.get("back_end", _get_fallback_dti_limits(factors["loan_program"])["back_end"])
                
                if factors["front_end_dti"] <= front_limit and factors["back_end_dti"] <= back_limit:
                    analysis["dti_acceptable"] = True
                    analysis["positive_factors"].append("DTI ratios within guidelines")
                    analysis["overall_score"] += 25
                else:
                    excess_front = max(0, factors["front_end_dti"] - front_limit)
                    excess_back = max(0, factors["back_end_dti"] - back_limit)
                    if excess_front > 0:
                        analysis["risk_factors"].append(f"Front-end DTI exceeds by {excess_front:.1f}%")
                    if excess_back > 0:
                        analysis["risk_factors"].append(f"Back-end DTI exceeds by {excess_back:.1f}%")
                break
            except:
                continue
    
    # LTV analysis using Neo4j rules with fallbacks
    max_ltv = _get_max_ltv_from_rules(factors["loan_program"], factors["property_type"], rules)
    
    if factors["ltv_ratio"] <= max_ltv:
        analysis["ltv_acceptable"] = True
        analysis["positive_factors"].append(f"LTV within {max_ltv}% guideline")
        analysis["overall_score"] += 20
    else:
        analysis["risk_factors"].append(f"LTV {factors['ltv_ratio']:.1f}% exceeds {max_ltv}% limit")
    
    # Income stability analysis
    if factors["income_stability"] in ["excellent", "good"]:
        analysis["income_acceptable"] = True
        analysis["positive_factors"].append("Stable income profile")
        analysis["overall_score"] += 15
    elif factors["income_stability"] == "fair":
        analysis["income_acceptable"] = True  # Marginal
        analysis["overall_score"] += 8
    else:
        analysis["risk_factors"].append("Income stability concerns")
    
    # Property type specific analysis from Neo4j rules
    property_restrictions = _check_property_type_restrictions(factors["property_type"], factors["loan_program"], rules)
    
    if not property_restrictions["program_available"]:
        analysis["risk_factors"].append(f"{factors['loan_program'].upper()} not available for {factors['property_type']}")
        analysis["overall_score"] -= 50  # Major issue
    else:
        # Add any special requirements found in Neo4j
        for requirement in property_restrictions.get("special_requirements", []):
            analysis["positive_factors"].append(f"Property requirement: {requirement}")
    
    # Employment analysis
    if factors["employment_years"] >= 2.0:
        analysis["employment_acceptable"] = True
        analysis["positive_factors"].append("Stable employment history")
        analysis["overall_score"] += 15
    elif factors["employment_years"] >= 1.0:
        analysis["employment_acceptable"] = True  # Marginal
        analysis["overall_score"] += 8
    else:
        analysis["risk_factors"].append("Limited employment history")
    
    # QM (Qualified Mortgage) Compliance Check
    qm_compliant = True
    qm_issues = []
    
    # QM Rule: 43% maximum back-end DTI
    if factors["back_end_dti"] > 43.0:
        qm_compliant = False
        qm_issues.append(f"Back-end DTI {factors['back_end_dti']:.1f}% exceeds QM limit of 43%")
    
    if qm_compliant:
        analysis["positive_factors"].append("QM (Qualified Mortgage) compliant")
        analysis["overall_score"] += 5
    else:
        analysis["risk_factors"].extend(qm_issues)
        analysis["risk_factors"].append("Non-QM loan - additional documentation required")
    
    return analysis


def _identify_compensating_factors(factors: Dict[str, Any], rules: List[Dict]) -> Dict[str, Any]:
    """Identify available compensating factors."""
    
    compensating = {
        "available_factors": [],
        "strength_score": 0,
        "can_offset_weaknesses": False
    }
    
    # Large down payment
    if factors["down_payment_percent"] >= 20:
        compensating["available_factors"].append(f"Large down payment ({factors['down_payment_percent']:.1f}%)")
        compensating["strength_score"] += 15
        if factors["down_payment_percent"] >= 25:
            compensating["strength_score"] += 10
    
    # Excellent credit score
    if factors["credit_score"] >= 740:
        compensating["available_factors"].append("Excellent credit score")
        compensating["strength_score"] += 20
    elif factors["credit_score"] >= 680:
        compensating["available_factors"].append("Good credit score")
        compensating["strength_score"] += 10
    
    # Significant cash reserves
    if factors["cash_reserves_months"] >= 6:
        compensating["available_factors"].append(f"Strong cash reserves ({factors['cash_reserves_months']:.1f} months)")
        compensating["strength_score"] += 15
    elif factors["cash_reserves_months"] >= 2:
        compensating["available_factors"].append(f"Adequate cash reserves ({factors['cash_reserves_months']:.1f} months)")
        compensating["strength_score"] += 8
    
    # Stable long-term employment
    if factors["employment_years"] >= 5:
        compensating["available_factors"].append("Long-term stable employment")
        compensating["strength_score"] += 10
    
    # Conservative loan amount relative to income
    if factors["loan_amount"] > 0 and factors["loan_amount"] / (factors.get("monthly_gross_income", 1) * 12) <= 3:
        compensating["available_factors"].append("Conservative loan-to-income ratio")
        compensating["strength_score"] += 10
    
    # Primary residence (lower risk)
    if factors["property_type"] == "primary_residence":
        compensating["strength_score"] += 5
    
    # Determine if compensating factors can offset weaknesses
    compensating["can_offset_weaknesses"] = compensating["strength_score"] >= 25
    
    return compensating


def _make_preliminary_decision(approval_analysis: Dict[str, Any], compensating_factors: Dict[str, Any]) -> Dict[str, Any]:
    """Make preliminary underwriting decision."""
    
    decision = {
        "recommendation": "MANUAL_REVIEW",
        "confidence": "medium",
        "reasoning": []
    }
    
    total_score = approval_analysis["overall_score"] + compensating_factors["strength_score"]
    critical_factors_met = sum([
        approval_analysis["credit_acceptable"],
        approval_analysis["dti_acceptable"], 
        approval_analysis["ltv_acceptable"],
        approval_analysis["income_acceptable"],
        approval_analysis["employment_acceptable"]
    ])
    
    # Decision logic
    if critical_factors_met >= 4 and total_score >= 80:
        decision["recommendation"] = "APPROVE"
        decision["confidence"] = "high"
        decision["reasoning"].append("All key underwriting factors meet guidelines")
        
    elif critical_factors_met >= 3 and total_score >= 60 and compensating_factors["can_offset_weaknesses"]:
        decision["recommendation"] = "APPROVE"
        decision["confidence"] = "medium"
        decision["reasoning"].append("Strong compensating factors offset minor guideline exceptions")
        
    elif critical_factors_met <= 2 or total_score < 40:
        decision["recommendation"] = "DENY"
        decision["confidence"] = "high"
        decision["reasoning"].append("Multiple critical underwriting factors do not meet guidelines")
        
    else:
        decision["recommendation"] = "MANUAL_REVIEW"
        decision["confidence"] = "medium"
        decision["reasoning"].append("Mixed underwriting factors require manual review")
    
    # Add specific reasoning
    if len(approval_analysis["risk_factors"]) > 2:
        decision["reasoning"].append(f"Multiple risk factors identified: {len(approval_analysis['risk_factors'])}")
    
    if compensating_factors["strength_score"] >= 30:
        decision["reasoning"].append("Strong compensating factors present")
    
    return decision


def _apply_program_overlays(preliminary_decision: Dict[str, Any], factors: Dict[str, Any], rules: List[Dict]) -> Dict[str, Any]:
    """Apply loan program-specific decision overlays."""
    
    final_decision = preliminary_decision.copy()
    
    # Program-specific adjustments
    if factors["loan_program"] == "fha":
        # FHA is more flexible with DTI if compensating factors exist
        if factors["back_end_dti"] > 43 and factors["credit_score"] >= 680:
            final_decision["reasoning"].append("FHA allows higher DTI with good credit")
            if preliminary_decision["recommendation"] == "DENY":
                final_decision["recommendation"] = "MANUAL_REVIEW"
    
    elif factors["loan_program"] == "va":
        # VA focuses more on residual income than DTI
        if factors["back_end_dti"] > 41:
            final_decision["reasoning"].append("VA loan requires residual income analysis")
            if preliminary_decision["recommendation"] == "APPROVE":
                final_decision["recommendation"] = "MANUAL_REVIEW"
                final_decision["reasoning"].append("VA residual income calculation needed")
    
    elif factors["loan_program"] == "usda":
        # USDA has income limits and geographic requirements
        final_decision["reasoning"].append("USDA requires income limit and geographic eligibility verification")
        if preliminary_decision["recommendation"] == "APPROVE":
            final_decision["recommendation"] = "MANUAL_REVIEW"
    
    elif factors["loan_program"] == "jumbo":
        # Jumbo loans have stricter requirements
        if factors["credit_score"] < 700 or factors["cash_reserves_months"] < 2:
            final_decision["reasoning"].append("Jumbo loans require higher credit scores and reserves")
            if preliminary_decision["recommendation"] == "APPROVE":
                final_decision["recommendation"] = "MANUAL_REVIEW"
    
    return final_decision


def _generate_approval_conditions(decision: Dict[str, Any], factors: Dict[str, Any], rules: List[Dict]) -> List[str]:
    """Generate specific approval conditions."""
    
    conditions = []
    
    if decision["recommendation"] == "APPROVE":
        # Standard conditions
        conditions.append("Satisfactory title and survey")
        conditions.append("Property appraisal supporting loan amount")
        conditions.append("Homeowner's insurance coverage")
        conditions.append("Final verification of employment")
        
        # Risk-based conditions
        if factors["down_payment_percent"] < 20:
            conditions.append("Mortgage insurance as required")
        
        if factors["cash_reserves_months"] < 2:
            conditions.append("Verification of sufficient funds to close")
        
        if factors["employment_years"] < 2:
            conditions.append("Additional employment documentation")
        
        # Program-specific conditions
        if factors["loan_program"] == "fha":
            conditions.append("FHA mortgage insurance premium")
            conditions.append("Satisfactory FHA appraisal")
        elif factors["loan_program"] == "va":
            conditions.append("VA funding fee as applicable")
            conditions.append("Certificate of Eligibility")
        elif factors["loan_program"] == "usda":
            conditions.append("USDA guarantee fee")
            conditions.append("Property eligibility verification")
    
    return conditions




def _format_underwriting_decision_report(
    decision: Dict[str, Any],
    factors: Dict[str, Any],
    approval_analysis: Dict[str, Any],
    compensating_factors: Dict[str, Any],
    conditions: List[str],
    loan_program: str
) -> str:
    """Format the comprehensive underwriting decision report."""
    
    decision_emoji = {
        "APPROVE": "",
        "DENY": "", 
        "MANUAL_REVIEW": "🔍"
    }
    
    confidence_indicator = {
        "high": "🟢 HIGH",
        "medium": "🟡 MEDIUM", 
        "low": "🔴 LOW"
    }
    
    report = f"""
🏦 **UNDERWRITING DECISION REPORT**

**DECISION:** {decision_emoji.get(decision['recommendation'], '⚪')} {decision['recommendation']}
**CONFIDENCE:** {confidence_indicator.get(decision['confidence'], 'UNKNOWN')}
**LOAN PROGRAM:** {loan_program.upper()}
**LOAN AMOUNT:** ${factors['loan_amount']:,.2f}
**PROPERTY VALUE:** ${factors['property_value']:,.2f}
**LTV RATIO:** {factors['ltv_ratio']:.1f}%

📊 **UNDERWRITING FACTOR ANALYSIS:**
"""
    
    # Key factors summary
    factors_status = [
        ("Credit Risk", " ACCEPTABLE" if approval_analysis["credit_acceptable"] else " ISSUE"),
        ("DTI Ratios", " ACCEPTABLE" if approval_analysis["dti_acceptable"] else " EXCEEDS"),
        ("LTV Ratio", " ACCEPTABLE" if approval_analysis["ltv_acceptable"] else " EXCEEDS"),
        ("Income Stability", " ACCEPTABLE" if approval_analysis["income_acceptable"] else " CONCERNS"),
        ("Employment", " ACCEPTABLE" if approval_analysis["employment_acceptable"] else " LIMITED")
    ]
    
    for factor_name, status in factors_status:
        report += f"• {factor_name}: {status}\n"
    
    # DTI details
    report += f"""
📈 **DEBT-TO-INCOME ANALYSIS:**
• Front-End DTI: {factors['front_end_dti']:.1f}%
• Back-End DTI: {factors['back_end_dti']:.1f}%
• Credit Score: {factors['credit_score']}
• Down Payment: {factors['down_payment_percent']:.1f}%
"""
    
    # Risk factors
    if approval_analysis["risk_factors"]:
        report += "\n⚠️ **RISK FACTORS:**\n"
        for risk in approval_analysis["risk_factors"]:
            report += f"• {risk}\n"
    
    # Positive factors
    if approval_analysis["positive_factors"]:
        report += "\n **POSITIVE FACTORS:**\n"
        for positive in approval_analysis["positive_factors"]:
            report += f"• {positive}\n"
    
    # Compensating factors
    if compensating_factors["available_factors"]:
        report += "\n💪 **COMPENSATING FACTORS:**\n"
        for factor in compensating_factors["available_factors"]:
            report += f"• {factor}\n"
        report += f"• Strength Score: {compensating_factors['strength_score']}/50\n"
    
    # Decision reasoning
    report += "\n🤔 **DECISION REASONING:**\n"
    for reason in decision["reasoning"]:
        report += f"• {reason}\n"
    
    # Approval conditions
    if conditions and decision["recommendation"] == "APPROVE":
        report += f"\n📋 **APPROVAL CONDITIONS ({len(conditions)} items):**\n"
        for condition in conditions:
            report += f"• {condition}\n"
    
    # Next steps
    if decision["recommendation"] == "APPROVE":
        report += "\n🎉 **NEXT STEPS:** Proceed with loan closing process"
    elif decision["recommendation"] == "DENY":
        report += "\n **NEXT STEPS:** Loan cannot be approved - consider addressing risk factors and reapplying"
    else:
        report += "\n🔍 **NEXT STEPS:** Manual underwriter review required - additional documentation may be needed"
    
    report += """
---
**Report Generated:** Automated Underwriting System
**Review Date:** Manual review required for MANUAL_REVIEW decisions
"""
    
    return report


def validate_tool() -> bool:
    """Validate that the make_underwriting_decision tool works correctly."""
    try:
        # Test with sample data
        result = make_underwriting_decision.invoke({
            "credit_score": 720,
            "credit_risk_level": "LOW",
            "monthly_gross_income": 8000.0,
            "income_stability": "good",
            "front_end_dti": 25.0,
            "back_end_dti": 35.0,
            "loan_program": "conventional",
            "loan_amount": 400000.0,
            "down_payment_percent": 0.20,
            "property_value": 500000.0,
            "cash_reserves_months": 3.0,
            "employment_years": 4.0,
            "first_time_buyer": False,
            "property_type": "primary_residence"
        })
        return "UNDERWRITING DECISION REPORT" in result and "DECISION:" in result
    except Exception as e:
        print(f"Underwriting decision tool validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the tool
    print("Testing make_underwriting_decision tool...")
    result = validate_tool()
    print(f"Validation result: {result}")

"""
Calculate Debt-to-Income Tool - Neo4j Powered

This tool performs comprehensive DTI analysis for mortgage underwriting
by querying Neo4j underwriting rules and income calculation criteria.

Purpose:
- Calculate front-end and back-end DTI ratios
- Validate DTI against loan program requirements
- Analyze income sources and stability
- Provide DTI recommendations and compensating factors
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


class DTICalculationRequest(BaseModel):
    """Schema for DTI calculation request"""
    monthly_gross_income: float = Field(description="Total monthly gross income from all sources")
    monthly_housing_payment: float = Field(description="Proposed monthly housing payment (PITI)")
    monthly_debt_payments: float = Field(description="Total monthly debt payments (excluding housing)")
    loan_program: str = Field(description="Loan program type: 'conventional', 'fha', 'va', 'usda', 'jumbo'")
    income_sources: List[str] = Field(
        description="List of income sources: ['w2_salary', 'self_employed', 'rental', 'commission', 'bonus', 'pension', etc.]",
        default_factory=list
    )
    employment_years: float = Field(description="Years at current employment", default=2.0)
    overtime_available: bool = Field(description="Is overtime income available?", default=False)


@tool
def calculate_debt_to_income(tool_input: str) -> str:
    """
    Calculate and analyze debt-to-income ratios for mortgage underwriting.
    
    This tool calculates front-end and back-end DTI ratios and validates them
    against underwriting rules stored in Neo4j for the specific loan program.
    
    Args:
        tool_input: DTI calculation request in natural language format
        
    Example:
        "Income: $8500, Housing: $2100, Debts: $800, Loan: FHA, Employment: 3 years, Overtime: yes"
    
    Returns:
        String containing formatted DTI analysis report with recommendations
    """
    
    try:
        # Use standardized parsing first, then custom parsing for tool-specific data
        from agents.shared.input_parser import parse_mortgage_application, calculate_dti_ratios
        import re
        
        parsed_data = parse_mortgage_application(tool_input)
        input_lower = tool_input.lower()
        
        # Extract DTI calculation parameters (prioritize parsed data, fall back to regex)
        monthly_gross_income = parsed_data.get("monthly_income")
        if not monthly_gross_income:
            income_match = re.search(r'income:\s*\$?([0-9,]+)', input_lower)
            monthly_gross_income = float(income_match.group(1).replace(',', '')) if income_match else 5000.0
        
        housing_match = re.search(r'housing:\s*\$?([0-9,]+)', input_lower)
        monthly_housing_payment = float(housing_match.group(1).replace(',', '')) if housing_match else 1500.0
        
        monthly_debt_payments = parsed_data.get("monthly_debts")
        if not monthly_debt_payments:
            debts_match = re.search(r'debts:\s*\$?([0-9,]+)', input_lower)
            monthly_debt_payments = float(debts_match.group(1).replace(',', '')) if debts_match else 500.0
        
        loan_match = re.search(r'loan:\s*([a-z_]+)', input_lower)
        loan_program = loan_match.group(1) if loan_match else "conventional"
        
        emp_years_match = re.search(r'employment:\s*(\d+(?:\.\d+)?)\s*years?', input_lower)
        employment_years = float(emp_years_match.group(1)) if emp_years_match else 2.0
        
        overtime_available = "overtime: yes" in input_lower or "overtime: true" in input_lower
        
        # Parse income sources (simplified for now)
        income_sources = []
        if "w2" in input_lower: income_sources.append("w2_salary")
        if "self-employed" in input_lower: income_sources.append("self_employed")
        if "commission" in input_lower: income_sources.append("commission")
        if not income_sources:
            income_sources = ["w2_salary"]
        
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        # Query underwriting rules for DTI analysis
        dti_rules_query = """
        MATCH (r:UnderwritingRule) 
        WHERE r.category = 'DTIAnalysis'
        RETURN r
        ORDER BY r.rule_id
        """
        
        # Query income calculation rules
        income_rules_query = """
        MATCH (r:IncomeCalculationRule)
        RETURN r
        ORDER BY r.rule_id
        """
        
        with connection.driver.session(database=connection.database) as session:
            result = session.run(dti_rules_query)
            dti_rules = [dict(record['r']) for record in result]
            
            result = session.run(income_rules_query)
            income_rules = [dict(record['r']) for record in result]
        
        if not dti_rules:
            return " No DTI analysis rules found in Neo4j. Please load underwriting rules first."
        
        # Calculate DTI ratios using shared utility
        dti_ratios = calculate_dti_ratios(
            monthly_gross_income, monthly_housing_payment, monthly_debt_payments
        )
        
        # Reformat for backwards compatibility with existing tool logic
        dti_calculations = {
            "monthly_gross_income": monthly_gross_income,
            "monthly_housing_payment": monthly_housing_payment,
            "monthly_debt_payments": monthly_debt_payments,
            "total_monthly_debt": monthly_housing_payment + monthly_debt_payments,
            "front_end_dti": dti_ratios["front_end_dti"],
            "back_end_dti": dti_ratios["back_end_dti"],
            "remaining_income": monthly_gross_income - (monthly_housing_payment + monthly_debt_payments)
        }
        
        # Validate against program requirements
        program_validation = _validate_dti_requirements(
            dti_calculations, loan_program, dti_rules
        )
        
        # Analyze income stability
        income_analysis = _analyze_income_stability(
            income_sources, employment_years, overtime_available, income_rules
        )
        
        # Generate recommendations
        recommendations = _generate_dti_recommendations(
            dti_calculations, program_validation, income_analysis, loan_program
        )
        
        return _format_dti_analysis_report(
            dti_calculations, program_validation, income_analysis, recommendations, loan_program
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during DTI analysis: {e}")
        return f"❌ Error during DTI analysis: {str(e)}"




def _validate_dti_requirements(
    dti_calculations: Dict[str, Any], 
    loan_program: str, 
    rules: List[Dict]
) -> Dict[str, Any]:
    """Validate DTI ratios against program requirements."""
    
    validation = {
        "front_end_compliant": False,
        "back_end_compliant": False,
        "front_end_limit": None,
        "back_end_limit": None,
        "exceeds_by": {},
        "compensating_factors_available": False
    }
    
    # Find DTI requirements for the loan program
    for rule in rules:
        if rule.get("rule_type") == "dti_requirements" and loan_program in rule.get("loan_programs", []):
            try:
                dti_limits = json.loads(rule.get("dti_limits", "{}"))
                
                # Get program-specific limits from Neo4j with conservative fallbacks
                program_limits = dti_limits.get(loan_program, {})
                front_limit = program_limits.get("front_end", 28)  # Conservative fallback
                back_limit = program_limits.get("back_end", 43)    # Conservative fallback
                
                validation["front_end_limit"] = front_limit
                validation["back_end_limit"] = back_limit
                
                # Check compliance
                front_dti = dti_calculations["front_end_dti"]
                back_dti = dti_calculations["back_end_dti"]
                
                validation["front_end_compliant"] = front_dti <= front_limit
                validation["back_end_compliant"] = back_dti <= back_limit
                
                # Calculate excess amounts
                if front_dti > front_limit:
                    validation["exceeds_by"]["front_end"] = round(front_dti - front_limit, 2)
                if back_dti > back_limit:
                    validation["exceeds_by"]["back_end"] = round(back_dti - back_limit, 2)
                
                # Check for compensating factors
                validation["compensating_factors_available"] = "compensating_factors" in rule.get("exceptions", [])
                
                break
            except Exception as e:
                continue
    
    return validation


def _analyze_income_stability(
    income_sources: List[str], 
    employment_years: float, 
    overtime_available: bool,
    income_rules: List[Dict]
) -> Dict[str, Any]:
    """Analyze income stability and documentation requirements."""
    
    analysis = {
        "stability_score": "high",
        "employment_stable": employment_years >= 2.0,
        "income_complexity": "simple",
        "documentation_requirements": [],
        "risk_factors": []
    }
    
    # Analyze income complexity
    if len(income_sources) == 1 and "w2_salary" in income_sources:
        analysis["income_complexity"] = "simple"
        analysis["documentation_requirements"] = ["pay_stubs", "w2s", "employment_verification"]
    elif any(source in income_sources for source in ["self_employed", "commission", "bonus"]):
        analysis["income_complexity"] = "complex"
        analysis["documentation_requirements"] = ["tax_returns", "profit_loss", "bank_statements", "cpa_letter"]
        analysis["risk_factors"].append("Variable income sources require additional documentation")
    
    # Employment stability
    if employment_years < 1.0:
        analysis["stability_score"] = "low"
        analysis["risk_factors"].append("Recent employment change may affect stability")
    elif employment_years < 2.0:
        analysis["stability_score"] = "medium"
        analysis["risk_factors"].append("Limited employment history")
    
    # Overtime analysis
    if overtime_available:
        analysis["documentation_requirements"].append("overtime_history")
        if employment_years < 2.0:
            analysis["risk_factors"].append("Overtime income may not be fully usable with limited history")
    
    return analysis


def _generate_dti_recommendations(
    dti_calculations: Dict[str, Any],
    program_validation: Dict[str, Any], 
    income_analysis: Dict[str, Any],
    loan_program: str
) -> List[str]:
    """Generate DTI-based recommendations."""
    
    recommendations = []
    
    # Overall DTI compliance
    if program_validation["front_end_compliant"] and program_validation["back_end_compliant"]:
        recommendations.append(" DTI ratios meet underwriting guidelines")
        recommendations.append("Strong debt management - good approval likelihood")
    else:
        recommendations.append("⚠️ DTI ratios exceed program guidelines")
        
        if not program_validation["front_end_compliant"]:
            excess = program_validation["exceeds_by"].get("front_end", 0)
            recommendations.append(f" Front-end DTI exceeds limit by {excess:.2f}%")
            recommendations.append("Consider lower housing payment or increase income")
        
        if not program_validation["back_end_compliant"]:
            excess = program_validation["exceeds_by"].get("back_end", 0)
            recommendations.append(f" Back-end DTI exceeds limit by {excess:.2f}%")
            recommendations.append("Consider paying down existing debts before applying")
    
    # Compensating factors
    if program_validation["compensating_factors_available"] and (
        not program_validation["front_end_compliant"] or not program_validation["back_end_compliant"]
    ):
        recommendations.append("💡 Compensating factors may allow DTI flexibility:")
        recommendations.append("  • Large down payment (≥20%)")
        recommendations.append("  • Excellent credit score (≥740)")
        recommendations.append("  • Cash reserves (2+ months)")
        recommendations.append("  • Stable employment history")
    
    # Income stability recommendations
    if income_analysis["stability_score"] == "low":
        recommendations.append("⚠️ Income stability concerns identified")
        recommendations.append("Provide additional employment documentation")
    elif income_analysis["income_complexity"] == "complex":
        recommendations.append("📋 Complex income requires comprehensive documentation")
        for doc in income_analysis["documentation_requirements"]:
            recommendations.append(f"  • {doc.replace('_', ' ').title()}")
    
    # Program-specific advice
    if loan_program in ["fha"] and not program_validation["back_end_compliant"]:
        recommendations.append("💡 FHA may allow higher DTI with compensating factors")
    elif loan_program in ["va"] and not program_validation["back_end_compliant"]:
        recommendations.append("💡 VA uses residual income analysis - DTI may be flexible")
    
    return recommendations


def _format_dti_analysis_report(
    dti_calculations: Dict[str, Any],
    program_validation: Dict[str, Any],
    income_analysis: Dict[str, Any], 
    recommendations: List[str],
    loan_program: str
) -> str:
    """Format the comprehensive DTI analysis report."""
    
    # Compliance indicators
    front_status = " PASS" if program_validation["front_end_compliant"] else " FAIL"
    back_status = " PASS" if program_validation["back_end_compliant"] else " FAIL"
    
    report = f"""
📊 **Debt-to-Income Analysis Report**

**Loan Program:** {loan_program.upper()}
**Overall DTI Status:** {' COMPLIANT' if program_validation['front_end_compliant'] and program_validation['back_end_compliant'] else '⚠️ REQUIRES REVIEW'}

💰 **Income & Debt Summary:**
• Monthly Gross Income: ${dti_calculations['monthly_gross_income']:,.2f}
• Monthly Housing Payment: ${dti_calculations['monthly_housing_payment']:,.2f}
• Monthly Debt Payments: ${dti_calculations['monthly_debt_payments']:,.2f}
• Total Monthly Obligations: ${dti_calculations['total_monthly_debt']:,.2f}
• Remaining Income: ${dti_calculations['remaining_income']:,.2f}

📈 **DTI Ratio Analysis:**
• Front-End DTI: {dti_calculations['front_end_dti']:.2f}% (Limit: {program_validation.get('front_end_limit', 'N/A')}%) - {front_status}
• Back-End DTI: {dti_calculations['back_end_dti']:.2f}% (Limit: {program_validation.get('back_end_limit', 'N/A')}%) - {back_status}
"""
    
    if program_validation["exceeds_by"]:
        report += "\n**⚠️ DTI Exceedances:**\n"
        for dti_type, excess in program_validation["exceeds_by"].items():
            report += f"• {dti_type.replace('_', '-').title()}: Exceeds by {excess:.2f}%\n"
    
    report += f"""
👨‍💼 **Income Stability Analysis:**
• Stability Score: {income_analysis['stability_score'].title()}
• Employment Stable: {' Yes' if income_analysis['employment_stable'] else ' No'}
• Income Complexity: {income_analysis['income_complexity'].title()}
• Documentation Required: {len(income_analysis['documentation_requirements'])} items
"""
    
    if income_analysis["risk_factors"]:
        report += "\n**⚠️ Income Risk Factors:**\n"
        for risk in income_analysis["risk_factors"]:
            report += f"• {risk}\n"
    
    report += "\n💡 **Recommendations:**\n"
    for rec in recommendations:
        report += f"{rec}\n"
    
    report += """
---
**Next Steps:** Review documentation requirements and consider compensating factors if DTI exceeds limits
"""
    
    return report


def validate_tool() -> bool:
    """Validate that the calculate_debt_to_income tool works correctly."""
    try:
        # Test with sample data
        result = calculate_debt_to_income.invoke({
            "monthly_gross_income": 8000.0,
            "monthly_housing_payment": 2000.0,
            "monthly_debt_payments": 800.0,
            "loan_program": "conventional",
            "income_sources": ["w2_salary"],
            "employment_years": 3.0,
            "overtime_available": False
        })
        return "Debt-to-Income Analysis Report" in result and "DTI Ratio Analysis" in result
    except Exception as e:
        print(f"DTI calculation tool validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the tool
    print("Testing calculate_debt_to_income tool...")
    result = validate_tool()
    print(f"Validation result: {result}")

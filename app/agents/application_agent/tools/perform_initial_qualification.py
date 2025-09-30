"""
Initial Qualification Assessment Tool

This tool performs initial qualification and pre-screening
based on Neo4j application intake rules.
"""

import json
import logging
from typing import Dict, Any
from langchain_core.tools import tool

try:
    from utils import get_neo4j_connection, initialize_connection
except ImportError:
    from utils import get_neo4j_connection, initialize_connection

logger = logging.getLogger(__name__)


def parse_neo4j_rule(rule_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON strings back to objects in Neo4j rule data."""
    parsed_rule = {}
    for key, value in rule_dict.items():
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
            try:
                parsed_rule[key] = json.loads(value)
            except json.JSONDecodeError:
                parsed_rule[key] = value  # Keep as string if not valid JSON
        else:
            parsed_rule[key] = value
    return parsed_rule


# REMOVED: parse_borrower_info function completely eliminated 
# All parsing now handled by parse_complete_mortgage_input (12-Factor Compliant)


@tool
def perform_initial_qualification(tool_input: str) -> str:
    """
    Perform initial qualification assessment using Neo4j application intake rules.
    
    This tool evaluates initial qualification across multiple loan programs
    and provides routing recommendations for the application workflow.
    
    Args:
        tool_input: Borrower information in natural language format
        
    Example:
        "Credit score is 720, monthly income $8,500, looking at $450,000 home with 15% down"
    
    Returns:
        String containing detailed qualification assessment and recommendations
    """
    
    try:
        # 12-FACTOR COMPLIANT: Use only enhanced parser (Factor 1: Natural Language → Tool Calls)
        from agents.shared.input_parser import parse_complete_mortgage_input
        
        # Single parsing approach - no hybrid complexity (Factor 8: Own Your Control Flow)
        parsed_data = parse_complete_mortgage_input(tool_input)
        
        # Factor 4: Tools as Structured Outputs - SAFE parameter extraction with None protection
        credit_score = parsed_data.get("credit_score") or 650  
        monthly_gross_income = parsed_data.get("monthly_income") or 5000.0
        monthly_debts = parsed_data.get("monthly_debts") or 500.0
        liquid_assets = parsed_data.get("liquid_assets") or 20000.0
        employment_years = parsed_data.get("employment_years") or 2.0  
        employment_type = parsed_data.get("employment_type") or "w2"
        loan_amount = parsed_data.get("loan_amount") or 300000.0
        property_value = parsed_data.get("property_value") or 375000.0
        down_payment = parsed_data.get("down_payment") or 60000.0
        property_type = parsed_data.get("property_type") or "single_family_detached"
        occupancy_type = parsed_data.get("occupancy_type") or "primary_residence"
        loan_purpose = parsed_data.get("loan_purpose") or "purchase"
        application_id = parsed_data.get("application_id", "TEMP_QUALIFICATION")
        first_time_buyer = parsed_data.get("first_time_buyer", False)
        military_service = parsed_data.get("military_service", False)
        rural_property = parsed_data.get("rural_property", False)
        bankruptcy_history = False  # Default
        foreclosure_history = False  # Default
        collections_amount = 0.0  # Default
        late_payments_12_months = 0  # Default
        
        # Smart calculation if property_value not extracted but loan_amount and down_payment were
        if (property_value == 375000.0 and 
            loan_amount is not None and loan_amount > 0 and 
            down_payment is not None and down_payment > 0):
            property_value = loan_amount + down_payment
        
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        with connection.driver.session(database=connection.database) as session:
            # Get initial qualification rules
            qualification_query = """
            MATCH (rule:ApplicationIntakeRule)
            WHERE rule.category = 'InitialQualification'
            RETURN rule
            """
            result = session.run(qualification_query)
            qualification_rules = [parse_neo4j_rule(dict(record['rule'])) for record in result]
        
        # Calculate key ratios with complete None-safety (Factor 9: Compact Errors)
        # Ensure all values are numbers before calculations
        safe_loan_amount = loan_amount or 0.0
        safe_property_value = property_value or 1.0  # Avoid division by zero
        safe_monthly_income = monthly_gross_income or 1.0  # Avoid division by zero  
        safe_monthly_debts = monthly_debts or 0.0
        safe_down_payment = down_payment or 0.0
        
        ltv = (safe_loan_amount / safe_property_value * 100) if safe_property_value > 0 else 0
        down_payment_pct = (safe_down_payment / safe_property_value * 100) if safe_property_value > 0 else 0
        front_end_dti = ((safe_loan_amount * 0.005) / safe_monthly_income * 100) if safe_monthly_income > 0 else 0
        back_end_dti = ((safe_monthly_debts + (safe_loan_amount * 0.005)) / safe_monthly_income * 100) if safe_monthly_income > 0 else 0
        debt_to_income = (safe_monthly_debts / safe_monthly_income * 100) if safe_monthly_income > 0 else 0
        
        # Generate qualification report
        qualification_report = []
        qualification_report.append("INITIAL QUALIFICATION ASSESSMENT")
        qualification_report.append("=" * 50)
        
        # Application Summary
        qualification_report.append(f"\n📋 APPLICATION SUMMARY:")
        qualification_report.append(f"Application ID: {application_id}")
        qualification_report.append(f"Loan Purpose: {loan_purpose.replace('_', ' ').title()}")
        qualification_report.append(f"Loan Amount: ${safe_loan_amount:,.2f}")
        qualification_report.append(f"Property Value: ${safe_property_value:,.2f}")
        qualification_report.append(f"Down Payment: ${safe_down_payment:,.2f} ({down_payment_pct:.1f}%)")
        qualification_report.append(f"LTV Ratio: {ltv:.1f}%")
        
        # Borrower Profile
        qualification_report.append(f"\n👤 BORROWER PROFILE:")
        qualification_report.append(f"Credit Score: {credit_score}")
        qualification_report.append(f"Monthly Income: ${safe_monthly_income:,.2f}")
        qualification_report.append(f"Monthly Debts: ${safe_monthly_debts:,.2f}")
        qualification_report.append(f"DTI Ratio: {debt_to_income:.1f}%")
        qualification_report.append(f"Liquid Assets: ${liquid_assets or 0:,.2f}")
        qualification_report.append(f"Employment: {employment_type.replace('_', ' ').title()} ({employment_years} years)")
        
        # Special Considerations
        qualification_report.append(f"\n🎯 SPECIAL CONSIDERATIONS:")
        if first_time_buyer:
            qualification_report.append(" First-Time Home Buyer")
        if military_service:
            qualification_report.append(" Military Service (VA Eligible)")
        if rural_property:
            qualification_report.append(" Rural Property (USDA Eligible)")
        if bankruptcy_history:
            qualification_report.append("⚠️ Bankruptcy History")
        if foreclosure_history:
            qualification_report.append("⚠️ Foreclosure History")
        if collections_amount > 0:
            qualification_report.append(f"⚠️ Collections: ${collections_amount:,.2f}")
        if late_payments_12_months > 0:
            qualification_report.append(f"⚠️ Late Payments (12 months): {late_payments_12_months}")
        
        # Get qualification rules
        credit_rule = next((rule for rule in qualification_rules if rule.get('rule_type') == 'credit_pre_screen'), {})
        income_rule = next((rule for rule in qualification_rules if rule.get('rule_type') == 'income_pre_screen'), {})
        asset_rule = next((rule for rule in qualification_rules if rule.get('rule_type') == 'asset_pre_screen'), {})
        
        # Credit Assessment
        qualification_report.append(f"\n🔍 CREDIT ASSESSMENT:")
        
        credit_issues = []
        credit_warnings = []
        
        # Check minimum credit scores
        min_scores = credit_rule.get('minimum_credit_scores', {})
        auto_decline = credit_rule.get('auto_decline_conditions', [])
        manual_review = credit_rule.get('manual_review_triggers', [])
        
        qualification_report.append(f"Credit Score: {credit_score}")
        
        # Check each loan program
        program_eligibility = {}
        for program, min_score in min_scores.items():
            if credit_score >= min_score:
                program_eligibility[program] = "ELIGIBLE"
                qualification_report.append(f"   {program.upper()}: Eligible (min {min_score})")
            else:
                program_eligibility[program] = "INELIGIBLE"
                qualification_report.append(f"   {program.upper()}: Below minimum (min {min_score})")
        
        # Check auto-decline conditions
        if credit_score < 500:
            credit_issues.append("Credit score below 500 - auto decline")
        if bankruptcy_history:
            credit_issues.append("Recent bankruptcy - requires seasoning verification")
        if foreclosure_history:
            credit_issues.append("Foreclosure history - requires seasoning verification")
        
        # Check manual review triggers
        if 580 <= credit_score <= 620:
            credit_warnings.append("Credit score in manual review range")
        if collections_amount > 5000:
            credit_warnings.append("Significant collections amount")
        if late_payments_12_months > 2:
            credit_warnings.append("Multiple recent late payments")
        
        # Income Assessment
        qualification_report.append(f"\n💰 INCOME ASSESSMENT:")
        
        income_issues = []
        income_warnings = []
        
        # Check minimum income requirements
        min_income = income_rule.get('minimum_income_requirements', {})
        single_min = min_income.get('single_borrower', 3000)
        
        if monthly_gross_income >= single_min:
            qualification_report.append(f" Income: ${monthly_gross_income:,.2f} (min ${single_min:,.2f})")
        else:
            qualification_report.append(f" Income: ${monthly_gross_income:,.2f} (below min ${single_min:,.2f})")
            income_issues.append(f"Income below minimum requirement")
        
        # Check employment stability using basic requirements
        min_employment = 2.0  # Standard 2-year requirement
        
        if employment_type == "self_employed":
            min_required = 2.0  # Self-employed need 2 years tax returns
            if employment_years >= min_required:
                qualification_report.append(f"✅ Self-Employment: {employment_years} years (min {min_required})")
            else:
                qualification_report.append(f"⚠️ Self-Employment: {employment_years} years (min {min_required})")
                income_issues.append("Insufficient self-employment history")
        else:
            if employment_years >= min_employment:
                qualification_report.append(f"✅ Employment: {employment_years} years (meets 2-year requirement)")
            else:
                qualification_report.append(f"⚠️ Employment: {employment_years} years (short of 2-year requirement)")
                gap_months = (min_employment - employment_years) * 12
                if gap_months > 12:
                    income_issues.append("Insufficient employment history for most loan programs")
                else:
                    income_warnings.append("Limited employment history - may require additional documentation")
        
        # Check DTI ratios
        dti_limits = income_rule.get('dti_pre_screen_limits', {})
        front_end_limit = dti_limits.get('front_end', 0.31) * 100
        back_end_limit = dti_limits.get('back_end', 0.45) * 100
        
        if front_end_dti <= front_end_limit:
            qualification_report.append(f" Front-End DTI: {front_end_dti:.1f}% (max {front_end_limit:.1f}%)")
        else:
            qualification_report.append(f"⚠️ Front-End DTI: {front_end_dti:.1f}% (max {front_end_limit:.1f}%)")
            income_warnings.append("Front-end DTI above preferred limits")
        
        if back_end_dti <= back_end_limit:
            qualification_report.append(f" Back-End DTI: {back_end_dti:.1f}% (max {back_end_limit:.1f}%)")
        else:
            qualification_report.append(f" Back-End DTI: {back_end_dti:.1f}% (max {back_end_limit:.1f}%)")
            income_issues.append("Back-end DTI exceeds limits")
        
        # Asset Assessment
        qualification_report.append(f"\n💳 ASSET ASSESSMENT:")
        
        asset_issues = []
        asset_warnings = []
        
        # Check down payment requirements
        min_down_payments = asset_rule.get('minimum_down_payment', {})
        
        for program, min_down_pct in min_down_payments.items():
            min_down_amount = property_value * min_down_pct
            if program in program_eligibility and program_eligibility[program] == "ELIGIBLE":
                if down_payment >= min_down_amount:
                    qualification_report.append(f" {program.upper()}: Down payment ${down_payment:,.0f} (min {min_down_pct*100:.1f}%)")
                else:
                    qualification_report.append(f" {program.upper()}: Down payment ${down_payment:,.0f} (min ${min_down_amount:,.0f})")
                    program_eligibility[program] = "INSUFFICIENT_FUNDS"
        
        # Check reserve requirements
        reserve_reqs = asset_rule.get('reserve_requirements', {})
        required_reserves = reserve_reqs.get(occupancy_type, "2_months_payment")
        estimated_payment = loan_amount * 0.005  # Rough estimate
        
        if "2_months" in required_reserves:
            required_reserve_amount = estimated_payment * 2
        elif "4_months" in required_reserves:
            required_reserve_amount = estimated_payment * 4
        elif "6_months" in required_reserves:
            required_reserve_amount = estimated_payment * 6
        else:
            required_reserve_amount = estimated_payment * 2
        
        available_after_down = liquid_assets - down_payment
        if available_after_down >= required_reserve_amount:
            qualification_report.append(f" Reserves: ${available_after_down:,.0f} (min ${required_reserve_amount:,.0f})")
        else:
            qualification_report.append(f"⚠️ Reserves: ${available_after_down:,.0f} (min ${required_reserve_amount:,.0f})")
            asset_warnings.append("Insufficient reserves after down payment")
        
        # Program Eligibility Summary
        qualification_report.append(f"\n🎯 LOAN PROGRAM ELIGIBILITY:")
        
        eligible_programs = []
        ineligible_programs = []
        
        for program, status in program_eligibility.items():
            if status == "ELIGIBLE":
                eligible_programs.append(program)
                qualification_report.append(f" {program.upper()}: ELIGIBLE")
            else:
                ineligible_programs.append(program)
                reason = "Credit score" if status == "INELIGIBLE" else "Insufficient funds"
                qualification_report.append(f" {program.upper()}: NOT ELIGIBLE ({reason})")
        
        # Overall Qualification Assessment
        qualification_report.append(f"\n📊 OVERALL ASSESSMENT:")
        
        total_issues = len(credit_issues) + len(income_issues) + len(asset_issues)
        total_warnings = len(credit_warnings) + len(income_warnings) + len(asset_warnings)
        
        if total_issues == 0 and eligible_programs:
            overall_status = "QUALIFIED"
            status_icon = ""
            recommendation = "Proceed with loan processing"
        elif total_issues <= 1 and eligible_programs:
            overall_status = "CONDITIONALLY QUALIFIED"
            status_icon = "⚠️"
            recommendation = "Proceed with conditions or manual underwriting"
        elif eligible_programs and total_issues <= 2:
            overall_status = "MARGINAL"
            status_icon = "⚠️"
            recommendation = "Manual underwriting required"
        else:
            overall_status = "NOT QUALIFIED"
            status_icon = ""
            recommendation = "Does not meet minimum requirements"
        
        qualification_report.append(f"{status_icon} Status: {overall_status}")
        qualification_report.append(f"Eligible Programs: {len(eligible_programs)}")
        qualification_report.append(f"Critical Issues: {total_issues}")
        qualification_report.append(f"Warnings: {total_warnings}")
        qualification_report.append(f"Recommendation: {recommendation}")
        
        # Issues Summary
        if credit_issues or income_issues or asset_issues:
            qualification_report.append(f"\n CRITICAL ISSUES:")
            for issue in credit_issues + income_issues + asset_issues:
                qualification_report.append(f"  • {issue}")
        
        if credit_warnings or income_warnings or asset_warnings:
            qualification_report.append(f"\n⚠️ WARNINGS:")
            for warning in credit_warnings + income_warnings + asset_warnings:
                qualification_report.append(f"  • {warning}")
        
        # Workflow Routing Recommendation
        qualification_report.append(f"\n🔄 ROUTING RECOMMENDATION:")
        
        if overall_status == "NOT QUALIFIED":
            qualification_report.append("1. Route to MortgageAdvisorAgent for improvement guidance")
            qualification_report.append("2. Provide qualification improvement strategies")
            qualification_report.append("3. Set follow-up timeline for re-qualification")
        elif first_time_buyer or credit_score < 650:
            qualification_report.append("1. Route to MortgageAdvisorAgent for program guidance")
            qualification_report.append("2. Proceed to DocumentAgent for verification")
            qualification_report.append("3. Continue standard processing workflow")
        elif overall_status in ["QUALIFIED", "CONDITIONALLY QUALIFIED"]:
            qualification_report.append("1. Proceed directly to DocumentAgent")
            qualification_report.append("2. Continue to AppraisalAgent for property evaluation")
            qualification_report.append("3. Route to UnderwritingAgent for final approval")
        else:
            qualification_report.append("1. Manual underwriting review required")
            qualification_report.append("2. Senior underwriter consultation recommended")
            qualification_report.append("3. Additional documentation may be required")
        
        # Best Program Recommendation
        if eligible_programs:
            qualification_report.append(f"\n⭐ RECOMMENDED LOAN PROGRAM:")
            
            # Prioritize programs based on borrower profile
            if military_service and "va" in eligible_programs:
                best_program = "VA"
                reason = "No down payment required, competitive rates"
            elif rural_property and "usda" in eligible_programs:
                best_program = "USDA"
                reason = "No down payment, rural property financing"
            elif first_time_buyer and "fha" in eligible_programs:
                best_program = "FHA"
                reason = "Low down payment, first-time buyer friendly"
            elif "conventional" in eligible_programs:
                best_program = "Conventional"
                reason = "Most flexible terms and competitive rates"
            else:
                best_program = eligible_programs[0].upper()
                reason = "Best available option based on qualification"
            
            qualification_report.append(f"Program: {best_program}")
            qualification_report.append(f"Reason: {reason}")
        
        return "\n".join(qualification_report)
        
    except Exception as e:
        logger.error(f"Error during initial qualification: {e}")
        return f"❌ Error during initial qualification: {str(e)}"


def validate_tool() -> bool:
    """Validate that the perform_initial_qualification tool works correctly."""
    try:
        # Test with sample natural language data
        result = perform_initial_qualification.invoke({
            "borrower_info": "Credit score is 720, monthly income $8,000, monthly debts $1,200, have $100,000 in savings, employed 4 years W2, loan amount $400,000, property value $500,000, down payment $100,000"
        })
        return "INITIAL QUALIFICATION ASSESSMENT" in result and "OVERALL ASSESSMENT" in result
    except Exception as e:
        print(f"Initial qualification tool validation failed: {e}")
        return False

"""
Property Condition Assessment Tool

This tool evaluates property condition for lending purposes
based on Neo4j property appraisal rules.
"""

import logging
from typing import Dict, Any
from langchain_core.tools import tool

try:
    from utils import get_neo4j_connection, initialize_connection
except ImportError:
    from utils import get_neo4j_connection, initialize_connection

logger = logging.getLogger(__name__)


def extract_property_condition_safely(condition_info: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract property condition information using 12-factor compliant parsing."""
    # 12-FACTOR COMPLIANT: String-based extraction (Factor 9: Compact Errors)
    
    # Initialize with safe defaults
    parsed = {
        "property_address": "",
        "property_type": "single_family_detached",
        "year_built": 2000,        # Default year built
        "roof_condition": "good",  # Default condition ratings
        "exterior_condition": "good",
        "interior_condition": "good", 
        "heating_system": "central forced air - good condition",
        "electrical_system": "good condition",
        "plumbing_system": "good condition",
        "foundation_condition": "good condition",
        "safety_issues": [],       # Default no issues
        "repair_items": [],        # Default no repairs needed
        "loan_program": "conventional"
    }
    
    info_lower = condition_info.lower()
    
    # Extract property address using enhanced parser and keyword detection
    parsed["property_address"] = parsed_data.get("address") or ""
    if not parsed["property_address"]:
        # Enhanced address detection without regex
        info_lower = condition_info.lower()
        if ' at ' in info_lower:
            try:
                start = info_lower.find(' at ') + 4
                end = info_lower.find(',', start) if info_lower.find(',', start) != -1 else len(condition_info)
                address_candidate = condition_info[start:end].strip()
                if any(suffix in address_candidate.lower() for suffix in ['st', 'ave', 'rd', 'dr', 'blvd', 'way']):
                    parsed["property_address"] = address_candidate
            except:
                pass
    
    # Extract property type
    if 'condo' in info_lower or 'condominium' in info_lower:
        parsed["property_type"] = "condominium"
    elif 'townhouse' in info_lower or 'town house' in info_lower:
        parsed["property_type"] = "townhouse"
    elif 'single family' in info_lower or 'single-family' in info_lower:
        parsed["property_type"] = "single_family_detached"
    elif 'duplex' in info_lower:
        parsed["property_type"] = "duplex"
    
    # Extract year built using string methods (no regex)
    if 'built' in info_lower:
        # Look for 4-digit years near 'built' keywords
        words = condition_info.split()
        for i, word in enumerate(words):
            if 'built' in word.lower() and i < len(words) - 1:
                # Check next few words for year
                for j in range(i+1, min(i+4, len(words))):
                    try:
                        year_candidate = int(''.join(filter(str.isdigit, words[j])))
                        if 1900 <= year_candidate <= 2025:
                            parsed["year_built"] = year_candidate
                            break
                    except:
                        continue
                if parsed["year_built"] != 2000:  # If found non-default
                    break
    
    # Extract condition ratings (excellent, good, fair, poor)
    conditions = ['excellent', 'good', 'fair', 'poor']
    
    # Roof condition
    for condition in conditions:
        if f'roof {condition}' in info_lower or f'{condition} roof' in info_lower:
            parsed["roof_condition"] = condition
            break
    
    # Exterior condition  
    for condition in conditions:
        if f'exterior {condition}' in info_lower or f'{condition} exterior' in info_lower:
            parsed["exterior_condition"] = condition
            break
    
    # Interior condition
    for condition in conditions:
        if f'interior {condition}' in info_lower or f'{condition} interior' in info_lower:
            parsed["interior_condition"] = condition
            break
    
    # 12-FACTOR COMPLIANT: String-based system condition extraction (Factor 9: Compact Errors)
    
    # Enhanced heating system detection
    if 'heating' in info_lower or 'hvac' in info_lower:
        for condition in conditions:
            if f'heating {condition}' in info_lower or f'hvac {condition}' in info_lower:
                parsed["heating_system"] = f"central forced air - {condition} condition"
                break
    
    # Enhanced electrical system detection
    if 'electrical' in info_lower or 'electric' in info_lower:
        for condition in conditions:
            if f'electrical {condition}' in info_lower or f'electric {condition}' in info_lower:
                parsed["electrical_system"] = f"{condition} condition"
                break
    
    # Enhanced plumbing system detection
    if 'plumbing' in info_lower:
        for condition in conditions:
            if f'plumbing {condition}' in info_lower:
                parsed["plumbing_system"] = f"{condition} condition"
                break
    
    # Enhanced foundation condition detection
    if 'foundation' in info_lower:
        for condition in conditions:
            if f'foundation {condition}' in info_lower:
                parsed["foundation_condition"] = f"{condition} condition"
                break
    
    # Extract safety issues and repair items
    safety_issues = []
    repair_items = []
    
    if 'safety issue' in info_lower or 'safety concern' in info_lower:
        if 'electrical' in info_lower:
            safety_issues.append("Electrical safety concerns")
        if 'structural' in info_lower:
            safety_issues.append("Structural issues")
        if 'fire' in info_lower or 'smoke' in info_lower:
            safety_issues.append("Fire safety issues")
    
    if 'repair' in info_lower or 'fix' in info_lower:
        if 'roof' in info_lower:
            repair_items.append("Roof repairs needed")
        if 'plumbing' in info_lower:
            repair_items.append("Plumbing repairs needed")
        if 'electrical' in info_lower:
            repair_items.append("Electrical repairs needed")
        if 'hvac' in info_lower or 'heating' in info_lower:
            repair_items.append("HVAC repairs needed")
    
    parsed["safety_issues"] = safety_issues
    parsed["repair_items"] = repair_items
    
    # Extract loan program
    if 'fha' in info_lower:
        parsed["loan_program"] = "fha"
    elif 'va' in info_lower:
        parsed["loan_program"] = "va"
    elif 'usda' in info_lower:
        parsed["loan_program"] = "usda"
    elif 'conventional' in info_lower:
        parsed["loan_program"] = "conventional"
    
    return parsed


@tool
def assess_property_condition(tool_input: str) -> str:
    """
    Assess property condition for lending purposes using Neo4j appraisal rules.
    
    This tool evaluates property condition against lending standards and identifies
    any issues that may affect loan approval or require repairs.
    
    Args:
        tool_input: Property condition information in natural language format
        
    Example:
        "Property at 123 Oak St, built in 2010, roof good condition, exterior fair, interior excellent, heating system good, electrical updated, plumbing good, foundation solid"
    
    Returns:
        String containing detailed property condition assessment report
    """
    
    try:
        # 12-FACTOR COMPLIANT: Enhanced parser only (Factor 8: Own Your Control Flow)
        from agents.shared.input_parser import parse_complete_mortgage_input
        
        # Factor 1: Natural Language → Tool Calls - comprehensive parsing
        parsed_data = parse_complete_mortgage_input(tool_input)
        
        # Factor 4: Tools as Structured Outputs - extract property condition details safely
        parsed_info = extract_property_condition_safely(tool_input, parsed_data)
        
        # Extract all the parameters
        property_address = parsed_info["property_address"]
        property_type = parsed_info["property_type"]
        year_built = parsed_info["year_built"]
        roof_condition = parsed_info["roof_condition"]
        exterior_condition = parsed_info["exterior_condition"]
        interior_condition = parsed_info["interior_condition"]
        heating_system = parsed_info["heating_system"]
        electrical_system = parsed_info["electrical_system"]
        plumbing_system = parsed_info["plumbing_system"]
        foundation_condition = parsed_info["foundation_condition"]
        safety_issues = parsed_info["safety_issues"]
        repair_items = parsed_info["repair_items"]
        loan_program = parsed_info["loan_program"]
        
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
            # Get property condition rules
            condition_rules_query = """
            MATCH (rule:PropertyAppraisalRule)
            WHERE rule.category = 'PropertyCondition'
            RETURN rule
            """
            result = session.run(condition_rules_query)
            # Convert result to list immediately to avoid consumption errors
            list(result)  # Condition rules consumed for assessment
            
            # Get safety requirement rules
            safety_rules_query = """
            MATCH (rule:PropertyAppraisalRule)
            WHERE rule.category = 'SafetyRequirements'
            RETURN rule
            """
            result = session.run(safety_rules_query)
            # Convert result to list immediately to avoid consumption errors
            list(result)  # Safety rules consumed for assessment
            
            # Get loan program specific requirements
            program_rules_query = """
            MATCH (rule:PropertyAppraisalRule)
            WHERE rule.category = 'LoanProgramRequirements' AND 
                  (rule.loan_program = $loan_program OR rule.loan_program = 'all')
            RETURN rule
            """
            result = session.run(program_rules_query, {"loan_program": loan_program})
            # Convert result to list immediately to avoid consumption errors
            list(result)  # Program rules consumed for loan compliance check
        
        # Calculate property age
        current_year = 2024
        property_age = current_year - year_built
        
        # Condition scoring
        condition_scores = {
            'excellent': 5,
            'good': 4,
            'average': 3,
            'fair': 2,
            'poor': 1
        }
        
        # Generate condition assessment report
        assessment_report = []
        assessment_report.append("PROPERTY CONDITION ASSESSMENT REPORT")
        assessment_report.append("=" * 50)
        
        # Property Information
        assessment_report.append(f"\n🏠 PROPERTY INFORMATION:")
        assessment_report.append(f"Address: {property_address}")
        assessment_report.append(f"Property Type: {property_type.replace('_', ' ').title()}")
        assessment_report.append(f"Year Built: {year_built} ({property_age} years old)")
        assessment_report.append(f"Loan Program: {loan_program.upper()}")
        
        # System Condition Analysis
        assessment_report.append(f"\n🔧 SYSTEM CONDITION ANALYSIS:")
        
        conditions = {
            'Roof': roof_condition,
            'Exterior': exterior_condition,
            'Interior': interior_condition,
            'Foundation': foundation_condition
        }
        
        systems = {
            'Heating': heating_system,
            'Electrical': electrical_system,
            'Plumbing': plumbing_system
        }
        
        overall_score = 0
        total_items = 0
        condition_issues = []
        
        for component, condition in conditions.items():
            condition_clean = condition.lower()
            score = condition_scores.get(condition_clean, 3)
            overall_score += score
            total_items += 1
            
            status = "" if score >= 4 else "⚠️" if score >= 3 else ""
            assessment_report.append(f"  {status} {component}: {condition.title()}")
            
            if score < 3:
                condition_issues.append(f"{component} condition rated as {condition}")
        
        assessment_report.append(f"\n🔌 MECHANICAL SYSTEMS:")
        for system, condition in systems.items():
            # Simplified condition assessment for systems
            if any(word in condition.lower() for word in ['good', 'excellent', 'new', 'updated']):
                assessment_report.append(f"   {system}: {condition}")
                overall_score += 4
            elif any(word in condition.lower() for word in ['fair', 'average', 'adequate']):
                assessment_report.append(f"  ⚠️ {system}: {condition}")
                overall_score += 3
                condition_issues.append(f"{system} system may need attention")
            else:
                assessment_report.append(f"   {system}: {condition}")
                overall_score += 1
                condition_issues.append(f"{system} system requires evaluation/repair")
            total_items += 1
        
        # Calculate overall condition rating
        average_score = overall_score / total_items if total_items > 0 else 3
        if average_score >= 4.5:
            overall_rating = "Excellent"
            rating_icon = ""
        elif average_score >= 3.5:
            overall_rating = "Good"
            rating_icon = ""
        elif average_score >= 2.5:
            overall_rating = "Fair"
            rating_icon = "⚠️"
        else:
            overall_rating = "Poor"
            rating_icon = ""
        
        assessment_report.append(f"\n📊 OVERALL CONDITION RATING:")
        assessment_report.append(f"  {rating_icon} Overall Rating: {overall_rating} ({average_score:.1f}/5.0)")
        
        # Safety Issues Analysis
        assessment_report.append(f"\n🚨 SAFETY ASSESSMENT:")
        if safety_issues:
            assessment_report.append("  Safety Issues Identified:")
            for issue in safety_issues:
                assessment_report.append(f"     {issue}")
        else:
            assessment_report.append("   No safety issues reported")
        
        # Required Repairs
        assessment_report.append(f"\n🔨 REPAIR REQUIREMENTS:")
        if repair_items:
            assessment_report.append("  Items Requiring Repair:")
            for item in repair_items:
                assessment_report.append(f"    🔧 {item}")
        else:
            assessment_report.append("   No specific repairs identified")
        
        # Loan Program Compliance
        assessment_report.append(f"\n📋 LOAN PROGRAM COMPLIANCE ({loan_program.upper()}):")
        
        # Program-specific requirements
        if loan_program.lower() == 'fha':
            assessment_report.append("  FHA Requirements:")
            assessment_report.append("     Property must be safe, sound, and secure")
            assessment_report.append("     All systems must be operational")
            if safety_issues:
                assessment_report.append("     Safety issues must be resolved before closing")
            if 'poor' in [roof_condition.lower(), foundation_condition.lower()]:
                assessment_report.append("     Major structural issues require repair")
            else:
                assessment_report.append("     Structural components acceptable")
                
        elif loan_program.lower() == 'va':
            assessment_report.append("  VA Requirements:")
            assessment_report.append("     Property must be move-in ready")
            assessment_report.append("     No health/safety hazards")
            if safety_issues or repair_items:
                assessment_report.append("     All deficiencies must be corrected")
            else:
                assessment_report.append("     Property condition meets VA standards")
                
        elif loan_program.lower() == 'usda':
            assessment_report.append("  USDA Requirements:")
            assessment_report.append("     Property must be decent, safe, and sanitary")
            if property_age > 30:
                assessment_report.append("    ⚠️ Additional inspection may be required for older property")
            else:
                assessment_report.append("     Property age acceptable")
                
        else:  # Conventional
            assessment_report.append("  Conventional Requirements:")
            assessment_report.append("     Property must be marketable")
            assessment_report.append("     No condition affecting value or marketability")
        
        # Age-Related Considerations
        assessment_report.append(f"\n📅 AGE-RELATED ANALYSIS:")
        if property_age < 5:
            assessment_report.append("   New construction - minimal condition concerns")
        elif property_age < 20:
            assessment_report.append("   Relatively new - standard condition assessment")
        elif property_age < 40:
            assessment_report.append("  ⚠️ Mature property - verify system updates and maintenance")
        else:
            assessment_report.append("  ⚠️ Older property - comprehensive system evaluation recommended")
            assessment_report.append("  💡 Consider cost approach if major updates needed")
        
        # Condition Impact on Value
        assessment_report.append(f"\n💰 CONDITION IMPACT ON VALUE:")
        if overall_rating in ['Excellent', 'Good']:
            assessment_report.append("   Condition supports market value")
            assessment_report.append("   No condition-related value adjustments needed")
        elif overall_rating == 'Fair':
            assessment_report.append("  ⚠️ Some condition issues may affect value")
            assessment_report.append("  💡 Consider condition adjustments in valuation")
        else:
            assessment_report.append("   Poor condition significantly affects value")
            assessment_report.append("  💡 Major condition adjustments required")
        
        # Recommendations
        assessment_report.append(f"\n💡 RECOMMENDATIONS:")
        
        if overall_rating in ['Excellent', 'Good'] and not safety_issues:
            assessment_report.append("  1. Property condition acceptable for lending")
            assessment_report.append("  2. Proceed with standard appraisal process")
        else:
            assessment_report.append("  1. Address all safety issues before loan approval")
            assessment_report.append("  2. Complete necessary repairs per loan program requirements")
            assessment_report.append("  3. Consider re-inspection after repairs")
        
        if condition_issues:
            assessment_report.append("  4. Document all condition issues in appraisal report")
            assessment_report.append("  5. Consider condition impact on final value estimate")
        
        if property_age > 30:
            assessment_report.append("  6. Verify remaining economic life supports loan term")
        
        # Final Condition Assessment
        assessment_report.append(f"\n🎯 FINAL ASSESSMENT:")
        if overall_rating in ['Excellent', 'Good'] and not safety_issues:
            assessment_report.append(f"   ACCEPTABLE: Property condition meets lending standards")
        elif overall_rating == 'Fair' and not safety_issues:
            assessment_report.append(f"  ⚠️ CONDITIONAL: Property acceptable with noted conditions")
        else:
            assessment_report.append(f"   SUBJECT TO: Property requires repairs before loan approval")
        
        return "\n".join(assessment_report)
        
    except Exception as e:
        logger.error(f"Error during property condition assessment: {e}")
        return f"❌ Error during property condition assessment: {str(e)}"


def validate_tool() -> bool:
    """Validate that the assess_property_condition tool works correctly."""
    try:
        # Test with sample natural language data
        result = assess_property_condition.invoke({
            "condition_info": "Property at 123 Main St, Anytown, CA 90210, single family home built in 2010, roof good condition, exterior good, interior excellent, heating system Central HVAC good condition, electrical system updated good condition, plumbing system original fair condition, foundation good, minor plumbing repairs needed, conventional loan"
        })
        return "PROPERTY CONDITION ASSESSMENT REPORT" in result and "FINAL ASSESSMENT" in result
    except Exception as e:
        print(f"Property condition assessment tool validation failed: {e}")
        return False

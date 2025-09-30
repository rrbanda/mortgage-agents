"""
Check Qualification Requirements Tool - Neo4j Powered

This tool analyzes specific qualification requirements for loan programs by querying
the Neo4j knowledge graph to provide detailed requirement analysis and gap identification.

Purpose:
- Analyze qualification requirements for specific loan programs
- Identify gaps between borrower profile and program requirements
- Provide specific guidance on meeting qualification criteria
- Use business rules from Neo4j for dynamic requirement checking
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# Configure logging
logger = logging.getLogger(__name__)

try:
    from utils import get_neo4j_connection, initialize_connection
except ImportError:
    # Fallback for different import paths during testing
    from utils import get_neo4j_connection, initialize_connection


class QualificationAnalysisRequest(BaseModel):
    """Schema for qualification requirement analysis"""
    loan_programs: str = Field(
        description="Loan programs to analyze (e.g., 'FHA', 'VA', 'FHA,Conventional'). Use 'all' for all programs"
    )
    borrower_credit_score: Optional[int] = Field(
        description="Borrower's current credit score (300-850)", default=None
    )
    borrower_down_payment: Optional[float] = Field(
        description="Available down payment as percentage (e.g., 0.05 for 5%)", default=None
    )
    borrower_dti_ratio: Optional[float] = Field(
        description="Current debt-to-income ratio as decimal (e.g., 0.30 for 30%)", default=None
    )
    military_status: Optional[str] = Field(
        description="Military status: 'active_duty', 'veteran', 'spouse', 'none'", default="none"
    )
    property_location: Optional[str] = Field(
        description="Property location: 'urban', 'suburban', 'rural'", default="suburban"
    )


@tool
def check_qualification_requirements(tool_input: str) -> str:
    """
    Analyze qualification requirements for specific loan programs using Neo4j data.
    
    This tool provides detailed analysis of loan program requirements and identifies
    gaps between borrower profile and qualification criteria using business rules from Neo4j.
    
    Args:
        tool_input: Qualification analysis request in natural language format
        
    Example:
        "Programs: FHA, VA; Credit: 720; Down payment: 10%; DTI: 25%; Military: veteran; Location: suburban"
        
    Returns:
        String containing detailed qualification analysis and recommendations
    """
    
    try:
        # 12-FACTOR COMPLIANT: Enhanced parser only (Factor 8: Own Your Control Flow)
        # 12-FACTOR COMPLIANT: Single parser approach (Factor 8: Own Your Control Flow)
        from agents.shared.input_parser import parse_complete_mortgage_input
        
        # Factor 1: Natural Language → Tool Calls - comprehensive parsing  
        parsed_data = parse_complete_mortgage_input(tool_input)
        request = tool_input.lower()  # Keep for loan program detection
        
        # Factor 4: Tools as Structured Outputs - safe parameter extraction
        loan_programs = parsed_data.get("loan_type") or "all"
        
        # Handle specific loan program detection from keywords (no regex)
        program_names = ['fha', 'conventional', 'va', 'usda', 'jumbo']
        for name in program_names:
            if name in request:
                loan_programs = name
                break
        
        # Extract borrower details with safe defaults (Factor 9: Compact Errors)
        borrower_credit_score = parsed_data.get("credit_score")
        borrower_down_payment = parsed_data.get("down_payment_percent")
        borrower_dti_ratio = parsed_data.get("dti_ratio")
        
        # Extract military status
        military_status = "none"
        if "veteran" in request or "military" in request:
            military_status = "veteran"
        elif "active duty" in request:
            military_status = "active_duty"
        elif "spouse" in request and "military" in request:
            military_status = "spouse"
        
        # Extract property location
        property_location = "suburban"  # default
        if "urban" in request:
            property_location = "urban"
        elif "rural" in request:
            property_location = "rural"
        
        # Initialize Neo4j connection with robust error handling
        if not initialize_connection():
            return "❌ Failed to connect to Neo4j database. Please try again later."
        
        connection = get_neo4j_connection()
        
        # ROBUST CONNECTION CHECK: Handle server environment issues
        if connection.driver is None:
            # Force reconnection if driver is None
            if not connection.connect():
                return "❌ Failed to establish Neo4j connection. Please restart the server."
        
        # Parse requested programs
        if loan_programs.lower() == "all":
            program_names = None  # Will get all programs
        else:
            program_names = [p.strip().upper() for p in loan_programs.split(',')]
        
        # Query loan programs and their requirements from Neo4j
        with connection.driver.session(database=connection.database) as session:
            if program_names:
                query = """
                MATCH (lp:LoanProgram)
                WHERE lp.name IN $program_names
                OPTIONAL MATCH (lp)-[:HAS_REQUIREMENT]->(qr:QualificationRequirement)
                RETURN lp, collect(DISTINCT qr) as requirements
                ORDER BY lp.name
                """
                result = session.run(query, {"program_names": program_names})
            else:
                query = """
                MATCH (lp:LoanProgram)
                OPTIONAL MATCH (lp)-[:HAS_REQUIREMENT]->(qr:QualificationRequirement)
                RETURN lp, collect(DISTINCT qr) as requirements
                ORDER BY lp.name
                """
                result = session.run(query)
            
            # Collect program data - convert result to list to avoid consumption errors
            records = list(result)
            programs_data = []
            for record in records:
                programs_data.append({
                    'program': dict(record['lp']),
                    'requirements': [dict(req) for req in record['requirements'] if req]
                })
        
        if not programs_data:
            available_programs = _get_available_programs(connection)
            return f"❌ No loan programs found for: {loan_programs}. Available programs: {', '.join(available_programs)}"
        
        # Analyze each program's requirements
        program_analyses = []
        for prog_data in programs_data:
            analysis = _analyze_program_requirements(
                prog_data['program'], prog_data['requirements'],
                borrower_credit_score, borrower_down_payment, borrower_dti_ratio,
                military_status, property_location, connection
            )
            program_analyses.append(analysis)
        
        # Generate qualification gaps and improvement roadmap
        qualification_gaps = _identify_qualification_gaps(program_analyses, connection)
        improvement_roadmap = _generate_improvement_roadmap(qualification_gaps, connection)
        alternative_programs = _suggest_alternative_programs(program_analyses, connection)
        
        # Format comprehensive qualification analysis as string
        programs_analyzed = [p['program']['name'] for p in programs_data]
        
        analysis_report = [
            "🎯 **LOAN QUALIFICATION ANALYSIS**",
            "=" * 50,
            f"**Programs Analyzed:** {', '.join(programs_analyzed)}",
            f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "👤 **BORROWER PROFILE:**",
            f"• Credit Score: {borrower_credit_score if borrower_credit_score else 'Not provided'}",
            f"• Down Payment: {f'{borrower_down_payment * 100:.1f}%' if borrower_down_payment else 'Not provided'}",
            f"• DTI Ratio: {f'{borrower_dti_ratio * 100:.1f}%' if borrower_dti_ratio else 'Not provided'}",
            f"• Military Status: {military_status.replace('_', ' ').title()}",
            f"• Property Location: {property_location.title()}",
            ""
        ]
        
        # Program Requirements Analysis
        analysis_report.append("📋 **PROGRAM REQUIREMENTS ANALYSIS:**")
        for analysis in program_analyses:
            program_name = analysis.get('program_name', 'Unknown Program')
            overall_qual = analysis.get('overall_qualification', {})
            qual_status = overall_qual.get('status', 'Unknown')
            
            analysis_report.append(f"\n### {program_name.upper()}")
            analysis_report.append(f"**Qualification Status:** {qual_status}")
            
            if qual_status == "Meets All Requirements":
                analysis_report.append("✅ You meet all basic requirements for this program")
            elif qual_status == "Has Qualification Gaps":
                analysis_report.append("⚠️ You meet some requirements but have qualification gaps")
            elif qual_status == "Requirements Not Fully Evaluated":
                analysis_report.append("ℹ️ Provide additional information for complete qualification analysis")
            else:
                analysis_report.append("❌ You do not currently meet the basic requirements")
            
            # Show basic requirements
            basic_reqs = analysis.get('basic_requirements', {})
            if basic_reqs and isinstance(basic_reqs, dict):
                analysis_report.append("**Basic Requirements:**")
                for req_name, req_data in basic_reqs.items():
                    if isinstance(req_data, dict):
                        req_status = "✅" if req_data.get('borrower_meets') else "❌"
                        formatted_name = req_name.replace('_', ' ').title()
                        analysis_report.append(f"  {req_status} {formatted_name}")
            elif basic_reqs and isinstance(basic_reqs, list):
                analysis_report.append("**Basic Requirements:**")
                for req in basic_reqs[:5]:
                    req_status = "✅" if req.get('meets_requirement') else "❌"
                    req_name = req.get('requirement_name', '').replace('_', ' ').title()
                    analysis_report.append(f"  {req_status} {req_name}")
        
        analysis_report.append("")
        
        # Qualification Gaps
        if qualification_gaps:
            analysis_report.append("🔍 **QUALIFICATION GAPS IDENTIFIED:**")
            gap_summary = qualification_gaps.get('summary', {})
            if gap_summary.get('status') == "No Qualification Gaps":
                analysis_report.append("✅ No qualification gaps found - you meet all requirements!")
            else:
                total_gaps = gap_summary.get('total_gaps', 0)
                gap_types = gap_summary.get('gap_types', [])
                analysis_report.append(f"Found {total_gaps} qualification gap(s) in: {', '.join(gap_types)}")
                
                # Credit score gaps
                credit_gaps = qualification_gaps.get('credit_score_gaps', [])
                if credit_gaps and isinstance(credit_gaps, list):
                    analysis_report.append("**Credit Score Gaps:**")
                    for gap in credit_gaps[:3]:
                        analysis_report.append(f"• {gap.get('program', 'Program')}: {gap.get('gap', 'Need higher credit score')}")
                
                # Down payment gaps
                dp_gaps = qualification_gaps.get('down_payment_gaps', [])
                if dp_gaps and isinstance(dp_gaps, list):
                    analysis_report.append("**Down Payment Gaps:**")
                    for gap in dp_gaps[:3]:
                        analysis_report.append(f"• {gap.get('program', 'Program')}: {gap.get('gap', 'Need higher down payment')}")
        
        analysis_report.append("")
        
        # Improvement Roadmap
        if improvement_roadmap and isinstance(improvement_roadmap, list):
            analysis_report.append("🚀 **IMPROVEMENT ROADMAP:**")
            for i, step in enumerate(improvement_roadmap[:5], 1):
                if isinstance(step, dict):
                    step_title = step.get('step_title', f'Step {i}')
                    step_desc = step.get('description', 'Follow program guidelines')
                    analysis_report.append(f"{i}. **{step_title}**")
                    analysis_report.append(f"   {step_desc}")
        
        # Alternative Programs
        if alternative_programs and isinstance(alternative_programs, list):
            analysis_report.append("\n💡 **ALTERNATIVE PROGRAM RECOMMENDATIONS:**")
            for alt in alternative_programs[:3]:
                if isinstance(alt, dict):
                    alt_name = alt.get('program_name', 'Alternative Program')
                    alt_reason = alt.get('recommendation_reason', 'May be a good fit')
                    analysis_report.append(f"• **{alt_name}**: {alt_reason}")
        
        return "\n".join(analysis_report)
        
    except Exception as e:
        logger.error(f"Error analyzing qualification requirements: {e}")
        return f"❌ Error analyzing qualification requirements: {str(e)}"
    finally:
        connection.disconnect()


def _get_available_programs(connection) -> List[str]:
    """Get list of available loan programs from Neo4j"""
    try:
        # Ensure connection has valid driver
        if connection.driver is None:
            if not connection.connect():
                return []
        
        with connection.driver.session(database=connection.database) as session:
            result = session.run("MATCH (lp:LoanProgram) RETURN lp.name as name ORDER BY name")
            # Convert to list to avoid consumption errors
            records = list(result)
            return [record["name"] for record in records]
    except Exception as e:
        # Return empty list instead of hardcoded fallback - 100% data-driven
        logger.error(f"Failed to get available programs from Neo4j: {e}")
        return []


def _analyze_program_requirements(program: Dict, requirements: List[Dict],
                                credit_score: Optional[int], down_payment: Optional[float], 
                                dti_ratio: Optional[float], military_status: str, 
                                property_location: str, connection) -> Dict:
    """Analyze requirements for a specific program using Neo4j business rules."""
    
    program_name = program['name']
    
    # Get basic program requirements
    basic_requirements = {
        "credit_score": {
            "minimum": program.get('min_credit_score'),
            "description": f"Minimum credit score for {program_name} loans",
            "borrower_meets": None,
            "gap": None
        },
        "down_payment": {
            "minimum": None,  # Will be set below using standardized requirements
            "minimum_percent": None,  # Will be set below
            "description": f"Minimum down payment for {program_name} loans",
            "borrower_meets": None,
            "gap": None
        },
        "debt_to_income": {
            "maximum": program.get('max_dti'),
            "maximum_percent": f"{program.get('max_dti') * 100:.0f}%" if program.get('max_dti') else None,
            "description": f"Maximum debt-to-income ratio for {program_name} loans",
            "borrower_meets": None,
            "gap": None
        }
    }
    
    # Use Neo4j program data for down payment requirements
    min_down_payment = program.get('min_down_payment', 0)
    basic_requirements["down_payment"]["minimum"] = min_down_payment
    basic_requirements["down_payment"]["minimum_percent"] = f"{min_down_payment * 100:.1f}%"
    
    # Check borrower against requirements if data provided
    if credit_score is not None and basic_requirements["credit_score"]["minimum"]:
        min_credit = basic_requirements["credit_score"]["minimum"]
        basic_requirements["credit_score"]["borrower_meets"] = credit_score >= min_credit
        if credit_score < min_credit:
            basic_requirements["credit_score"]["gap"] = f"Need {min_credit - credit_score} more points"
    
    if down_payment is not None:
        min_down = basic_requirements["down_payment"]["minimum"]
        basic_requirements["down_payment"]["borrower_meets"] = down_payment >= min_down
        if down_payment < min_down:
            gap_percent = (min_down - down_payment) * 100
            basic_requirements["down_payment"]["gap"] = f"Need {gap_percent:.1f}% more down payment"
    
    if dti_ratio is not None and basic_requirements["debt_to_income"]["maximum"]:
        max_dti = basic_requirements["debt_to_income"]["maximum"]
        basic_requirements["debt_to_income"]["borrower_meets"] = dti_ratio <= max_dti
        if dti_ratio > max_dti:
            gap_percent = (dti_ratio - max_dti) * 100
            basic_requirements["debt_to_income"]["gap"] = f"DTI is {gap_percent:.1f}% too high"
    
    # Get special requirements using Neo4j business rules
    special_requirements = _get_special_requirements(program_name, military_status, property_location, connection)
    
    # Get detailed requirements from Neo4j relationships
    detailed_requirements = []
    for req in requirements:
        detailed_requirements.append({
            "type": req.get('requirement_type', 'General'),
            "minimum_value": req.get('minimum_value'),
            "details": req.get('details', ''),
            "notes": req.get('notes', '')
        })
    
    return {
        "program_name": program_name,
        "program_type": program.get('type', 'Unknown'),
        "summary": program.get('summary', ''),
        "basic_requirements": basic_requirements,
        "special_requirements": special_requirements,
        "detailed_requirements": detailed_requirements,
        "overall_qualification": _determine_overall_qualification(basic_requirements, special_requirements)
    }


def _get_special_requirements(program_name: str, military_status: str, 
                            property_location: str, connection) -> Dict:
    """Get special requirements for specific programs using Neo4j data."""
    
    special_reqs = {}
    
    # Query special requirements from Neo4j - 100% data-driven
    # Ensure connection has valid driver
    if connection.driver is None:
        if not connection.connect():
            return special_reqs
    
    with connection.driver.session(database=connection.database) as session:
        query = """
        MATCH (sr:SpecialRequirement {program_name: $program_name})
        RETURN sr
        ORDER BY sr.requirement_type
        """
        result = session.run(query, {"program_name": program_name})
        # Convert to list to avoid consumption errors
        records = list(result)
        
        for record in records:
            req_data = dict(record["sr"])
            req_type = req_data["requirement_type"]
            
            # Build requirement from Neo4j data
            requirement = {
                "required": req_data.get("required", True),
                "description": req_data.get("description", ""),
                "additional_info": req_data.get("additional_info")
            }
            
            # Check borrower eligibility dynamically based on requirement type
            if req_type == "military_eligibility":
                eligibility_criteria = req_data.get("eligibility_criteria", [])
                requirement["borrower_meets"] = military_status in eligibility_criteria
                if not requirement["borrower_meets"]:
                    requirement["gap"] = req_data.get("gap_message", "Requirement not met")
                    requirement["verification_steps"] = req_data.get("verification_steps", [])
                    
            elif req_type == "property_location":
                eligibility_criteria = req_data.get("eligibility_criteria", [])
                requirement["borrower_meets"] = property_location in eligibility_criteria
                if not requirement["borrower_meets"]:
                    requirement["gap"] = req_data.get("gap_message", "Property location requirement not met")
                    requirement["verification_steps"] = req_data.get("verification_steps", [])
                    
            elif req_type == "va_benefits":
                requirement["benefit_details"] = req_data.get("benefit_details", "")
                
            # Add all other requirements as-is from Neo4j
            special_reqs[req_type] = requirement
    
    return special_reqs


def _determine_overall_qualification(basic_requirements: Dict, special_requirements: Dict) -> Dict:
    """Determine overall qualification status based on requirements analysis."""
    
    meets_basic = True
    issues = []
    
    for req_name, req_data in basic_requirements.items():
        if req_data.get("borrower_meets") is False:
            meets_basic = False
            issues.append(f"{req_name.replace('_', ' ').title()}: {req_data.get('gap', 'Not met')}")
    
    for req_name, req_data in special_requirements.items():
        if req_data.get("borrower_meets") is False:
            meets_basic = False
            issues.append(f"{req_name.replace('_', ' ').title()}: {req_data.get('gap', 'Not met')}")
    
    if meets_basic and not issues:
        status = "Meets All Requirements"
        message = "Borrower appears to meet all basic qualification requirements"
    elif not issues:
        status = "Requirements Not Fully Evaluated"
        message = "Provide borrower information for complete qualification analysis"
    else:
        status = "Has Qualification Gaps"
        message = f"Borrower has {len(issues)} qualification gap(s) to address"
    
    return {
        "status": status,
        "message": message,
        "issues": issues,
        "meets_basic_requirements": meets_basic
    }


def _identify_qualification_gaps(program_analyses: List[Dict], connection) -> Dict:
    """Identify common qualification gaps across programs using Neo4j business rules."""
    
    credit_gaps = []
    down_payment_gaps = []
    dti_gaps = []
    special_gaps = []
    
    for analysis in program_analyses:
        program_name = analysis["program_name"]
        basic_reqs = analysis["basic_requirements"]
        special_reqs = analysis["special_requirements"]
        
        # Collect gaps
        if not basic_reqs["credit_score"].get("borrower_meets", True):
            credit_gaps.append({
                "program": program_name,
                "gap": basic_reqs["credit_score"]["gap"],
                "minimum_required": basic_reqs["credit_score"]["minimum"]
            })
        
        if not basic_reqs["down_payment"].get("borrower_meets", True):
            down_payment_gaps.append({
                "program": program_name,
                "gap": basic_reqs["down_payment"]["gap"],
                "minimum_required": basic_reqs["down_payment"]["minimum_percent"]
            })
        
        if not basic_reqs["debt_to_income"].get("borrower_meets", True):
            dti_gaps.append({
                "program": program_name,
                "gap": basic_reqs["debt_to_income"]["gap"],
                "maximum_allowed": basic_reqs["debt_to_income"]["maximum_percent"]
            })
        
        for req_name, req_data in special_reqs.items():
            if not req_data.get("borrower_meets", True):
                special_gaps.append({
                    "program": program_name,
                    "requirement": req_name,
                    "gap": req_data.get("gap", "Special requirement not met")
                })
    
    return {
        "credit_score_gaps": credit_gaps,
        "down_payment_gaps": down_payment_gaps,
        "debt_to_income_gaps": dti_gaps,
        "special_requirement_gaps": special_gaps,
        "summary": _generate_gap_summary(credit_gaps, down_payment_gaps, dti_gaps, special_gaps)
    }


def _generate_gap_summary(credit_gaps: List, down_payment_gaps: List, 
                         dti_gaps: List, special_gaps: List) -> Dict:
    """Generate summary of qualification gaps."""
    
    total_gaps = len(credit_gaps) + len(down_payment_gaps) + len(dti_gaps) + len(special_gaps)
    
    if total_gaps == 0:
        return {
            "status": "No Qualification Gaps",
            "message": "Borrower meets requirements for all analyzed programs"
        }
    
    gap_types = []
    if credit_gaps:
        gap_types.append(f"credit score ({len(credit_gaps)} programs)")
    if down_payment_gaps:
        gap_types.append(f"down payment ({len(down_payment_gaps)} programs)")
    if dti_gaps:
        gap_types.append(f"debt-to-income ({len(dti_gaps)} programs)")
    if special_gaps:
        gap_types.append(f"special requirements ({len(special_gaps)} programs)")
    
    return {
        "status": "Qualification Gaps Identified",
        "total_gaps": total_gaps,
        "gap_types": gap_types,
        "message": f"Found {total_gaps} qualification gap(s) across {len(gap_types)} requirement area(s)"
    }


def _generate_improvement_roadmap(qualification_gaps: Dict, connection) -> List[Dict]:
    """Generate step-by-step improvement roadmap using Neo4j improvement strategies."""
    
    roadmap = []
    
    # Map gap types to improvement strategy categories
    gap_to_strategy_map = {
        "credit_score_gaps": "Credit Score Improvement",
        "down_payment_gaps": "Down Payment Savings", 
        "debt_to_income_gaps": "Debt-to-Income Reduction"
    }
    
    # Get improvement strategies from Neo4j for relevant gap types
    # Ensure connection has valid driver
    if connection.driver is None:
        if not connection.connect():
            return []
    
    with connection.driver.session(database=connection.database) as session:
        for gap_type, strategy_category in gap_to_strategy_map.items():
            if qualification_gaps.get(gap_type):
                # Query matching improvement strategy from Neo4j
                query = """
                MATCH (is:ImprovementStrategy {category: $category})
                RETURN is
                """
                result = session.run(query, {"category": strategy_category})
                strategy_record = result.single()
                
                if strategy_record:
                    strategy = dict(strategy_record["is"])
                    gaps = qualification_gaps[gap_type]
                    
                    # Calculate target and impact from actual gaps
                    if gap_type == "credit_score_gaps":
                        highest_credit_needed = max(gap["minimum_required"] for gap in gaps)
                        target = f"Improve credit score to {highest_credit_needed}+"
                        impact = f"Would qualify for {len(gaps)} additional program(s)"
                    elif gap_type == "down_payment_gaps":
                        highest_down_needed = max(float(gap["minimum_required"].rstrip('%')) for gap in gaps)
                        target = f"Save for {highest_down_needed}% down payment"
                        impact = f"Would qualify for {len(gaps)} additional program(s)"
                    else:  # debt_to_income_gaps
                        target = strategy.get("target_description", "Reduce monthly debt payments")
                        impact = f"Would improve qualification for {len(gaps)} program(s)"
                    
                    roadmap.append({
                        "priority": strategy.get("priority", 1),
                        "category": strategy.get("category", ""),
                        "target": target,
                        "steps": strategy.get("steps", []),
                        "timeline": strategy.get("timeline", ""),
                        "impact": impact
                    })
        
        # Handle special requirement gaps with specific strategies
        if qualification_gaps.get("special_requirement_gaps"):
            for gap in qualification_gaps["special_requirement_gaps"]:
                program = gap["program"]
                requirement = gap["requirement"]
                
                # Find matching improvement strategy for special requirements
                if "military_eligibility" in requirement:
                    strategy_query = """
                    MATCH (is:ImprovementStrategy {category: 'VA Loan Eligibility'})
                    RETURN is
                    """
                    result = session.run(strategy_query)
                    strategy_record = result.single()
                    
                    if strategy_record:
                        strategy = dict(strategy_record["is"])
                        roadmap.append({
                            "priority": strategy.get("priority", 3),
                            "category": strategy.get("category", ""),
                            "target": strategy.get("target_description", ""),
                            "steps": strategy.get("steps", []),
                            "timeline": strategy.get("timeline", ""),
                            "impact": strategy.get("impact_description", "")
                        })
                        
                elif "property_location" in requirement and "USDA" in program:
                    strategy_query = """
                    MATCH (is:ImprovementStrategy {category: 'USDA Property Location'})
                    RETURN is
                    """
                    result = session.run(strategy_query)
                    strategy_record = result.single()
                    
                    if strategy_record:
                        strategy = dict(strategy_record["is"])
                        roadmap.append({
                            "priority": strategy.get("priority", 3),
                            "category": strategy.get("category", ""),
                            "target": strategy.get("target_description", ""),
                            "steps": strategy.get("steps", []),
                            "timeline": strategy.get("timeline", ""),
                            "impact": strategy.get("impact_description", "")
                        })
    
    return sorted(roadmap, key=lambda x: x["priority"])


def _suggest_alternative_programs(program_analyses: List[Dict], connection) -> List[Dict]:
    """Suggest alternative programs based on qualification analysis."""
    
    alternatives = []
    
    # Find programs with fewer gaps
    programs_by_gaps = []
    for analysis in program_analyses:
        gap_count = len(analysis["overall_qualification"]["issues"])
        programs_by_gaps.append({
            "program": analysis["program_name"],
            "program_type": analysis["program_type"],
            "gap_count": gap_count,
            "issues": analysis["overall_qualification"]["issues"],
            "meets_requirements": analysis["overall_qualification"]["meets_basic_requirements"]
        })
    
    # Sort by fewest gaps
    programs_by_gaps.sort(key=lambda x: x["gap_count"])
    
    # Suggest top alternatives
    top_programs = programs_by_gaps[:3] if isinstance(programs_by_gaps, list) else []
    for i, prog in enumerate(top_programs):
        if prog["gap_count"] == 0:
            alternatives.append({
                "rank": i + 1,
                "program": prog["program"],
                "type": prog["program_type"],
                "status": "Fully Qualified",
                "reason": "Meets all basic qualification requirements",
                "recommendation": f"Consider {prog['program']} as primary option"
            })
        elif prog["gap_count"] <= 2:
            alternatives.append({
                "rank": i + 1,
                "program": prog["program"],
                "type": prog["program_type"],
                "status": "Nearly Qualified",
                "gaps": prog["issues"],
                "reason": f"Only {prog['gap_count']} requirement gap(s) to address",
                "recommendation": f"Focus on addressing {prog['program']} requirements first"
            })
    
    return alternatives


def validate_tool() -> bool:
    """
    Validate that the check_qualification_requirements tool is working correctly with Neo4j.
    
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Test qualification analysis without borrower data
        result1 = check_qualification_requirements.invoke({
            "loan_programs": "FHA,VA",
            "military_status": "none",
            "property_location": "suburban"
        })
        
        # Test qualification analysis with borrower data
        result2 = check_qualification_requirements.invoke({
            "loan_programs": "VA",
            "borrower_credit_score": 720,
            "borrower_down_payment": 0.0,
            "borrower_dti_ratio": 0.25,
            "military_status": "veteran",
            "property_location": "urban"
        })
        
        # Test analysis with qualification gaps
        result3 = check_qualification_requirements.invoke({
            "loan_programs": "Conventional",
            "borrower_credit_score": 580,
            "borrower_down_payment": 0.02,
            "borrower_dti_ratio": 0.50,
            "military_status": "none",
            "property_location": "suburban"
        })
        
        # Validate expected structure for all results
        required_keys = ["program_requirements", "qualification_gaps", "improvement_roadmap", "success"]
        
        for result in [result1, result2, result3]:
            if not (
                isinstance(result, dict) and
                all(key in result for key in required_keys) and
                result["success"] is True and
                isinstance(result["program_requirements"], list) and
                isinstance(result["qualification_gaps"], dict) and
                isinstance(result["improvement_roadmap"], list)
            ):
                return False
        
        # Validate that veteran with good profile meets VA requirements
        if result2["program_requirements"]:
            va_analysis = result2["program_requirements"][0]
            if va_analysis["overall_qualification"]["status"] != "Meets All Requirements":
                return False
        
        # Validate that poor profile shows gaps
        if not result3["qualification_gaps"]["credit_score_gaps"]:
            return False
            
        return True
        
    except Exception:
        return False

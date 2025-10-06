# Output Processing Specification v1.0


```markdown
# Output Processing Specification v1.0

## Purpose
Define how MCP tools return structured business logic results and how agents synthesize them into user-facing responses.

---

## Architecture Overview

```
MCP Tool Execution
    ↓
Structured Output (Pydantic) ← Tool Scope
    ↓
Agent Synthesis
    ↓
Natural Language Response ← Agent Scope
    ↓
End User
```

---

## Two-Layer Output Architecture

### Layer 1: Tool Output (Business Logic Results)
- **Format**: Pydantic models
- **Consumer**: Agent (not user)
- **Purpose**: Machine-readable results with all computed data
- **Contains**: Status codes, calculations, routing metadata, issues

### Layer 2: Agent Response (User Communication)
- **Format**: Natural language text
- **Consumer**: End user
- **Purpose**: Clear, helpful communication
- **Contains**: Explanations, recommendations, next steps

---

## 1. Tool Output Schemas

**File**: `agents/shared/output_schemas.py` (NEW FILE)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

# ==================== BASE SCHEMA ====================

class ToolResult(BaseModel):
    """
    Base class for all MCP tool outputs.
    
    Purpose: Ensure consistent structure across all tools.
    Consumer: Agent reasoning layer
    """
    success: bool = Field(
        ...,
        description="Whether tool executed without errors"
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO timestamp of execution"
    )
    
    tool_name: str = Field(
        ...,
        description="Name of tool that generated this result"
    )
    
    execution_time_ms: Optional[int] = Field(
        None,
        description="Execution time in milliseconds"
    )
    
    class Config:
        extra = "forbid"  # Strict - no unexpected fields


# ==================== QUALIFICATION RESULT ====================

class QualificationResult(ToolResult):
    """
    Output from perform_initial_qualification tool.
    
    Contains all qualification data for agent to synthesize response.
    NOT formatted for direct user consumption.
    """
    tool_name: str = "perform_initial_qualification"
    
    # ===== Primary Status =====
    status: Literal[
        "QUALIFIED",
        "NOT_QUALIFIED", 
        "CONDITIONAL",
        "MANUAL_REVIEW"
    ] = Field(..., description="Overall qualification status")
    
    # ===== Program Eligibility =====
    eligible_programs: List[str] = Field(
        default_factory=list,
        description="Programs borrower qualifies for (conventional, fha, va, usda)"
    )
    
    ineligible_programs: Dict[str, str] = Field(
        default_factory=dict,
        description="Programs not eligible for with reasons. Key=program, Value=reason"
    )
    
    # ===== Credit Analysis =====
    credit_score_used: Optional[int] = Field(
        None,
        description="Credit score used for qualification"
    )
    
    credit_issues: List[str] = Field(
        default_factory=list,
        description="Credit-related issues identified"
    )
    
    credit_warnings: List[str] = Field(
        default_factory=list,
        description="Credit-related warnings"
    )
    
    # ===== Income Analysis =====
    monthly_income: Optional[float] = Field(
        None,
        description="Monthly income used for calculation"
    )
    
    front_end_dti: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Front-end DTI ratio as percentage"
    )
    
    back_end_dti: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Back-end DTI ratio as percentage"
    )
    
    income_issues: List[str] = Field(
        default_factory=list,
        description="Income-related issues"
    )
    
    income_warnings: List[str] = Field(
        default_factory=list,
        description="Income-related warnings"
    )
    
    # ===== Asset Analysis =====
    liquid_assets: Optional[float] = Field(
        None,
        description="Available liquid assets"
    )
    
    required_reserves: Optional[float] = Field(
        None,
        description="Required reserve amount"
    )
    
    down_payment_available: Optional[float] = Field(
        None,
        description="Available down payment"
    )
    
    ltv_ratio: Optional[float] = Field(
        None,
        ge=0,
        le=200,
        description="Loan-to-value ratio as percentage"
    )
    
    asset_issues: List[str] = Field(
        default_factory=list,
        description="Asset-related issues"
    )
    
    asset_warnings: List[str] = Field(
        default_factory=list,
        description="Asset-related warnings"
    )
    
    # ===== Routing & Next Steps =====
    next_agent: Optional[str] = Field(
        None,
        description="Which agent should handle next (DocumentAgent, MortgageAdvisorAgent, etc.)"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations"
    )
    
    requires_manual_review: bool = Field(
        False,
        description="Whether case needs manual underwriter review"
    )
    
    # ===== Summary Counts =====
    total_issues: int = Field(
        0,
        ge=0,
        description="Total count of issues across all categories"
    )
    
    total_warnings: int = Field(
        0,
        ge=0,
        description="Total count of warnings across all categories"
    )


# ==================== COMPLETENESS RESULT ====================

class CompletenessResult(ToolResult):
    """
    Output from check_application_completeness tool.
    
    Contains detailed analysis of what's missing vs provided.
    """
    tool_name: str = "check_application_completeness"
    
    # ===== Overall Status =====
    completeness_status: Literal[
        "COMPLETE",
        "SUBSTANTIALLY_COMPLETE",
        "INCOMPLETE"
    ] = Field(..., description="Overall completeness assessment")
    
    # ===== Completion Metrics =====
    completion_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of required fields completed"
    )
    
    required_completion_threshold: float = Field(
        85.0,
        description="Minimum required completion percentage"
    )
    
    # ===== Field Analysis =====
    provided_fields_count: int = Field(
        ...,
        ge=0,
        description="Number of fields provided"
    )
    
    missing_fields_count: int = Field(
        ...,
        ge=0,
        description="Number of required fields missing"
    )
    
    # ===== Documentation Status =====
    documents_provided: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of documents provided. [{name, status}]"
    )
    
    documents_missing: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of documents missing. [{name, reason}]"
    )
    
    # ===== Conditional Requirements =====
    conditional_docs_needed: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Documents needed based on loan type/employment. [{doc, condition, reason}]"
    )
    
    # ===== Section Breakdown =====
    section_completeness: Dict[str, float] = Field(
        default_factory=dict,
        description="Completion % by section. {section_name: percentage}"
    )
    
    # ===== Next Steps =====
    next_action: str = Field(
        ...,
        description="Recommended next action"
    )
    
    can_proceed: bool = Field(
        ...,
        description="Whether application can proceed to next stage"
    )


# ==================== URLA GENERATION RESULT ====================

class URLAGenerationResult(ToolResult):
    """
    Output from generate_urla_1003_form tool.
    
    Contains URLA generation status and validation results.
    """
    tool_name: str = "generate_urla_1003_form"
    
    # ===== Generation Status =====
    urla_form_id: Optional[str] = Field(
        None,
        description="Generated URLA form ID"
    )
    
    form_version: str = Field(
        "1003_2021",
        description="URLA form version used"
    )
    
    generation_status: Literal[
        "GENERATED",
        "PARTIAL",
        "FAILED"
    ] = Field(..., description="Form generation status")
    
    # ===== Completion Analysis =====
    sections_completed: int = Field(
        ...,
        ge=0,
        description="Number of URLA sections completed"
    )
    
    sections_total: int = Field(
        ...,
        ge=0,
        description="Total number of URLA sections"
    )
    
    fields_completed: int = Field(
        ...,
        ge=0,
        description="Number of fields populated"
    )
    
    fields_total: int = Field(
        ...,
        ge=0,
        description="Total number of fields"
    )
    
    completion_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall form completion percentage"
    )
    
    # ===== Validation Results =====
    validation_errors: List[str] = Field(
        default_factory=list,
        description="Validation errors found"
    )
    
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="Validation warnings"
    )
    
    # ===== Compliance Status =====
    compliance_status: Literal[
        "COMPLIANT",
        "NEEDS_REVIEW",
        "NON_COMPLIANT"
    ] = Field(..., description="Regulatory compliance status")
    
    fannie_mae_compliant: bool = Field(
        False,
        description="Meets Fannie Mae requirements"
    )
    
    freddie_mac_compliant: bool = Field(
        False,
        description="Meets Freddie Mac requirements"
    )
    
    # ===== Generated Data =====
    urla_data_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of populated URLA sections"
    )
    
    # ===== Next Steps =====
    ready_for_submission: bool = Field(
        False,
        description="Whether form is ready for lender submission"
    )
    
    required_actions: List[str] = Field(
        default_factory=list,
        description="Actions needed before submission"
    )


# ==================== APPLICATION INTAKE RESULT ====================

class ApplicationIntakeResult(ToolResult):
    """
    Output from receive_mortgage_application tool.
    
    Contains intake processing status and validation results.
    """
    tool_name: str = "receive_mortgage_application"
    
    # ===== Application Info =====
    application_id: str = Field(
        ...,
        description="Generated or retrieved application ID"
    )
    
    received_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When application was received"
    )
    
    # ===== Processing Status =====
    intake_status: Literal[
        "RECEIVED",
        "INCOMPLETE",
        "VALIDATION_ERROR",
        "DUPLICATE"
    ] = Field(..., description="Intake processing status")
    
    # ===== Validation Results =====
    validation_passed: bool = Field(
        ...,
        description="Whether all validations passed"
    )
    
    validation_errors: List[str] = Field(
        default_factory=list,
        description="Critical validation errors"
    )
    
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical warnings"
    )
    
    # ===== Data Quality =====
    data_quality_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall data quality score"
    )
    
    fields_validated: int = Field(
        ...,
        ge=0,
        description="Number of fields validated"
    )
    
    fields_failed: int = Field(
        ...,
        ge=0,
        description="Number of fields that failed validation"
    )
    
    # ===== Applicant Profile =====
    applicant_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of applicant information"
    )
    
    loan_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of loan request"
    )
    
    # ===== Routing Decision =====
    next_agent: str = Field(
        ...,
        description="Which agent should handle next"
    )
    
    workflow_stage: str = Field(
        ...,
        description="Current workflow stage"
    )
    
    priority_level: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        "MEDIUM",
        description="Processing priority"
    )
    
    # ===== Storage Confirmation =====
    stored_in_database: bool = Field(
        False,
        description="Whether data was successfully stored"
    )
    
    storage_id: Optional[str] = Field(
        None,
        description="Database storage identifier"
    )


# ==================== ERROR RESULT ====================

class ErrorResult(ToolResult):
    """
    Standard error response for any tool failure.
    
    Use this when tool cannot complete successfully.
    """
    success: bool = False
    
    error_code: str = Field(
        ...,
        description="Machine-readable error code"
    )
    
    error_message: str = Field(
        ...,
        description="Human-readable error description"
    )
    
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context"
    )
    
    retry_possible: bool = Field(
        False,
        description="Whether operation can be retried"
    )
    
    user_action_required: Optional[str] = Field(
        None,
        description="What user needs to do to resolve"
    )
```

---

## 2. Tool Output Implementation Pattern

**File**: `tools/perform_initial_qualification.py` (EXAMPLE)

```python
from agents.shared.output_schemas import QualificationResult, ErrorResult
from agents.shared.schemas import MortgageInput
from mcp import tool
import logging

logger = logging.getLogger(__name__)

@tool
def perform_initial_qualification(data: MortgageInput) -> QualificationResult:
    """
    Perform initial qualification assessment.
    
    Args:
        data: Pre-validated mortgage application data
        
    Returns:
        QualificationResult: Structured qualification analysis
        
    Note: Returns Pydantic model, NOT user-facing text.
    Agent will synthesize response from this data.
    """
    try:
        start_time = time.time()
        
        # Query Neo4j rules
        credit_rules = get_qualification_rules("credit")
        income_rules = get_qualification_rules("income")
        asset_rules = get_qualification_rules("assets")
        
        # Initialize result data
        eligible_programs = []
        ineligible_programs = {}
        credit_issues = []
        income_issues = []
        asset_issues = []
        
        # ===== CREDIT ANALYSIS =====
        min_scores = credit_rules.get("minimum_credit_scores", {})
        
        for program, min_score in min_scores.items():
            if data.credit_score and data.credit_score >= min_score:
                eligible_programs.append(program)
            else:
                ineligible_programs[program] = f"Credit score {data.credit_score} below minimum {min_score}"
        
        # Check for credit issues
        if data.credit_score and data.credit_score < 580:
            credit_issues.append("credit_score_very_low")
        
        # ===== INCOME ANALYSIS =====
        if data.monthly_income:
            dti_front = calculate_front_end_dti(data)
            dti_back = calculate_back_end_dti(data)
            
            max_dti = income_rules.get("max_back_end_dti", 43)
            if dti_back > max_dti:
                income_issues.append(f"dti_exceeds_limit_{max_dti}")
        else:
            income_issues.append("income_not_provided")
            dti_front = None
            dti_back = None
        
        # ===== ASSET ANALYSIS =====
        if data.property_value and data.loan_amount:
            ltv = (data.loan_amount / data.property_value) * 100
        else:
            ltv = None
        
        # Calculate required reserves
        required_reserves = calculate_required_reserves(data, asset_rules)
        
        if data.liquid_assets and required_reserves:
            if data.liquid_assets < required_reserves:
                asset_issues.append("insufficient_reserves")
        
        # ===== DETERMINE STATUS =====
        total_issues = len(credit_issues) + len(income_issues) + len(asset_issues)
        
        if total_issues == 0 and eligible_programs:
            status = "QUALIFIED"
            next_agent = "DocumentAgent"
        elif total_issues <= 2 and eligible_programs:
            status = "CONDITIONAL"
            next_agent = "DocumentAgent"
        elif eligible_programs:
            status = "MANUAL_REVIEW"
            next_agent = "UnderwritingAgent"
        else:
            status = "NOT_QUALIFIED"
            next_agent = "MortgageAdvisorAgent"
        
        # ===== BUILD RECOMMENDATIONS =====
        recommendations = []
        if status == "QUALIFIED":
            recommendations.append("proceed_to_documentation")
        elif status == "NOT_QUALIFIED":
            if credit_issues:
                recommendations.append("improve_credit_score")
            if income_issues:
                recommendations.append("increase_income_or_reduce_debts")
            if asset_issues:
                recommendations.append("increase_savings_for_reserves")
        
        # ===== RETURN STRUCTURED RESULT =====
        execution_time = int((time.time() - start_time) * 1000)
        
        return QualificationResult(
            success=True,
            tool_name="perform_initial_qualification",
            execution_time_ms=execution_time,
            status=status,
            eligible_programs=eligible_programs,
            ineligible_programs=ineligible_programs,
            credit_score_used=data.credit_score,
            credit_issues=credit_issues,
            credit_warnings=[],
            monthly_income=data.monthly_income,
            front_end_dti=dti_front,
            back_end_dti=dti_back,
            income_issues=income_issues,
            income_warnings=[],
            liquid_assets=data.liquid_assets,
            required_reserves=required_reserves,
            down_payment_available=data.down_payment,
            ltv_ratio=ltv,
            asset_issues=asset_issues,
            asset_warnings=[],
            next_agent=next_agent,
            recommendations=recommendations,
            requires_manual_review=(status == "MANUAL_REVIEW"),
            total_issues=total_issues,
            total_warnings=0
        )
        
    except Exception as e:
        logger.error(f"Qualification failed: {e}")
        return ErrorResult(
            success=False,
            tool_name="perform_initial_qualification",
            error_code="QUALIFICATION_ERROR",
            error_message=str(e),
            retry_possible=True
        )
```

---

## 3. Agent Response Synthesis

**File**: `agents/response_formatter.py` (NEW FILE)

```python
from agents.shared.output_schemas import (
    QualificationResult,
    CompletenessResult,
    URLAGenerationResult,
    ApplicationIntakeResult
)
from typing import Union

class ResponseFormatter:
    """
    Formats structured tool outputs into user-friendly responses.
    
    Responsibilities:
    - Convert Pydantic models to natural language
    - Add helpful context and explanations
    - Include actionable next steps
    - Maintain consistent tone
    
    Does NOT:
    - Execute business logic
    - Query databases
    - Make decisions
    """
    
    @staticmethod
    def format_qualification(result: QualificationResult) -> str:
        """
        Convert QualificationResult to user response.
        
        Args:
            result: Structured qualification data from tool
            
        Returns:
            Natural language response for user
        """
        if result.status == "QUALIFIED":
            return ResponseFormatter._format_qualified(result)
        elif result.status == "NOT_QUALIFIED":
            return ResponseFormatter._format_not_qualified(result)
        elif result.status == "CONDITIONAL":
            return ResponseFormatter._format_conditional(result)
        else:  # MANUAL_REVIEW
            return ResponseFormatter._format_manual_review(result)
    
    @staticmethod
    def _format_qualified(result: QualificationResult) -> str:
        """Format response for qualified borrowers"""
        response = []
        
        response.append("QUALIFICATION APPROVED")
        response.append("=" * 50)
        response.append("")
        response.append("Great news! Based on your financial profile, you qualify for mortgage financing.")
        response.append("")
        
        # Profile Summary
        response.append("YOUR PROFILE:")
        if result.credit_score_used:
            response.append(f"• Credit Score: {result.credit_score_used}")
        if result.back_end_dti:
            response.append(f"• Debt-to-Income Ratio: {result.back_end_dti:.1f}%")
        if result.ltv_ratio:
            response.append(f"• Loan-to-Value: {result.ltv_ratio:.1f}%")
        response.append("")
        
        # Eligible Programs
        response.append("ELIGIBLE LOAN PROGRAMS:")
        for program in result.eligible_programs:
            program_desc = ResponseFormatter._get_program_description(program)
            response.append(f"• {program_desc}")
        response.append("")
        
        # Next Steps
        response.append("NEXT STEPS:")
        response.append("1. Gather required documentation")
        response.append("2. Complete full application")
        response.append("3. Schedule property appraisal")
        response.append("4. Review loan estimates")
        response.append("")
        response.append("Ready to proceed? I'll help you with the documentation phase.")
        
        return "\n".join(response)
    
    @staticmethod
    def _format_not_qualified(result: QualificationResult) -> str:
        """Format response for non-qualified borrowers"""
        response = []
        
        response.append("QUALIFICATION ASSESSMENT")
        response.append("=" * 50)
        response.append("")
        response.append("Based on current information, you don't meet minimum requirements yet.")
        response.append("")
        
        # Issues Identified
        response.append("AREAS NEEDING IMPROVEMENT:")
        all_issues = result.credit_issues + result.income_issues + result.asset_issues
        for issue in all_issues:
            readable_issue = ResponseFormatter._format_issue(issue)
            response.append(f"• {readable_issue}")
        response.append("")
        
        # Recommendations
        response.append("IMPROVEMENT RECOMMENDATIONS:")
        for rec in result.recommendations:
            readable_rec = ResponseFormatter._format_recommendation(rec)
            response.append(f"{readable_rec}")
        response.append("")
        
        response.append("Would you like me to connect you with a mortgage advisor?")
        response.append("They can create a personalized improvement plan.")
        
        return "\n".join(response)
    
    @staticmethod
    def _get_program_description(program: str) -> str:
        """Get friendly description of loan program"""
        descriptions = {
            "conventional": "Conventional - Best rates and flexible terms",
            "fha": "FHA - Lower down payment (3.5%), great for first-time buyers",
            "va": "VA - No down payment required, for military/veterans",
            "usda": "USDA - Rural property financing, no down payment"
        }
        return descriptions.get(program, program.title())
    
    @staticmethod
    def _format_issue(issue_code: str) -> str:
        """Convert issue code to readable text"""
        issue_map = {
            "credit_score_very_low": "Credit score below minimum requirements",
            "dti_exceeds_limit_43": "Debt-to-income ratio above 43% limit",
            "insufficient_reserves": "Not enough cash reserves after down payment",
            "income_not_provided": "Income information needed"
        }
        return issue_map.get(issue_code, issue_code.replace("_", " ").title())
    
    @staticmethod
    def _format_recommendation(rec_code: str) -> str:
        """Convert recommendation code to actionable advice"""
        rec_map = {
            "improve_credit_score": "1. Focus on improving credit score:\n   - Pay down credit card balances\n   - Make all payments on time\n   - Dispute any errors on credit report",
            "increase_income_or_reduce_debts": "2. Improve debt-to-income ratio:\n   - Pay off or pay down existing debts\n   - Increase income through raises or additional work\n   - Consider a co-borrower",
            "increase_savings_for_reserves": "3. Build up cash reserves:\n   - Increase savings account balance\n   - Consider gift funds from family\n   - Review retirement account options"
        }
        return rec_map.get(rec_code, rec_code.replace("_", " ").title())
    
    @staticmethod
    def format_completeness(result: CompletenessResult) -> str:
        """Format completeness check result"""
        response = []
        
        response.append("APPLICATION COMPLETENESS CHECK")
        response.append("=" * 50)
        response.append("")
        
        # Status
        status_icon = {
            "COMPLETE": "✓",
            "SUBSTANTIALLY_COMPLETE": "~",
            "INCOMPLETE": "✗"
        }.get(result.completeness_status, "?")
        
        response.append(f"Status: {status_icon} {result.completeness_status}")
        response.append(f"Completion: {result.completion_percentage:.1f}%")
        response.append(f"Required: {result.required_completion_threshold:.0f}%")
        response.append("")
        
        # Missing documents
        if result.documents_missing:
            response.append("MISSING DOCUMENTATION:")
            for doc in result.documents_missing:
                response.append(f"• {doc['name']} - {doc['reason']}")
            response.append("")
        
        # Next action
        response.append(f"NEXT ACTION: {result.next_action}")
        
        if result.can_proceed:
            response.append("")
            response.append("You can proceed to the next stage while gathering remaining items.")
        
        return "\n".join(response)
```

---

## 4. Agent Integration

**File**: `agents/mortgage_agent.py`

```python
from langgraph.graph import StateGraph
from agents.shared.output_schemas import QualificationResult
from agents.response_formatter import ResponseFormatter
from tools.perform_initial_qualification import perform_initial_qualification

def agent_node(state: dict) -> dict:
    """
    Agent node that calls tools and formats responses.
    
    Flow:
    1. Determine which tool to call based on parsed input
    2. Call tool (receives structured Pydantic result)
    3. Format result for user using ResponseFormatter
    4. Return natural language response
    """
    parsed_data = state["parsed_data"]
    
    # Determine intent and call appropriate tool
    if state.get("intent") == "check_qualification":
        # Call tool - returns Pydantic model
        tool_result = perform_initial_qualification(parsed_data)
        
        # Format for user - returns string
        if isinstance(tool_result, QualificationResult):
            user_response = ResponseFormatter.format_qualification(tool_result)
        else:
            user_response = "An error occurred during qualification check."
        
        return {
            **state,
            "tool_result": tool_result,  # Keep structured data
            "final_output": user_response,  # User-facing text
            "next_agent": tool_result.next_agent if hasattr(tool_result, 'next_agent') else None
        }
    
    # Handle other intents...
    return state
```

---

## 5. Testing Requirements

**File**: `tests/test_output_schemas.py`

```python
import pytest
from agents.shared.output_schemas import QualificationResult, ErrorResult

class TestQualificationResult:
    """Test qualification output schema"""
    
    def test_valid_qualified_result(self):
        """Test creating qualified result"""
        result = QualificationResult(
            success=True,
            tool_name="perform_initial_qualification",
            status="QUALIFIED",
            eligible_programs=["conventional", "fha"],
            credit_score_used=720,
            back_end_dti=38.5,
            total_issues=0,
            total_warnings=0,
            next_agent="DocumentAgent",
            recommendations=["proceed_to_documentation"]
        )
        
        assert result.status == "QUALIFIED"
        assert len(result.eligible_programs) == 2
        assert result.total_issues == 0
    
    def test_dti_validation(self):
        """DTI must be 0-100"""
        with pytest.raises(ValueError):
            QualificationResult(
                success=True,
                tool_name="test",
                status="QUALIFIED",
                back_end_dti=150  # Invalid
            )

class TestResponseFormatter:
    """Test response formatting"""
    
    def test_format_qualified_response(self):
        """Test formatting qualified result"""
        result = QualificationResult(
            success=True,
            tool_name="perform_initial_qualification",
            status="QUALIFIED",
            eligible_programs=["conventional"],
            credit_score_used=720,
            next_agent="DocumentAgent",
            recommendations=[]
        )
        
        response = ResponseFormatter.format_qualification(result)
        
        assert "QUALIFICATION APPROVED" in response
        assert "720" in response
        assert "Conventional" in response
        assert "NEXT STEPS" in response
```

---

## 6. Key Principles

### Tool Outputs Should:
✓ Be machine-readable Pydantic models  
✓ Contain ALL computed values  
✓ Include routing metadata  
✓ Have clear status codes  
✓ List all issues and warnings  
✓ Provide recommendations as codes  

### Tool Outputs Should NOT:
✗ Contain formatted text for users  
✗ Include explanatory paragraphs  
✗ Have inconsistent field names  
✗ Mix data types  
✗ Skip error handling  

### Agent Responses Should:
✓ Be natural, conversational language  
✓ Explain technical terms  
✓ Provide actionable next steps  
✓ Be consistent in tone  
✓ Include all relevant context  

### Agent Responses Should NOT:
✗ Include raw data structures  
✗ Use technical jargon without explanation  
✗ Be overly verbose  
✗ Skip important information  

---

## 7. Migration Checklist

### Phase 1: Create Output
```markdown
## 7. Migration Checklist

### Phase 1: Create Output Schemas
- [ ] Create `agents/shared/output_schemas.py`
- [ ] Define all tool result models (QualificationResult, CompletenessResult, etc.)
- [ ] Add validators where needed
- [ ] Test schema instantiation independently
- [ ] Verify all current tool return values can map to schemas

### Phase 2: Create Response Formatter
- [ ] Create `agents/response_formatter.py`
- [ ] Implement format methods for each result type
- [ ] Create helper methods for common formatting
- [ ] Test formatting with sample Pydantic models
- [ ] Ensure tone consistency across all responses

### Phase 3: Update One Tool at a Time
- [ ] Start with simplest tool (e.g., check_completeness)
- [ ] Change return type from `str` to result schema
- [ ] Update business logic to populate schema fields
- [ ] Test tool returns valid Pydantic model
- [ ] Move to next tool only after tests pass

### Phase 4: Update Agent Response Layer
- [ ] Modify agent_node to call ResponseFormatter
- [ ] Keep structured tool result in state
- [ ] Return formatted text to user
- [ ] Test end-to-end flow
- [ ] Verify user sees natural language, not JSON

### Phase 5: Validate Complete System
- [ ] All tools return Pydantic models
- [ ] All agent responses use ResponseFormatter
- [ ] No raw data structures shown to users
- [ ] Consistent tone across all responses
- [ ] Error handling works correctly

---

## 8. Response Formatting Patterns

### Pattern 1: Status-Based Responses

```python
def format_by_status(result: QualificationResult) -> str:
    """Route to appropriate formatter based on status"""
    formatters = {
        "QUALIFIED": format_qualified,
        "NOT_QUALIFIED": format_not_qualified,
        "CONDITIONAL": format_conditional,
        "MANUAL_REVIEW": format_manual_review
    }
    
    formatter = formatters.get(result.status)
    return formatter(result) if formatter else format_generic(result)
```

### Pattern 2: Template-Based Formatting

```python
QUALIFIED_TEMPLATE = """
✓ QUALIFICATION APPROVED

{greeting}

YOUR PROFILE:
{profile_details}

ELIGIBLE PROGRAMS:
{programs}

NEXT STEPS:
{next_steps}
"""

def format_with_template(result: QualificationResult) -> str:
    """Use template for consistent structure"""
    return QUALIFIED_TEMPLATE.format(
        greeting=get_greeting(result),
        profile_details=format_profile(result),
        programs=format_programs(result.eligible_programs),
        next_steps=format_next_steps(result.recommendations)
    )
```

### Pattern 3: LLM-Based Dynamic Formatting

```python
def format_with_llm(result: QualificationResult) -> str:
    """Let LLM create natural response from structured data"""
    
    prompt = f"""Generate a friendly mortgage qualification response.

Status: {result.status}
Credit Score: {result.credit_score_used}
Eligible Programs: {result.eligible_programs}
DTI: {result.back_end_dti}%
Issues: {result.total_issues}

Write 2-3 paragraphs explaining the qualification result clearly and helpfully.
Include specific next steps."""

    llm = ChatAnthropic(model="claude-sonnet-4")
    response = llm.invoke(prompt)
    
    return response.content
```

**Recommendation**: Use Pattern 1 (status-based) for consistency, Pattern 3 (LLM) for complex scenarios.

---

## 9. Error Handling

### Tool Error Response

```python
@tool
def perform_initial_qualification(data: MortgageInput) -> Union[QualificationResult, ErrorResult]:
    """Tool with proper error handling"""
    try:
        # Business logic
        result = calculate_qualification(data)
        return result
        
    except DatabaseConnectionError as e:
        return ErrorResult(
            success=False,
            tool_name="perform_initial_qualification",
            error_code="DB_CONNECTION_FAILED",
            error_message="Unable to connect to rules database",
            error_details={"exception": str(e)},
            retry_possible=True,
            user_action_required="Please try again in a moment"
        )
    
    except ValidationError as e:
        return ErrorResult(
            success=False,
            tool_name="perform_initial_qualification",
            error_code="VALIDATION_ERROR",
            error_message="Input data validation failed",
            error_details={"errors": e.errors()},
            retry_possible=False,
            user_action_required="Please provide complete information"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ErrorResult(
            success=False,
            tool_name="perform_initial_qualification",
            error_code="INTERNAL_ERROR",
            error_message="An unexpected error occurred",
            retry_possible=True,
            user_action_required="Please contact support if this persists"
        )
```

### Agent Error Formatting

```python
def format_error(error: ErrorResult) -> str:
    """Format error for user"""
    
    if error.error_code == "DB_CONNECTION_FAILED":
        return """
⚠️ TEMPORARY SERVICE ISSUE

We're experiencing a temporary connection issue.

What this means:
- Your information is safe
- No action needed from you
- This usually resolves quickly

Please try again in a few moments. If the issue persists, our team has been notified.
"""
    
    elif error.error_code == "VALIDATION_ERROR":
        return f"""
 INFORMATION NEEDED

{error.user_action_required}

Details: {error.error_message}

What to do:
1. Review the information you provided
2. Correct any missing or invalid fields
3. Submit again
"""
    
    else:  # Generic error
        return f"""
⚠️ UNEXPECTED ERROR

Something went wrong while processing your request.

Error ID: {error.timestamp}

{error.user_action_required or 'Please try again or contact support.'}
"""
```

---

## 10. Output Quality Standards

### Structured Output (Tool Level)

**Must Have:**
- All fields properly typed
- Status codes from predefined enum
- Counts and metrics accurate
- Routing information included
- Timestamp for auditing

**Example of Good Tool Output:**
```python
QualificationResult(
    success=True,
    timestamp="2025-10-04T10:30:00Z",
    tool_name="perform_initial_qualification",
    status="QUALIFIED",
    eligible_programs=["conventional", "fha"],
    credit_score_used=720,
    back_end_dti=38.5,
    ltv_ratio=80.0,
    total_issues=0,
    total_warnings=1,
    next_agent="DocumentAgent",
    recommendations=["proceed_to_documentation"]
)
```

**Example of Poor Tool Output:**
```python
#  DON'T DO THIS
{
    "result": "you qualify",  # Unstructured
    "stuff": [720, 38.5],     # Unclear field names
    "next": "docs"            # Abbreviated
}
```

### Natural Language Response (Agent Level)

**Must Have:**
- Clear status or outcome
- Specific numbers/metrics
- Actionable next steps
- Appropriate tone
- No technical jargon (or explained if used)

**Example of Good User Response:**
```
✓ QUALIFICATION APPROVED

Great news! Based on your financial profile, you qualify for mortgage financing.

YOUR PROFILE:
• Credit Score: 720
• Debt-to-Income Ratio: 38.5%
• Loan-to-Value: 80.0%

ELIGIBLE LOAN PROGRAMS:
• Conventional - Best rates and flexible terms
• FHA - Lower down payment option

NEXT STEPS:
1. Gather required documentation
2. Complete full application
3. Schedule property appraisal

Ready to proceed? I'll help you with the documentation phase.
```

**Example of Poor User Response:**
```
#  DON'T DO THIS
Status: QUALIFIED
Programs: conventional, fha
DTI: 38.5
LTV: 80.0
Next: DocumentAgent

# Problems:
# - No context or explanation
# - Technical abbreviations
# - No next steps
# - Not conversational
```

---

## 11. Common Anti-Patterns to Avoid

###  Anti-Pattern 1: Mixing Concerns

```python
# WRONG - Tool returns user-facing text
@tool
def perform_qualification(data: MortgageInput) -> str:
    result = calculate(data)
    return f"You qualify for {result.programs}!"  #  Formatting in tool
```

```python
# RIGHT - Tool returns structured data
@tool
def perform_qualification(data: MortgageInput) -> QualificationResult:
    result = calculate(data)
    return QualificationResult(
        status="QUALIFIED",
        eligible_programs=result.programs
    )  # ✓ Agent formats later
```

###  Anti-Pattern 2: Inconsistent Status Codes

```python
# WRONG - Random status strings
return {"status": "ok"}           # Different from other tools
return {"status": "good"}         # No standard
return {"status": "qualified"}    # Inconsistent capitalization
```

```python
# RIGHT - Enum-based status
class Status(str, Enum):
    QUALIFIED = "QUALIFIED"
    NOT_QUALIFIED = "NOT_QUALIFIED"

return QualificationResult(status=Status.QUALIFIED)  # ✓ Consistent
```

###  Anti-Pattern 3: Incomplete Error Handling

```python
# WRONG - Generic exception bubble up
@tool
def tool_name(data):
    result = risky_operation()  # Might fail
    return result  #  No error handling
```

```python
# RIGHT - Structured error response
@tool
def tool_name(data) -> Union[SuccessResult, ErrorResult]:
    try:
        result = risky_operation()
        return SuccessResult(...)
    except Exception as e:
        return ErrorResult(
            error_code="OPERATION_FAILED",
            error_message=str(e),
            retry_possible=True
        )  # ✓ Clear error contract
```

###  Anti-Pattern 4: Losing Structure in Agent

```python
# WRONG - Agent returns raw tool output
def agent_node(state):
    tool_result = call_tool(state["data"])
    return {"output": str(tool_result)}  #  Dumps Pydantic as string
```

```python
# RIGHT - Agent formats properly
def agent_node(state):
    tool_result = call_tool(state["data"])
    user_response = ResponseFormatter.format(tool_result)  # ✓ Proper formatting
    return {
        "tool_result": tool_result,      # Keep structured
        "final_output": user_response    # User-facing text
    }
```

---

## 12. Success Criteria

### Tool Output Layer
✓ All tools return Pydantic models  
✓ No tools return raw strings with data  
✓ All status codes use enums  
✓ Error handling returns ErrorResult  
✓ All computed values included in result  
✓ Routing metadata (next_agent) present  
✓ Timestamps for audit trail  

### Agent Response Layer
✓ All responses use ResponseFormatter  
✓ Consistent tone across responses  
✓ No raw Pydantic models shown to users  
✓ All technical terms explained  
✓ Actionable next steps included  
✓ Appropriate formatting (headers, bullets)  
✓ Error messages user-friendly  

### Integration
✓ Tools → Pydantic → Agent → String pipeline works  
✓ State preserves both structured and formatted data  
✓ No information lost in formatting  
✓ End-to-end tests pass  
✓ User experience is clear and helpful  

---

## 13. Testing Strategy

### Unit Tests - Output Schemas

```python
# Test schema validation
def test_qualification_result_validation():
    # Valid result
    result = QualificationResult(
        success=True,
        tool_name="test",
        status="QUALIFIED",
        eligible_programs=["conventional"]
    )
    assert result.status == "QUALIFIED"
    
    # Invalid DTI
    with pytest.raises(ValidationError):
        QualificationResult(
            success=True,
            tool_name="test",
            status="QUALIFIED",
            back_end_dti=150  # Out of range
        )
```

### Integration Tests - Tool to Response

```python
def test_qualification_flow():
    # Create input
    input_data = MortgageInput(
        credit_score=720,
        monthly_income=8000,
        loan_amount=400000
    )
    
    # Call tool
    tool_result = perform_initial_qualification(input_data)
    
    # Verify structured output
    assert isinstance(tool_result, QualificationResult)
    assert tool_result.success == True
    assert len(tool_result.eligible_programs) > 0
    
    # Format for user
    user_response = ResponseFormatter.format_qualification(tool_result)
    
    # Verify natural language
    assert isinstance(user_response, str)
    assert "QUALIFICATION" in user_response
    assert "NEXT STEPS" in user_response
    assert str(tool_result.credit_score_used) in user_response
```

### End-to-End Tests

```python
def test_full_workflow():
    # User input
    raw_input = "Sarah, 720 credit, wants $400k loan"
    
    # Parse input
    parser = UnifiedInputParser()
    parsed = parser.parse(raw_input)
    
    # Call tool
    tool_result = perform_initial_qualification(parsed)
    
    # Format response
    final_response = ResponseFormatter.format_qualification(tool_result)
    
    # Verify complete flow
    assert isinstance(parsed, MortgageInput)
    assert isinstance(tool_result, QualificationResult)
    assert isinstance(final_response, str)
    assert "Sarah" not in tool_result.dict()  # Tool has no names
    assert "720" in final_response  # User sees credit score
```

---

## 14. Documentation Requirements

Each tool must document its output schema:

```python
@tool
def perform_initial_qualification(data: MortgageInput) -> QualificationResult:
    """
    Perform initial mortgage qualification assessment.
    
    Args:
        data: Validated mortgage application data
        
    Returns:
        QualificationResult with:
            - status: Overall qualification outcome
            - eligible_programs: List of programs borrower qualifies for
            - credit_score_used: Credit score used in analysis
            - dti ratios: Front-end and back-end DTI calculations
            - issues: List of qualification issues by category
            - recommendations: Suggested next steps
            - next_agent: Which agent should handle next
            
    Example:
        >>> result = perform_initial_qualification(data)
        >>> result.status
        'QUALIFIED'
        >>> result.eligible_programs
        ['conventional', 'fha']
    """
```

---

## End of Specification

**Summary:**
- Tools return structured Pydantic models (machine-readable)
- Agents format responses with ResponseFormatter (human-readable)
- Two-layer architecture keeps concerns separated
- Consistent patterns across all tools
- Clear error handling
- User experience is natural and helpful

**Next Steps:**
1. Implement output schemas
2. Create response formatter
3. Update tools one at a time
4. Test thoroughly at each step
5. Deploy incrementally

For input processing, see: `INPUT_PROCESSING_SPEC.md`
```

---

This specification is complete and ready for Cursor to implement. It provides:

1. **Complete Pydantic schemas** for all tool outputs
2. **ResponseFormatter class** with examples
3. **Integration patterns** for agents
4. **Error handling** strategies
5. **Testing requirements**
6. **Migration checklist**
7. **Anti-patterns to avoid**
8. **Success criteria**

Give this to Cursor and ask it to implement **Phase 1 first** (output schemas only), test thoroughly, then move to Phase 2.
# Data Models and Schemas

## Pydantic Input Schemas

### ApplicationIntakeInput

```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class ApplicationIntakeInput(BaseModel):
    """Input schema for application intake rules evaluation"""
    personal_info: Dict[str, Any] = Field(
        description="Personal information including name, ssn, dob, phone, email"
    )
    current_address: Dict[str, Any] = Field(
        description="Current address information"
    )
    employment: Dict[str, Any] = Field(
        description="Employment information"
    )
    loan_details: Dict[str, Any] = Field(
        description="Loan details including purpose, amount, property info"
    )
    financial: Dict[str, Any] = Field(
        description="Financial information including assets and debts"
    )
    property_info: Dict[str, Any] = Field(
        description="Property information including type and occupancy"
    )
```

### QualificationInput

```python
from pydantic import BaseModel, Field
from typing import Literal

class QualificationInput(BaseModel):
    """Input schema for qualification threshold evaluation"""
    credit_score: int = Field(ge=300, le=850, description="Credit score")
    monthly_income: float = Field(gt=0, description="Monthly income")
    monthly_debts: float = Field(ge=0, description="Monthly debt payments")
    down_payment_amount: float = Field(ge=0, description="Down payment amount")
    down_payment_percent: float = Field(ge=0.0, le=1.0, description="Down payment percentage")
    loan_amount: float = Field(gt=0, description="Loan amount")
    property_value: float = Field(gt=0, description="Property value")
    loan_purpose: Literal["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
    property_type: Literal["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
    occupancy_type: Literal["primary_residence", "second_home", "investment_property"]
```

### CreditScoreInput

```python
from pydantic import BaseModel, Field
from typing import List

class CreditScoreInput(BaseModel):
    """Input schema for credit score assessment"""
    credit_score: int = Field(ge=300, le=850, description="Credit score")
    credit_issues: List[str] = Field(
        description="List of credit issues (bankruptcy, foreclosure, collections, late_payments)"
    )
    credit_history_length: int = Field(ge=0, description="Credit history length in years")
    recent_inquiries: int = Field(ge=0, description="Recent credit inquiries")
    credit_utilization: float = Field(ge=0.0, le=1.0, description="Credit utilization ratio")
```

### FinancialAssessmentInput

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class FinancialAssessmentInput(BaseModel):
    """Input schema for financial assessment rules"""
    employment_type: Literal["w2", "self_employed", "contract", "retired", "other"]
    monthly_income: float = Field(gt=0, description="Monthly income")
    annual_income: float = Field(gt=0, description="Annual income")
    years_employed: float = Field(ge=0, description="Years employed")
    income_stability: Literal["stable", "variable", "seasonal"]
    additional_income: List[Dict[str, Any]] = Field(
        description="Additional income sources"
    )
    income_documentation: List[str] = Field(
        description="Available income documentation"
    )
```

### DocumentVerificationInput

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class DocumentVerificationInput(BaseModel):
    """Input schema for document verification rules"""
    loan_purpose: Literal["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
    employment_type: Literal["w2", "self_employed", "contract", "retired", "other"]
    property_type: Literal["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
    documents_provided: List[str] = Field(
        description="List of provided document types"
    )
    document_dates: Dict[str, str] = Field(
        description="Document dates"
    )
    document_quality: Dict[str, str] = Field(
        description="Document quality assessments"
    )
```

### UnderwritingInput

```python
from pydantic import BaseModel, Field
from typing import Literal

class UnderwritingInput(BaseModel):
    """Input schema for underwriting rules evaluation"""
    credit_score: int = Field(ge=300, le=850, description="Credit score")
    dti_ratio: float = Field(ge=0.0, le=1.0, description="Debt-to-income ratio")
    ltv_ratio: float = Field(ge=0.0, le=1.0, description="Loan-to-value ratio")
    loan_amount: float = Field(gt=0, description="Loan amount")
    property_value: float = Field(gt=0, description="Property value")
    employment_stability: str = Field(description="Employment stability assessment")
    asset_reserves: float = Field(ge=0, description="Asset reserves")
    loan_purpose: Literal["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
    property_type: Literal["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
    occupancy_type: Literal["primary_residence", "second_home", "investment_property"]
```

### PricingInput

```python
from pydantic import BaseModel, Field
from typing import Literal

class PricingInput(BaseModel):
    """Input schema for pricing rules evaluation"""
    credit_score: int = Field(ge=300, le=850, description="Credit score")
    loan_amount: float = Field(gt=0, description="Loan amount")
    ltv_ratio: float = Field(ge=0.0, le=1.0, description="Loan-to-value ratio")
    loan_purpose: Literal["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
    property_type: Literal["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
    occupancy_type: Literal["primary_residence", "second_home", "investment_property"]
    down_payment_percent: float = Field(ge=0.0, le=1.0, description="Down payment percentage")
    lock_period: int = Field(ge=0, description="Rate lock period in days")
```

### ComplianceInput

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Literal

class ComplianceInput(BaseModel):
    """Input schema for compliance rules evaluation"""
    loan_amount: float = Field(gt=0, description="Loan amount")
    property_value: float = Field(gt=0, description="Property value")
    borrower_income: float = Field(gt=0, description="Borrower income")
    property_address: str = Field(description="Property address")
    loan_purpose: Literal["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
    property_type: Literal["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
    occupancy_type: Literal["primary_residence", "second_home", "investment_property"]
    borrower_demographics: Dict[str, Any] = Field(
        description="Borrower demographic information"
    )
```

## Pydantic Output Schemas

### ApplicationIntakeResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class ApplicationIntakeResult(BaseModel):
    """Output schema for application intake rules evaluation"""
    validation_status: Literal["VALID", "INVALID", "INCOMPLETE"]
    required_fields_status: Dict[str, bool]
    format_validation_errors: List[str]
    completeness_percentage: float = Field(ge=0.0, le=1.0)
    missing_critical_fields: List[str]
    conditional_requirements: Dict[str, List[str]]
    recommendations: List[str]
```

### QualificationResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class QualificationResult(BaseModel):
    """Output schema for qualification threshold evaluation"""
    qualification_status: Literal["HighlyQualified", "Qualified", "QualifiedWithConditions", "NotQualified"]
    qualification_score: int = Field(ge=0, le=150)
    eligible_programs: List[str]
    credit_assessment: Dict[str, Any]
    income_assessment: Dict[str, Any]
    asset_assessment: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    threshold_details: Dict[str, Any]
```

### CreditScoreResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class CreditScoreResult(BaseModel):
    """Output schema for credit score assessment"""
    credit_category: Literal["excellent", "good", "fair", "poor"]
    qualification_boost: int = Field(ge=-10, le=25)
    recommendation_message: str
    eligible_programs: List[str]
    credit_issues_analysis: Dict[str, Any]
    improvement_recommendations: List[str]
    threshold_comparison: Dict[str, Any]
```

### FinancialAssessmentResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class FinancialAssessmentResult(BaseModel):
    """Output schema for financial assessment rules"""
    qualifying_income: float
    income_stability_assessment: Literal["stable", "needs_review", "unstable"]
    documentation_requirements: List[str]
    income_calculation_method: str
    additional_income_qualification: Dict[str, Any]
    recommendations: List[str]
    dti_impact: Dict[str, Any]
```

### DocumentVerificationResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class DocumentVerificationResult(BaseModel):
    """Output schema for document verification rules"""
    verification_status: Literal["COMPLETE", "INCOMPLETE", "PENDING"]
    required_documents: List[str]
    provided_documents: List[str]
    missing_documents: List[str]
    conditional_requirements: Dict[str, List[str]]
    document_quality_issues: List[str]
    recommendations: List[str]
    compliance_status: Dict[str, Any]
```

### UnderwritingResult

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class UnderwritingResult(BaseModel):
    """Output schema for underwriting rules evaluation"""
    underwriting_decision: Literal["APPROVED", "CONDITIONAL", "DENIED", "MANUAL_REVIEW"]
    risk_score: int = Field(ge=0, le=100)
    risk_factors: List[str]
    mitigating_factors: List[str]
    conditions: List[str]
    recommendations: List[str]
    automated_decision: bool
    manual_review_reasons: List[str]
```

### PricingResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PricingResult(BaseModel):
    """Output schema for pricing rules evaluation"""
    base_rate: float
    rate_adjustments: List[Dict[str, Any]]
    final_rate: float
    fees: Dict[str, float]
    total_fees: float
    apr: float
    pricing_tier: str
    recommendations: List[str]
```

### ComplianceResult

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class ComplianceResult(BaseModel):
    """Output schema for compliance rules evaluation"""
    compliance_status: Literal["COMPLIANT", "NON_COMPLIANT", "REQUIRES_REVIEW"]
    regulatory_checks: Dict[str, Any]
    fair_lending_assessment: Dict[str, Any]
    privacy_compliance: Dict[str, Any]
    audit_trail_requirements: List[str]
    compliance_issues: List[str]
    recommendations: List[str]
```

## Neo4j Data Models

### ApplicationIntakeRule Node

```cypher
CREATE (rule:ApplicationIntakeRule {
    rule_id: "APPLICATION_REQUIRED_FIELDS",
    category: "ApplicationRequirements",
    rule_type: "required_fields",
    personal_info: ["first_name", "last_name", "ssn", "date_of_birth", "phone", "email"],
    current_address: ["street", "city", "state", "zip", "years_at_address"],
    employment: ["employer_name", "title", "years_employed", "monthly_income"],
    loan_details: ["loan_purpose", "loan_amount", "property_address", "property_value"],
    financial: ["assets", "debts", "monthly_expenses"],
    property_info: ["property_type", "occupancy_type", "property_use"],
    description: "Required fields for complete mortgage application"
})
```

### BusinessRule Node

```cypher
CREATE (rule:BusinessRule {
    rule_type: "CreditScoreAssessment",
    category: "excellent",
    min_threshold: 740,
    max_threshold: 850,
    description: "Excellent credit score - qualifies for best rates",
    qualification_boost: 25,
    recommendation_message: "Excellent credit score - qualifies for best rates and most programs"
})
```

### QualificationThreshold Node

```cypher
CREATE (threshold:QualificationThreshold {
    status: "HighlyQualified",
    min_score: 75,
    max_score: 150,
    description: "Highly qualified for this loan program",
    recommendation_priority: 1
})
```

### DocumentVerificationRule Node

```cypher
CREATE (rule:DocumentVerificationRule {
    rule_id: "DOCUMENT_REQUIREMENTS_STANDARD",
    category: "Standard",
    document_type: "pay_stub",
    required_count: 2,
    period: "most_recent_30_days",
    description: "Standard pay stub requirements"
})
```

## Data Validation Rules

### Input Validation

1. **Required Fields**: All required fields must be present
2. **Data Types**: Fields must match expected data types
3. **Value Ranges**: Numeric fields must be within valid ranges
4. **Enum Values**: String fields must match allowed enum values
5. **Format Validation**: SSN, phone, email formats must be valid

### Business Rule Validation

1. **Rule Existence**: Business rules must exist in Neo4j
2. **Rule Consistency**: Rules must be internally consistent
3. **Rule Completeness**: All required rule components must be present
4. **Rule Validity**: Rules must be valid and executable

### Output Validation

1. **Result Completeness**: All expected result fields must be present
2. **Result Consistency**: Results must be internally consistent
3. **Result Validity**: Results must be valid and meaningful
4. **Error Handling**: Errors must be properly formatted and informative

## Data Transformation

### Input Transformation

1. **Type Conversion**: Convert string inputs to appropriate types
2. **Format Normalization**: Normalize phone numbers, SSNs, etc.
3. **Data Cleaning**: Remove invalid characters and normalize data
4. **Validation**: Validate data against business rules

### Output Transformation

1. **Result Formatting**: Format results for client consumption
2. **Error Formatting**: Format errors consistently
3. **Data Serialization**: Serialize complex objects to JSON
4. **Response Packaging**: Package responses with metadata

## Data Persistence

### Neo4j Storage

1. **Rule Storage**: Store business rules as nodes with properties
2. **Relationship Storage**: Store rule relationships and dependencies
3. **Indexing**: Create indexes for efficient rule queries
4. **Versioning**: Support rule versioning and history

### Caching Strategy

1. **Rule Caching**: Cache frequently accessed rules
2. **Result Caching**: Cache rule evaluation results
3. **Query Caching**: Cache Neo4j query results
4. **Cache Invalidation**: Invalidate cache when rules change

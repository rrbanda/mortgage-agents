# API Contracts and Schemas

## MCP Tool Definitions

### Tool 1: Evaluate Application Intake Rules

**Tool Name**: `evaluate_application_intake_rules`

**Description**: Evaluate application data against application intake business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "application_data": {
      "type": "object",
      "properties": {
        "personal_info": {
          "type": "object",
          "description": "Personal information including name, ssn, dob, phone, email"
        },
        "current_address": {
          "type": "object",
          "description": "Current address information"
        },
        "employment": {
          "type": "object",
          "description": "Employment information"
        },
        "loan_details": {
          "type": "object",
          "description": "Loan details including purpose, amount, property info"
        },
        "financial": {
          "type": "object",
          "description": "Financial information including assets and debts"
        },
        "property_info": {
          "type": "object",
          "description": "Property information including type and occupancy"
        }
      },
      "required": ["personal_info", "current_address", "employment", "loan_details", "financial", "property_info"]
    }
  },
  "required": ["application_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "validation_status": {
      "type": "string",
      "enum": ["VALID", "INVALID", "INCOMPLETE"]
    },
    "required_fields_status": {
      "type": "object",
      "description": "Dict of field validation results"
    },
    "format_validation_errors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of format validation issues"
    },
    "completeness_percentage": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "missing_critical_fields": {
      "type": "array",
      "items": {"type": "string"}
    },
    "conditional_requirements": {
      "type": "object",
      "description": "Dict of conditional field requirements"
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### Tool 2: Check Qualification Thresholds

**Tool Name**: `check_qualification_thresholds`

**Description**: Check borrower qualification against qualification threshold business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "qualification_data": {
      "type": "object",
      "properties": {
        "credit_score": {
          "type": "integer",
          "minimum": 300,
          "maximum": 850
        },
        "monthly_income": {
          "type": "number",
          "minimum": 0
        },
        "monthly_debts": {
          "type": "number",
          "minimum": 0
        },
        "down_payment_amount": {
          "type": "number",
          "minimum": 0
        },
        "down_payment_percent": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "loan_amount": {
          "type": "number",
          "minimum": 0
        },
        "property_value": {
          "type": "number",
          "minimum": 0
        },
        "loan_purpose": {
          "type": "string",
          "enum": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
        },
        "property_type": {
          "type": "string",
          "enum": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
        },
        "occupancy_type": {
          "type": "string",
          "enum": ["primary_residence", "second_home", "investment_property"]
        }
      },
      "required": ["credit_score", "monthly_income", "monthly_debts", "loan_amount", "property_value", "loan_purpose", "property_type", "occupancy_type"]
    }
  },
  "required": ["qualification_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "qualification_status": {
      "type": "string",
      "enum": ["HighlyQualified", "Qualified", "QualifiedWithConditions", "NotQualified"]
    },
    "qualification_score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    },
    "eligible_programs": {
      "type": "array",
      "items": {"type": "string"}
    },
    "credit_assessment": {
      "type": "object",
      "description": "Dict with credit score evaluation"
    },
    "income_assessment": {
      "type": "object",
      "description": "Dict with DTI analysis"
    },
    "asset_assessment": {
      "type": "object",
      "description": "Dict with down payment analysis"
    },
    "issues": {
      "type": "array",
      "items": {"type": "string"}
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "threshold_details": {
      "type": "object",
      "description": "Dict with specific threshold comparisons"
    }
  }
}
```

### Tool 3: Assess Credit Score Rules

**Tool Name**: `assess_credit_score_rules`

**Description**: Assess credit score against credit assessment business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "credit_data": {
      "type": "object",
      "properties": {
        "credit_score": {
          "type": "integer",
          "minimum": 300,
          "maximum": 850
        },
        "credit_issues": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of credit issues (bankruptcy, foreclosure, collections, late_payments)"
        },
        "credit_history_length": {
          "type": "integer",
          "minimum": 0,
          "description": "Credit history length in years"
        },
        "recent_inquiries": {
          "type": "integer",
          "minimum": 0,
          "description": "Recent credit inquiries"
        },
        "credit_utilization": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Credit utilization ratio"
        }
      },
      "required": ["credit_score"]
    }
  },
  "required": ["credit_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "credit_category": {
      "type": "string",
      "enum": ["excellent", "good", "fair", "poor"]
    },
    "qualification_boost": {
      "type": "integer",
      "minimum": -10,
      "maximum": 25
    },
    "recommendation_message": {
      "type": "string"
    },
    "eligible_programs": {
      "type": "array",
      "items": {"type": "string"}
    },
    "credit_issues_analysis": {
      "type": "object",
      "description": "Dict with issue impact assessment"
    },
    "improvement_recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "threshold_comparison": {
      "type": "object",
      "description": "Dict with specific threshold details"
    }
  }
}
```

### Tool 4: Evaluate Income Calculation Rules

**Tool Name**: `evaluate_income_calculation_rules`

**Description**: Evaluate income data against income calculation business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "income_data": {
      "type": "object",
      "properties": {
        "employment_type": {
          "type": "string",
          "enum": ["w2", "self_employed", "contract", "retired", "other"]
        },
        "monthly_income": {
          "type": "number",
          "minimum": 0
        },
        "annual_income": {
          "type": "number",
          "minimum": 0
        },
        "years_employed": {
          "type": "number",
          "minimum": 0
        },
        "income_stability": {
          "type": "string",
          "enum": ["stable", "variable", "seasonal"]
        },
        "additional_income": {
          "type": "array",
          "items": {"type": "object"},
          "description": "Additional income sources"
        },
        "income_documentation": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Available income documentation"
        }
      },
      "required": ["employment_type", "monthly_income"]
    }
  },
  "required": ["income_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "qualifying_income": {
      "type": "number"
    },
    "income_stability_assessment": {
      "type": "string",
      "enum": ["stable", "needs_review", "unstable"]
    },
    "documentation_requirements": {
      "type": "array",
      "items": {"type": "string"}
    },
    "income_calculation_method": {
      "type": "string"
    },
    "additional_income_qualification": {
      "type": "object",
      "description": "Dict with additional income analysis"
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "dti_impact": {
      "type": "object",
      "description": "Dict with debt-to-income ratio impact"
    }
  }
}
```

### Tool 5: Check Document Verification Rules

**Tool Name**: `check_document_verification_rules`

**Description**: Check document requirements against document verification business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "document_data": {
      "type": "object",
      "properties": {
        "loan_purpose": {
          "type": "string",
          "enum": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
        },
        "employment_type": {
          "type": "string",
          "enum": ["w2", "self_employed", "contract", "retired", "other"]
        },
        "property_type": {
          "type": "string",
          "enum": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
        },
        "documents_provided": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of provided document types"
        },
        "document_dates": {
          "type": "object",
          "description": "Document dates"
        },
        "document_quality": {
          "type": "object",
          "description": "Document quality assessments"
        }
      },
      "required": ["loan_purpose", "employment_type", "property_type"]
    }
  },
  "required": ["document_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "verification_status": {
      "type": "string",
      "enum": ["COMPLETE", "INCOMPLETE", "PENDING"]
    },
    "required_documents": {
      "type": "array",
      "items": {"type": "string"}
    },
    "provided_documents": {
      "type": "array",
      "items": {"type": "string"}
    },
    "missing_documents": {
      "type": "array",
      "items": {"type": "string"}
    },
    "conditional_requirements": {
      "type": "object",
      "description": "Dict of conditional document requirements"
    },
    "document_quality_issues": {
      "type": "array",
      "items": {"type": "string"}
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "compliance_status": {
      "type": "object",
      "description": "Dict with compliance check results"
    }
  }
}
```

### Tool 6: Assess Underwriting Rules

**Tool Name**: `assess_underwriting_rules`

**Description**: Assess loan application against underwriting business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "underwriting_data": {
      "type": "object",
      "properties": {
        "credit_score": {
          "type": "integer",
          "minimum": 300,
          "maximum": 850
        },
        "dti_ratio": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "ltv_ratio": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "loan_amount": {
          "type": "number",
          "minimum": 0
        },
        "property_value": {
          "type": "number",
          "minimum": 0
        },
        "employment_stability": {
          "type": "string"
        },
        "asset_reserves": {
          "type": "number",
          "minimum": 0
        },
        "loan_purpose": {
          "type": "string",
          "enum": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
        },
        "property_type": {
          "type": "string",
          "enum": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
        },
        "occupancy_type": {
          "type": "string",
          "enum": ["primary_residence", "second_home", "investment_property"]
        }
      },
      "required": ["credit_score", "dti_ratio", "ltv_ratio", "loan_amount", "property_value", "loan_purpose", "property_type", "occupancy_type"]
    }
  },
  "required": ["underwriting_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "underwriting_decision": {
      "type": "string",
      "enum": ["APPROVED", "CONDITIONAL", "DENIED", "MANUAL_REVIEW"]
    },
    "risk_score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100
    },
    "risk_factors": {
      "type": "array",
      "items": {"type": "string"}
    },
    "mitigating_factors": {
      "type": "array",
      "items": {"type": "string"}
    },
    "conditions": {
      "type": "array",
      "items": {"type": "string"}
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "automated_decision": {
      "type": "boolean"
    },
    "manual_review_reasons": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### Tool 7: Evaluate Pricing Rules

**Tool Name**: `evaluate_pricing_rules`

**Description**: Evaluate loan pricing against pricing business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "pricing_data": {
      "type": "object",
      "properties": {
        "credit_score": {
          "type": "integer",
          "minimum": 300,
          "maximum": 850
        },
        "loan_amount": {
          "type": "number",
          "minimum": 0
        },
        "ltv_ratio": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "loan_purpose": {
          "type": "string",
          "enum": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
        },
        "property_type": {
          "type": "string",
          "enum": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
        },
        "occupancy_type": {
          "type": "string",
          "enum": ["primary_residence", "second_home", "investment_property"]
        },
        "down_payment_percent": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "lock_period": {
          "type": "integer",
          "minimum": 0,
          "description": "Rate lock period in days"
        }
      },
      "required": ["credit_score", "loan_amount", "ltv_ratio", "loan_purpose", "property_type", "occupancy_type"]
    }
  },
  "required": ["pricing_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "base_rate": {
      "type": "number"
    },
    "rate_adjustments": {
      "type": "array",
      "items": {"type": "object"}
    },
    "final_rate": {
      "type": "number"
    },
    "fees": {
      "type": "object",
      "description": "Dict with fee breakdown"
    },
    "total_fees": {
      "type": "number"
    },
    "apr": {
      "type": "number"
    },
    "pricing_tier": {
      "type": "string"
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### Tool 8: Check Compliance Rules

**Tool Name**: `check_compliance_rules`

**Description**: Check loan application against compliance business rules.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "compliance_data": {
      "type": "object",
      "properties": {
        "loan_amount": {
          "type": "number",
          "minimum": 0
        },
        "property_value": {
          "type": "number",
          "minimum": 0
        },
        "borrower_income": {
          "type": "number",
          "minimum": 0
        },
        "property_address": {
          "type": "string"
        },
        "loan_purpose": {
          "type": "string",
          "enum": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"]
        },
        "property_type": {
          "type": "string",
          "enum": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"]
        },
        "occupancy_type": {
          "type": "string",
          "enum": ["primary_residence", "second_home", "investment_property"]
        },
        "borrower_demographics": {
          "type": "object",
          "description": "Borrower demographic information"
        }
      },
      "required": ["loan_amount", "property_value", "borrower_income", "loan_purpose", "property_type", "occupancy_type"]
    }
  },
  "required": ["compliance_data"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "compliance_status": {
      "type": "string",
      "enum": ["COMPLIANT", "NON_COMPLIANT", "REQUIRES_REVIEW"]
    },
    "regulatory_checks": {
      "type": "object",
      "description": "Dict with regulatory check results"
    },
    "fair_lending_assessment": {
      "type": "object",
      "description": "Dict with fair lending analysis"
    },
    "privacy_compliance": {
      "type": "object",
      "description": "Dict with privacy regulation compliance"
    },
    "audit_trail_requirements": {
      "type": "array",
      "items": {"type": "string"}
    },
    "compliance_issues": {
      "type": "array",
      "items": {"type": "string"}
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

## Error Response Schema

All tools return errors in the following format:

```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "object",
      "properties": {
        "code": {
          "type": "string"
        },
        "message": {
          "type": "string"
        },
        "details": {
          "type": "object"
        }
      },
      "required": ["code", "message"]
    }
  }
}
```

## Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `RULES_NOT_FOUND`: Business rules not found in database
- `DATABASE_ERROR`: Database connection or query error
- `INTERNAL_ERROR`: Internal server error
- `TIMEOUT_ERROR`: Request timeout

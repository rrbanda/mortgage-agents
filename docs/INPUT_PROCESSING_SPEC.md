
# Input Processing Specification v1.0

## Purpose
Define how raw user input is converted to structured data BEFORE any business logic, agent reasoning, or tool execution occurs.

---

## Architecture Overview

```
User Input (Natural Language)
    ↓
Entry Point Parser ← YOU ARE HERE
    ↓
Structured Data (MortgageInput)
    ↓
Routing Logic
    ↓
Agent + Tools
```

---

## Scope: Entry Point Parser ONLY

### What This Layer Does:
 Extract entities from natural language  
 Validate data formats (SSN format, email format, etc.)  
 Convert to structured Pydantic model  
 Basic type coercion (string "720" → int 720)  
 Handle multiple input variations  

### What This Layer Does NOT Do:
 Apply business rules (DTI limits, LTV ratios)  
 Query Neo4j for rules  
 Calculate eligibility  
 Check document completeness  
 Validate against underwriting guidelines  
 Make qualification decisions  

**Rule of thumb**: If it requires domain knowledge or database access, it's NOT parsing.

---

## 1. Input Schema Definition

**File**: `agents/shared/schemas.py` (NEW FILE)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

class MortgageInput(BaseModel):
    """
    Universal input schema for mortgage processing.
    
    Scope: Data extraction and FORMAT validation only.
    All fields Optional to handle partial information.
    """
    
    # ==================== PERSONAL INFO ====================
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Borrower's first name"
    )
    
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Borrower's last name"
    )
    
    middle_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Borrower's middle name or initial"
    )
    
    # ==================== CONTACT INFO ====================
    phone: Optional[str] = Field(
        None,
        description="Phone number in format: xxx-xxx-xxxx"
    )
    
    email: Optional[str] = Field(
        None,
        description="Email address"
    )
    
    ssn: Optional[str] = Field(
        None,
        description="Social Security Number in format: xxx-xx-xxxx"
    )
    
    date_of_birth: Optional[str] = Field(
        None,
        description="Date of birth in format: YYYY-MM-DD"
    )
    
    # ==================== FINANCIAL INFO ====================
    credit_score: Optional[int] = Field(
        None,
        ge=300,
        le=850,
        description="Credit score between 300-850"
    )
    
    monthly_income: Optional[float] = Field(
        None,
        gt=0,
        description="Monthly gross income in dollars"
    )
    
    annual_income: Optional[float] = Field(
        None,
        gt=0,
        description="Annual gross income in dollars"
    )
    
    monthly_debts: Optional[float] = Field(
        None,
        ge=0,
        description="Total monthly debt payments in dollars"
    )
    
    liquid_assets: Optional[float] = Field(
        None,
        ge=0,
        description="Available liquid assets (checking, savings, investments)"
    )
    
    # ==================== LOAN INFO ====================
    loan_amount: Optional[float] = Field(
        None,
        gt=0,
        description="Requested loan amount in dollars"
    )
    
    loan_purpose: Optional[Literal[
        "purchase",
        "refinance", 
        "cash_out_refinance",
        "construction",
        "renovation"
    ]] = Field(None, description="Purpose of the loan")
    
    down_payment: Optional[float] = Field(
        None,
        ge=0,
        description="Down payment amount in dollars"
    )
    
    down_payment_percent: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Down payment as decimal (0.20 = 20%)"
    )
    
    # ==================== PROPERTY INFO ====================
    property_address: Optional[str] = Field(
        None,
        description="Full property address or street address"
    )
    
    property_value: Optional[float] = Field(
        None,
        gt=0,
        description="Property value or purchase price in dollars"
    )
    
    property_type: Optional[Literal[
        "single_family_detached",
        "condominium",
        "townhouse",
        "pud",
        "manufactured",
        "multi_family_2_4_units"
    ]] = Field(None, description="Type of property")
    
    occupancy_type: Optional[Literal[
        "primary_residence",
        "second_home",
        "investment_property"
    ]] = Field(None, description="How property will be used")
    
    # ==================== EMPLOYMENT INFO ====================
    employer_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Current employer name"
    )
    
    employment_type: Optional[Literal[
        "w2",
        "self_employed",
        "contract",
        "retired",
        "other"
    ]] = Field(None, description="Type of employment")
    
    years_employed: Optional[float] = Field(
        None,
        ge=0,
        description="Years at current employer"
    )
    
    job_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Current job title or position"
    )
    
    # ==================== ADDRESS DETAILS ====================
    current_street: Optional[str] = Field(None, description="Current street address")
    current_city: Optional[str] = Field(None, description="Current city")
    current_state: Optional[str] = Field(None, description="Current state (2-letter code)")
    current_zip: Optional[str] = Field(None, description="Current ZIP code")
    years_at_address: Optional[float] = Field(None, ge=0, description="Years at current address")
    
    # ==================== CONTEXT & METADATA ====================
    application_id: Optional[str] = Field(
        None,
        description="Existing application ID (e.g., APP_20250101_123456_SMI)"
    )
    
    intent: Optional[str] = Field(
        None,
        description="Classified user intent (apply, check_status, etc.)"
    )
    
    # ==================== SPECIAL FLAGS ====================
    first_time_buyer: bool = Field(
        False,
        description="True if first-time home buyer"
    )
    
    military_service: bool = Field(
        False,
        description="True if military service or veteran"
    )
    
    rural_property: bool = Field(
        False,
        description="True if property in rural area (USDA eligible)"
    )
    
    # ==================== FORMAT VALIDATORS ====================
    
    @validator('ssn')
    def validate_ssn_format(cls, v):
        """Validate SSN format: xxx-xx-xxxx"""
        if v is None:
            return v
        import re
        if not re.match(r'^\d{3}-\d{2}-\d{4}$', v):
            raise ValueError('SSN must be in format xxx-xx-xxxx')
        return v
    
    @validator('phone')
    def validate_phone_format(cls, v):
        """Validate phone format: xxx-xxx-xxxx"""
        if v is None:
            return v
        import re
        # Remove common separators and validate
        cleaned = v.replace(' ', '').replace('.', '').replace('-', '')
        if not re.match(r'^\d{10}$', cleaned):
            raise ValueError('Phone must be 10 digits')
        # Return in standard format
        return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
    
    @validator('email')
    def validate_email_format(cls, v):
        """Basic email format validation"""
        if v is None:
            return v
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Email must contain @ and domain')
        return v.lower()
    
    @validator('date_of_birth')
    def validate_dob_format(cls, v):
        """Validate date format: YYYY-MM-DD"""
        if v is None:
            return v
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Date of birth must be YYYY-MM-DD format')
        return v
    
    @validator('current_state')
    def validate_state_format(cls, v):
        """Validate state code: 2 letters"""
        if v is None:
            return v
        if len(v) != 2 or not v.isalpha():
            raise ValueError('State must be 2-letter code (e.g., CA, TX)')
        return v.upper()
    
    @validator('current_zip')
    def validate_zip_format(cls, v):
        """Validate ZIP code format"""
        if v is None:
            return v
        import re
        # Accept 5-digit or 9-digit (ZIP+4)
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('ZIP must be 5 digits or ZIP+4 format')
        return v
    
    @validator('down_payment_percent')
    def validate_down_payment_range(cls, v):
        """Ensure down payment percent is between 0 and 1"""
        if v is not None and not (0 <= v <= 1):
            raise ValueError('Down payment percent must be 0.0-1.0 (e.g., 0.20 for 20%)')
        return v
    
    @validator('annual_income', always=True)
    def calculate_annual_from_monthly(cls, v, values):
        """Auto-calculate annual income if only monthly provided"""
        if v is None and values.get('monthly_income'):
            return values['monthly_income'] * 12
        return v
    
    @validator('monthly_income', always=True)
    def calculate_monthly_from_annual(cls, v, values):
        """Auto-calculate monthly income if only annual provided"""
        if v is None and values.get('annual_income'):
            return values['annual_income'] / 12
        return v
    
    # ==================== COMPUTED PROPERTIES ====================
    
    @property
    def calculated_loan_amount(self) -> Optional[float]:
        """Calculate loan amount from property value and down payment"""
        if self.property_value and self.down_payment_percent:
            return self.property_value * (1 - self.down_payment_percent)
        return self.loan_amount
    
    @property
    def calculated_down_payment(self) -> Optional[float]:
        """Calculate down payment from property value and percent"""
        if self.property_value and self.down_payment_percent:
            return self.property_value * self.down_payment_percent
        return self.down_payment
    
    @property
    def full_name(self) -> Optional[str]:
        """Construct full name from parts"""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p)
    
    @property
    def is_complete(self) -> bool:
        """Check if essential fields are present (format check only)"""
        essential = [
            self.first_name,
            self.last_name,
            self.phone,
            self.email
        ]
        return all(essential)
    
    class Config:
        extra = "allow"  # Allow additional fields
        use_enum_values = True
        validate_assignment = True
```

---

## 2. Parser Implementation

**File**: `agents/shared/input_parser.py` (MODIFY EXISTING)

Add this class at the TOP of the file:

```python
import logging
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from pydantic import ValidationError
from .schemas import MortgageInput

logger = logging.getLogger(__name__)

class UnifiedInputParser:
    """
    Primary input parser using LLM extraction with regex fallback.
    
    Strategy:
    1. Try LLM-based extraction (best for natural language variations)
    2. Fall back to regex extraction (reliable for structured formats)
    3. Always validate with Pydantic (ensures data quality)
    
    Examples of inputs handled:
    - "Sarah Johnson, 720 credit, wants $400k loan"
    - "John Smith applying for mortgage, income $8000/month, SSN 123-45-6789"
    - "Check status of application APP_20250101_123456_SMI"
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize parser.
        
        Args:
            use_llm: If True, use LLM for parsing. If False, use regex only.
        """
        self.use_llm = use_llm
        if use_llm:
            self.llm = ChatAnthropic(
                model="claude-sonnet-4",
                temperature=0  # Deterministic output
            )
            self.pydantic_parser = PydanticOutputParser(pydantic_object=MortgageInput)
    
    def parse(self, text: str) -> MortgageInput:
        """
        Main parsing entry point.
        
        Args:
            text: Raw natural language input from user
            
        Returns:
            MortgageInput: Validated, structured data
            
        Raises:
            ValidationError: If critical format validation fails
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        try:
            if self.use_llm:
                return self._llm_parse(text)
            else:
                return self._regex_fallback(text)
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}, trying regex fallback")
            return self._regex_fallback(text)
    
    def _llm_parse(self, text: str) -> MortgageInput:
        """
        Primary parsing using LLM extraction.
        
        Advantages:
        - Handles casual language ("my credit is around 720")
        - Understands context ("buying my first house")
        - Recognizes variations ("300k" = 300000)
        """
        prompt_template = """Extract mortgage application information from the user's message.

{format_instructions}

User Message:
{text}

Instructions:
- Extract ALL available information
- Use null for missing fields
- Convert "k" notation to full numbers (300k = 300000)
- Convert annual income to monthly (divide by 12)
- Recognize casual language patterns
- Extract employer name if mentioned
- Identify loan purpose from context
- Set boolean flags based on keywords (first time buyer, military, rural)

Output only valid JSON matching the schema above."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"],
            partial_variables={
                "format_instructions": self.pydantic_parser.get_format_instructions()
            }
        )
        
        chain = prompt | self.llm | self.pydantic_parser
        result = chain.invoke({"text": text})
        
        logger.info(f"LLM parsing successful. Extracted: {result.dict(exclude_none=True)}")
        return result
    
    def _regex_fallback(self, text: str) -> MortgageInput:
        """
        Fallback to existing regex-based parsing.
        
        Uses: Existing parse_complete_mortgage_input() function
        """
        # Import existing parser
        parsed_dict = parse_complete_mortgage_input(text)
        
        # Convert dict to MortgageInput with validation
        try:
            return MortgageInput(**parsed_dict)
        except ValidationError as e:
            logger.error(f"Validation errors: {e}")
            # Return with partial data, invalid fields removed
            valid_fields = {}
            for field, value in parsed_dict.items():
                try:
                    # Try to validate individual field
                    test_model = MortgageInput(**{field: value})
                    valid_fields[field] = value
                except ValidationError:
                    logger.warning(f"Skipping invalid field {field}={value}")
            
            return MortgageInput(**valid_fields)
```

**KEEP all existing functions below this class** (they become the regex fallback)

---

## 3. Testing Requirements

**File**: `tests/test_input_parsing.py` (NEW FILE)

```python
import pytest
from agents.shared.input_parser import UnifiedInputParser
from agents.shared.schemas import MortgageInput
from pydantic import ValidationError

class TestMortgageInputSchema:
    """Test Pydantic schema validation"""
    
    def test_valid_complete_input(self):
        """Test schema with all fields"""
        data = MortgageInput(
            first_name="John",
            last_name="Smith",
            ssn="123-45-6789",
            phone="555-123-4567",
            email="john@example.com",
            credit_score=720,
            monthly_income=8000,
            loan_amount=400000,
            property_value=500000
        )
        assert data.first_name == "John"
        assert data.credit_score == 720
    
    def test_ssn_format_validation(self):
        """SSN must be xxx-xx-xxxx format"""
        with pytest.raises(ValidationError, match="SSN must be in format"):
            MortgageInput(ssn="invalid")
        
        with pytest.raises(ValidationError):
            MortgageInput(ssn="123456789")  # Missing dashes
    
    def test_credit_score_range(self):
        """Credit score must be 300-850"""
        with pytest.raises(ValidationError):
            MortgageInput(credit_score=900)  # Too high
        
        with pytest.raises(ValidationError):
            MortgageInput(credit_score=200)  # Too low
    
    def test_phone_normalization(self):
        """Phone numbers should be normalized"""
        data = MortgageInput(phone="5551234567")
        assert data.phone == "555-123-4567"
    
    def test_computed_properties(self):
        """Test calculated fields"""
        data = MortgageInput(
            property_value=500000,
            down_payment_percent=0.20
        )
        assert data.calculated_loan_amount == 400000
        assert data.calculated_down_payment == 100000

class TestUnifiedInputParser:
    """Test parser functionality"""
    
    def test_basic_parsing(self):
        """Test parsing simple input"""
        parser = UnifiedInputParser(use_llm=False)  # Use regex for speed
        result = parser.parse("Sarah Johnson, credit 720, wants $400k loan")
        
        assert isinstance(result, MortgageInput)
        assert result.first_name == "Sarah"
        assert result.last_name == "Johnson"
        assert result.credit_score == 720
    
    def test_empty_input(self):
        """Empty input should raise error"""
        parser = UnifiedInputParser()
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse("")
    
    def test_partial_information(self):
        """Parser should handle incomplete data"""
        parser = UnifiedInputParser(use_llm=False)
        result = parser.parse("John Smith, 720 credit")
        
        assert result.first_name == "John"
        assert result.credit_score == 720
        assert result.loan_amount is None  # Not provided

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 4. Integration Pattern

**Example: LangGraph Node**

```python
from agents.shared.input_parser import UnifiedInputParser
from agents.shared.schemas import MortgageInput

def parse_input_node(state: dict) -> dict:
    """
    First node in graph - parses raw input.
    
    Responsibilities:
    - Extract structured data
    - Validate formats
    - Handle parsing errors gracefully
    
    Does NOT:
    - Apply business rules
    - Query database
    - Make decisions
    """
    parser = UnifiedInputParser()
    
    try:
        parsed_data = parser.parse(state["raw_input"])
        
        return {
            **state,
            "parsed_data": parsed_data,
            "parse_error": None,
            "ready_for_routing": True
        }
        
    except ValidationError as e:
        # Format validation failed
        return {
            **state,
            "parsed_data": None,
            "parse_error": f"Invalid input format: {e}",
            "ready_for_routing": False
        }
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Parsing failed: {e}")
        return {
            **state,
            "parsed_data": None,
            "parse_error": "Unable to understand input. Please provide more information.",
            "ready_for_routing": False
        }
```

---

## 5. Migration Checklist

### Phase 1: Create Foundation
- [ ] Create `agents/shared/schemas.py` with `MortgageInput`
- [ ] Add all validators to schema
- [ ] Test schema validation independently
- [ ] Verify all current fields are captured

### Phase 2: Add Parser Class
- [ ] Add `UnifiedInputParser` to top of `input_parser.py`
- [ ] Keep all existing regex functions as fallback
- [ ] Test LLM parsing with sample inputs
- [ ] Test regex fallback

### Phase 3: Update Entry Point
- [ ] Make `parse_input_node` first node in LangGraph
- [ ] Update state to include `parsed_data: MortgageInput`
- [ ] Test full graph with new parser

### Phase 4: Validate
- [ ] Run all tests
- [ ] Verify parsing accuracy >= 95%
- [ ] Check fallback triggers correctly
- [ ] Ensure no business logic in parser

---

## 6. Success Criteria

 `MortgageInput` schema compiles without errors  
 All validators work correctly  
 LLM parsing handles casual language  
 Regex fallback works when LLM unavailable  
 Format validation catches bad data early  
 NO business rules in parsing layer  
 Tests pass with >90% coverage  
 Downstream nodes receive structured data  

---

## 7. Common Pitfalls to Avoid

 **DON'T** add business logic to validators  
```python
# WRONG - This is business logic
@validator('credit_score')
def check_program_eligibility(cls, v):
    if v < 620:
        raise ValueError("Doesn't qualify for conventional")
```

 **DON'T** query database in parser  
```python
# WRONG - Database queries belong in tools
def parse(self, text):
    rules = query_neo4j("MATCH (r:Rule)...")  # NO!
```

 **DON'T** make fields required prematurely  
```python
# WRONG - User might provide partial info
first_name: str = Field(...)  # Makes it required

# RIGHT - Allow partial data
first_name: Optional[str] = Field(None)
```

 **DO** keep it simple - just extraction and format validation

---

## End of Specification

For output processing specification, see: `OUTPUT_PROCESSING_SPEC.md`
```


"""
Standardized Input Parsing Library for Mortgage Agents

This module provides robust, standardized parsing functions to replace
the fragmented regex patterns scattered across all agent tools.

Key Benefits:
- Handles multiple input formats automatically
- Consistent parsing across all agents  
- Robust error handling with sensible defaults
- Easily extensible for new formats
"""

import re
from typing import Optional, Union, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedData:
    """Container for parsed data with metadata about parsing success"""
    value: Any
    confidence: float  # 0.0 to 1.0
    source_pattern: str
    raw_input: str


class StandardInputParser:
    """Standardized parser for mortgage application data"""
    
    @staticmethod
    def parse_name(text: str) -> Dict[str, Optional[str]]:
        """Parse full name into components - DEMO-FRIENDLY with flexible patterns"""
        patterns = [
            # High-confidence patterns (try these first)
            r"(?:name|i'm|i am)\s*(?:is\s*)?:?\s*([a-zA-Z]+\s+[a-zA-Z]+)",  # "I'm John Smith"
            r"(?:application\s+for|mortgage\s+for)\s+([a-zA-Z]+\s+[a-zA-Z]+)",  # "mortgage for john smith"  
            r"([a-zA-Z]+\s+[a-zA-Z]+),\s*(?:DOB|SSN|phone|email)",  # "John Smith, DOB:"
            r"(?:borrower|applicant|customer):\s*([a-zA-Z]+\s+[a-zA-Z]+)",  # "borrower: John Smith"
            
            # Demo-friendly patterns (more flexible, case insensitive)
            r"(?:for|apply)\s+(?:mortgage\s+)?([a-zA-Z]+\s+[a-zA-Z]+)(?:\s+(?:wants|needs|credit|with|income))",  # "apply john smith wants"
            r"(?:hey\s+)?(?:i'm|im)\s+([a-zA-Z]+\s+[a-zA-Z]+)",  # "hey im mike jones"
            r"^([a-zA-Z]+\s+[a-zA-Z]+)(?:\s+(?:wants|needs|applying|mortgage))",  # "john smith wants mortgage"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                full_name = match.group(1).strip()
                name_parts = full_name.split()
                
                result = {
                    "first_name": name_parts[0] if name_parts else None,
                    "last_name": name_parts[-1] if len(name_parts) > 1 else None,
                    "middle_name": " ".join(name_parts[1:-1]) if len(name_parts) > 2 else None,
                    "full_name": full_name
                }
                return result
        
        return {"first_name": None, "last_name": None, "middle_name": None, "full_name": None}
    
    @staticmethod
    def parse_credit_score(text: str) -> Optional[int]:
        """Parse credit score - DEMO-FRIENDLY with casual language"""
        patterns = [
            # Standard patterns
            r'credit\s*(?:score)?\s*(?:is|of|:)?\s*(\d{3})',
            r'credit[:\s]+(\d{3})',
            r'score[:\s]+(\d{3})',
            r'fico[:\s]+(\d{3})',
            
            # Demo-friendly casual patterns
            r'(?:my\s+)?credit\s+(?:is\s+)?(?:around\s+|about\s+)?(\d{3})',  # "my credit is around 720"
            r'(?:credit\s+)?score\s+(?:is\s+)?(?:around\s+|about\s+)?(\d{3})',  # "score is about 720"
            r'(?:have\s+)?(?:a\s+)?(\d{3})\s+credit(?:\s+score)?',  # "have a 720 credit score"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 300 <= score <= 850:  # Valid credit score range
                    return score
        return None
    
    @staticmethod
    def _parse_income_smart(text: str) -> Optional[float]:
        """Smart income parsing that distinguishes annual vs monthly and normalizes to monthly"""
        text_lower = text.lower()
        
        # Explicit annual income patterns - convert to monthly
        annual_patterns = [
            r'(?:annual|yearly)\s*income\s*(?:is|of|:)?\s*\$?([0-9,]+)',
            r'(?:making|earn|make)\s*\$?([0-9,]+)(?:\s*/?\s*year|/year|/yr|\s*annually|\s*per\s*year)',
            r'salary\s*(?:is|of|:)?\s*\$?([0-9,]+)(?:\s*/?\s*year|/year|/yr|\s*annually|\s*per\s*year)?',
            r'income\s*\$?([0-9,]+)(?:\s*/?\s*year|/year|/yr|\s*annually|\s*per\s*year)',
        ]
        
        for pattern in annual_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    annual_amount = float(match.group(1).replace(',', ''))
                    return annual_amount / 12  # Convert to monthly
                except ValueError:
                    continue
        
        # Explicit monthly income patterns - return as-is
        monthly_patterns = [
            r'monthly\s*income\s*(?:is|of|:)?\s*\$?([0-9,]+)',
            r'(?:making|earn|income)\s*\$?([0-9,]+)(?:\s*/?\s*month|/month|/mo|\s*monthly|\s*per\s*month)',
            # Demo-friendly casual patterns
            r'(?:i\s+)?(?:make|earn)\s+(?:about\s+|around\s+)?\$?([0-9]+)k?\s+(?:per\s+month|monthly|a\s+month)',  # "i make about 5k per month"
            r'(?:making|earning)\s+(?:about\s+|around\s+)?\$?([0-9]+)k?\s+(?:each\s+month|monthly)',  # "making about 5k monthly"
        ]
        
        for pattern in monthly_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    # Handle "k" notation in casual monthly income (5k = 5000)
                    if 'k' in pattern and amount < 100:  # If it's a "k" pattern and small number
                        amount = amount * 1000
                    return amount
                except ValueError:
                    continue
        
        # Ambiguous income patterns - assume annual and convert to monthly
        # This handles cases like "Income: 95000" which are typically annual salaries
        ambiguous_patterns = [
            r'income\s*(?:is|of|:)?\s*\$?([0-9,]+)',
            r'(?:making|earn)\s*\$?([0-9,]+)(?!\s*/?\s*(?:month|mo|monthly))',
        ]
        
        for pattern in ambiguous_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    # Heuristic: if amount > 15000, likely annual; otherwise monthly
                    if amount > 15000:
                        return amount / 12  # Convert annual to monthly
                    else:
                        return amount  # Assume monthly
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse_currency(text: str, field_name: str) -> Optional[float]:
        """Parse currency amounts - handles multiple formats"""
        # Special handling for income to distinguish annual vs monthly
        if field_name == "income":
            return StandardInputParser._parse_income_smart(text)
        
        # Create field-specific patterns for non-income fields
        field_patterns = {
            "loan": [
                r'loan\s*(?:amount|for)?\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'loan[:\s]+(\d+)',
            ],
            "down_payment": [
                r'(?:down\s*payment)\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'down[:\s]+(\d+)',
            ],
            "debts": [
                r'(?:monthly\s*)?debt(?:s)?\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'debts[:\s]+(\d+)',
            ],
            "assets": [
                r'(?:assets?|savings?|cash)\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'assets[:\s]+(\d+)',
            ]
        }
        
        patterns = field_patterns.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def parse_property_details(text: str) -> Dict[str, Any]:
        """Parse property details - handles multiple formats"""
        result = {
            "address": None,
            "property_type": None,
            "bedrooms": None,
            "bathrooms": None,
            "square_feet": None,
            "year_built": None,
            "property_value": None
        }
        
        # Address patterns
        address_patterns = [
            r'(?:address|property|located):\s*([^,\n]+(?:,\s*[^,\n]+)*)',
            r'(?:at|on)\s+([^,\n]+(?:,\s*[^,\n]+)*)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["address"] = match.group(1).strip()
                break
        
        # Property type
        type_patterns = [
            r'type:\s*([a-z_]+)',
            r'(single[\s_]family|condominium|townhouse|multi[\s_]family)',
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["property_type"] = match.group(1).lower().replace(' ', '_')
                break
        
        # Bedrooms - multiple formats
        bedroom_patterns = [
            r'(?:bedrooms?:\s*(\d+)|(\d+)\s*bed)',
            r'(\d+)\s*br',
            r'(\d+)\s*bedroom',
        ]
        
        for pattern in bedroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["bedrooms"] = int(match.group(1) or match.group(2))
                break
        
        # Bathrooms - multiple formats  
        bathroom_patterns = [
            r'(?:bathrooms?:\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*bath)',
            r'(\d+(?:\.\d+)?)\s*ba',
            r'(\d+(?:\.\d+)?)\s*bathroom',
        ]
        
        for pattern in bathroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["bathrooms"] = float(match.group(1) or match.group(2))
                break
        
        # Square feet
        sqft_patterns = [
            r'(?:sqft|sq\.?\s*ft|square\s*feet?):\s*(\d+)',
            r'(\d+)\s*(?:sqft|sq\.?\s*ft|square\s*feet?)',
        ]
        
        for pattern in sqft_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["square_feet"] = int(match.group(1))
                break
        
        # Year built
        year_patterns = [
            r'(?:built|year):\s*(\d{4})',
            r'built\s+in\s+(\d{4})',
            r'(\d{4})\s*built',
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 1800 <= year <= 2030:  # Reasonable year range
                    result["year_built"] = year
                break
        
        # Property value
        value_patterns = [
            r'(?:value|worth|price):\s*\$?([0-9,]+)',
            r'property[^0-9]*(\d+)',
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result["property_value"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue
        
        return result
    
    @staticmethod
    def parse_contact_info(text: str) -> Dict[str, Optional[str]]:
        """Parse contact information - handles multiple formats"""
        result = {
            "phone": None,
            "email": None,
            "ssn": None,
            "date_of_birth": None
        }
        
        # Phone patterns - DEMO-FRIENDLY
        phone_patterns = [
            r'phone\s*(?:number)?\s*(?:is|:)?\s*(\d{3}[-.]\d{3}[-.]\d{4})',
            r'(\d{3}[-.]\d{3}[-.]\d{4})',
            # Demo-friendly casual patterns  
            r'(?:call\s+me\s+at|phone\s+is|my\s+number\s+is)\s+([0-9\s\-\.]{10,})',  # "call me at 555 123 4567"
            r'(?:reach\s+me\s+at|contact\s+at)\s+([0-9\s\-\.]{10,})',  # flexible spacing
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["phone"] = match.group(1).replace('.', '-')
                break
        
        # Email patterns
        email_patterns = [
            r'email\s*(?:address)?\s*(?:is|:)?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["email"] = match.group(1)
                break
        
        # SSN patterns - DEMO-FRIENDLY
        ssn_patterns = [
            r'ssn\s*(?:is|:)?\s*(\d{3}-\d{2}-\d{4})',
            r'social\s*security\s*(?:number)?\s*(?:is|:)?\s*(\d{3}-\d{2}-\d{4})',
            # Demo-friendly casual patterns
            r'(?:my\s+)?social\s+(?:is\s+)?(\d{3}-\d{2}-\d{4})',  # "social is 123-45-6789"
            r'ssn\s+(\d{3}-\d{2}-\d{4})',  # "ssn 123-45-6789"
        ]
        
        for pattern in ssn_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["ssn"] = match.group(1)
                break
        
        # Date of birth patterns
        dob_patterns = [
            r'(?:birth|dob|born)\s*(?:date|on)?\s*(?:is|:)?\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Convert MM/DD/YYYY to YYYY-MM-DD if needed
                if '/' in date_str or '-' in date_str and len(date_str.split('-')[2]) == 4:
                    try:
                        parts = date_str.replace('/', '-').split('-')
                        if len(parts) == 3 and len(parts[2]) == 4:
                            result["date_of_birth"] = f"{parts[2]}-{parts[0]:0>2}-{parts[1]:0>2}"
                        else:
                            result["date_of_birth"] = date_str
                    except:
                        result["date_of_birth"] = date_str
                else:
                    result["date_of_birth"] = date_str
                break
        
        return result


# Convenience functions for common use cases
def parse_mortgage_application(text: str) -> Dict[str, Any]:
    """Parse complete mortgage application text with smart calculations"""
    parser = StandardInputParser()
    
    result = {}
    result.update(parser.parse_name(text))
    result.update(parser.parse_contact_info(text))
    result.update(parser.parse_property_details(text))
    
    # Financial information
    result["credit_score"] = parser.parse_credit_score(text)
    result["monthly_income"] = parser.parse_currency(text, "income")
    result["loan_amount"] = parser.parse_currency(text, "loan")
    result["down_payment"] = parser.parse_currency(text, "down_payment")
    result["monthly_debts"] = parser.parse_currency(text, "debts")
    result["liquid_assets"] = parser.parse_currency(text, "assets")
    
    # Calculate derived fields (safe calculation)
    if result.get("monthly_income"):
        try:
            result["annual_income"] = result["monthly_income"] * 12
        except (TypeError, ValueError):
            result["annual_income"] = None
    
    # Calculate down payment percentage (safe calculation)
    if result.get("down_payment") and result.get("property_value"):
        try:
            result["down_payment_percent"] = result["down_payment"] / result["property_value"]
        except (TypeError, ZeroDivisionError):
            result["down_payment_percent"] = None
    
    # Calculate DTI ratios (if we have housing payment info)
    # Note: Housing payment would need to be parsed from specific input
    # For now, we'll add a placeholder for tools to calculate
    result["needs_dti_calculation"] = True
    
    return result


def calculate_dti_ratios(monthly_income: float, housing_payment: float, monthly_debts: float = 0) -> Dict[str, float]:
    """Calculate front-end and back-end DTI ratios"""
    if monthly_income <= 0:
        return {"front_end_dti": 0.0, "back_end_dti": 0.0}
    
    front_end_dti = (housing_payment / monthly_income) * 100
    back_end_dti = ((housing_payment + monthly_debts) / monthly_income) * 100
    
    return {
        "front_end_dti": round(front_end_dti, 1),
        "back_end_dti": round(back_end_dti, 1),
        "front_end_ratio": round(front_end_dti / 100, 3),
        "back_end_ratio": round(back_end_dti / 100, 3)
    }


def validate_parsed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean parsed data"""
    cleaned = {}
    
    for key, value in data.items():
        if value is not None and value != "":
            cleaned[key] = value
    
    return cleaned


# Enhanced parsing functions to eliminate all regex dependency
def parse_application_id(text: str) -> Optional[str]:
    """Parse application IDs like APP_20250930_134209_MAR"""
    import re
    patterns = [
        r'(APP_\d{8}_\d{6}_[A-Z]{3})',  # Full format
        r'(APP_[A-Z0-9_]+)',            # General APP format
        r'application[:\s]+([A-Z0-9_]+)', # Application: APP_123
        r'app[:\s]+([A-Z0-9_]+)',       # app: APP_123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def parse_structured_parameters(text: str) -> Dict[str, Any]:
    """Parse structured parameters like 'Application: APP_123, Loan: purchase'"""
    import re
    result = {}
    
    # Common parameter patterns
    parameter_patterns = {
        'application_id': [r'(?:application|app)[:\s]+([A-Z0-9_]+)'],
        'loan_type': [r'loan[:\s]+([a-z_]+)'],
        'employment_type': [r'employment[:\s]+([a-z_]+)'],
        'property_type': [r'property[:\s]+([a-z_]+)'],
        'occupancy_type': [r'occupancy[:\s]+([a-z_]+)'],
        'document_type': [r'type[:\s]+([a-z_]+)'],
        'status_filter': [r'status[:\s]+([a-z_]+)'],
    }
    
    text_lower = text.lower()
    
    for param_name, patterns in parameter_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                result[param_name] = match.group(1)
                break
    
    # Boolean flags
    boolean_flags = {
        'co_borrower': ['co-borrower: yes', 'co-borrower: true', 'has co-borrower'],
        'first_time_buyer': ['first time', 'first-time'],
        'military_service': ['military', 'veteran', 'va eligible'],
        'rural_property': ['rural', 'usda eligible'],
    }
    
    for flag_name, triggers in boolean_flags.items():
        result[flag_name] = any(trigger in text_lower for trigger in triggers)
    
    return result


def parse_intent_classification(text: str) -> Dict[str, Any]:
    """Classify user intent from natural language"""
    text_lower = text.lower().strip()
    
    intent_patterns = {
        'check_status': [
            'check status', 'track status', 'status of', 'what is the status',
            'status check', 'application status', 'where is my application'
        ],
        'apply_mortgage': [
            'apply for mortgage', 'start application', 'mortgage application',
            'want to apply', 'apply for loan', 'get a mortgage'
        ],
        'get_documents': [
            'what documents', 'document requirements', 'what do i need',
            'required documents', 'documentation needed'
        ],
        'check_qualification': [
            'qualify for', 'do i qualify', 'qualification check',
            'am i eligible', 'can i get approved'
        ],
        'loan_programs': [
            'loan programs', 'what loans', 'loan options', 'available programs',
            'types of loans', 'loan products'
        ],
        'extract_document': [
            'extract from', 'process document', 'analyze document',
            'read document', 'get data from'
        ]
    }
    
    result = {'intent': 'general_inquiry', 'confidence': 0.5}
    
    for intent, triggers in intent_patterns.items():
        for trigger in triggers:
            if trigger in text_lower:
                result['intent'] = intent
                result['confidence'] = 0.9
                break
        if result['confidence'] > 0.8:
            break
    
    return result


def parse_complete_mortgage_input(text: str) -> Dict[str, Any]:
    """Complete parser that handles ALL mortgage agent input types - eliminates regex dependency"""
    # Start with base mortgage application parsing
    result = parse_mortgage_application(text)
    
    # Add application ID parsing
    app_id = parse_application_id(text)
    if app_id:
        result['application_id'] = app_id
    
    # Add structured parameters
    structured_params = parse_structured_parameters(text)
    result.update(structured_params)
    
    # Add intent classification
    intent_info = parse_intent_classification(text)
    result.update(intent_info)
    
    # Enhanced monetary value extraction (CRITICAL FIX)
    monetary_values = parse_monetary_values_enhanced(text)
    result.update(monetary_values)
    
    # Additional context parsing for tools
    # Enhanced employer extraction - DEMO-FRIENDLY (safe patterns to avoid blunders)
    employer_patterns = [
        r'(?:work\s+at|employed\s+at|job\s+at)\s+([A-Za-z][A-Za-z0-9\s&\.]{2,30})',  # "work at Google"
        r'(?:i\s+work\s+for|employed\s+by)\s+([A-Za-z][A-Za-z0-9\s&\.]{2,30})',  # "i work for Microsoft"
        r'(?:im\s+a\s+\w+\s+at)\s+([A-Za-z][A-Za-z0-9\s&\.]{2,30})',  # "im a developer at Apple"
        r'(?:software\s+developer\s+at|engineer\s+at|developer\s+at)\s+([A-Za-z][A-Za-z0-9\s&\.]{2,30})',  # "software developer at Google"
    ]
    
    for pattern in employer_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            employer_candidate = match.group(1).strip().title()
            # Safety check: avoid extracting common words as employers
            excluded_words = ['The', 'A', 'An', 'My', 'This', 'That', 'Home', 'Work', 'Software', 'Developer', 'Engineer']
            if employer_candidate not in excluded_words and len(employer_candidate.split()) <= 4:
                result['employer_name'] = employer_candidate
                break
    
    # SURGICAL FIX: Safe loan purpose detection for 100% demo-friendliness  
    if not result.get("loan_purpose"):
        text_lower = text.lower()
        # Safe loan purpose detection (context-aware to prevent blunders)
        if any(phrase in text_lower for phrase in ['buying my first house', 'buying a house', 'buying my house', 'first house', 'new home']):
            result["loan_purpose"] = "purchase"
        elif 'purchase' in text_lower and any(word in text_lower for word in ['home', 'house', 'property']):
            result["loan_purpose"] = "purchase"
        elif any(phrase in text_lower for phrase in ['refinance', 'refi', 'lower rate', 'better rate']):
            result["loan_purpose"] = "refinance"
    
    result['original_input'] = text
    result['parsed_timestamp'] = datetime.now().isoformat()
    
    return result


def parse_monetary_values_enhanced(text: str) -> Dict[str, Any]:
    """Enhanced monetary value extraction for property values, loan amounts, income, etc."""
    result = {}
    text_lower = text.lower()
    
    # Extract property values using simple string searching
    import re
    
    # DEMO-FRIENDLY property value patterns (handles k notation, flexible formats)
    property_patterns = [
        # Standard formats
        r'\$([0-9,]+)(?:\s*(?:home|property|house))',  # $450,000 home
        r'(?:at\s+a\s*|looking\s+at\s*)\$([0-9,]+)(?:\s*(?:home|property|house))?',  # at a $425,000 property
        r'(?:looking\s+at\s+a\s+)([0-9,]+)(?:\s*(?:property|home|house))',  # looking at a 425000 property
        
        # Demo-friendly "k" notation 
        r'([0-9]+)k(?:\s+(?:home|house|property))',  # 300k house
        r'(?:for|need|want).*?([0-9]+)k(?:\s+(?:home|house|property))',  # need 250k home
        r'([0-9]+)k(?:\s+(?:loan|mortgage))',  # 300k loan
        
        # Flexible formats
        r'([0-9,]+)(?:\s+(?:property|home|house))',  # 425000 property
        r'(?:worth|cost|price)\s*([0-9,]+)',  # worth 400000
        r'\$([0-9,]+)'  # Any dollar amount as fallback
    ]
    
    for pattern in property_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_text = match.group(1).replace(',', '')
                amount = float(amount_text)
                
                # Handle "k" notation (convert 300k to 300000)
                if 'k' in pattern and amount < 10000:  # If it's a "k" pattern and small number
                    amount = amount * 1000
                
                if 50000 <= amount <= 5000000:  # Reasonable property range
                    result['property_value'] = amount
                    break
            except:
                continue
    
    # Extract down payment percentages
    down_payment_patterns = [
        r'(\d+)%\s*down',  # 15% down
        r'with\s+(\d+)%\s+down',  # with 15% down
        r'(\d+)\s*percent\s*down'  # 15 percent down
    ]
    
    for pattern in down_payment_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                percent_num = float(match.group(1))
                if 3 <= percent_num <= 50:  # 3% to 50% down payment range
                    result['down_payment_percent'] = percent_num / 100
                    break
            except:
                continue
    
    # Calculate loan amount if we have property value and down payment
    if result.get('property_value') and result.get('down_payment_percent'):
        property_val = result['property_value']
        down_percent = result['down_payment_percent']
        result['loan_amount'] = property_val * (1 - down_percent)
        result['down_payment'] = property_val * down_percent
    elif result.get('property_value'):
        # Default to 80% LTV if no down payment specified
        property_val = result['property_value']
        result['loan_amount'] = property_val * 0.8
        result['down_payment'] = property_val * 0.2
        result['down_payment_percent'] = 0.2
    
    return result

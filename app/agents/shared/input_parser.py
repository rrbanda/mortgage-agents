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
        """Parse full name into components - handles multiple formats"""
        patterns = [
            r"(?:-\s*)?(?:name|i'm|i am)\s*(?:is\s*)?:?\s*([a-zA-Z]+(?:\s+[a-zA-Z]+)*)",
            r"(?:borrower|applicant|customer):\s*([a-zA-Z]+(?:\s+[a-zA-Z]+)*)",
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # Direct name format
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
        """Parse credit score - handles multiple formats"""
        patterns = [
            r'credit\s*(?:score)?\s*(?:is|of|:)?\s*(\d{3})',
            r'credit[:\s]+(\d{3})',
            r'score[:\s]+(\d{3})',
            r'fico[:\s]+(\d{3})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 300 <= score <= 850:  # Valid credit score range
                    return score
        return None
    
    @staticmethod
    def parse_currency(text: str, field_name: str) -> Optional[float]:
        """Parse currency amounts - handles multiple formats"""
        # Create field-specific patterns
        field_patterns = {
            "income": [
                r'(?:monthly\s*)?income\s*(?:is|of|:)?\s*\$?([0-9,]+)(?:\s*/?\s*month)?',
                r'(?:annual|yearly)\s*income\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'salary\s*(?:is|of|:)?\s*\$?([0-9,]+)',
                r'income[:\s]+(\d+)',
            ],
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
        
        # Phone patterns
        phone_patterns = [
            r'phone\s*(?:number)?\s*(?:is|:)?\s*(\d{3}[-.]\d{3}[-.]\d{4})',
            r'(\d{3}[-.]\d{3}[-.]\d{4})',
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
        
        # SSN patterns
        ssn_patterns = [
            r'ssn\s*(?:is|:)?\s*(\d{3}-\d{2}-\d{4})',
            r'social\s*security\s*(?:number)?\s*(?:is|:)?\s*(\d{3}-\d{2}-\d{4})',
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
    """Parse complete mortgage application text"""
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
    
    return result


def validate_parsed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean parsed data"""
    cleaned = {}
    
    for key, value in data.items():
        if value is not None and value != "":
            cleaned[key] = value
    
    return cleaned

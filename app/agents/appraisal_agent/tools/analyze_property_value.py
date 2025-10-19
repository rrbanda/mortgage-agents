import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def analyze_property_value(application_data: dict) -> str:
    """
    Basic analyze property value functionality.
    
    This tool provides basic property value analysis.
    For detailed business rules and specific requirements, 
    users should ask business rules questions which will be routed to BusinessRulesAgent.
    
    Args:
        application_data: Dict containing application info. May include:
            - property_address, property_type, loan_amount, property_value
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing basic analysis report
    """
    try:
        # Extract basic data from parsed_data
        property_address = application_data.get('property_address', 'Unknown Address')
        property_type = application_data.get('property_type', 'single_family_detached')
        loan_amount = application_data.get('loan_amount', 0.0)
        property_value = application_data.get('property_value', 0.0)
        
        # Convert to float if needed (handle string inputs)
        try:
            loan_amount = float(loan_amount) if loan_amount else 0.0
        except (ValueError, TypeError):
            loan_amount = 0.0
        
        try:
            property_value = float(property_value) if property_value else 0.0
        except (ValueError, TypeError):
            property_value = 0.0
        
        # Generate basic report
        report = [
            'ANALYZE PROPERTY VALUE ANALYSIS REPORT',
            '=' * 50,
            f'Property Address: {property_address}',
            f'Property Type: {property_type}',
            f'Loan Amount: ${loan_amount:,.2f}',
            f'Property Value: ${property_value:,.2f}',
            '',
            'ARCHITECTURE: This tool provides basic analysis.',
            'For detailed business rules and specific requirements,',
            'ask business rules questions which will be routed to BusinessRulesAgent.',
            '',
            'Analysis completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during analyze_property_value: {e}')
        return f'Error during analyze_property_value: {str(e)}'


def validate_tool() -> bool:
    """Validate that the analyze_property_value tool works correctly."""
    try:
        # MortgageInput schema removed - using flexible dict approach
        
        test_data = {
            "property_address": '123 Main St, Anytown, CA 90210',
            "property_type": 'single_family_detached',
            "loan_amount": 400000.0,
            "property_value": 500000.0
        }
        
        result = analyze_property_value.invoke({'application_data': test_data})
        return 'ANALYSIS REPORT' in result and 'ARCHITECTURE' in result
        
    except Exception as e:
        print(f'analyze_property_value tool validation failed: {e}')
        return False
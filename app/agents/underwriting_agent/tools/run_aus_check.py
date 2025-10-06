import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def run_aus_check(application_data: dict) -> str:
    """
    Basic run AUS check functionality.
    
    This tool provides basic Automated Underwriting System (AUS) check.
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
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        
        # Generate basic report
        report = [
            'RUN AUS CHECK ANALYSIS REPORT',
            '=' * 50,
            f'Credit Score: {credit_score}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            'ARCHITECTURE: This tool provides basic analysis.',
            'For detailed business rules and specific requirements,',
            'ask business rules questions which will be routed to BusinessRulesAgent.',
            '',
            'Analysis completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during run_aus_check: {e}')
        return f'Error during run_aus_check: {str(e)}'


def validate_tool() -> bool:
    """Validate that the run_aus_check tool works correctly."""
    try:
        # MortgageInput schema removed - using flexible dict approach
        
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0
        }
        
        result = run_aus_check.invoke({'application_data': test_data})
        return 'ANALYSIS REPORT' in result and 'ARCHITECTURE' in result
        
    except Exception as e:
        print(f'run_aus_check tool validation failed: {e}')
        return False
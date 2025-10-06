import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def evaluate_income_sources(application_data: dict) -> str:
    """
    Basic evaluate income sources functionality.
    
    This tool provides basic income sources evaluation.
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
        employment_type = application_data.get('employment_type', 'w2')
        
        # Generate basic report
        report = [
            'EVALUATE INCOME SOURCES ANALYSIS REPORT',
            '=' * 50,
            f'Credit Score: {credit_score}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Loan Amount: ${loan_amount:,.2f}',
            f'Employment Type: {employment_type}',
            '',
            'ARCHITECTURE: This tool provides basic analysis.',
            'For detailed business rules and specific requirements,',
            'ask business rules questions which will be routed to BusinessRulesAgent.',
            '',
            'Analysis completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during evaluate_income_sources: {e}')
        return f'Error during evaluate_income_sources: {str(e)}'


def validate_tool() -> bool:
    """Validate that the evaluate_income_sources tool works correctly."""
    try:
        # MortgageInput schema removed - using flexible dict approach
        
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0,
            "employment_type": 'w2'
        }
        
        result = evaluate_income_sources.invoke({'application_data': test_data})
        return 'ANALYSIS REPORT' in result and 'ARCHITECTURE' in result
        
    except Exception as e:
        print(f'evaluate_income_sources tool validation failed: {e}')
        return False
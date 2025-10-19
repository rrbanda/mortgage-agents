import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def run_aus_check(application_data: dict) -> str:
    """
    Submit application to Automated Underwriting System (AUS) for evaluation.
    
    OPERATIONAL TOOL: Simulates AUS submission and displays results.
    NO hardcoded AUS rules or approval criteria.
    Agent should call Neo4j MCP tools (read_neo4j_cypher) for AUS rules and requirements.
    
    Args:
        application_data: Dict containing application info. May include:
            - credit_score, monthly_income, monthly_debts, loan_amount
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing AUS check results report
    """
    try:
        # Extract application data
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        
        # Calculate DTI for informational purposes
        dti = (monthly_debts / monthly_income * 100) if monthly_income > 0 else 0
        
        # Generate AUS submission report (NO hardcoded results)
        report = [
            'AUTOMATED UNDERWRITING SYSTEM (AUS) CHECK REPORT',
            '=' * 50,
            '',
            '📋 APPLICATION SUBMITTED TO AUS:',
            f'Credit Score: {credit_score}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Debt-to-Income Ratio: {dti:.2f}%',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            '🔄 AUS PROCESSING STATUS:',
            '• Application data submitted successfully',
            '• AUS evaluation in progress',
            '• Awaiting automated decision',
            '',
            '⚠️ OPERATIONAL TOOL - NO HARDCODED AUS RULES:',
            'This tool simulates AUS submission only.',
            'For AUS rules and requirements, agent should call Neo4j MCP tools.',
            'Use read_neo4j_cypher to query AUS rules and evaluation criteria.',
            '',
            '✓ AUS check submitted successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during run_aus_check: {e}')
        return f'Error during run_aus_check: {str(e)}'


def validate_tool() -> bool:
    """Validate that the run_aus_check tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0
        }
        
        result = run_aus_check.invoke({'application_data': test_data})
        return 'AUS CHECK REPORT' in result and 'AUS PROCESSING STATUS' in result
        
    except Exception as e:
        print(f'run_aus_check tool validation failed: {e}')
        return False
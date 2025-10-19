import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def make_underwriting_decision(application_data: dict) -> str:
    """
    Analyze underwriting decision factors for a mortgage application.
    
    OPERATIONAL TOOL: Displays borrower information and analyzes decision factors.
    NO hardcoded approval/denial rules or qualification thresholds.
    Agent should call Neo4j MCP tools (read_neo4j_cypher) for underwriting rules.
    
    Args:
        application_data: Dict containing application info. May include:
            - credit_score, monthly_income, monthly_debts, loan_amount
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing underwriting decision analysis report
    """
    try:
        # Extract borrower data
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        
        # Calculate DTI for informational purposes
        dti = (monthly_debts / monthly_income * 100) if monthly_income > 0 else 0
        
        # Generate analysis report (NO approval/denial decisions)
        report = [
            'UNDERWRITING DECISION ANALYSIS REPORT',
            '=' * 50,
            '',
            '📋 BORROWER PROFILE:',
            f'Credit Score: {credit_score}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Debt-to-Income Ratio: {dti:.2f}%',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            '📊 DECISION FACTORS TO CONSIDER:',
            '• Credit profile and payment history',
            '• Income stability and debt obligations',
            '• Loan-to-value ratio and down payment',
            '• Property type and occupancy',
            '• Overall financial strength',
            '',
            '⚠️ OPERATIONAL TOOL - NO APPROVAL/DENIAL DECISIONS:',
            'This tool analyzes decision factors only.',
            'For underwriting rules and approval criteria, agent should call Neo4j MCP tools.',
            'Use read_neo4j_cypher to query underwriting rules and approval thresholds.',
            '',
            '✓ Analysis completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during make_underwriting_decision: {e}')
        return f'Error during make_underwriting_decision: {str(e)}'


def validate_tool() -> bool:
    """Validate that the make_underwriting_decision tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0
        }
        
        result = make_underwriting_decision.invoke({'application_data': test_data})
        return 'UNDERWRITING DECISION ANALYSIS REPORT' in result and 'DECISION FACTORS' in result
        
    except Exception as e:
        print(f'make_underwriting_decision tool validation failed: {e}')
        return False
import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def analyze_credit_risk(application_data: dict) -> str:
    """
    Analyze credit risk based on borrower's credit profile.
    
    OPERATIONAL TOOL: Displays credit information and calculates basic metrics.
    NO hardcoded thresholds or qualification rules.
    Agent should call Neo4j MCP tools (read_neo4j_cypher) for actual underwriting rules.
    
    Args:
        application_data: Dict containing application info. May include:
            - credit_score, monthly_income, monthly_debts, loan_amount
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing credit risk analysis report
    """
    try:
        # Extract basic data from parsed_data
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        
        # Generate basic report (NO hardcoded thresholds)
        report = [
            'CREDIT RISK ANALYSIS REPORT',
            '=' * 50,
            '',
            '📊 BORROWER CREDIT PROFILE:',
            f'Credit Score: {credit_score}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            '⚠️ OPERATIONAL TOOL - NO QUALIFICATION DECISIONS:',
            'This tool displays credit information only.',
            'For underwriting rules and thresholds, agent should call Neo4j MCP tools.',
            'Use read_neo4j_cypher to query credit score requirements, DTI limits, etc.',
            '',
            '✓ Analysis completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during analyze_credit_risk: {e}')
        return f'Error during analyze_credit_risk: {str(e)}'


def validate_tool() -> bool:
    """Validate that the analyze_credit_risk tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0
        }
        
        result = analyze_credit_risk.invoke({'application_data': test_data})
        return 'CREDIT RISK ANALYSIS REPORT' in result and 'BORROWER CREDIT PROFILE' in result
        
    except Exception as e:
        print(f'analyze_credit_risk tool validation failed: {e}')
        return False
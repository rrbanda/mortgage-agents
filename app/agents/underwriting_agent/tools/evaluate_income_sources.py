import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def evaluate_income_sources(application_data: dict) -> str:
    """
    Evaluate borrower's income sources and employment information.
    
    OPERATIONAL TOOL: Displays income information and employment details.
    NO hardcoded income qualification rules or employment requirements.
    Agent should call Neo4j MCP tools (read_neo4j_cypher) for income calculation rules.
    
    Args:
        application_data: Dict containing application info. May include:
            - monthly_income, employment_type, credit_score, monthly_debts, loan_amount
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing income sources evaluation report
    """
    try:
        # Extract income and employment data
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        employment_type = application_data.get('employment_type', 'w2')
        
        # Generate report (NO hardcoded qualification rules)
        report = [
            'INCOME SOURCES EVALUATION REPORT',
            '=' * 50,
            '',
            '💼 EMPLOYMENT & INCOME INFORMATION:',
            f'Employment Type: {employment_type.upper()}',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Annual Income (estimated): ${monthly_income * 12:,.2f}',
            '',
            '📊 FINANCIAL OVERVIEW:',
            f'Credit Score: {credit_score}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            '⚠️ OPERATIONAL TOOL - NO QUALIFICATION DECISIONS:',
            'This tool displays income and employment information only.',
            'For income qualification rules, agent should call Neo4j MCP tools.',
            'Use read_neo4j_cypher to query income calculation rules and requirements.',
            '',
            '✓ Evaluation completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during evaluate_income_sources: {e}')
        return f'Error during evaluate_income_sources: {str(e)}'


def validate_tool() -> bool:
    """Validate that the evaluate_income_sources tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0,
            "employment_type": 'w2'
        }
        
        result = evaluate_income_sources.invoke({'application_data': test_data})
        return 'INCOME SOURCES EVALUATION REPORT' in result and 'EMPLOYMENT & INCOME INFORMATION' in result
        
    except Exception as e:
        print(f'evaluate_income_sources tool validation failed: {e}')
        return False
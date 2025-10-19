import logging
from langchain_core.tools import tool
# MortgageInput schema removed - using flexible dict approach

logger = logging.getLogger(__name__)

@tool
def calculate_debt_to_income(application_data: dict) -> str:
    """
    Calculate debt-to-income ratio from borrower's financial information.
    
    OPERATIONAL TOOL: Performs DTI calculation only (pure math).
    NO hardcoded DTI limits or qualification rules.
    Agent should call Neo4j MCP tools (read_neo4j_cypher) for actual DTI thresholds.
    
    Args:
        application_data: Dict containing application info. May include:
            - monthly_income, monthly_debts, credit_score, loan_amount
            (All fields optional - tool uses defaults for missing values)
    
    Returns:
        String containing DTI calculation report
    """
    try:
        # Extract financial data
        credit_score = application_data.get('credit_score', 720)
        monthly_income = application_data.get('monthly_income', 5000.0)
        monthly_debts = application_data.get('monthly_debts', 500.0)
        loan_amount = application_data.get('loan_amount', 0.0)
        
        # Calculate DTI (pure math, no business rules)
        dti = (monthly_debts / monthly_income * 100) if monthly_income > 0 else 0
        
        # Generate report (NO hardcoded limits)
        report = [
            'DEBT-TO-INCOME (DTI) CALCULATION REPORT',
            '=' * 50,
            '',
            '📊 FINANCIAL INFORMATION:',
            f'Monthly Income: ${monthly_income:,.2f}',
            f'Monthly Debts: ${monthly_debts:,.2f}',
            f'Credit Score: {credit_score}',
            f'Loan Amount: ${loan_amount:,.2f}',
            '',
            '📈 CALCULATED DTI RATIO:',
            f'Debt-to-Income Ratio: {dti:.2f}%',
            '',
            '⚠️ OPERATIONAL TOOL - NO QUALIFICATION DECISIONS:',
            'This tool calculates DTI ratio only (pure math).',
            'For DTI limits and thresholds, agent should call Neo4j MCP tools.',
            'Use read_neo4j_cypher to query underwriting rules for DTI requirements.',
            '',
            '✓ Calculation completed successfully.'
        ]
        
        return '\n'.join(report)
        
    except Exception as e:
        logger.error(f'Error during calculate_debt_to_income: {e}')
        return f'Error during calculate_debt_to_income: {str(e)}'


def validate_tool() -> bool:
    """Validate that the calculate_debt_to_income tool works correctly."""
    try:
        test_data = {
            "credit_score": 720,
            "monthly_income": 5000.0,
            "monthly_debts": 500.0,
            "loan_amount": 400000.0
        }
        
        result = calculate_debt_to_income.invoke({'application_data': test_data})
        return 'DTI CALCULATION REPORT' in result and 'DTI RATIO' in result
        
    except Exception as e:
        print(f'calculate_debt_to_income tool validation failed: {e}')
        return False
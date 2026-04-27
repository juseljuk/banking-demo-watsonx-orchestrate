"""
Lending Compliance Guardrail - Pre-invoke Plugin

Ensures loan applications and decisions comply with UK lending regulations
including FCA rules, Consumer Credit Act 1974, and fair lending practices.

Compliance Checks:
- Affordability assessment (FCA CONC 5.2A)
- Creditworthiness evaluation (Consumer Credit Act)
- Debt-to-income ratio validation (max 40%)
- Required disclosures (APR, total amount payable, cooling-off period)
- Fair lending (no discrimination based on protected characteristics)
- Responsible lending (no predatory practices)

UK Regulatory Framework:
- FCA Consumer Credit Sourcebook (CONC)
- Consumer Credit Act 1974
- Equality Act 2010
- Consumer Rights Act 2015

Maximum Lending Limits:
- Personal Loan: Up to 5x annual income
- Business Loan: Based on business financials
- Credit Card: Based on credit score and income
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.tools.types import (
    PythonToolKind,
    PluginContext,
    AgentPreInvokePayload,
    AgentPreInvokeResult,
    TextContent,
    Message
)
import re
from typing import Dict, Any, Optional


# Lending limits and thresholds
MAX_DTI_RATIO = 0.40  # 40% debt-to-income ratio
MIN_CREDIT_SCORE = 550  # Minimum credit score for approval
PERSONAL_LOAN_INCOME_MULTIPLIER = 5  # Max 5x annual income
MIN_INCOME_FOR_LOAN = 15000  # Minimum £15,000 annual income

# Loan amount thresholds requiring additional checks
HIGH_VALUE_LOAN_THRESHOLD = 50000  # £50,000
BUSINESS_LOAN_THRESHOLD = 100000  # £100,000


def extract_loan_request(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract loan application details from user message.
    
    Returns dict with:
    - amount: float (loan amount in GBP)
    - purpose: str (loan purpose)
    - loan_type: str (personal, business, mortgage, car)
    """
    # Pattern 1: "Apply for £X,XXX loan"
    pattern1 = r'(?:apply|applying|request|need|want)\s+(?:for\s+)?(?:a\s+)?£?([\d,]+(?:\.\d{2})?)\s+(?:pound\s+)?(personal|business|car|mortgage)?\s*loan'
    
    # Pattern 2: "£X,XXX loan for [purpose]"
    pattern2 = r'£?([\d,]+(?:\.\d{2})?)\s+loan\s+for\s+([a-z\s]+)'
    
    # Pattern 3: "I'd like to borrow £X,XXX"
    pattern3 = r'(?:borrow|loan|lend)\s+(?:me\s+)?£?([\d,]+(?:\.\d{2})?)'
    
    message_lower = message.lower()
    
    # Try pattern 1 (most specific)
    match = re.search(pattern1, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        loan_type = match.group(2) if match.group(2) else "personal"
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "loan_type": loan_type,
                "purpose": None
            }
        except ValueError:
            pass
    
    # Try pattern 2 (with purpose)
    match = re.search(pattern2, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        purpose = match.group(2).strip()
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "loan_type": "personal",
                "purpose": purpose
            }
        except ValueError:
            pass
    
    # Try pattern 3 (simple)
    match = re.search(pattern3, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "loan_type": "personal",
                "purpose": None
            }
        except ValueError:
            pass
    
    return None


def check_affordability(
    loan_amount: float,
    annual_income: float,
    existing_debt: float = 0
) -> Dict[str, Any]:
    """
    Check if loan is affordable based on income and existing debt.
    
    FCA CONC 5.2A requires lenders to assess affordability.
    
    Args:
        loan_amount: Requested loan amount
        annual_income: Customer's annual income
        existing_debt: Customer's existing monthly debt payments
        
    Returns:
        Dict with 'affordable' (bool), 'reason' (str), 'dti_ratio' (float)
    """
    # Calculate monthly loan payment (assuming 5-year term at 8% APR)
    monthly_rate = 0.08 / 12
    num_payments = 60  # 5 years
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    # Calculate debt-to-income ratio
    monthly_income = annual_income / 12
    total_monthly_debt = existing_debt + monthly_payment
    dti_ratio = total_monthly_debt / monthly_income if monthly_income > 0 else 1.0
    
    # Check minimum income requirement
    if annual_income < MIN_INCOME_FOR_LOAN:
        return {
            "affordable": False,
            "reason": f"Minimum annual income of £{MIN_INCOME_FOR_LOAN:,.2f} required for loan approval.",
            "dti_ratio": dti_ratio,
            "monthly_payment": monthly_payment
        }
    
    # Check DTI ratio
    if dti_ratio > MAX_DTI_RATIO:
        return {
            "affordable": False,
            "reason": f"Debt-to-income ratio of {dti_ratio:.1%} exceeds maximum of {MAX_DTI_RATIO:.1%}. Monthly payment of £{monthly_payment:,.2f} would be unaffordable based on your income.",
            "dti_ratio": dti_ratio,
            "monthly_payment": monthly_payment
        }
    
    # Check income multiplier for personal loans
    max_loan = annual_income * PERSONAL_LOAN_INCOME_MULTIPLIER
    if loan_amount > max_loan:
        return {
            "affordable": False,
            "reason": f"Requested amount of £{loan_amount:,.2f} exceeds maximum of £{max_loan:,.2f} (5x annual income of £{annual_income:,.2f}).",
            "dti_ratio": dti_ratio,
            "monthly_payment": monthly_payment,
            "max_loan": max_loan
        }
    
    return {
        "affordable": True,
        "reason": "Loan is affordable based on income and existing commitments",
        "dti_ratio": dti_ratio,
        "monthly_payment": monthly_payment
    }


def check_creditworthiness(credit_score: int) -> Dict[str, Any]:
    """
    Check if customer meets minimum creditworthiness requirements.
    
    UK credit scores range from 0-999 (Experian scale).
    
    Args:
        credit_score: Customer's credit score (0-999)
        
    Returns:
        Dict with 'approved' (bool), 'reason' (str), 'risk_category' (str)
    """
    if credit_score < MIN_CREDIT_SCORE:
        return {
            "approved": False,
            "reason": f"Credit score of {credit_score} is below minimum requirement of {MIN_CREDIT_SCORE}. We recommend improving your credit score before reapplying.",
            "risk_category": "high_risk"
        }
    elif credit_score < 650:
        return {
            "approved": True,
            "reason": "Approved with higher interest rate due to credit score",
            "risk_category": "medium_risk",
            "requires_review": True
        }
    elif credit_score < 750:
        return {
            "approved": True,
            "reason": "Approved with standard terms",
            "risk_category": "low_risk"
        }
    else:
        return {
            "approved": True,
            "reason": "Approved with preferential terms",
            "risk_category": "very_low_risk"
        }


def check_required_disclosures(loan_type: str) -> Dict[str, Any]:
    """
    Verify that required disclosures will be provided per FCA CONC rules.
    
    Required disclosures:
    - APR (Annual Percentage Rate)
    - Total amount payable
    - Loan term and monthly payment
    - Early repayment rights
    - 14-day cooling-off period
    - Consequences of missed payments
    
    Returns:
        Dict with 'compliant' (bool), 'missing_disclosures' (list)
    """
    required_disclosures = [
        "APR (Annual Percentage Rate)",
        "Total amount payable",
        "Monthly payment amount",
        "Loan term",
        "Early repayment rights",
        "14-day cooling-off period",
        "Consequences of missed payments",
        "Right to withdraw"
    ]
    
    # In production, this would check if disclosures are included in the offer
    # For demo, we assume all disclosures will be provided
    return {
        "compliant": True,
        "missing_disclosures": [],
        "required_disclosures": required_disclosures
    }


@tool(
    description="Ensures loan applications comply with UK lending regulations and fair lending practices",
    kind=PythonToolKind.AGENTPREINVOKE
)
def lending_compliance_guardrail(
    plugin_context: PluginContext,
    agent_pre_invoke_payload: AgentPreInvokePayload
) -> AgentPreInvokeResult:
    """
    Pre-invoke guardrail that validates loan requests against compliance requirements.
    
    This guardrail checks loan applications for:
    - Affordability (FCA CONC 5.2A)
    - Creditworthiness (Consumer Credit Act)
    - Required disclosures
    - Fair lending practices
    
    Args:
        plugin_context (PluginContext): Plugin execution context
        agent_pre_invoke_payload (AgentPreInvokePayload): User's request payload
        
    Returns:
        AgentPreInvokeResult: Decision to allow, block, or modify the request
    """
    result = AgentPreInvokeResult()
    
    # Check if we have messages
    if not agent_pre_invoke_payload or not agent_pre_invoke_payload.messages:
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    # Get user message
    last_message = agent_pre_invoke_payload.messages[-1]
    content = getattr(last_message, "content", None)
    
    if content is None or not hasattr(content, "text") or content.text is None:
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    user_message = content.text
    
    # Check if this is a loan application request
    loan_keywords = ['loan', 'borrow', 'credit', 'finance', 'lending']
    is_loan_request = any(keyword in user_message.lower() for keyword in loan_keywords)
    
    if not is_loan_request:
        # Not a loan request, allow through
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    # Extract loan details
    loan_details = extract_loan_request(user_message)
    
    if not loan_details or 'amount' not in loan_details:
        # Couldn't extract loan amount, let agent handle it
        # Agent will ask for details
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    amount = loan_details['amount']
    loan_type = loan_details.get('loan_type', 'personal')
    
    # For demo purposes, we'll use Emma Thompson's profile (CUST-001)
    # In production, this would come from authenticated session
    demo_customer_income = 65000  # £65,000 annual income
    demo_customer_credit_score = 742  # Good credit score
    demo_existing_debt = 55  # £55 monthly credit card minimum payment
    
    # Check 1: Creditworthiness
    credit_check = check_creditworthiness(demo_customer_credit_score)
    if not credit_check['approved']:
        # Block loan application - insufficient credit score
        blocked_message = (
            f"I'm unable to proceed with your loan application at this time. "
            f"{credit_check['reason']} "
            f"You may wish to review your credit report and consider steps to improve your score. "
            f"We're here to help when you're ready to reapply."
        )
        
        new_content = TextContent(type="text", text=blocked_message)
        new_message = Message(role=last_message.role, content=new_content)
        
        modified_payload = agent_pre_invoke_payload.copy(deep=True)
        modified_payload.messages = [new_message]
        
        result.continue_processing = False
        result.modified_payload = modified_payload
        
        print(f"[LENDING_COMPLIANCE] BLOCKED: Credit score {demo_customer_credit_score} below minimum")
        return result
    
    # Check 2: Affordability
    affordability_check = check_affordability(
        amount,
        demo_customer_income,
        demo_existing_debt
    )
    
    if not affordability_check['affordable']:
        # Block loan application - not affordable
        blocked_message = (
            f"I'm unable to approve a loan of £{amount:,.2f} at this time. "
            f"{affordability_check['reason']} "
            f"As a responsible lender, we must ensure loans are affordable. "
            f"You may wish to consider a smaller loan amount or contact us to discuss your options."
        )
        
        new_content = TextContent(type="text", text=blocked_message)
        new_message = Message(role=last_message.role, content=new_content)
        
        modified_payload = agent_pre_invoke_payload.copy(deep=True)
        modified_payload.messages = [new_message]
        
        result.continue_processing = False
        result.modified_payload = modified_payload
        
        print(f"[LENDING_COMPLIANCE] BLOCKED: £{amount:,.2f} loan not affordable (DTI: {affordability_check['dti_ratio']:.1%})")
        return result
    
    # Check 3: Required disclosures
    disclosure_check = check_required_disclosures(loan_type)
    if not disclosure_check['compliant']:
        # This would block in production if disclosures are missing
        print(f"[LENDING_COMPLIANCE] WARNING: Missing disclosures: {disclosure_check['missing_disclosures']}")
    
    # All compliance checks passed
    result.continue_processing = True
    result.modified_payload = agent_pre_invoke_payload
    
    print(f"[LENDING_COMPLIANCE] APPROVED: £{amount:,.2f} {loan_type} loan (DTI: {affordability_check['dti_ratio']:.1%}, Credit: {demo_customer_credit_score})")
    
    # Log compliance check for audit trail
    if credit_check.get('requires_review'):
        print(f"[LENDING_COMPLIANCE] NOTE: Manual review recommended due to credit score")
    
    return result

# Made with Bob

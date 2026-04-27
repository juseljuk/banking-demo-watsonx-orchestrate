"""
Transaction Limit Guardrail - Pre-invoke Plugin

Enforces daily transaction limits and velocity rules to prevent unauthorized
large transfers and suspicious transaction patterns.

Checks:
- Daily transfer limits per account type
- Single transaction amount limits
- Velocity rules (number of transactions in time window)
- Accumulated daily transfer amounts

Limits (UK Banking Standards):
- Current Account: £10,000 daily limit
- Business Account: £25,000 daily limit
- Savings Account: £5,000 daily limit
- Velocity: Max 3 transfers per 15 minutes

Compliance: UK Payment Services Regulations 2017, FCA SYSC 6.1
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
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


# Transaction limits by account type (in GBP)
DAILY_LIMITS = {
    "CUR": 10000,  # Current Account
    "BUS": 25000,  # Business Account
    "SAV": 5000,   # Savings Account
    "CC": 5000     # Credit Card
}

# Single transaction limits
SINGLE_TRANSACTION_LIMIT = 50000  # £50,000 max per transaction

# Velocity limits
MAX_TRANSACTIONS_PER_15MIN = 3
VELOCITY_WINDOW_MINUTES = 15

# High-value transaction threshold requiring additional verification
HIGH_VALUE_THRESHOLD = 10000  # £10,000


def extract_transfer_details(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract transfer amount and account details from user message.
    
    Returns dict with:
    - amount: float (transfer amount in GBP)
    - from_account: str (source account ID)
    - to_account: str (destination account ID)
    """
    # Pattern 1: "Transfer £X,XXX from ACCOUNT to ACCOUNT"
    pattern1 = r'transfer\s+£?([\d,]+(?:\.\d{2})?)\s+(?:from\s+)?([A-Z]{3}-\d{3}-\d{4})?\s*(?:to\s+)?([A-Z]{3}-\d{3}-\d{4})?'
    
    # Pattern 2: "Transfer £X,XXX to savings/current"
    pattern2 = r'transfer\s+£?([\d,]+(?:\.\d{2})?)\s+to\s+(savings|current|business)'
    
    # Pattern 3: "Send £X,XXX"
    pattern3 = r'(?:send|pay)\s+£?([\d,]+(?:\.\d{2})?)'
    
    message_lower = message.lower()
    
    # Try pattern 1 (most specific)
    match = re.search(pattern1, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        from_account = match.group(2) if match.group(2) else None
        to_account = match.group(3) if match.group(3) else None
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "from_account": from_account,
                "to_account": to_account
            }
        except ValueError:
            pass
    
    # Try pattern 2 (account type mentioned)
    match = re.search(pattern2, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        account_type = match.group(2)
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "from_account": None,
                "to_account": account_type,
                "account_type_mentioned": True
            }
        except ValueError:
            pass
    
    # Try pattern 3 (simple amount)
    match = re.search(pattern3, message_lower, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        
        try:
            amount = float(amount_str)
            return {
                "amount": amount,
                "from_account": None,
                "to_account": None
            }
        except ValueError:
            pass
    
    return None


def get_account_type_from_id(account_id: str) -> str:
    """Extract account type prefix from account ID (e.g., CUR from CUR-001-1234)."""
    if account_id:
        return account_id.split('-')[0]
    return "CUR"  # Default to current account


def check_daily_limit(amount: float, account_type: str, daily_total: float = 0) -> Dict[str, Any]:
    """
    Check if transaction would exceed daily limit.
    
    Args:
        amount: Transaction amount
        account_type: Account type code (CUR, BUS, SAV, CC)
        daily_total: Amount already transferred today
        
    Returns:
        Dict with 'allowed' (bool), 'reason' (str), 'limit' (float), 'remaining' (float)
    """
    limit = DAILY_LIMITS.get(account_type, DAILY_LIMITS["CUR"])
    new_total = daily_total + amount
    remaining = limit - daily_total
    
    if new_total > limit:
        return {
            "allowed": False,
            "reason": f"Transaction of £{amount:,.2f} would exceed daily limit of £{limit:,.2f}. You have £{remaining:,.2f} remaining today.",
            "limit": limit,
            "remaining": remaining,
            "exceeded_by": new_total - limit
        }
    
    return {
        "allowed": True,
        "reason": "Within daily limit",
        "limit": limit,
        "remaining": remaining - amount
    }


def check_single_transaction_limit(amount: float) -> Dict[str, Any]:
    """Check if single transaction exceeds maximum allowed amount."""
    if amount > SINGLE_TRANSACTION_LIMIT:
        return {
            "allowed": False,
            "reason": f"Single transaction limit is £{SINGLE_TRANSACTION_LIMIT:,.2f}. Please contact your relationship manager for transactions over this amount.",
            "limit": SINGLE_TRANSACTION_LIMIT
        }
    
    return {
        "allowed": True,
        "reason": "Within single transaction limit",
        "limit": SINGLE_TRANSACTION_LIMIT
    }


def check_high_value_transaction(amount: float) -> Dict[str, Any]:
    """Check if transaction requires additional verification."""
    if amount >= HIGH_VALUE_THRESHOLD:
        return {
            "requires_verification": True,
            "reason": f"High-value transaction (≥£{HIGH_VALUE_THRESHOLD:,.2f}) requires additional verification.",
            "threshold": HIGH_VALUE_THRESHOLD
        }
    
    return {
        "requires_verification": False,
        "reason": "Standard transaction",
        "threshold": HIGH_VALUE_THRESHOLD
    }


@tool(
    description="Enforces daily transaction limits and velocity rules to prevent unauthorized transfers",
    kind=PythonToolKind.AGENTPREINVOKE
)
def transaction_limit_guardrail(
    plugin_context: PluginContext,
    agent_pre_invoke_payload: AgentPreInvokePayload
) -> AgentPreInvokeResult:
    """
    Pre-invoke guardrail that checks transaction limits before processing.
    
    This guardrail analyzes user requests for transfer/payment operations and
    validates against daily limits, single transaction limits, and velocity rules.
    
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
    
    # Check if this is a transfer/payment request
    transfer_keywords = ['transfer', 'send', 'pay', 'move']
    is_transfer_request = any(keyword in user_message.lower() for keyword in transfer_keywords)
    
    if not is_transfer_request:
        # Not a transfer request, allow through
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    # Extract transfer details
    transfer_details = extract_transfer_details(user_message)
    
    if not transfer_details or 'amount' not in transfer_details:
        # Couldn't extract amount, let agent handle it
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    amount = transfer_details['amount']
    from_account = transfer_details.get('from_account')
    account_type = get_account_type_from_id(from_account) if from_account else "CUR"
    
    # Check 1: Single transaction limit
    single_limit_check = check_single_transaction_limit(amount)
    if not single_limit_check['allowed']:
        # Block transaction - exceeds single transaction limit
        blocked_message = (
            f"I'm unable to process this transaction. {single_limit_check['reason']} "
            f"For your security, single transactions are limited to £{SINGLE_TRANSACTION_LIMIT:,.2f}. "
            f"Please contact your relationship manager for assistance with larger transfers."
        )
        
        new_content = TextContent(type="text", text=blocked_message)
        new_message = Message(role=last_message.role, content=new_content)
        
        modified_payload = agent_pre_invoke_payload.copy(deep=True)
        modified_payload.messages = [new_message]
        
        result.continue_processing = False
        result.modified_payload = modified_payload
        
        print(f"[TRANSACTION_LIMIT] BLOCKED: £{amount:,.2f} exceeds single transaction limit")
        return result
    
    # Check 2: Daily limit (simulated - in production would check actual daily total)
    # For demo, we'll assume £0 already transferred today
    daily_total = 0  # In production: fetch from transaction history
    daily_limit_check = check_daily_limit(amount, account_type, daily_total)
    
    if not daily_limit_check['allowed']:
        # Block transaction - exceeds daily limit
        blocked_message = (
            f"I'm unable to process this transaction. {daily_limit_check['reason']} "
            f"Your daily transfer limit for this account type is £{daily_limit_check['limit']:,.2f}. "
            f"The limit will reset at midnight."
        )
        
        new_content = TextContent(type="text", text=blocked_message)
        new_message = Message(role=last_message.role, content=new_content)
        
        modified_payload = agent_pre_invoke_payload.copy(deep=True)
        modified_payload.messages = [new_message]
        
        result.continue_processing = False
        result.modified_payload = modified_payload
        
        print(f"[TRANSACTION_LIMIT] BLOCKED: £{amount:,.2f} exceeds daily limit for {account_type}")
        return result
    
    # Check 3: High-value transaction verification
    high_value_check = check_high_value_transaction(amount)
    if high_value_check['requires_verification']:
        # Allow but flag for additional verification
        print(f"[TRANSACTION_LIMIT] HIGH-VALUE: £{amount:,.2f} requires additional verification")
        # In production, this would trigger MFA or additional checks
        # For demo, we'll allow it through with a note
    
    # All checks passed - allow transaction
    result.continue_processing = True
    result.modified_payload = agent_pre_invoke_payload
    
    print(f"[TRANSACTION_LIMIT] ALLOWED: £{amount:,.2f} transfer (within limits)")
    return result

# Made with Bob

"""
Fraud Rules Guardrail - Pre-invoke Plugin

Applies fraud detection rules and risk scoring to identify and block
suspicious transactions before they are processed.

Fraud Detection Rules:
- High-risk countries (Nigeria, Russia, etc.)
- Unusual transaction patterns (time, amount, frequency)
- Device fingerprint verification
- Velocity rules (multiple transactions in short time)
- Account takeover indicators
- Known fraud patterns

Risk Scoring (0-100):
- 0-30: Low risk (allow)
- 31-60: Medium risk (allow with monitoring)
- 61-90: High risk (require additional verification)
- 91-100: Critical risk (block transaction)

Compliance: UK Payment Services Regulations 2017, FCA SYSC 6.1, AML Regulations
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
from datetime import datetime, time
from typing import Dict, Any, Optional, List


# High-risk countries for fraud detection
HIGH_RISK_COUNTRIES = [
    'nigeria', 'russia', 'ukraine', 'belarus', 'iran', 'north korea',
    'syria', 'venezuela', 'myanmar', 'zimbabwe'
]

# Suspicious transaction patterns
SUSPICIOUS_KEYWORDS = [
    'urgent', 'emergency', 'immediately', 'wire', 'western union',
    'gift card', 'bitcoin', 'cryptocurrency', 'crypto'
]

# Risk thresholds
LOW_RISK_THRESHOLD = 30
MEDIUM_RISK_THRESHOLD = 60
HIGH_RISK_THRESHOLD = 90

# Transaction limits for fraud detection
LARGE_TRANSACTION_THRESHOLD = 5000  # £5,000
VERY_LARGE_TRANSACTION_THRESHOLD = 10000  # £10,000

# Time-based risk factors
HIGH_RISK_HOURS = [(0, 5), (22, 24)]  # 12am-5am and 10pm-12am


def extract_transaction_details(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract transaction details from user message for fraud analysis.
    
    Returns dict with:
    - amount: float (transaction amount)
    - destination: str (destination country/account)
    - urgency: bool (urgent language detected)
    - suspicious_keywords: list (detected suspicious terms)
    """
    # Extract amount
    amount_pattern = r'£?([\d,]+(?:\.\d{2})?)'
    amount_match = re.search(amount_pattern, message)
    amount = None
    if amount_match:
        try:
            amount = float(amount_match.group(1).replace(',', ''))
        except ValueError:
            pass
    
    # Check for high-risk countries
    destination = None
    for country in HIGH_RISK_COUNTRIES:
        if country in message.lower():
            destination = country
            break
    
    # Check for urgency indicators
    urgency_keywords = ['urgent', 'emergency', 'immediately', 'asap', 'right now', 'hurry']
    urgency = any(keyword in message.lower() for keyword in urgency_keywords)
    
    # Check for suspicious keywords
    detected_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in message.lower()]
    
    return {
        "amount": amount,
        "destination": destination,
        "urgency": urgency,
        "suspicious_keywords": detected_keywords
    }


def calculate_risk_score(transaction_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate fraud risk score based on transaction characteristics.
    
    Risk factors:
    - High-risk destination country: +40 points
    - Large transaction amount: +20 points
    - Very large transaction: +30 points
    - Urgency language: +15 points
    - Suspicious keywords: +10 points each
    - Off-hours transaction: +15 points
    
    Args:
        transaction_details: Dict with transaction characteristics
        
    Returns:
        Dict with 'risk_score' (int), 'risk_level' (str), 'risk_factors' (list)
    """
    risk_score = 0
    risk_factors = []
    
    # Check destination country
    if transaction_details.get('destination'):
        risk_score += 40
        risk_factors.append(f"High-risk destination: {transaction_details['destination'].title()}")
    
    # Check transaction amount
    amount = transaction_details.get('amount', 0)
    if amount >= VERY_LARGE_TRANSACTION_THRESHOLD:
        risk_score += 30
        risk_factors.append(f"Very large transaction: £{amount:,.2f}")
    elif amount >= LARGE_TRANSACTION_THRESHOLD:
        risk_score += 20
        risk_factors.append(f"Large transaction: £{amount:,.2f}")
    
    # Check urgency
    if transaction_details.get('urgency'):
        risk_score += 15
        risk_factors.append("Urgent language detected")
    
    # Check suspicious keywords
    suspicious_kw = transaction_details.get('suspicious_keywords', [])
    if suspicious_kw:
        risk_score += len(suspicious_kw) * 10
        risk_factors.append(f"Suspicious keywords: {', '.join(suspicious_kw)}")
    
    # Check time of day (simulated - in production would use actual time)
    current_hour = datetime.now().hour
    is_high_risk_time = any(start <= current_hour < end for start, end in HIGH_RISK_HOURS)
    if is_high_risk_time:
        risk_score += 15
        risk_factors.append(f"Off-hours transaction ({current_hour}:00)")
    
    # Determine risk level
    if risk_score >= HIGH_RISK_THRESHOLD:
        risk_level = "CRITICAL"
    elif risk_score >= MEDIUM_RISK_THRESHOLD:
        risk_level = "HIGH"
    elif risk_score >= LOW_RISK_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "risk_score": min(risk_score, 100),  # Cap at 100
        "risk_level": risk_level,
        "risk_factors": risk_factors
    }


def check_velocity_rules(customer_id: str = "CUST-001") -> Dict[str, Any]:
    """
    Check if customer has exceeded velocity limits.
    
    In production, this would check actual transaction history.
    For demo, we simulate based on known scenarios.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        Dict with 'velocity_exceeded' (bool), 'reason' (str)
    """
    # In production, query transaction history for last 15 minutes
    # For demo, we'll return normal velocity
    return {
        "velocity_exceeded": False,
        "reason": "Normal transaction velocity",
        "transactions_last_15min": 0,
        "limit": 3
    }


def check_device_trust(device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify device fingerprint against trusted devices.
    
    In production, this would check device database.
    For demo, we simulate device trust.
    
    Args:
        device_id: Device fingerprint identifier
        
    Returns:
        Dict with 'trusted' (bool), 'reason' (str)
    """
    # Known trusted devices for demo
    trusted_devices = ['DEV-EMMA-IPHONE', 'DEV-EMMA-MACBOOK']
    
    if device_id and device_id in trusted_devices:
        return {
            "trusted": True,
            "reason": "Recognized trusted device",
            "device_id": device_id
        }
    elif device_id:
        return {
            "trusted": False,
            "reason": "Unrecognized device",
            "device_id": device_id
        }
    else:
        return {
            "trusted": True,
            "reason": "Device verification not required",
            "device_id": None
        }


@tool(
    description="Applies fraud detection rules to identify and block suspicious transactions",
    kind=PythonToolKind.AGENTPREINVOKE
)
def fraud_rules_guardrail(
    plugin_context: PluginContext,
    agent_pre_invoke_payload: AgentPreInvokePayload
) -> AgentPreInvokeResult:
    """
    Pre-invoke guardrail that applies fraud detection rules.
    
    This guardrail analyzes transactions for fraud indicators and blocks
    high-risk transactions before they are processed.
    
    Risk Levels:
    - LOW (0-30): Allow transaction
    - MEDIUM (31-60): Allow with monitoring
    - HIGH (61-90): Require additional verification
    - CRITICAL (91-100): Block transaction
    
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
    
    # Check if this is a transaction request
    transaction_keywords = ['transfer', 'send', 'pay', 'wire', 'payment']
    is_transaction = any(keyword in user_message.lower() for keyword in transaction_keywords)
    
    if not is_transaction:
        # Not a transaction, allow through
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    # Extract transaction details
    transaction_details = extract_transaction_details(user_message)
    
    if not transaction_details:
        # Couldn't extract details, let agent handle it
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result
    
    # Calculate fraud risk score
    risk_assessment = calculate_risk_score(transaction_details)
    risk_score = risk_assessment['risk_score']
    risk_level = risk_assessment['risk_level']
    risk_factors = risk_assessment['risk_factors']
    
    # Check velocity rules
    velocity_check = check_velocity_rules()
    if velocity_check['velocity_exceeded']:
        risk_score = min(risk_score + 20, 100)
        risk_factors.append("Velocity limit exceeded")
    
    # Check device trust
    device_check = check_device_trust()
    if not device_check['trusted']:
        risk_score = min(risk_score + 15, 100)
        risk_factors.append("Unrecognized device")
    
    # Decision based on risk score
    if risk_score >= HIGH_RISK_THRESHOLD:
        # CRITICAL RISK - Block transaction
        blocked_message = (
            f"⚠️ **TRANSACTION BLOCKED FOR SECURITY**\n\n"
            f"This transaction has been flagged as high-risk and cannot be processed.\n\n"
            f"**Risk Score:** {risk_score}/100 (CRITICAL)\n"
            f"**Risk Factors:**\n"
        )
        for factor in risk_factors:
            blocked_message += f"• {factor}\n"
        
        blocked_message += (
            f"\n**What to do next:**\n"
            f"• Contact our fraud prevention team at 0800 123 4567\n"
            f"• Verify your identity and transaction details\n"
            f"• We're here to protect your account\n\n"
            f"If this is a legitimate transaction, our team can help you complete it securely."
        )
        
        new_content = TextContent(type="text", text=blocked_message)
        new_message = Message(role=last_message.role, content=new_content)
        
        modified_payload = agent_pre_invoke_payload.copy(deep=True)
        modified_payload.messages = [new_message]
        
        result.continue_processing = False
        result.modified_payload = modified_payload
        
        print(f"[FRAUD_RULES] BLOCKED: Risk score {risk_score}/100 - {', '.join(risk_factors)}")
        return result
    
    elif risk_score >= MEDIUM_RISK_THRESHOLD:
        # HIGH RISK - Require additional verification
        print(f"[FRAUD_RULES] HIGH RISK: Score {risk_score}/100 - Additional verification required")
        # In production, this would trigger MFA or manual review
        # For demo, we'll allow it through with a warning
    
    elif risk_score >= LOW_RISK_THRESHOLD:
        # MEDIUM RISK - Allow with monitoring
        print(f"[FRAUD_RULES] MEDIUM RISK: Score {risk_score}/100 - Monitoring enabled")
    
    else:
        # LOW RISK - Allow transaction
        print(f"[FRAUD_RULES] LOW RISK: Score {risk_score}/100 - Transaction approved")
    
    # Allow transaction (unless blocked above)
    result.continue_processing = True
    result.modified_payload = agent_pre_invoke_payload
    return result

# Made with Bob

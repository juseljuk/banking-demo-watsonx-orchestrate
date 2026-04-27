"""
PII Protection Guardrail - Post-invoke Plugin

Redacts sensitive personal information from agent responses to protect customer privacy.
This guardrail runs AFTER the agent generates a response and sanitizes PII before
returning to the user.

Redaction Patterns:
- Account numbers: Full number → ****1234 (last 4 digits)
- Sort codes: 20-00-00 → **-**-00 (last 2 digits)
- National Insurance numbers: AB123456D → ******456D (last 4 chars)
- Email addresses: emma.thompson@email.co.uk → e***@***.co.uk
- Phone numbers: +44 20 7946 0123 → +44 ** **** 0123 (last 4 digits)
- Credit card numbers: 1234567890123456 → ****3456 (last 4 digits)
- IBANs: GB29NWBK60161331926819 → GB********************6819 (last 4 digits)

Compliance: GDPR, UK Data Protection Act 2018, FCA SYSC 3.2.6R
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.tools.types import (
    PythonToolKind,
    PluginContext,
    AgentPostInvokePayload,
    AgentPostInvokeResult,
    TextContent,
    Message
)
import re
from typing import Dict, Any


def redact_account_numbers(text: str) -> str:
    """Redact account numbers to show only last 4 digits."""
    # Match 8-digit account numbers
    pattern = r'\b\d{8}\b'
    def replacer(match):
        num = match.group()
        return f"****{num[-4:]}"
    return re.sub(pattern, replacer, text)


def redact_sort_codes(text: str) -> str:
    """Redact sort codes to show only last 2 digits."""
    # Match sort codes in format XX-XX-XX
    pattern = r'\b\d{2}-\d{2}-(\d{2})\b'
    return re.sub(pattern, r'**-**-\1', text)


def redact_ni_numbers(text: str) -> str:
    """Redact National Insurance numbers to show only last 4 characters."""
    # Match NI numbers: 2 letters, 6 digits, 1 letter (e.g., AB123456D)
    pattern = r'\b[A-Z]{2}\d{6}[A-Z]\b'
    def replacer(match):
        ni = match.group()
        return f"******{ni[-4:]}"
    return re.sub(pattern, replacer, text)


def redact_emails(text: str) -> str:
    """Redact email addresses to show only first letter and domain."""
    # Match email addresses
    pattern = r'\b([a-zA-Z])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
    def replacer(match):
        first_char = match.group(1)
        domain = match.group(2)
        # Mask domain except TLD
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            masked_domain = '*' * len(domain_parts[0]) + '.' + domain_parts[-1]
        else:
            masked_domain = domain
        return f"{first_char}***@{masked_domain}"
    return re.sub(pattern, replacer, text)


def redact_phone_numbers(text: str) -> str:
    """Redact phone numbers to show only last 4 digits."""
    # Match UK phone numbers: +44 XX XXXX XXXX or +44 XXXX XXX XXX
    pattern = r'\+44\s*\d{2,4}\s*\d{3,4}\s*(\d{4})\b'
    return re.sub(pattern, r'+44 ** **** \1', text)


def redact_credit_cards(text: str) -> str:
    """Redact credit card numbers to show only last 4 digits."""
    # Match 16-digit credit card numbers (with or without spaces/dashes)
    pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b'
    return re.sub(pattern, r'****\1', text)


def redact_ibans(text: str) -> str:
    """Redact IBANs to show only country code and last 4 digits."""
    # Match IBANs: 2 letters followed by 2 digits and up to 30 alphanumeric chars
    pattern = r'\b([A-Z]{2}\d{2})[A-Z0-9]{1,26}([A-Z0-9]{4})\b'
    return re.sub(pattern, r'\1********************\2', text)


def apply_all_redactions(text: str) -> str:
    """Apply all PII redaction patterns to text."""
    text = redact_account_numbers(text)
    text = redact_sort_codes(text)
    text = redact_ni_numbers(text)
    text = redact_emails(text)
    text = redact_phone_numbers(text)
    text = redact_credit_cards(text)
    text = redact_ibans(text)
    return text


@tool(
    description="Redacts sensitive PII from agent responses to protect customer privacy",
    kind=PythonToolKind.AGENTPOSTINVOKE
)
def pii_protection_guardrail(
    plugin_context: PluginContext,
    agent_post_invoke_payload: AgentPostInvokePayload
) -> AgentPostInvokeResult:
    """
    Post-invoke guardrail that redacts PII from agent responses.
    
    This guardrail scans the agent's response for sensitive information and
    applies redaction patterns before returning to the user.
    
    Args:
        plugin_context (PluginContext): Plugin execution context
        agent_post_invoke_payload (AgentPostInvokePayload): Agent's response payload
        
    Returns:
        AgentPostInvokeResult: Modified payload with PII redacted
    """
    result = AgentPostInvokeResult()
    
    # Check if we have messages
    if not agent_post_invoke_payload or not agent_post_invoke_payload.messages or len(agent_post_invoke_payload.messages) == 0:
        result.continue_processing = False
        return result
    
    # Get agent's response
    first_msg = agent_post_invoke_payload.messages[0]
    content = getattr(first_msg, "content", None)
    
    if content is None or not hasattr(content, "text") or content.text is None:
        result.continue_processing = False
        return result
    
    response_text = content.text
    
    # Apply all PII redaction patterns
    redacted_text = apply_all_redactions(response_text)
    
    # Check if any redactions were made
    redactions_made = response_text != redacted_text
    
    if redactions_made:
        # Log redaction event (in production, this would go to audit log)
        print(f"[PII_PROTECTION] Redacted PII from response (length: {len(response_text)} → {len(redacted_text)})")
    
    # Create modified response with redacted text
    new_content = TextContent(type="text", text=redacted_text)
    new_message = Message(role=first_msg.role, content=new_content)
    
    modified_payload = agent_post_invoke_payload.copy(deep=True)
    modified_payload.messages[0] = new_message
    
    result.continue_processing = True
    result.modified_payload = modified_payload
    return result

# Made with Bob

"""
Test cases for PII Protection Guardrail

Tests the redaction logic for various types of sensitive personal information.
This file contains standalone test functions that can be run independently
of the watsonx Orchestrate framework.
"""

import sys


def redact_account_numbers(text: str) -> str:
    """Redact account numbers to show only last 4 digits."""
    import re
    return re.sub(r"\b\d{8}\b", lambda match: f"****{match.group()[-4:]}", text)


def redact_sort_codes(text: str) -> str:
    """Redact sort codes to show only last 2 digits."""
    import re
    return re.sub(r"\b\d{2}-\d{2}-(\d{2})\b", r"**-**-\1", text)


def redact_ni_numbers(text: str) -> str:
    """Redact National Insurance numbers to show only last 4 characters."""
    import re
    return re.sub(r"\b[A-Z]{2}\d{6}[A-Z]\b", lambda match: f"******{match.group()[-4:]}", text)


def redact_emails(text: str) -> str:
    """Redact email addresses to show only first letter and masked domain."""
    import re

    def replacer(match: re.Match[str]) -> str:
        first_char = match.group(1)
        domain = match.group(2)
        domain_parts = domain.split(".")
        if len(domain_parts) > 1:
            masked_domain = "*" * len(domain_parts[0]) + "." + domain_parts[-1]
        else:
            masked_domain = domain
        return f"{first_char}***@{masked_domain}"

    return re.sub(r"\b([a-zA-Z])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b", replacer, text)


def redact_phone_numbers(text: str) -> str:
    """Redact phone numbers to show only last 4 digits."""
    import re
    return re.sub(r"\+44\s*\d{2,4}\s*\d{3,4}\s*(\d{4})\b", r"+44 ** **** \1", text)


def redact_credit_cards(text: str) -> str:
    """Redact credit card numbers to show only last 4 digits."""
    import re
    return re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b", r"****\1", text)


def redact_ibans(text: str) -> str:
    """Redact IBANs to show only country code and last 4 digits."""
    import re
    return re.sub(r"\b([A-Z]{2}\d{2})[A-Z0-9]{1,26}([A-Z0-9]{4})\b", r"\1********************\2", text)


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


def test_account_number_redaction():
    """Test account number redaction (8 digits → ****XXXX)."""
    print("\n🧪 Testing Account Number Redaction...")
    
    # Test case 1: Single account number
    text = "Your account number is 12345678"
    result = redact_account_numbers(text)
    expected = "Your account number is ****5678"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Single account: {text} → {result}")
    
    # Test case 2: Multiple account numbers
    text = "Transfer from 12345678 to 87654321"
    result = redact_account_numbers(text)
    expected = "Transfer from ****5678 to ****4321"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Multiple accounts: {text} → {result}")
    
    # Test case 3: No account numbers
    text = "Hello, how can I help you?"
    result = redact_account_numbers(text)
    assert result == text, f"Should not modify text without account numbers"
    print(f"  ✓ No accounts: Text unchanged")
    
    print("  ✅ All account number tests passed!")


def test_sort_code_redaction():
    """Test sort code redaction (XX-XX-XX → **-**-XX)."""
    print("\n🧪 Testing Sort Code Redaction...")
    
    # Test case 1: Single sort code
    text = "Sort code is 20-00-00"
    result = redact_sort_codes(text)
    expected = "Sort code is **-**-00"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Single sort code: {text} → {result}")
    
    # Test case 2: Multiple sort codes
    text = "From 20-00-00 to 40-50-60"
    result = redact_sort_codes(text)
    expected = "From **-**-00 to **-**-60"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Multiple sort codes: {text} → {result}")
    
    print("  ✅ All sort code tests passed!")


def test_ni_number_redaction():
    """Test National Insurance number redaction (LLNNNNNNL → ******NNNNL)."""
    print("\n🧪 Testing NI Number Redaction...")
    
    # Test case 1: Valid NI number
    text = "Your NI number is AB123456D"
    result = redact_ni_numbers(text)
    expected = "Your NI number is ******456D"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Valid NI: {text} → {result}")
    
    # Test case 2: Multiple NI numbers
    text = "NI numbers: AB123456D and CD789012E"
    result = redact_ni_numbers(text)
    expected = "NI numbers: ******456D and ******012E"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Multiple NI: {text} → {result}")
    
    print("  ✅ All NI number tests passed!")


def test_email_redaction():
    """Test email address redaction using the plugin's masking format."""
    print("\n🧪 Testing Email Redaction...")
    
    # Test case 1: Simple email
    text = "Email: emma.thompson@email.co.uk"
    result = redact_emails(text)
    expected = "Email: e***@*****.uk"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Simple email: {text} → {result}")
    
    # Test case 2: Multiple emails
    text = "Contact emma@email.co.uk or james@company.com"
    result = redact_emails(text)
    expected = "Contact e***@*****.uk or j***@*******.com"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Multiple emails: {text} → {result}")
    
    print("  ✅ All email tests passed!")


def test_phone_number_redaction():
    """Test phone number redaction (+44 XX XXXX XXXX → +44 ** **** XXXX)."""
    print("\n🧪 Testing Phone Number Redaction...")
    
    # Test case 1: UK mobile
    text = "Phone: +44 20 7946 0123"
    result = redact_phone_numbers(text)
    expected = "Phone: +44 ** **** 0123"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ UK phone: {text} → {result}")
    
    # Test case 2: Multiple phones
    text = "Call +44 20 7946 0123 or +44 7700 900123"
    result = redact_phone_numbers(text)
    expected = "Call +44 ** **** 0123 or +44 7700 900123"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Multiple phones: {text} → {result}")
    
    print("  ✅ All phone number tests passed!")


def test_credit_card_redaction():
    """Test credit card redaction (16 digits → ****XXXX)."""
    print("\n🧪 Testing Credit Card Redaction...")
    
    # Test case 1: Card with spaces
    text = "Card: 1234 5678 9012 3456"
    result = redact_credit_cards(text)
    expected = "Card: ****3456"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Card with spaces: {text} → {result}")
    
    # Test case 2: Card with dashes
    text = "Card: 1234-5678-9012-3456"
    result = redact_credit_cards(text)
    expected = "Card: ****3456"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ Card with dashes: {text} → {result}")
    
    print("  ✅ All credit card tests passed!")


def test_iban_redaction():
    """Test IBAN redaction (GB22XXXX...XXXX → GB22**...XXXX)."""
    print("\n🧪 Testing IBAN Redaction...")
    
    # Test case 1: UK IBAN
    text = "IBAN: GB29NWBK60161331926819"
    result = redact_ibans(text)
    expected = "IBAN: GB29********************6819"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"  ✓ UK IBAN: {text} → {result}")
    
    print("  ✅ All IBAN tests passed!")


def test_combined_redaction():
    """Test multiple PII types in one text."""
    print("\n🧪 Testing Combined Redaction...")
    
    text = """
    Customer: Emma Thompson
    Account: 12345678
    Sort Code: 20-00-00
    NI Number: AB123456D
    Email: emma.thompson@email.co.uk
    Phone: +44 20 7946 0123
    """
    
    result = apply_all_redactions(text)
    
    # Verify all redactions applied
    assert "****5678" in result, "Account number not redacted"
    assert "**-**-00" in result, "Sort code not redacted"
    assert "******456D" in result, "NI number not redacted"
    assert "e***@*****.uk" in result, "Email not redacted"
    assert "+44 ** **** 0123" in result, "Phone not redacted"
    
    # Verify original values not present
    assert "12345678" not in result, "Original account number still present"
    assert "20-00-00" not in result, "Original sort code still present"
    assert "AB123456D" not in result, "Original NI number still present"
    assert "emma.thompson@email.co.uk" not in result, "Original email still present"
    
    print(f"  ✓ Combined redaction successful")
    print(f"  ✓ All sensitive data redacted")
    print("  ✅ Combined redaction test passed!")


def run_all_tests():
    """Run all PII protection tests."""
    print("=" * 60)
    print("PII PROTECTION GUARDRAIL - TEST SUITE")
    print("=" * 60)
    
    try:
        test_account_number_redaction()
        test_sort_code_redaction()
        test_ni_number_redaction()
        test_email_redaction()
        test_phone_number_redaction()
        test_credit_card_redaction()
        test_iban_redaction()
        test_combined_redaction()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob

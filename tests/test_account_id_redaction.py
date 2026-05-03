"""
Test account ID redaction in PII protection guardrail.

This test verifies that account IDs like CUR-001-1234 are properly
redacted to CUR-***-1234 when the guardrail is applied.
"""

import sys
import os

# Add parent directory to path to import the guardrail
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugins.pii_protection_guardrail import redact_account_ids, apply_all_redactions


def test_account_id_redaction():
    """Test that account IDs are properly redacted."""
    
    # Test individual account ID types
    test_cases = [
        ("CUR-001-1234", "CUR-***-1234"),
        ("SAV-001-5678", "SAV-***-5678"),
        ("CC-001-9012", "CC-***-9012"),
        ("BUS-002-3456", "BUS-***-3456"),
    ]
    
    print("Testing individual account ID redaction:")
    for original, expected in test_cases:
        result = redact_account_ids(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {original} → {result} (expected: {expected})")
        assert result == expected, f"Failed: {original} → {result} (expected: {expected})"
    
    print("\nAll individual account ID tests passed!")


def test_account_ids_in_context():
    """Test account ID redaction in realistic banking responses."""
    
    test_cases = [
        (
            "Your accounts are: CUR-001-1234 (Current), SAV-001-5678 (Savings), CC-001-9012 (Credit Card)",
            "Your accounts are: CUR-***-1234 (Current), SAV-***-5678 (Savings), CC-***-9012 (Credit Card)"
        ),
        (
            "Account CUR-001-1234 has a balance of £4,250.50",
            "Account CUR-***-1234 has a balance of £4,250.50"
        ),
        (
            "Transfer from SAV-001-5678 to CUR-001-1234 completed",
            "Transfer from SAV-***-5678 to CUR-***-1234 completed"
        ),
    ]
    
    print("\nTesting account IDs in context:")
    for original, expected in test_cases:
        result = redact_account_ids(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Original: {original}")
        print(f"    Result:   {result}")
        print(f"    Expected: {expected}")
        assert result == expected, f"Failed context test"
    
    print("\nAll context tests passed!")


def test_full_redaction_pipeline():
    """Test that account IDs are redacted along with other PII."""
    
    text = """
    Customer Emma Thompson (emma.thompson@email.co.uk, +44 20 7946 0123)
    has the following accounts:
    - CUR-001-1234: Current Account (12345678, sort code: 20-00-00)
    - SAV-001-5678: Savings Account (87654321, sort code: 20-00-00)
    - CC-001-9012: Credit Card (5425233430109903)
    National Insurance: AB123456D
    IBAN: GB29NWBK60161331926819
    """
    
    result = apply_all_redactions(text)
    
    print("\nTesting full redaction pipeline:")
    print("Original text:")
    print(text)
    print("\nRedacted text:")
    print(result)
    
    # Verify account IDs are redacted
    assert "CUR-***-1234" in result, "CUR account ID not redacted"
    assert "SAV-***-5678" in result, "SAV account ID not redacted"
    assert "CC-***-9012" in result, "CC account ID not redacted"
    
    # Verify other PII is also redacted
    assert "****1234" in result or "****5678" in result, "Account numbers not redacted"
    assert "**-**-00" in result, "Sort codes not redacted"
    assert "e***@" in result, "Email not redacted"
    assert "+44 ** ****" in result, "Phone not redacted"
    assert "******456D" in result, "NI number not redacted"
    
    print("\n✓ Full pipeline test passed!")
    print("\nNote: Security notice is added by the guardrail plugin when redactions occur.")
    print("The notice will appear in actual agent responses: '🔒 For your security, some sensitive information has been masked in this response.'")


if __name__ == "__main__":
    test_account_id_redaction()
    test_account_ids_in_context()
    test_full_redaction_pipeline()
    print("\n" + "="*50)
    print("All account ID redaction tests passed! ✓")
    print("="*50)

# Made with Bob

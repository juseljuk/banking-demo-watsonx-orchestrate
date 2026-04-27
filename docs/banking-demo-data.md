# Banking Demo - Dummy Data Specification

This document provides comprehensive dummy data for all banking demo scenarios. This data will be used by the Python tools to simulate realistic banking operations without connecting to actual banking systems.

---

## Table of Contents

1. [Customer Profiles](#customer-profiles)
2. [Account Data](#account-data)
3. [Transaction Data](#transaction-data)
4. [Fraud Scenarios](#fraud-scenarios)
5. [Loan Application Data](#loan-application-data)
6. [Credit Bureau Data](#credit-bureau-data)
7. [Device & Location Data](#device--location-data)
8. [Demo Scenario Mappings](#demo-scenario-mappings)

---

## 1. Customer Profiles

### Customer 1: Emma Thompson (Primary Demo Customer)
```json
{
  "customer_id": "CUST-001",
  "first_name": "Emma",
  "last_name": "Thompson",
  "email": "emma.thompson@email.co.uk",
  "phone": "+44 20 7946 0123",
  "mobile": "+44 7700 900123",
  "date_of_birth": "1985-06-15",
  "ni_number_last_4": "456D",
  "address": {
    "street": "42 Kensington High Street",
    "city": "London",
    "postcode": "W8 5SA",
    "country": "United Kingdom"
  },
  "customer_since": "2018-03-15",
  "customer_tier": "Gold",
  "preferred_language": "English",
  "employment": {
    "status": "Employed",
    "employer": "Digital Solutions Ltd",
    "position": "Senior Software Engineer",
    "annual_income": 65000,
    "employment_length_years": 6
  },
  "credit_score": 742,
  "risk_profile": "Low"
}
```

### Customer 2: James Patel (Business Customer)
```json
{
  "customer_id": "CUST-002",
  "first_name": "James",
  "last_name": "Patel",
  "email": "james.patel@patelconsulting.co.uk",
  "phone": "+44 20 7946 0456",
  "mobile": "+44 7700 900456",
  "date_of_birth": "1978-11-22",
  "ni_number_last_4": "890C",
  "address": {
    "street": "15 Canary Wharf",
    "city": "London",
    "postcode": "E14 5AB",
    "country": "United Kingdom"
  },
  "customer_since": "2015-08-20",
  "customer_tier": "Platinum",
  "preferred_language": "English",
  "employment": {
    "status": "Self-Employed",
    "employer": "Patel Consulting Ltd",
    "position": "Managing Director",
    "annual_income": 125000,
    "employment_length_years": 12
  },
  "credit_score": 785,
  "risk_profile": "Low"
}
```

### Customer 3: Sophie Williams (Young Professional)
```json
{
  "customer_id": "CUST-003",
  "first_name": "Sophie",
  "last_name": "Williams",
  "email": "sophie.williams@email.co.uk",
  "phone": "+44 161 496 0789",
  "mobile": "+44 7700 900789",
  "date_of_birth": "1995-03-08",
  "ni_number_last_4": "234B",
  "address": {
    "street": "78 Deansgate",
    "city": "Manchester",
    "postcode": "M3 2BW",
    "country": "United Kingdom"
  },
  "customer_since": "2020-01-10",
  "customer_tier": "Silver",
  "preferred_language": "English",
  "employment": {
    "status": "Employed",
    "employer": "Creative Marketing Ltd",
    "position": "Marketing Coordinator",
    "annual_income": 32000,
    "employment_length_years": 3
  },
  "credit_score": 680,
  "risk_profile": "Medium"
}
```

---

## 2. Account Data

### Emma Thompson's Accounts

#### Current Account
```json
{
  "account_id": "CUR-001-1234",
  "customer_id": "CUST-001",
  "account_type": "Current Account",
  "account_name": "Premier Current Account",
  "account_number_masked": "****1234",
  "sort_code": "20-00-00",
  "account_number_full": "12345678",
  "iban": "GB29 NWBK 2000 0012 3456 78",
  "current_balance": 4250.50,
  "available_balance": 4250.50,
  "currency": "GBP",
  "status": "Active",
  "opened_date": "2018-03-15",
  "interest_rate": 0.01,
  "monthly_fee": 0.00,
  "overdraft_facility": true,
  "overdraft_limit": 500.00,
  "daily_withdrawal_limit": 500.00,
  "daily_transfer_limit": 10000.00
}
```

#### Savings Account
```json
{
  "account_id": "SAV-001-5678",
  "customer_id": "CUST-001",
  "account_type": "Savings Account",
  "account_name": "Instant Access Saver",
  "account_number_masked": "****5678",
  "sort_code": "20-00-00",
  "account_number_full": "87654321",
  "iban": "GB29 NWBK 2000 0087 6543 21",
  "current_balance": 18750.00,
  "available_balance": 18750.00,
  "currency": "GBP",
  "status": "Active",
  "opened_date": "2018-03-15",
  "interest_rate": 4.25,
  "aer": 4.33,
  "monthly_fee": 0.00,
  "minimum_balance": 0.00
}
```

#### Credit Card
```json
{
  "account_id": "CC-001-9012",
  "customer_id": "CUST-001",
  "account_type": "Credit Card",
  "account_name": "Platinum Rewards Card",
  "card_number_masked": "****9012",
  "card_number_full": "5425233430109903",
  "credit_limit": 12000.00,
  "current_balance": 1856.75,
  "available_credit": 10143.25,
  "currency": "GBP",
  "status": "Active",
  "opened_date": "2019-06-01",
  "apr": 18.9,
  "minimum_payment": 55.00,
  "payment_due_date": "2026-05-15",
  "last_payment_date": "2026-04-15",
  "last_payment_amount": 400.00,
  "rewards_points": 18650,
  "cash_advance_limit": 2400.00
}
```

### James Patel's Accounts

#### Business Current Account
```json
{
  "account_id": "BUS-002-3456",
  "customer_id": "CUST-002",
  "account_type": "Business Current Account",
  "account_name": "Patel Consulting Ltd",
  "account_number_masked": "****3456",
  "sort_code": "20-00-00",
  "account_number_full": "34567890",
  "iban": "GB29 NWBK 2000 0034 5678 90",
  "current_balance": 68450.25,
  "available_balance": 68450.25,
  "currency": "GBP",
  "status": "Active",
  "opened_date": "2015-08-20",
  "interest_rate": 0.05,
  "monthly_fee": 12.50,
  "daily_withdrawal_limit": 5000.00,
  "daily_transfer_limit": 25000.00
}
```

#### Business Savings Account
```json
{
  "account_id": "SAV-002-7890",
  "customer_id": "CUST-002",
  "account_type": "Business Savings Account",
  "account_name": "Business Reserve Account",
  "account_number_masked": "****7890",
  "sort_code": "20-00-00",
  "account_number_full": "78901234",
  "iban": "GB29 NWBK 2000 0078 9012 34",
  "current_balance": 125600.00,
  "available_balance": 125600.00,
  "currency": "GBP",
  "status": "Active",
  "opened_date": "2015-08-20",
  "interest_rate": 3.75,
  "aer": 3.82,
  "monthly_fee": 0.00
}
```

---

## 3. Transaction Data

### Emma Thompson's Recent Transactions (Current Account)

```json
[
  {
    "transaction_id": "TXN-20260425-001",
    "account_id": "CUR-001-1234",
    "date": "2026-04-25",
    "time": "14:32:15",
    "type": "Debit Card",
    "category": "Groceries",
    "merchant": "Waitrose",
    "description": "Grocery Purchase",
    "amount": -87.45,
    "balance_after": 4250.50,
    "status": "Posted",
    "location": "London, UK"
  },
  {
    "transaction_id": "TXN-20260424-002",
    "account_id": "CUR-001-1234",
    "date": "2026-04-24",
    "time": "09:15:30",
    "type": "Faster Payment",
    "category": "Salary",
    "merchant": "Digital Solutions Ltd",
    "description": "Salary Payment",
    "amount": 3950.00,
    "balance_after": 4337.95,
    "status": "Posted",
    "location": "BACS Transfer"
  },
  {
    "transaction_id": "TXN-20260423-003",
    "account_id": "CUR-001-1234",
    "date": "2026-04-23",
    "time": "18:45:22",
    "type": "Debit Card",
    "category": "Dining",
    "merchant": "The Ivy Restaurant",
    "description": "Restaurant",
    "amount": -65.50,
    "balance_after": 387.95,
    "status": "Posted",
    "location": "London, UK"
  },
  {
    "transaction_id": "TXN-20260422-004",
    "account_id": "CUR-001-1234",
    "date": "2026-04-22",
    "time": "16:20:10",
    "type": "Direct Debit",
    "category": "Utilities",
    "merchant": "British Gas",
    "description": "Gas & Electric Bill",
    "amount": -125.80,
    "balance_after": 453.45,
    "status": "Posted",
    "location": "Direct Debit"
  },
  {
    "transaction_id": "TXN-20260421-005",
    "account_id": "CUR-001-1234",
    "date": "2026-04-21",
    "time": "11:30:45",
    "type": "Debit Card",
    "category": "Petrol",
    "merchant": "Shell Petrol Station",
    "description": "Fuel Purchase",
    "amount": -45.30,
    "balance_after": 579.25,
    "status": "Posted",
    "location": "London, UK"
  }
]
```

### Pending Deposits

```json
[
  {
    "transaction_id": "TXN-PENDING-001",
    "account_id": "CUR-001-1234",
    "date": "2026-04-25",
    "time": "16:00:00",
    "type": "Cheque Deposit",
    "category": "Cheque",
    "description": "Mobile Cheque Deposit",
    "amount": 1200.00,
    "status": "Pending",
    "expected_clear_date": "2026-04-26",
    "cheque_number": "000123"
  }
]
```

---

## 4. Fraud Scenarios

### Scenario 1: Suspicious International Transfer (HIGH RISK)

```json
{
  "transaction_id": "TXN-FRAUD-001",
  "account_id": "CUR-001-1234",
  "customer_id": "CUST-001",
  "date": "2026-04-26",
  "time": "02:15:30",
  "type": "International Transfer",
  "recipient": {
    "name": "Unknown Recipient",
    "iban": "NG12 3456 7890 1234 5678 90",
    "bank": "International Bank Ltd",
    "country": "Nigeria",
    "swift_code": "INTLNGLA"
  },
  "amount": 3500.00,
  "currency": "GBP",
  "status": "Blocked",
  "risk_analysis": {
    "risk_score": 92,
    "risk_level": "HIGH",
    "fraud_probability": 0.92,
    "triggered_rules": [
      "Large international transfer",
      "New recipient",
      "High-risk country",
      "Unusual time (2 AM)",
      "9x higher than average transaction",
      "Different device/location"
    ],
    "customer_profile_analysis": {
      "average_transaction": 400.00,
      "typical_transfer_domestic": true,
      "typical_transfer_amount": 150.00,
      "international_transfers_last_year": 0,
      "new_recipient": true
    },
    "device_analysis": {
      "device_id": "DEV-UNKNOWN-001",
      "device_type": "Desktop",
      "browser": "Chrome 120",
      "os": "Windows 11",
      "known_device": false,
      "location": "Lagos, Nigeria",
      "ip_address": "197.210.xxx.xxx",
      "vpn_detected": true
    },
    "recommended_action": "BLOCK",
    "confidence": 0.95
  },
  "action_taken": {
    "blocked": true,
    "customer_notified": true,
    "notification_channels": ["SMS", "Email", "Mobile App"],
    "case_created": true,
    "case_id": "FRAUD-CASE-001",
    "assigned_to": "Fraud Investigation Team"
  }
}
```

### Scenario 2: Account Takeover Pattern (HIGH RISK)

```json
{
  "incident_id": "FRAUD-INC-002",
  "customer_id": "CUST-001",
  "account_id": "CUR-001-1234",
  "date": "2026-04-26",
  "incident_type": "Account Takeover Attempt",
  "events": [
    {
      "event_id": "EVT-001",
      "timestamp": "2026-04-26T01:30:00Z",
      "type": "Failed Login",
      "location": "Moscow, Russia",
      "ip_address": "185.220.xxx.xxx",
      "device": "Unknown Mobile Device"
    },
    {
      "event_id": "EVT-002",
      "timestamp": "2026-04-26T01:32:15Z",
      "type": "Failed Login",
      "location": "Moscow, Russia",
      "ip_address": "185.220.xxx.xxx",
      "device": "Unknown Mobile Device"
    },
    {
      "event_id": "EVT-003",
      "timestamp": "2026-04-26T01:35:45Z",
      "type": "Failed Login",
      "location": "Moscow, Russia",
      "ip_address": "185.220.xxx.xxx",
      "device": "Unknown Mobile Device"
    },
    {
      "event_id": "EVT-004",
      "timestamp": "2026-04-26T01:40:00Z",
      "type": "Password Reset Request",
      "location": "Moscow, Russia",
      "ip_address": "185.220.xxx.xxx"
    },
    {
      "event_id": "EVT-005",
      "timestamp": "2026-04-26T01:45:30Z",
      "type": "Large Transfer Attempt",
      "amount": 4000.00,
      "currency": "GBP",
      "location": "Moscow, Russia",
      "ip_address": "185.220.xxx.xxx",
      "status": "Blocked by System"
    }
  ],
  "risk_analysis": {
    "risk_score": 98,
    "risk_level": "CRITICAL",
    "pattern_detected": "Account Takeover",
    "indicators": [
      "Multiple failed login attempts",
      "Foreign location (Russia)",
      "Password reset after failed logins",
      "Immediate large transfer attempt",
      "Unknown device",
      "Time: 1-2 AM (unusual for customer)"
    ]
  },
  "action_taken": {
    "account_locked": true,
    "customer_notified": true,
    "notification_sent": "2026-04-26T01:46:00Z",
    "notification_channels": ["Phone Call", "SMS", "Email"],
    "case_created": true,
    "case_id": "FRAUD-CASE-002",
    "priority": "Critical",
    "assigned_to": "Senior Fraud Investigator"
  }
}
```

### Scenario 3: Legitimate Transaction (LOW RISK)

```json
{
  "transaction_id": "TXN-LEGIT-001",
  "account_id": "CUR-001-1234",
  "customer_id": "CUST-001",
  "date": "2026-04-26",
  "time": "10:30:00",
  "type": "Debit Card Purchase",
  "merchant": "John Lewis",
  "category": "Electronics",
  "amount": 899.00,
  "currency": "GBP",
  "location": "London, UK",
  "status": "Approved",
  "risk_analysis": {
    "risk_score": 15,
    "risk_level": "LOW",
    "fraud_probability": 0.05,
    "triggered_rules": [],
    "customer_profile_analysis": {
      "known_merchant": true,
      "typical_location": true,
      "typical_time": true,
      "within_spending_pattern": true,
      "previous_purchases_at_merchant": 3
    },
    "device_analysis": {
      "device_id": "DEV-EMMA-IPHONE",
      "device_type": "Mobile",
      "known_device": true,
      "location": "London, UK",
      "location_matches_home": true
    },
    "recommended_action": "APPROVE",
    "confidence": 0.98
  },
  "action_taken": {
    "approved": true,
    "real_time_processing": true,
    "processing_time_ms": 245
  }
}
```

---

## 5. Loan Application Data

### Scenario 1: Personal Loan - Emma Thompson (APPROVED)

```json
{
  "application_id": "LOAN-APP-001",
  "customer_id": "CUST-001",
  "application_date": "2026-04-26",
  "loan_type": "Personal Loan",
  "loan_purpose": "Home Improvements",
  "requested_amount": 20000.00,
  "requested_term_months": 60,
  "application_status": "Approved",
  "currency": "GBP",
  
  "applicant_info": {
    "employment_status": "Employed",
    "employer": "Digital Solutions Ltd",
    "position": "Senior Software Engineer",
    "employment_length_years": 6,
    "annual_income": 65000.00,
    "monthly_income": 5416.67,
    "other_income": 0.00
  },
  
  "financial_profile": {
    "credit_score": 742,
    "credit_score_source": "Experian UK",
    "existing_debt": {
      "credit_cards": 1856.75,
      "car_loan": 0.00,
      "student_loans": 0.00,
      "mortgage": 0.00,
      "other": 0.00,
      "total": 1856.75
    },
    "monthly_debt_payments": 55.00,
    "debt_to_income_ratio": 0.010,
    "debt_to_income_percentage": "1.0%",
    "payment_history": "Excellent",
    "bankruptcies": 0,
    "collections": 0,
    "late_payments_12_months": 0
  },
  
  "eligibility_assessment": {
    "eligible": true,
    "approved_amount": 30000.00,
    "max_approved_amount": 35000.00,
    "approval_factors": [
      "Excellent credit score (742)",
      "Very low debt-to-income ratio (0.6%)",
      "Stable employment (6 years)",
      "High income ($145,000)",
      "Perfect payment history",
      "No derogatory marks"
    ],
    "risk_rating": "A+ (Excellent)",
    "approval_confidence": 0.98
  },
  
  "loan_offers": [
    {
      "offer_id": "OFFER-001-A",
      "loan_amount": 25000.00,
      "term_months": 36,
      "apr": 7.5,
      "monthly_payment": 775.00,
      "total_interest": 2900.00,
      "total_repayment": 27900.00,
      "recommended": false
    },
    {
      "offer_id": "OFFER-001-B",
      "loan_amount": 25000.00,
      "term_months": 60,
      "apr": 8.2,
      "monthly_payment": 509.00,
      "total_interest": 5540.00,
      "total_repayment": 30540.00,
      "recommended": true
    },
    {
      "offer_id": "OFFER-001-C",
      "loan_amount": 25000.00,
      "term_months": 84,
      "apr": 9.1,
      "monthly_payment": 395.00,
      "total_interest": 8180.00,
      "total_repayment": 33180.00,
      "recommended": false
    }
  ],
  
  "selected_offer": "OFFER-001-B",
  
  "approval_workflow": {
    "status": "Approved",
    "approval_date": "2026-04-26",
    "approval_time": "10:45:00",
    "processing_time_minutes": 15,
    "automated_approval": true,
    "manual_review_required": false,
    "compliance_checks": {
      "identity_verified": true,
      "income_verified": true,
      "credit_check_completed": true,
      "aml_check_passed": true,
      "ofac_screening_passed": true,
      "fraud_check_passed": true
    },
    "next_steps": [
      "Review and sign loan agreement",
      "E-signature via DocuSign",
      "Funds disbursement within 24 hours",
      "First payment due: June 1, 2026"
    ]
  }
}
```

### Scenario 2: Business Loan - Michael Chen (PENDING REVIEW)

```json
{
  "application_id": "LOAN-APP-002",
  "customer_id": "CUST-002",
  "application_date": "2026-04-26",
  "loan_type": "Business Term Loan",
  "loan_purpose": "Equipment Purchase",
  "requested_amount": 500000.00,
  "requested_term_months": 60,
  "application_status": "Pending Manual Review",
  
  "business_info": {
    "business_name": "Chen Consulting LLC",
    "business_type": "Limited Liability Company",
    "industry": "Professional Services - Consulting",
    "years_in_business": 12,
    "number_of_employees": 8,
    "annual_revenue": 1250000.00,
    "annual_expenses": 780000.00,
    "net_income": 470000.00,
    "tax_id": "XX-XXXXXXX"
  },
  
  "applicant_info": {
    "role": "Owner",
    "ownership_percentage": 100,
    "personal_guarantee": true,
    "personal_credit_score": 785,
    "personal_annual_income": 280000.00
  },
  
  "financial_profile": {
    "business_credit_score": 680,
    "credit_score_source": "Dun & Bradstreet",
    "existing_business_debt": {
      "term_loans": 0.00,
      "lines_of_credit": 50000.00,
      "equipment_financing": 0.00,
      "other": 0.00,
      "total": 50000.00
    },
    "monthly_debt_payments": 2500.00,
    "debt_service_coverage_ratio": 2.8,
    "cash_flow_analysis": {
      "average_monthly_revenue": 104166.67,
      "average_monthly_expenses": 65000.00,
      "average_monthly_net": 39166.67,
      "cash_reserves": 156789.00,
      "months_of_reserves": 4.0
    }
  },
  
  "collateral": {
    "type": "Equipment",
    "description": "Manufacturing equipment and machinery",
    "estimated_value": 650000.00,
    "loan_to_value_ratio": 0.77,
    "appraisal_required": true,
    "appraisal_status": "Pending"
  },
  
  "eligibility_assessment": {
    "eligible": true,
    "preliminary_approval": true,
    "approved_amount": 500000.00,
    "approval_factors": [
      "Strong business credit (680)",
      "Excellent personal credit (785)",
      "12 years in business",
      "Positive cash flow",
      "Good debt service coverage ratio (2.8)",
      "Adequate collateral (77% LTV)",
      "Strong personal guarantee"
    ],
    "risk_rating": "B+ (Good)",
    "manual_review_required": true,
    "review_reasons": [
      "Loan amount exceeds $250,000",
      "Requires collateral appraisal",
      "Business loan requires underwriter review"
    ]
  },
  
  "preliminary_offer": {
    "loan_amount": 500000.00,
    "term_months": 60,
    "estimated_apr": 9.5,
    "estimated_monthly_payment": 10450.00,
    "estimated_total_interest": 127000.00,
    "estimated_total_repayment": 627000.00,
    "note": "Final terms subject to underwriter approval and collateral appraisal"
  },
  
  "approval_workflow": {
    "status": "Pending Manual Review",
    "submission_date": "2026-04-26",
    "submission_time": "11:30:00",
    "automated_processing_complete": true,
    "compliance_checks": {
      "identity_verified": true,
      "business_verified": true,
      "beneficial_ownership_verified": true,
      "aml_check_passed": true,
      "ofac_screening_passed": true,
      "fraud_check_passed": true
    },
    "pending_items": [
      "Underwriter review",
      "Collateral appraisal",
      "Financial statement verification",
      "Equipment purchase documentation"
    ],
    "estimated_decision_date": "2026-04-29",
    "assigned_underwriter": "Senior Commercial Underwriter",
    "next_steps": [
      "Underwriter will contact within 24 hours",
      "Schedule collateral appraisal",
      "Provide additional documentation if requested",
      "Estimated approval: 2-3 business days"
    ]
  }
}
```

### Scenario 3: Car Finance - Sophie Williams (CONDITIONAL APPROVAL)

```json
{
  "application_id": "LOAN-APP-003",
  "customer_id": "CUST-003",
  "application_date": "2026-04-26",
  "loan_type": "Hire Purchase Agreement",
  "loan_purpose": "Vehicle Purchase",
  "requested_amount": 22000.00,
  "requested_term_months": 60,
  "application_status": "Conditional Approval",
  "currency": "GBP",
  
  "vehicle_info": {
    "year": 2024,
    "make": "Volkswagen",
    "model": "Golf",
    "trim": "SE",
    "registration": "AB24 XYZ",
    "mileage": 12000,
    "condition": "Used - Excellent",
    "purchase_price": 25000.00,
    "deposit": 3000.00,
    "part_exchange_value": 0.00
  },
  
  "applicant_info": {
    "employment_status": "Employed",
    "employer": "Creative Marketing Ltd",
    "position": "Marketing Coordinator",
    "employment_length_years": 3,
    "annual_income": 32000.00,
    "monthly_income": 2666.67,
    "other_income": 0.00
  },
  
  "financial_profile": {
    "credit_score": 680,
    "credit_score_source": "Equifax UK",
    "existing_debt": {
      "credit_cards": 2400.00,
      "student_loans": 15500.00,
      "car_finance": 0.00,
      "other": 0.00,
      "total": 17900.00
    },
    "monthly_debt_payments": 285.00,
    "debt_to_income_ratio": 0.107,
    "debt_to_income_percentage": "10.7%",
    "payment_history": "Good",
    "late_payments_12_months": 1,
    "collections": 0
  },
  
  "eligibility_assessment": {
    "eligible": true,
    "conditional_approval": true,
    "approved_amount": 22000.00,
    "conditions": [
      "Proof of income (3 months payslips)",
      "Proof of address (council tax bill)",
      "Vehicle inspection report",
      "Proof of insurance"
    ],
    "approval_factors": [
      "Good credit score (680)",
      "Stable employment (3 years)",
      "Reasonable debt-to-income (10.7%)",
      "Adequate deposit (12%)"
    ],
    "risk_factors": [
      "One late payment in last 12 months",
      "Limited credit history (young professional)",
      "Higher DTI with new finance payment"
    ],
    "risk_rating": "B (Acceptable)",
    "approval_confidence": 0.85
  },
  
  "finance_offer": {
    "finance_amount": 22000.00,
    "term_months": 60,
    "apr": 7.9,
    "monthly_payment": 445.00,
    "total_interest": 4700.00,
    "total_repayment": 26700.00,
    "loan_to_value_ratio": 0.88,
    "conditions_must_be_met_by": "2026-05-03"
  },
  
  "approval_workflow": {
    "status": "Conditional Approval",
    "approval_date": "2026-04-26",
    "approval_time": "14:20:00",
    "processing_time_minutes": 25,
    "automated_approval": false,
    "manual_review_completed": true,
    "compliance_checks": {
      "identity_verified": true,
      "income_preliminary_verified": true,
      "credit_check_completed": true,
      "vehicle_value_verified": true,
      "fraud_check_passed": true
    },
    "pending_documents": [
      "3 months payslips",
      "Council tax bill or tenancy agreement",
      "Vehicle inspection report",
      "Proof of motor insurance"
    ],
    "next_steps": [
      "Upload required documents within 7 days",
      "Complete vehicle inspection",
      "Obtain motor insurance quote",
      "Final approval within 24 hours of document submission",
      "Funds available for vehicle purchase"
    ]
  }
}
```

---

## 6. Credit Bureau Data

### Emma Thompson - Credit Report Summary

```json
{
  "customer_id": "CUST-001",
  "report_date": "2026-04-26",
  "bureau": "Experian UK",
  
  "credit_score": {
    "score": 742,
    "score_range": "0-999",
    "rating": "Good",
    "percentile": 68,
    "factors_affecting_score": [
      "Excellent payment history",
      "Low credit utilization (15%)",
      "Good length of credit history (8 years)",
      "Limited recent credit searches"
    ]
  },
  
  "credit_accounts": [
    {
      "account_type": "Credit Card",
      "creditor": "Barclaycard",
      "account_number": "****9012",
      "opened_date": "2019-06-01",
      "credit_limit": 12000.00,
      "current_balance": 1856.75,
      "utilization": 15.5,
      "status": "Open",
      "payment_status": "Current",
      "months_reviewed": 60,
      "late_payments": 0
    },
    {
      "account_type": "Credit Card",
      "creditor": "American Express",
      "account_number": "****3456",
      "opened_date": "2020-03-15",
      "credit_limit": 8000.00,
      "current_balance": 0.00,
      "utilization": 0.0,
      "status": "Open",
      "payment_status": "Current",
      "months_reviewed": 48,
      "late_payments": 0
    },
    {
      "account_type": "Car Finance",
      "creditor": "Santander Consumer Finance",
      "account_number": "****7890",
      "opened_date": "2020-08-01",
      "original_amount": 18000.00,
      "current_balance": 0.00,
      "status": "Closed - Settled",
      "payment_status": "Paid in Full",
      "months_reviewed": 48,
      "late_payments": 0,
      "settled_date": "2024-08-01"
    }
  ],
  
  "credit_searches": [
    {
      "date": "2026-04-26",
      "creditor": "First National Bank UK",
      "search_type": "Hard",
      "reason": "Personal Loan Application"
    },
    {
      "date": "2025-11-15",
      "creditor": "Tesco Bank",
      "search_type": "Soft",
      "reason": "Quotation Search"
    }
  ],
  
  "public_records": {
    "ccjs": 0,
    "bankruptcies": 0,
    "ivas": 0,
    "defaults": 0
  },
  
  "payment_history": {
    "total_accounts": 3,
    "accounts_in_good_standing": 3,
    "on_time_payment_percentage": 100,
    "late_payments_30_days": 0,
    "late_payments_60_days": 0,
    "late_payments_90_days": 0
  }
}
```

---

## 7. Device & Location Data

### Known Devices - Emma Thompson

```json
[
  {
    "device_id": "DEV-EMMA-IPHONE",
    "device_type": "Mobile",
    "device_name": "Emma's iPhone 14 Pro",
    "os": "iOS 17.4",
    "browser": "Safari",
    "first_seen": "2023-09-15",
    "last_seen": "2026-04-26",
    "status": "Active",
    "trusted": true,
    "typical_locations": [
      "London, UK",
      "Kensington, London"
    ],
    "typical_usage_hours": "07:00-23:00"
  },
  {
    "device_id": "DEV-EMMA-MACBOOK",
    "device_type": "Desktop",
    "device_name": "Emma's MacBook Pro",
    "os": "macOS Sonoma 14.4",
    "browser": "Chrome 122",
    "first_seen": "2021-05-20",
    "last_seen": "2026-04-25",
    "status": "Active",
    "trusted": true,
    "typical_locations": [
      "London, UK"
    ],
    "typical_usage_hours": "08:00-18:00"
  }
]
```

### Suspicious Device - Fraud Scenario

```json
{
  "device_id": "DEV-UNKNOWN-001",
  "device_type": "Desktop",
  "device_name": "Unknown Windows PC",
  "os": "Windows 11",
  "browser": "Chrome 120",
  "first_seen": "2026-04-26",
  "last_seen": "2026-04-26",
  "status": "Blocked",
  "trusted": false,
  "location": "Lagos, Nigeria",
  "ip_address": "197.210.xxx.xxx",
  "vpn_detected": true,
  "proxy_detected": true,
  "risk_indicators": [
    "First time device",
    "Foreign location",
    "VPN usage",
    "Unusual time of access",
    "Multiple failed login attempts"
  ],
  "risk_score": 95
}
```

---

## 8. Demo Scenario Mappings

### Scenario 1: Simple Account Inquiry
**Customer Request**: "What's my current account balance?"

**Data Used**:
- Customer: Emma Thompson (CUST-001)
- Account: CUR-001-1234
- Current Balance: £4,250.50

**Expected Response**:
```
Your current account (****1234) has a balance of £4,250.50
and an available balance of £4,250.50.
```

---

### Scenario 2: Multi-Step Request
**Customer Request**: "Transfer £1,500 to my savings, check pending deposits, and tell me when my credit card payment is due."

**Data Used**:
- Customer: Emma Thompson (CUST-001)
- From Account: CUR-001-1234 (Balance: £4,250.50)
- To Account: SAV-001-5678 (Balance: £18,750.00)
- Pending Deposit: £1,200 (clears 2026-04-26)
- Credit Card: CC-001-9012 (Due: 2026-05-15, Amount: £55.00)

**Expected Response**:
```
✓ Successfully transferred £1,500 from current account (****1234) to savings (****5678)
  - New current account balance: £2,750.50
  - New savings balance: £20,250.00

✓ You have 1 pending deposit:
  - Amount: £1,200.00
  - Expected to clear: 26 April 2026

✓ Credit card payment information:
  - Card: ****9012
  - Payment due: 15 May 2026
  - Minimum payment: £55.00
  - Current balance: £1,856.75
```

---

### Scenario 3: Fraud Detection - Suspicious Transaction
**Trigger**: Large international transfer attempt

**Data Used**:
- Transaction: TXN-FRAUD-001
- Risk Score: 92/100
- Risk Level: HIGH
- Action: BLOCKED

**Expected Response**:
```
⚠️ SECURITY ALERT

We've detected and blocked a suspicious transaction on your account:
- Amount: £3,500.00
- Type: International transfer
- Destination: Nigeria
- Time: 2:15 AM

This transaction was blocked because:
• It's 9x larger than your typical transactions
• New international recipient
• Unusual time of day
• Different device and location

Your account is secure. If you did not attempt this transaction,
no action is needed. If you did attempt this transfer, please
contact us on 0800 XXX XXXX to verify.

Case ID: FRAUD-CASE-001
```

---

### Scenario 4: Personal Loan Application
**Customer Request**: "I'd like to apply for a £20,000 personal loan for home improvements."

**Data Used**:
- Customer: Emma Thompson (CUST-001)
- Credit Score: 742
- Annual Income: £65,000
- DTI Ratio: 1.0%
- Application: LOAN-APP-001

**Expected Response**:
```
Great news! Based on your excellent credit profile, you're pre-approved
for a personal loan.

Your Profile:
✓ Credit Score: 742 (Good)
✓ Debt-to-Income Ratio: 1.0% (Excellent)
✓ Employment: 6 years at Digital Solutions Ltd
✓ Annual Income: £65,000

You're approved for up to £25,000. Here are your loan options for £20,000:

Option 1: 3-Year Term
• Monthly Payment: £618
• APR: 6.9%
• Total Interest: £2,248
• Total Repayment: £22,248

Option 2: 5-Year Term (Recommended) ⭐
• Monthly Payment: £400
• APR: 7.5%
• Total Interest: £4,000
• Total Repayment: £24,000

Option 3: 7-Year Term
• Monthly Payment: £310
• APR: 8.4%
• Total Interest: £6,040
• Total Repayment: £26,040

Would you like to proceed with one of these options?
```

---

## Data Files Structure

All this data should be stored in JSON files for easy access by the demo tools:

```
data/
├── customers.json          # Customer profiles
├── accounts.json           # Account information
├── transactions.json       # Transaction history
├── fraud_scenarios.json    # Fraud detection scenarios
├── loan_applications.json  # Loan application data
├── credit_reports.json     # Credit bureau data
└── devices.json           # Device and location data
```

---

## Usage in Python Tools

Example of how tools will access this data:

```python
import json
from typing import Dict, Any

# Load data files
with open('data/customers.json', 'r') as f:
    CUSTOMERS = json.load(f)

with open('data/accounts.json', 'r') as f:
    ACCOUNTS = json.load(f)

@tool
def check_account_balance(account_id: str) -> Dict[str, Any]:
    """Check account balance using dummy data."""
    account = ACCOUNTS.get(account_id)
    if not account:
        return {
            "status": "error",
            "message": f"Account {account_id} not found"
        }
    
    return {
        "status": "success",
        "account_id": account["account_id"],
        "account_type": account["account_type"],
        "account_number_masked": account["account_number_masked"],
        "current_balance": account["current_balance"],
        "available_balance": account["available_balance"],
        "currency": account["currency"]
    }
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-26  
**Created By**: Bob (AI Planning Agent)  
**Status**: Ready for Implementation
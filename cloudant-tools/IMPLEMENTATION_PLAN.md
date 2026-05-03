# Cloudant Tools Implementation Plan

## Objective

Replace the current MCP-server-based demo integrations with a new standalone Python tool implementation under [`cloudant-tools`](cloudant-tools) backed by IBM Cloudant on IBM Cloud.

This plan focuses on:

- designing the Cloudant data architecture
- mapping current MCP capabilities to standalone Python tools
- defining a clean project structure for implementation
- planning secure access patterns for IBM Cloudant
- avoiding implementation at this stage

---

## 1. Current State Summary

The existing toolkit servers read static JSON files and simulate backend behavior:

- [`toolkits/core_banking_server.py:59`](toolkits/core_banking_server.py:59) exposes core banking operations
- [`toolkits/fraud_detection_server.py:35`](toolkits/fraud_detection_server.py:35) exposes fraud/risk operations
- [`toolkits/loan_processing_server.py:35`](toolkits/loan_processing_server.py:35) exposes lending operations

The source data currently lives in:

- [`data/customers.json`](data/customers.json)
- [`data/accounts.json`](data/accounts.json)
- [`data/transactions.json`](data/transactions.json)
- [`data/credit_reports.json`](data/credit_reports.json)
- [`data/devices.json`](data/devices.json)
- [`data/fraud_scenarios.json`](data/fraud_scenarios.json)
- [`data/loan_applications.json`](data/loan_applications.json)

### Key observations

1. The current data is entity-oriented, but the JSON shape is inconsistent:
   - some files are maps keyed by ID, e.g. [`data/customers.json`](data/customers.json)
   - some files are arrays, e.g. [`data/transactions.json`](data/transactions.json)

2. Current MCP tools are a mix of:
   - read-only query tools
   - calculated/derived tools
   - simulated write/workflow tools

3. Some capabilities are placeholders rather than real persisted operations:
   - [`transfer_funds`](toolkits/core_banking_server.py:368) computes balances but does not persist
   - [`block_transaction`](toolkits/fraud_detection_server.py:364) returns a fake case ID
   - [`initiate_loan_approval`](toolkits/loan_processing_server.py:619) creates a generated application ID but does not save it

4. Sensitive data currently exists in raw form in demo JSON:
   - full PIN in [`data/customers.json:4`](data/customers.json:4)
   - full NI number in [`data/customers.json:11`](data/customers.json:11)
   - full account/card numbers in [`data/accounts.json:8`](data/accounts.json:8) and [`data/accounts.json:45`](data/accounts.json:45)

For this demo, that full PII can remain available in Cloudant seed data and tool responses because PII masking is intentionally demonstrated through guardrail plugins rather than through the persistence layer.

---

## 2. Design Principles for the New Cloudant-Based Solution

### 2.1 Functional principles

The new solution should:

- expose standalone Python tools instead of MCP server tools
- read and write to Cloudant directly
- preserve the existing demo behavior where useful
- convert simulated flows into persisted domain operations
- support both query tools and state-changing tools

### 2.2 Data principles

The Cloudant model should:

- use one JSON document per domain entity or event
- support efficient lookup by primary IDs and common query paths
- separate mutable business state from immutable event history
- preserve enough denormalized data for fast tool responses
- avoid joins where possible, since Cloudant is document-first

### 2.3 Demo security principles

The implementation should:

- preserve full demo PII in Cloudant where needed to support guardrail demonstrations
- allow standalone Python tools to return full values when the demo flow requires it
- rely on guardrail plugins for masking/redaction demonstrations rather than data-layer masking
- use IAM/API-key based Cloudant access via IBM Cloud credentials
- isolate service credentials in environment variables or watsonx Orchestrate connections
- define audit/event records for sensitive actions where useful for traceability

---

## 3. Proposed Cloudant Database Architecture

## Recommended approach: multiple logical databases

Use separate Cloudant databases by domain, rather than one monolithic database.

### Proposed databases

1. `bank_customers`
2. `bank_accounts`
3. `bank_transactions`
4. `bank_credit`
5. `bank_devices`
6. `bank_fraud`
7. `bank_loans`
8. `bank_audit`

This is the cleanest option because it aligns with the current tool domains and reduces design complexity.

### Why multiple databases

Benefits:

- clearer separation of concerns
- simpler index design per domain
- easier export/import and environment seeding
- lower risk of index sprawl
- cleaner least-privilege and operational ownership later

Tradeoff:

- cross-domain queries are application-side, not database-side

That tradeoff is acceptable here because the current tools already assemble data in Python.

---

## 4. Document Model by Database

## 4.1 `bank_customers`

### Document type: customer profile

One customer per document.

#### Example ID strategy

- `_id = customer:CUST-001`

#### Fields

- `doc_type`: `customer`
- `customer_id`
- `first_name`
- `last_name`
- `email`
- `phone`
- `mobile`
- `date_of_birth`
- `customer_since`
- `customer_tier`
- `preferred_language`
- `risk_profile`
- `employment`
- `address`
- `auth`
- `identifiers`
- `derived`

#### Demo-sensitive field handling

For this demo, the customer document may retain raw values from [`data/customers.json`](data/customers.json) so that guardrail plugins can demonstrate masking and redaction behavior against realistic source data.

That means the seeded customer document may keep:

- plaintext PIN from [`data/customers.json:4`](data/customers.json:4)
- full NI number from [`data/customers.json:11`](data/customers.json:11)
- unmasked contact data and address fields

A demo-oriented customer structure can still group these fields clearly:

#### Suggested auth block

```json
{
  "auth": {
    "pin": "1234",
    "status": "active"
  }
}
```

#### Suggested identifiers block

```json
{
  "identifiers": {
    "ni_number_full": "AB123456D",
    "ni_number_last_4": "456D"
  }
}
```

Note: if this plan is later evolved beyond demo scope, these fields should be redesigned for hashing, masking, or encryption.

### Required indexes

- by `customer_id`
- by `email`
- by `risk_profile`
- by `customer_tier`

---

## 4.2 `bank_accounts`

### Document type: account

One account per document.

#### Example ID strategy

- `_id = account:CUR-001-1234`

#### Fields

- `doc_type`: `account`
- `account_id`
- `customer_id`
- `account_type`
- `account_name`
- `currency`
- `status`
- `opened_date`
- `balances`
- `product_terms`
- `identifiers`
- `limits`
- `servicing`

### Normalize current account fields

Current account data from [`data/accounts.json`](data/accounts.json) should be standardized because different product types currently have different top-level shapes.

#### Suggested common structure

```json
{
  "balances": {
    "ledger_balance": 4250.50,
    "available_balance": 4250.50,
    "available_credit": null
  },
  "identifiers": {
    "sort_code": "20-00-00",
    "account_number_full": "12345678",
    "iban": "GB29 NWBK 2000 0012 3456 78",
    "card_number_full": null
  },
  "limits": {
    "daily_withdrawal_limit": 500.00,
    "daily_transfer_limit": 10000.00,
    "overdraft_limit": 500.00,
    "credit_limit": null,
    "cash_advance_limit": null
  },
  "servicing": {
    "payment_due_date": null,
    "minimum_payment": null,
    "last_payment_date": null,
    "last_payment_amount": null
  }
}
```

This lets all account tools return a consistent response envelope while preserving full values for demo and guardrail testing.

### Required indexes

- by `account_id`
- by `customer_id`
- by `account_type`
- by `status`

---

## 4.3 `bank_transactions`

### Document types

- `transaction`
- `pending_transaction`
- `transfer_event`

Use one document per transaction/event.

#### Example ID strategy

- `_id = txn:TXN-20260425-001`
- `_id = txn:TXN-PENDING-001`
- `_id = transfer:TXN-<generated-id>`

### Fields

- `doc_type`
- `transaction_id`
- `account_id`
- `customer_id`
- `date`
- `timestamp`
- `type`
- `category`
- `merchant`
- `description`
- `amount`
- `currency`
- `status`
- `location`
- `balance_after`
- `metadata`

### Reason for adding `customer_id`

Current transactions in [`data/transactions.json`](data/transactions.json) only carry `account_id`. For Cloudant, add `customer_id` redundantly for query performance.

### State-changing behavior

For future standalone Python tools:

- money movement should create immutable transaction event docs
- account balance updates should update the account doc in [`bank_accounts`](bank_accounts)
- optionally add an audit event in [`bank_audit`](bank_audit)

### Required indexes

- by `transaction_id`
- by `account_id` + `date`
- by `customer_id` + `date`
- by `status`
- by `type`

---

## 4.4 `bank_credit`

### Document types

- `credit_report`
- optionally later: `credit_report_snapshot`

One active credit report per customer is enough for current demo parity.

#### Example ID strategy

- `_id = credit-report:CUST-001`

### Fields

Based on [`data/credit_reports.json`](data/credit_reports.json):

- `doc_type`
- `customer_id`
- `bureau`
- `report_date`
- `credit_score`
- `credit_accounts`
- `credit_searches`
- `public_records`
- `payment_history`

### Required indexes

- by `customer_id`
- by `bureau`
- by `report_date`

---

## 4.5 `bank_devices`

### Document type: device

One device per document.

#### Example ID strategy

- `_id = device:DEV-EMMA-IPHONE`

### Fields

Based on [`data/devices.json`](data/devices.json):

- `doc_type`
- `device_id`
- `customer_id`
- `device_type`
- `device_name`
- `os`
- `browser`
- `first_seen`
- `last_seen`
- `status`
- `trusted`
- `typical_locations`
- `typical_usage_hours`
- `risk_score`
- `risk_indicators`
- `network_metadata`

### Required indexes

- by `device_id`
- by `customer_id`
- by `trusted`
- by `status`
- by `risk_score`

---

## 4.6 `bank_fraud`

### Document types

- `fraud_scenario`
- `fraud_case`
- `fraud_alert`
- `fraud_incident`
- later optionally `risk_evaluation`

This database should handle both demo seed scenarios and runtime case management.

#### Example ID strategy

- `_id = fraud-scenario:TXN-FRAUD-001`
- `_id = fraud-case:FRAUD-CASE-001`
- `_id = fraud-alert:<generated-id>`
- `_id = fraud-incident:FRAUD-INC-002`

### Split current mixed scenario data

[`data/fraud_scenarios.json`](data/fraud_scenarios.json) currently mixes:
- transaction scenarios
- incidents
- embedded action outcomes

In Cloudant, preserve the seed scenarios, but also create proper operational doc types for live actions.

### Required indexes

- by `customer_id`
- by `account_id`
- by `transaction_id`
- by `case_id`
- by `risk_analysis.risk_level`
- by `action_taken.case_created`

---

## 4.7 `bank_loans`

### Document types

- `loan_application`
- `loan_offer`
- `loan_document`
- `esignature_request`
- `loan_disbursement`

### Recommended structure

Keep `loan_application` as the primary aggregate root because the current file already behaves like one rich aggregate in [`data/loan_applications.json`](data/loan_applications.json).

#### Example ID strategy

- `_id = loan-application:LOAN-APP-001`
- `_id = loan-document:DOC-<id>`
- `_id = esignature:<id>`
- `_id = disbursement:<id>`

### Fields for `loan_application`

- `doc_type`
- `application_id`
- `customer_id`
- `application_date`
- `loan_type`
- `loan_purpose`
- `requested_amount`
- `requested_term_months`
- `application_status`
- `currency`
- `applicant_info`
- `financial_profile`
- `eligibility_assessment`
- `offers`
- `selected_offer_id`
- `approval_workflow`
- `business_info`
- `vehicle_info`
- `collateral`

### Why keep offers embedded

Current tools such as [`generate_loan_offers`](toolkits/loan_processing_server.py:557) and [`get_loan_application`](toolkits/loan_processing_server.py:733) need a single response envelope. Embedding offers under the application keeps reads simple.

Separate `loan_offer` docs are optional later if offer lifecycle becomes independent.

### Required indexes

- by `application_id`
- by `customer_id`
- by `application_status`
- by `loan_type`
- by `application_date`

---

## 4.8 `bank_audit`

### Document types

- `audit_event`
- `auth_session`
- `tool_execution_log`

### Why this database is important

The current core banking tool stores sessions in a file via [`load_sessions()`](toolkits/core_banking_server.py:32) and [`save_sessions()`](toolkits/core_banking_server.py:43). That must move to persistent storage.

### Session document

#### Example ID strategy

- `_id = session:<token-or-uuid>`

### Fields

- `doc_type`: `auth_session`
- `session_token`
- `customer_id`
- `created_at`
- `expires_at`
- `status`
- `auth_method`

### Audit event document

- `doc_type`: `audit_event`
- `event_type`
- `customer_id`
- `account_id`
- `application_id`
- `transaction_id`
- `tool_name`
- `timestamp`
- `actor`
- `result`
- `details`

### Required indexes

- by `customer_id`
- by `session_token`
- by `status`
- by `event_type`
- by `timestamp`

---

## 5. Tool Mapping: Current MCP Tools to Standalone Python Tools

## 5.1 Core banking tool mapping

### Current tools from [`toolkits/core_banking_server.py:59`](toolkits/core_banking_server.py:59)

1. `authenticate_customer`
2. `get_current_customer`
3. `check_account_balance`
4. `get_recent_transactions`
5. `transfer_funds`
6. `check_pending_deposits`
7. `get_payment_due_date`
8. `get_customer_accounts`

### Planned standalone Python tools

#### `authenticate_customer`
Purpose:
- validate customer credentials
- create persistent session in Cloudant

Cloudant reads/writes:
- read [`bank_customers`](bank_customers)
- write [`bank_audit`](bank_audit)

Notes:
- for demo parity, plaintext PIN comparison can remain aligned with the source dataset from [`data/customers.json:4`](data/customers.json:4)
- if the solution is later hardened beyond demo scope, this should be replaced with hash verification

#### `get_current_customer`
Purpose:
- resolve active session to customer profile and accounts

Cloudant reads:
- [`bank_audit`](bank_audit) for session
- [`bank_customers`](bank_customers)
- [`bank_accounts`](bank_accounts)

#### `check_account_balance`
Purpose:
- return balance summary for an account

Cloudant reads:
- [`bank_accounts`](bank_accounts)

#### `get_recent_transactions`
Purpose:
- return posted transactions for an account with limit support

Cloudant reads:
- [`bank_transactions`](bank_transactions)

#### `transfer_funds`
Purpose:
- perform actual persisted transfer

Cloudant reads/writes:
- read [`bank_accounts`](bank_accounts)
- write [`bank_transactions`](bank_transactions)
- update [`bank_accounts`](bank_accounts)
- write [`bank_audit`](bank_audit)

Notes:
- current simulated behavior in [`toolkits/core_banking_server.py:405`](toolkits/core_banking_server.py:405) becomes real persistence logic

#### `check_pending_deposits`
Purpose:
- list pending deposits

Cloudant reads:
- [`bank_transactions`](bank_transactions)

#### `get_payment_due_date`
Purpose:
- retrieve credit-card servicing information

Cloudant reads:
- [`bank_accounts`](bank_accounts)

#### `get_customer_accounts`
Purpose:
- list accounts by customer

Cloudant reads:
- [`bank_accounts`](bank_accounts)

---

## 5.2 Fraud tool mapping

### Current tools from [`toolkits/fraud_detection_server.py:35`](toolkits/fraud_detection_server.py:35)

1. `analyze_transaction_risk`
2. `check_customer_profile`
3. `verify_device_fingerprint`
4. `check_velocity_rules`
5. `block_transaction`
6. `send_fraud_alert`
7. `create_fraud_case`
8. `get_fraud_scenario`

### Planned standalone Python tools

#### `analyze_transaction_risk`
Purpose:
- calculate fraud risk from transaction context plus customer/device history

Cloudant reads:
- [`bank_accounts`](bank_accounts)
- [`bank_customers`](bank_customers)
- [`bank_transactions`](bank_transactions)
- [`bank_devices`](bank_devices)
- [`bank_fraud`](bank_fraud)

Cloudant writes:
- optional `risk_evaluation` doc in [`bank_fraud`](bank_fraud)
- audit event in [`bank_audit`](bank_audit)

Notes:
- current logic in [`toolkits/fraud_detection_server.py:232`](toolkits/fraud_detection_server.py:232) is intentionally simplistic and should be redesigned as rule-based scoring over Cloudant data

#### `check_customer_profile`
Purpose:
- return fraud profile derived from customer, accounts, and historical transactions

Cloudant reads:
- [`bank_customers`](bank_customers)
- [`bank_transactions`](bank_transactions)
- [`bank_fraud`](bank_fraud)

#### `verify_device_fingerprint`
Purpose:
- determine whether device is known, trusted, blocked, or risky

Cloudant reads:
- [`bank_devices`](bank_devices)

#### `check_velocity_rules`
Purpose:
- count transactions and aggregate amount over timeframe

Cloudant reads:
- [`bank_transactions`](bank_transactions)

Notes:
- this should become a real query instead of the placeholder response in [`toolkits/fraud_detection_server.py:347`](toolkits/fraud_detection_server.py:347)

#### `block_transaction`
Purpose:
- update transaction status and record fraud action

Cloudant reads/writes:
- [`bank_transactions`](bank_transactions)
- [`bank_fraud`](bank_fraud)
- [`bank_audit`](bank_audit)

#### `send_fraud_alert`
Purpose:
- create alert record and optionally integrate downstream notification service later

Cloudant writes:
- [`bank_fraud`](bank_fraud)
- [`bank_audit`](bank_audit)

#### `create_fraud_case`
Purpose:
- persist fraud investigation case

Cloudant writes:
- [`bank_fraud`](bank_fraud)
- [`bank_audit`](bank_audit)

#### `get_fraud_scenario`
Purpose:
- return seeded fraud scenario data for demo flows

Cloudant reads:
- [`bank_fraud`](bank_fraud)

---

## 5.3 Loan processing tool mapping

### Current tools from [`toolkits/loan_processing_server.py:35`](toolkits/loan_processing_server.py:35)

1. `calculate_loan_eligibility`
2. `check_credit_score`
3. `calculate_debt_to_income`
4. `generate_loan_offers`
5. `initiate_loan_approval`
6. `generate_loan_documents`
7. `send_for_esignature`
8. `disburse_funds`
9. `get_loan_application`

### Planned standalone Python tools

#### `calculate_loan_eligibility`
Purpose:
- derive eligibility from customer, credit, and debt data

Cloudant reads:
- [`bank_customers`](bank_customers)
- [`bank_credit`](bank_credit)
- optionally [`bank_accounts`](bank_accounts)

Notes:
- current logic in [`toolkits/loan_processing_server.py:431`](toolkits/loan_processing_server.py:431) can be preserved initially and then refined

#### `check_credit_score`
Purpose:
- return current credit bureau snapshot

Cloudant reads:
- [`bank_credit`](bank_credit)

#### `calculate_debt_to_income`
Purpose:
- compute DTI from income and debt obligations

Cloudant reads:
- [`bank_customers`](bank_customers)
- [`bank_credit`](bank_credit)

#### `generate_loan_offers`
Purpose:
- generate offer set from requested amount and risk profile

Cloudant reads:
- [`bank_customers`](bank_customers)
- [`bank_credit`](bank_credit)

Cloudant writes:
- optionally update application or offer preview doc in [`bank_loans`](bank_loans)

#### `initiate_loan_approval`
Purpose:
- create persisted application record

Cloudant writes:
- [`bank_loans`](bank_loans)
- [`bank_audit`](bank_audit)

#### `generate_loan_documents`
Purpose:
- create document metadata records

Cloudant reads/writes:
- read [`bank_loans`](bank_loans)
- write [`bank_loans`](bank_loans)
- write [`bank_audit`](bank_audit)

#### `send_for_esignature`
Purpose:
- create e-sign request metadata and status tracking

Cloudant reads/writes:
- read [`bank_customers`](bank_customers)
- write [`bank_loans`](bank_loans)
- write [`bank_audit`](bank_audit)

#### `disburse_funds`
Purpose:
- record disbursement and optionally create banking transaction

Cloudant reads/writes:
- read [`bank_loans`](bank_loans)
- update [`bank_loans`](bank_loans)
- write [`bank_transactions`](bank_transactions)
- update [`bank_accounts`](bank_accounts)
- write [`bank_audit`](bank_audit)

#### `get_loan_application`
Purpose:
- retrieve loan application aggregate

Cloudant reads:
- [`bank_loans`](bank_loans)

---

## 6. Proposed `cloudant-tools` Directory Structure

```text
cloudant-tools/
  IMPLEMENTATION_PLAN.md
  README.md
  requirements.txt
  .env.example
  import_seed_data.py
  seed/
    customers.json
    accounts.json
    transactions.json
    credit_reports.json
    devices.json
    fraud_scenarios.json
    loan_applications.json
  common/
    __init__.py
    config.py
    cloudant_client.py
    errors.py
    models.py
    masking.py
    auth.py
    audit.py
    ids.py
    validators.py
  repositories/
    __init__.py
    customers_repository.py
    accounts_repository.py
    transactions_repository.py
    credit_repository.py
    devices_repository.py
    fraud_repository.py
    loans_repository.py
    audit_repository.py
  tools/
    __init__.py
    core_banking_tools.py
    fraud_tools.py
    loan_tools.py
  docs/
    cloudant-schema.md
    indexing-strategy.md
    migration-plan.md
    security-model.md
  tests/
    test_core_banking_tools.py
    test_fraud_tools.py
    test_loan_tools.py
    test_seed_import.py
```

## Structure rationale

### [`cloudant-tools/common`](cloudant-tools/common)
Shared platform utilities:
- connection management
- data masking
- auth/session helpers
- validation
- audit helpers

### [`cloudant-tools/repositories`](cloudant-tools/repositories)
Encapsulates Cloudant CRUD/query logic by domain.

This is important because tool functions should not contain raw query/index code.

### [`cloudant-tools/tools`](cloudant-tools/tools)
Contains the actual standalone Python tool functions.

These should eventually use the watsonx Orchestrate `@tool` decorator when implemented.

### [`cloudant-tools/seed`](cloudant-tools/seed)
Holds transformed seed data for Cloudant import.

Do not rely directly on the current [`data/`](data/) structure during implementation because the current files are source material, not final Cloudant document shape.

---

## 7. Planned Tool Module Design

## 7.1 [`cloudant-tools/tools/core_banking_tools.py`](cloudant-tools/tools/core_banking_tools.py)

Planned functions:

- `authenticate_customer`
- `get_current_customer`
- `check_account_balance`
- `get_recent_transactions`
- `transfer_funds`
- `check_pending_deposits`
- `get_payment_due_date`
- `get_customer_accounts`

Dependencies:

- customer repository
- account repository
- transaction repository
- audit/session repository
- masking utilities

## 7.2 [`cloudant-tools/tools/fraud_tools.py`](cloudant-tools/tools/fraud_tools.py)

Planned functions:

- `analyze_transaction_risk`
- `check_customer_profile`
- `verify_device_fingerprint`
- `check_velocity_rules`
- `block_transaction`
- `send_fraud_alert`
- `create_fraud_case`
- `get_fraud_scenario`

Dependencies:

- transaction repository
- customer repository
- device repository
- fraud repository
- audit repository

## 7.3 [`cloudant-tools/tools/loan_tools.py`](cloudant-tools/tools/loan_tools.py)

Planned functions:

- `calculate_loan_eligibility`
- `check_credit_score`
- `calculate_debt_to_income`
- `generate_loan_offers`
- `initiate_loan_approval`
- `generate_loan_documents`
- `send_for_esignature`
- `disburse_funds`
- `get_loan_application`

Dependencies:

- customer repository
- credit repository
- loan repository
- account repository
- transaction repository
- audit repository

---

## 8. Cloudant Indexing Strategy

Each database should use JSON indexes for the exact tool query paths.

## Recommended indexes by domain

### `bank_customers`
- `customer_id`
- `email`
- `customer_tier`
- `risk_profile`

### `bank_accounts`
- `account_id`
- `customer_id`
- `account_type`
- `status`

### `bank_transactions`
- `[account_id, date]`
- `[customer_id, date]`
- `[account_id, status]`
- `[customer_id, status]`
- `[type, status]`

### `bank_credit`
- `customer_id`
- `report_date`

### `bank_devices`
- `device_id`
- `customer_id`
- `[customer_id, trusted]`
- `[customer_id, status]`

### `bank_fraud`
- `scenario_id`
- `case_id`
- `transaction_id`
- `customer_id`
- `[customer_id, risk_level]`

### `bank_loans`
- `application_id`
- `customer_id`
- `application_status`
- `[customer_id, application_date]`
- `[loan_type, application_status]`

### `bank_audit`
- `session_token`
- `customer_id`
- `timestamp`
- `[event_type, timestamp]`

---

## 9. Data Migration Plan from Current JSON

## Phase 1: transform current source files into Cloudant-ready docs

Transform:

- map-shaped files into one-doc-per-record sets
- array-shaped transaction file into one-doc-per-transaction
- embed `doc_type`
- assign `_id`
- add denormalized keys like `customer_id` to transactions where missing
- mask sensitive identifiers for standard-access documents

## Phase 2: seed Cloudant

Create a script in [`cloudant-tools/import_seed_data.py`](cloudant-tools/import_seed_data.py) that:

1. connects to IBM Cloudant
2. creates missing databases
3. creates indexes
4. transforms source seed data
5. bulk inserts docs
6. prints seed summary

## Phase 3: validate domain queries

Verify all planned tool access patterns work against indexes:
- account lookup by customer
- recent transactions by account
- pending deposits by account
- device lookup by device/customer
- loan application lookup by customer/application
- fraud scenario lookup by ID

---

## 10. IBM Cloud Connection Design

Because the Cloudant service is in IBM Cloud and you have admin privileges, the implementation should assume IBM-managed connectivity.

## Expected configuration

Use environment variables like:

```bash
CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_IAM_URL=https://iam.cloud.ibm.com/identity/token
CLOUDANT_DB_CUSTOMERS=bank_customers
CLOUDANT_DB_ACCOUNTS=bank_accounts
CLOUDANT_DB_TRANSACTIONS=bank_transactions
CLOUDANT_DB_CREDIT=bank_credit
CLOUDANT_DB_DEVICES=bank_devices
CLOUDANT_DB_FRAUD=bank_fraud
CLOUDANT_DB_LOANS=bank_loans
CLOUDANT_DB_AUDIT=bank_audit
```

If these tools are later imported into watsonx Orchestrate, credentials should come from a connection rather than hardcoded env in source.

---

## 11. Security and Compliance Recommendations

## Must change before implementation

### Replace plaintext PIN storage
Current plaintext PIN in [`data/customers.json:4`](data/customers.json:4) must never be carried over as-is.

Use:
- salted hash
- configurable verification helper
- optional failed-attempt counter in audit/session docs

### Mask sensitive outputs
Do not return:
- full NI number from [`data/customers.json:11`](data/customers.json:11)
- full account number from [`data/accounts.json:8`](data/accounts.json:8)
- full card number from [`data/accounts.json:45`](data/accounts.json:45)

### Add audit events for sensitive operations
Required for:
- authentication
- fund transfer
- transaction block
- fraud case creation
- loan application initiation
- loan disbursement

---

## 12. Recommended Implementation Sequence

## Phase A: foundation
1. Create [`cloudant-tools`](cloudant-tools) structure
2. Add Cloudant client wrapper
3. Add config loader
4. Add repositories
5. Add masking and auth helpers

## Phase B: seed and schema
6. Define document schemas
7. Create database/index bootstrap
8. Build seed import script
9. Load initial demo data into Cloudant

## Phase C: read-only tools first
10. Implement:
   - account balance
   - recent transactions
   - customer accounts
   - credit score
   - loan application lookup
   - fraud scenario lookup
   - device fingerprint check

## Phase D: derived/calculation tools
11. Implement:
   - debt-to-income
   - loan eligibility
   - loan offers
   - customer fraud profile
   - velocity rules
   - transaction risk analysis

## Phase E: state-changing tools
12. Implement:
   - authentication/session
   - transfer funds
   - block transaction
   - send fraud alert
   - create fraud case
   - initiate loan approval
   - generate loan documents metadata
   - send for e-signature metadata
   - disburse funds

## Phase F: testing and hardening
13. Unit test repository layer
14. Unit test tool logic
15. Validate masking and auth behavior
16. Validate seed/import repeatability

---

## 13. Recommended First Deliverables After Planning

After this plan is approved, the first implementation deliverables should be:

1. [`cloudant-tools/README.md`](cloudant-tools/README.md)
2. [`cloudant-tools/.env.example`](cloudant-tools/.env.example)
3. [`cloudant-tools/requirements.txt`](cloudant-tools/requirements.txt)
4. [`cloudant-tools/common/config.py`](cloudant-tools/common/config.py)
5. [`cloudant-tools/common/cloudant_client.py`](cloudant-tools/common/cloudant_client.py)
6. [`cloudant-tools/docs/cloudant-schema.md`](cloudant-tools/docs/cloudant-schema.md)
7. [`cloudant-tools/import_seed_data.py`](cloudant-tools/import_seed_data.py)

Only after that should the standalone tools themselves be implemented.

---

## 14. Final Recommendation

Use Cloudant as a domain-separated document store with:

- one document per entity/event
- one database per domain
- repository-based Python access
- masked outputs
- persisted sessions and audit events
- embedded aggregates where responses need to stay simple

This design best matches:

- the current demo data structure in [`data/`](data/)
- the current tool responsibilities in [`toolkits/`](toolkits/)
- the operational reality of Cloudant as a document database
- the future goal of converting mock server behavior into real persisted tool behavior
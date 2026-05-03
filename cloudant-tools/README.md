# Cloudant Tools

Standalone Python tools backed by IBM Cloudant for the banking demo.

This directory is the replacement for the former MCP-server-based toolkit implementation. It now contains the direct Python tool modules, shared Cloudant access code, repository modules, bootstrap utilities, and supporting documentation for the current Cloudant-backed architecture.

## What is in this folder

[`cloudant-tools`](cloudant-tools) currently contains four categories of artifacts:

### 1. Runtime code required by the imported tools

These are part of the active implementation and should remain:

- [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py)
- [`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py)
- [`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py)
- [`cloudant-tools/common/`](cloudant-tools/common)
- [`cloudant-tools/repositories/`](cloudant-tools/repositories)
- [`cloudant-tools/requirements.txt`](cloudant-tools/requirements.txt)

### 2. Support utilities

These are not agent-facing tools, but they are useful for setup, validation, and local troubleshooting:

- [`cloudant-tools/scripts/`](cloudant-tools/scripts)
- [`cloudant-tools/tests_smoke.py`](cloudant-tools/tests_smoke.py)

### 3. Documentation

These explain the design and current tradeoffs:

- [`cloudant-tools/README.md`](cloudant-tools/README.md)
- [`cloudant-tools/IMPLEMENTATION_PLAN.md`](cloudant-tools/IMPLEMENTATION_PLAN.md)
- [`cloudant-tools/SESSION_ENHANCEMENT.md`](cloudant-tools/SESSION_ENHANCEMENT.md)

### 4. Local-only or cleanup-candidate artifacts

These are not required for the deployed runtime:

- [`cloudant-tools/.env`](cloudant-tools/.env)
- [`cloudant-tools/debug_transactions.py`](cloudant-tools/debug_transactions.py)
- [`cloudant-tools/__pycache__/`](cloudant-tools/__pycache__)

[`cloudant-tools/.env`](cloudant-tools/.env) is especially sensitive because it contains local credentials and should never be treated as a deployable artifact.

## Current architecture

At a high level, the implementation flow is:

1. An agent calls a standalone Python tool such as [`authenticate_customer()`](cloudant-tools/core_banking_tools.py:25), [`analyze_transaction_risk()`](cloudant-tools/fraud_detection_tools.py:61), or [`check_credit_score()`](cloudant-tools/loan_processing_tools.py:197)
2. The tool declares Cloudant connection requirements using [`ExpectedCredentials`](cloudant-tools/core_banking_tools.py:19)
3. The tool reads business data through repositories such as [`AccountRepository`](cloudant-tools/repositories/accounts.py), [`CustomerRepository`](cloudant-tools/repositories/customers.py), [`TransactionRepository`](cloudant-tools/repositories/transactions.py), or [`FraudCaseRepository`](cloudant-tools/repositories/fraud_cases.py)
4. The repositories use the shared configuration and Cloudant client code in [`cloudant-tools/common/config.py`](cloudant-tools/common/config.py:121) and [`cloudant-tools/common/cloudant_client.py`](cloudant-tools/common/cloudant_client.py:19)
5. Cloudant returns the matching documents, and the tool formats the response for the agent

In short:

- agents call tools
- tools call repositories
- repositories call Cloudant

## Why the repositories exist

The repositories are intentionally separate from the tool functions.

They provide:

- **Separation of concerns**: tools focus on business behavior, repositories focus on persistence and query logic
- **Reuse**: multiple tools can share the same lookup logic
- **Maintainability**: document-shape or index changes are usually isolated to repository code
- **Testability**: repository behavior can be validated independently of agent orchestration
- **Flexibility**: the storage layer can evolve later without changing tool contracts

A simple example:

- [`authenticate_customer()`](cloudant-tools/core_banking_tools.py:25) does not implement raw Cloudant API calls itself
- it uses customer access logic from [`cloudant-tools/repositories/customers.py`](cloudant-tools/repositories/customers.py)
- that repository builds on common repository behavior from [`cloudant-tools/repositories/base.py`](cloudant-tools/repositories/base.py:13)

## Current folder assessment

### Required for runtime
Keep these as part of the active Cloudant-backed solution:

- [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py)
- [`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py)
- [`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py)
- [`cloudant-tools/common/`](cloudant-tools/common)
- [`cloudant-tools/repositories/`](cloudant-tools/repositories)
- [`cloudant-tools/requirements.txt`](cloudant-tools/requirements.txt)

### Useful support artifacts
Keep these because they help with setup, validation, or documentation:

- [`cloudant-tools/scripts/`](cloudant-tools/scripts)
- [`cloudant-tools/tests_smoke.py`](cloudant-tools/tests_smoke.py)
- [`cloudant-tools/IMPLEMENTATION_PLAN.md`](cloudant-tools/IMPLEMENTATION_PLAN.md)
- [`cloudant-tools/SESSION_ENHANCEMENT.md`](cloudant-tools/SESSION_ENHANCEMENT.md)

### Not required for deployed runtime
These are local or cleanup-oriented:

- [`cloudant-tools/debug_transactions.py`](cloudant-tools/debug_transactions.py) is a one-off debugging helper
- [`cloudant-tools/__pycache__/`](cloudant-tools/__pycache__) is generated Python cache data
- [`cloudant-tools/.env`](cloudant-tools/.env) is only for local development and currently contains secrets

### Important note on the loan tool module
[`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py) is still needed and should remain in place.

However, unlike [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py) and [`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py), it currently contains some duplicated Cloudant configuration and client setup logic instead of fully reusing the shared code under [`cloudant-tools/common/`](cloudant-tools/common). That inconsistency is known, but it is intentionally not being refactored yet.

## Demo PII model

This is a demo environment, not a production deployment.

The persistence layer intentionally preserves realistic full demo values, including PII, because masking and redaction are demonstrated through agent guardrail plugins rather than by masking data in the repositories or storage layer.

See [`cloudant-tools/IMPLEMENTATION_PLAN.md`](cloudant-tools/IMPLEMENTATION_PLAN.md) for the fuller rationale.

## Configuration model

The Cloudant-backed implementation supports three configuration sources, resolved in this order by [`get_cloudant_settings()`](cloudant-tools/common/config.py:121):

1. watsonx Orchestrate runtime connection lookup
2. watsonx Orchestrate injected environment variables
3. local development environment values

### watsonx Orchestrate deployment
For watsonx Orchestrate deployments:

1. Import [`connections/cloudant-connection.yaml`](connections/cloudant-connection.yaml)
2. Configure credentials for app id `cloudant`
3. Import [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py), [`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py), and [`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py)
4. Import or update the agents that reference those tool names

The tool modules declare the dependency directly through [`ExpectedCredentials`](cloudant-tools/core_banking_tools.py:19), [`ExpectedCredentials`](cloudant-tools/fraud_detection_tools.py:21), and [`ExpectedCredentials`](cloudant-tools/loan_processing_tools.py:26).

### Local development
For local development, use a local environment file such as [`cloudant-tools/.env`](cloudant-tools/.env), but do not commit real secrets.

Relevant local variables include:

- `CLOUDANT_URL`
- `CLOUDANT_API_KEY`
- `CLOUDANT_IAM_URL`
- `CLOUDANT_DB_CUSTOMERS`
- `CLOUDANT_DB_ACCOUNTS`
- `CLOUDANT_DB_TRANSACTIONS`
- `CLOUDANT_DB_CREDIT`
- `CLOUDANT_DB_DEVICES`
- `CLOUDANT_DB_FRAUD`
- `CLOUDANT_DB_LOANS`
- `CLOUDANT_DB_AUDIT`

## Current structure

```text
cloudant-tools/
  README.md
  IMPLEMENTATION_PLAN.md
  SESSION_ENHANCEMENT.md
  requirements.txt
  common/
  repositories/
  scripts/
  core_banking_tools.py
  fraud_detection_tools.py
  loan_processing_tools.py
  tests_smoke.py
  .env                  # local only, contains secrets if present
  debug_transactions.py # local debug helper
  __pycache__/          # generated cache files
```

## Current status

Implemented:

1. Shared configuration and Cloudant client helpers
2. Cloudant repository layer by business domain
3. Standalone Python tools for banking, fraud, and loan use cases
4. Bootstrap, indexing, and seed-support utilities
5. Smoke-test validation for the Cloudant-backed data-access layer

Current limitations:

- some former MCP behaviors still remain simplified
- [`check_pending_deposits()`](cloudant-tools/core_banking_tools.py:165) is implemented, but some banking write operations from the old simulation were intentionally not migrated yet
- [`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py) is valid for current use, but remains a future consistency refactor candidate
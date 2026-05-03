# Session Handling Enhancement for Cloudant Tools

## Current State

The standalone Cloudant-backed Python tools are currently designed to be stateless between calls.

For example, [`authenticate_customer()`](cloudant-tools/core_banking_tools.py:25) returns:

- `status`
- `customer_id`
- `customer_name`
- `message`

It does **not** return a session token.

This is different from the legacy MCP implementation in [`core_banking_server.py`](toolkits/core_banking_server.py:205), which generated a `session_token` and persisted session state in [`sessions.json`](toolkits/data/data/sessions.json).

## Why This Is Acceptable Now

For the current demo and orchestration flow, a separate session token is not required because:

- the new tools are intended to work as independent, stateless operations
- downstream tool calls can use `customer_id` directly
- watsonx Orchestrate manages tool invocation flow at the agent level
- removing file-based session state makes the new implementation simpler and more robust

## Potential Future Enhancement

If stronger authenticated session handling is needed later, a dedicated session layer can be added.

### When to Add It

Introduce session management if any of the following become requirements:

- authenticated state must persist across multiple tool calls
- tools must reject requests that are not tied to a validated login session
- customer identity must be revalidated without resending PIN
- session expiry, revocation, or logout becomes necessary
- audit/compliance requires explicit session tracking

## Recommended Design

### 1. Add a Cloudant session store

Create a dedicated Cloudant database, for example:

- `bank_sessions`

Each session document could include fields such as:

```json
{
  "_id": "SESSION-CUST-001-20260502120000",
  "session_id": "SESSION-CUST-001-20260502120000",
  "customer_id": "CUST-001",
  "created_at": "2026-05-02T12:00:00Z",
  "expires_at": "2026-05-02T12:30:00Z",
  "status": "active",
  "authentication_method": "pin",
  "last_accessed_at": "2026-05-02T12:05:00Z"
}
```

### 2. Extend [`authenticate_customer()`](cloudant-tools/core_banking_tools.py:25)

Return a `session_id` after successful authentication, for example:

```json
{
  "status": "success",
  "customer_id": "CUST-001",
  "customer_name": "Emma Thompson",
  "message": "Welcome back, Emma!",
  "session_id": "SESSION-CUST-001-20260502120000"
}
```

### 3. Add session validation helper logic

Create reusable validation in a shared repository or auth module:

- create session
- validate session
- extend session activity timestamp
- expire session
- revoke session

### 4. Protect sensitive tools

Sensitive tools could optionally require `session_id`, such as:

- account access tools
- payment initiation tools
- transfer tools
- customer profile tools
- loan approval actions

### 5. Add expiry and revocation rules

Suggested defaults:

- inactivity timeout: 15–30 minutes
- absolute lifetime: 8–12 hours
- manual logout support
- automatic invalidation after repeated failed validation

## Suggested Implementation Components

Possible future files:

- `cloudant-tools/repositories/sessions.py`
- `cloudant-tools/common/auth.py`
- `cloudant-tools/tests/test_sessions.py`

Possible future tools:

- `validate_session`
- `logout_customer`

## Migration Notes

If session support is added later:

- keep backward compatibility for current stateless demo flows where possible
- make `session_id` required only for higher-risk operations first
- avoid recreating the old file-based model from [`sessions.json`](toolkits/data/data/sessions.json)
- store session state only in Cloudant or another managed persistence layer

## Recommendation

Do not implement session handling yet.

Current stateless behavior is appropriate for the present demo scope. If the project evolves toward stronger authentication, regulated access control, or production-like banking flows, Cloudant-backed session management should be the next enhancement.
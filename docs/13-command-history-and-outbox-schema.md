# 13 — Command receipts, audit history, outbox, and worker-state schema

## Objective

Persist the records needed for atomic commands and retryable work before building transaction or worker handlers.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-REC-001–003; FR-INT-012; FR-VAL-001–002; VT-05,09,10,13.

**Dependencies:** [12 — Firm, client, period, engagement, assignment, and guard schema](12-scope-and-identity-schema.md)

**Execution gate:** file 12 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_command_receipt/audit_command_receipt.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_command_receipt/audit_command_receipt.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_command_receipt/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_event/audit_event.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_event/audit_event.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_event/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_outbox_operation/audit_outbox_operation.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_outbox_operation/audit_outbox_operation.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_outbox_operation/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_operation_attempt/audit_operation_attempt.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_operation_attempt/audit_operation_attempt.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_operation_attempt/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_runtime_epoch/audit_runtime_epoch.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_runtime_epoch/audit_runtime_epoch.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_runtime_epoch/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/operations.py`
- **Create:** `production/audit_practice/audit_practice/patches/v1_operation_indexes.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_operation_schema.py`
- **Modify:** `production/audit_practice/audit_practice/patches.txt`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Audit Command Receipt stores actor binding, scope, command type, idempotency key, canonical request digest, result reference and commit revision. Uniqueness includes scope/actor/action/key; changed payload with the same logical key must later conflict rather than return unrelated content.

2. Audit Event is append-only with event type, actor/system-duty identity, scope, prior/new revision, safe payload reference and correlation ID. Never serialize secrets or whole evidence bytes into events. Business event time and external observation time are distinct.

3. Audit Outbox Operation has typed operation/target, scope, request digest, idempotency identity, status, attempt count, next attempt, expected epoch, lease/fence and result reference. State includes PENDING, RUNNING, RETRY_WAIT, SUCCEEDED, FAILED and OUTCOME_UNKNOWN. There is no arbitrary URL or executable Python field.

4. Audit Operation Attempt preserves claimed fence, start/end, response class, uncertainty and provider correlation. Audit Runtime Epoch is a local cached reference to an independently controlled epoch, not the authority after restore. Add unique operation keys and indexes for due-state leasing.

5. Controllers use the protected base. Add migration tests for all tables/indexes, unique operation identities and immutable events. Do not enqueue jobs or call providers yet.

## Acceptance Criteria

- [ ] All control tables precede any handler and migrate idempotently.
- [ ] Duplicate command and operation keys fail without silently replacing history.
- [ ] Event content excludes secret fields; invalid operation types are rejected.
- [ ] OUTCOME_UNKNOWN is representable without relabeling it FAILED or SUCCEEDED.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_operation_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 17 — Atomic command transactions, revisions, and idempotency

## Objective

Implement a small application command boundary that commits domain state, history, generations and outbox intent atomically.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-GATE-008; FR-ACC-010–011; FR-REC-001–003; FR-VAL-001–004; VT-04–10.

**Dependencies:** [13 — Command receipts, audit history, outbox, and worker-state schema](13-command-history-and-outbox-schema.md); [16 — Role/assignment authorization across every access path](16-scoped-action-authorization.md)

**Execution gate:** file 16 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/__init__.py`
- **Create:** `production/audit_practice/audit_practice/application/commands.py`
- **Create:** `production/audit_practice/audit_practice/application/transactions.py`
- **Create:** `production/audit_practice/audit_practice/application/digests.py`
- **Create:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Create:** `production/audit_practice/audit_practice/api/errors.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_commands.py`
- **Modify:** `production/audit_practice/audit_practice/security/write_context.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Define execute(command_name, payload, expected_revision, idempotency_key) with action-specific schemas and whitelisted handlers; disallow dispatch to arbitrary dotted Python names. Authenticate and authorize before returning a replay result. Canonical request digest includes target/scope/action/payload version.

2. Acquire locks in the R0-proven order: client-period guard, then ordered engagement/record guards. Require expected revision for mutations. Atomically update affected revisions and safety/input generations with audit event, command receipt and outbox intent. Never call a remote provider while holding database locks.

3. Use Frappe transaction semantics for the pinned version. Avoid nested helper commits and avoid catching exceptions then accidentally committing partial writes. Roll back a caught command failure before generating its error response. Fail deadlock/revision conflicts predictably; bounded retry only when the whole command is safely replayable.

4. Grant internal write context only inside the authorized unit of work and clear it in finally. Application SQL cannot bypass record invariants; any low-level conditional UPDATE must validate row counts, approved scope and expected revision explicitly.

5. Use Python Decimal values encoded as schema-defined strings in request digests, rfc8785.dumps for JSON bytes and hashlib.sha256. Same idempotency key with changed payload fails VERSION_CONFLICT; rejected replay never leaks another actor/scope result. Do not create a generic repository/event-sourcing framework.

## Acceptance Criteria

- [ ] A failure between domain mutation and outbox insertion rolls back all business rows.
- [ ] Two independent connections with the same revision yield at most one mutation.
- [ ] Concurrent linked accounting/audit mutations share the correct client-period guard.
- [ ] Identical retry yields one effect; changed payload and unauthorized replay fail.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_commands
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

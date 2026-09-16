# 55 — Transactional release authorization and single release identity

## Objective

Implement the professional release linearization point without permitting delivery before independent checkpoint verification.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-001–007; FR-REC-001–003; G8; VT-04–08,09,12.

**Dependencies:** [54 — Final artifacts, signature lineage, and eligible release candidates](54-final-artifacts-and-release-candidates.md)

**Execution gate:** file 54 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/release.py`
- **Create:** `production/audit_practice/audit_practice/domain/release_policy.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_release_authorization.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. authorize_release requires the current assigned signatory, exact eligible candidate, expected revision and idempotency key. Validate current service-specific gates, EQR, management approvals, opinion/discussion where required, signatures, protection evidence and recipient scope.

2. Use the R0 lock order beginning with the shared client-period guard, then candidate/engagement. Compare candidate evaluated generations to current input/safety generations and authorization epoch inside the transaction. A stale candidate returns INPUTS_NOT_EVALUATED; current source mutation and release have one documented serialization.

3. Commit one append-only Release Event, command receipt, event history and CHECKPOINT_PUBLISH outbox intent together. Do not create the report-delivery operation in this transaction. Release event identity and lineage are reused for all retries/checkpoint/archive.

4. Record professional authorization time versus subsequent checkpoint/delivery times separately. Later employee departure does not rewrite the valid release decision, but current hold/recipient/system-duty policy still governs delivery. New material facts after release open a controlled impact/amendment path.

5. Block generic REST/import/Desk writes to release event/candidate protected fields. Repeated authorize with identical request returns the existing authorized identity; changed payload or different actor/scope cannot reuse the prior success.

## Acceptance Criteria

- [ ] Two racing signatory requests create at most one release event.
- [ ] Paused invalidation processing never permits an old-generation release.
- [ ] Release event and checkpoint intent commit together or both roll back.
- [ ] No final-report delivery can occur merely because RELEASE_AUTHORIZED is recorded.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_release_authorization
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

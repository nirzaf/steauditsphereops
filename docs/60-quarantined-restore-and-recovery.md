# 60 — Quarantined restore, reconciliation, and safe recovery resume

## Objective

Implement recovery controls that survive database rollback and prevent old workers or restored outbox rows from reissuing documents.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REC-004–008; ET-41; VT-13,23–24; P0-11 production recheck.

**Dependencies:** [53 — Independent checkpoint storage and non-rollbackable epoch adapter](53-independent-checkpoint-and-epoch-store.md); [59 — Post-issue amendments and supersession lineage](59-controlled-amendment-workflow.md)

**Execution gate:** file 59 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Independent recovery/records operator owns quarantine, credential rotation and resume; a production restore is not authorized by this WBS.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/recovery.py`
- **Create:** `scripts/production/recovery.py`
- **Create:** `docs/production/recovery-runbook.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_recovery.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/dispatcher.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/leases.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Before restore, external control disables outward credentials/egress and advances the independent recovery epoch. Restore to a quarantined environment and start no privileged worker automatically. A restored database feature flag alone is insufficient because it may predate the incident.

2. Inventory restored releases/candidates/operations and compare exact external checkpoints, provider artifacts, delivery evidence and authoritative identity/permission state. Reconstruct already-issued historical identities under controlled recovery records, without invoking a new professional release or resending documents.

3. Detect pending operations whose provider effect already occurred and reconcile same identity/digest. OUTCOME_UNKNOWN remains held for operator investigation. Retire old leases and credentials and account for requests already in flight; local CAS fencing alone does not prevent every remote effect.

4. Permit resume only after independently approved reconciliation, matching epoch and agreed RPO/RTO evidence. Re-enable capabilities incrementally using operator-controlled credentials; no generic admin button that clears quarantine without evidence.

5. Implement scripts/production/recovery.py with plan/validate/report defaults and explicit authorized execution on allowlisted disposable sites. Real restore/credential changes are operator-run irreversible operations requiring the user's confirmation policy, not background AI actions.

## Acceptance Criteria

- [ ] Restoring a DB from before release cannot cause another issuance/delivery.
- [ ] Old worker epoch/fence cannot publish results after recovery.
- [ ] Unmatched checkpoint or uncertain send prevents resume.
- [ ] A real disposable restore drill records measured RPO/RTO and independent approval.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_recovery
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

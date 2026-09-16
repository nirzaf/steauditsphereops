# 61 — Signatory, records, delivery, and recovery workspaces

## Objective

Expose release and records controls with accurate ordered states and no UI path that bypasses a server guard.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL; FR-REC; FR-NAV-006–007; FR-UX-006–007.

**Dependencies:** [33 — Production staff workspace and restricted client portal](33-production-workspaces-and-client-portal.md); [60 — Quarantined restore, reconciliation, and safe recovery resume](60-quarantined-restore-and-recovery.md)

**Execution gate:** file 60 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/public/js/records_workspace.js`
- **Create:** `tests/production/release.spec.js`
- **Create:** `production/audit_practice/audit_practice/tests/test_records_routes.py`
- **Modify:** `production/audit_practice/audit_practice/public/js/portal.js`
- **Modify:** `production/audit_practice/audit_practice/ui/routes.py`
- **Modify:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.js`
- **Modify:** `production/audit_practice/audit_practice/public/css/portal.css`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Show finalization blockers, exact report/FS versions/hashes, signatory authority, approval generations, protection evidence, release identity, checkpoint, delivery outcome and archive separately. Never display RELEASE_AUTHORIZED as DELIVERED.

2. Signatory initiates authorized release; records custodian verifies checkpoint/archive/holds; recovery operator sees quarantine/reconciliation. Technical or presenter roles gain no signature authority merely by viewing diagnostics.

3. Provide retry/reconcile actions only for the typed operations safe to retry. An uncertain send prompts investigation, not a generic resend button. Re-check current revisions server-side for every action.

4. Client portal shows only authorized published deliverables and accurately marks supersession. It excludes internal checkpoints, professional notes and control credentials. Next-action links open the exact blocked record or required independent task.

## Acceptance Criteria

- [ ] No UI action can deliver without a verified checkpoint.
- [ ] Blocked/stale/unknown states remain visible and actionable without fake success.
- [ ] Records, signatory and recovery powers remain separated.
- [ ] Client sees exact permitted current/superseded outputs and nothing internal.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
npx playwright test --config playwright.production.config.js tests/production/release.spec.js
./scripts/production/dev test audit_practice.tests.test_records_routes
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 62 — R4 release fault-injection and recovery acceptance gate

## Objective

Prove the complete release/control chain under concurrency, provider failures and restore before production rollout is considered.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** Section 27/R4; FR-E2E-006–007; ET-33–42; VT-04–15,20–24.

**Dependencies:** [61 — Signatory, records, delivery, and recovery workspaces](61-release-records-and-recovery-ui.md)

**Execution gate:** file 61 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Independent operator schedules and authorizes the disposable drill and captures live evidence; validate-only command is not a completed drill.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management).

## Target Files

- **Create:** `production/audit_practice/audit_practice/tests/test_r4_faults.py`
- **Create:** `scripts/production/run_release_drill.py`
- **Create:** `docs/production/r4-exit.md`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Enumerate failure points before/after final artifact storage, signing, protection verification, release commit, checkpoint write/readback/local commit, delivery submission/response and archive. Inject a crash or timeout at each boundary and reconcile expected state.

2. Race current source/journal/authority/hold changes with release authorization using real independent DB connections and explicit barriers. Assert the documented linearization, exact candidate generations and one release identity, not just final UI text.

3. Use R0-approved non-production provider targets to prove no first delivery before verified independent checkpoint; no mismatched report/FS; no stale authorization; no blind duplicate email; no obsolete epoch publication. Distinguish in-flight remote uncertainty from failures the application can conclusively prevent.

4. Perform a disposable restore from before an already-checkpointed release with remote artifacts intact. Record external quarantine, old-worker retirement, reconciliation, measured RPO/RTO and independent resume approval. No production recipients or professional report issued.

## Acceptance Criteria

- [ ] All enumerated crash boundaries produce a safe blocked/reconciled outcome.
- [ ] No stale-generation or checkpoint-less delivery is observed in the tested matrix.
- [ ] Restore drill retains one issued identity and no uncontrolled replay.
- [ ] R4 exit includes actual provider and recovery evidence, not mock-only checkmarks.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_r4_faults
python3 scripts/production/run_release_drill.py --environment staging --validate-only
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

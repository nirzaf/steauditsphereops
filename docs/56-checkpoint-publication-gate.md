# 56 — Publish and verify the release checkpoint before delivery intent

## Objective

Make independent checkpoint verification a mandatory persisted predecessor of all final-deliverable distribution.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-004–006; FR-REC-005; VT-15,23–24.

**Dependencies:** [53 — Independent checkpoint storage and non-rollbackable epoch adapter](53-independent-checkpoint-and-epoch-store.md); [55 — Transactional release authorization and single release identity](55-guarded-release-authorization.md)

**Execution gate:** file 55 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/checkpoints.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_checkpoint_gate.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Execute CHECKPOINT_PUBLISH only through the restricted checkpoint adapter. Resolve immutable release/candidate payload from trusted records, not arbitrary queue-supplied JSON or URLs. Require current valid epoch and approved checkpoint capability.

2. Write create-once canonical checkpoint, read back exact bytes/provider version and verify digest/authenticity. Then record the verified reference in a guarded local completion transaction with expected fence/epoch. Local failure after remote success must reconcile the same checkpoint.

3. Only after verified checkpoint reference is committed may a policy evaluation enqueue typed FINAL_DELIVERY intent. Require current artifact pair, recipient set, hold/distribution policy and environment permission. Keep production outward delivery disabled by default until the rollout task.

4. Failure/timeout/permission drift remains CHECKPOINT_PENDING/BLOCKED with operator detail; do not fall back to local JSON or skip the independent store. If the original author has departed, retain history and evaluate system-duty authorization rather than inventing a new professional signature.

5. Publish visible checkpoint status without leaking external credentials or internal retention-control details to clients. Test all crash points around write/readback/local commit/next-intent creation.

## Acceptance Criteria

- [ ] No FINAL_DELIVERY outbox entry exists before checkpoint VERIFIED.
- [ ] Lost local completion reconciles the already stored external checkpoint.
- [ ] Changed checkpoint digest, stale fence or epoch prevents delivery intent.
- [ ] Checkpoint outage cannot be converted into simulated production success.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_checkpoint_gate
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

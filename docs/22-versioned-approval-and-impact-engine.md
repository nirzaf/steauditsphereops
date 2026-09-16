# 22 — Version-bound decisions and synchronous invalidation

## Objective

Provide reusable professional approval and input-impact services without duplicating authority logic in each feature.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-REV-001–008; FR-ACC-010–011; FR-REL-002; VT-04,06–08,12,19.

**Dependencies:** [16 — Role/assignment authorization across every access path](16-scoped-action-authorization.md); [21 — Exact receipts, preserved snapshots, and canonical manifests](21-exact-snapshots-and-manifests.md)

**Execution gate:** file 21 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/approvals.py`
- **Create:** `production/audit_practice/audit_practice/application/impact.py`
- **Create:** `production/audit_practice/audit_practice/domain/approval_policy.py`
- **Create:** `production/audit_practice/audit_practice/jobs/impact.py`
- **Create:** `production/audit_practice/audit_practice/api/approvals.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_approvals_and_impact.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Approve/reject/conditionally approve only an exact submitted snapshot/manifest with expected target revision and input generation. Resolve actor, assignment and decision-kind authority server-side; exclude all relevant preparers/responders from independent clearance, not merely the current owner.

2. Treat missing rationale/conditions or stale view tokens as a validation/conflict. Frontend approval display must identify the same snapshot the command signs. Keep decision records append-only; supersede rather than update prior conclusions.

3. On a relevant source, mapping, journal, materiality, population, disclosure or authority change, atomically increment the client-period safety/input generation and append Impact Case in the source transaction. Downstream evaluations are unusable until their evaluated generation matches the guard. Do not rely on a running background worker to block release.

4. Discover affected dependencies asynchronously with captured generation. Publish evaluation CURRENT only with a compare-and-set against the still-current guard; discard stale worker results as historical. Do not implement a blanket metadata-only exemption: record impact classification and approved reason.

5. Distinguish future authority from historical validity. Employee departure blocks new commands/queued user exports but does not retroactively erase a valid approval or automatically prohibit a system-duty delivery already authorized under current policy. Unresolved contradictions or applicable holds still block.

## Acceptance Criteria

- [ ] Author self-review and mismatched displayed/target snapshot are denied.
- [ ] Paused impact worker cannot allow an old-generation approval/release evaluation.
- [ ] An old-generation impact job cannot publish CURRENT after a newer mutation.
- [ ] Conditional decisions do not satisfy unconditional final approval.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_approvals_and_impact
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

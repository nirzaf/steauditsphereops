# 24 — R1 secure-core integration and bypass regression gate

## Objective

Verify the production foundation as a connected system before adding client-facing workflow features.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** Section 27/R1; FR-AUTH; FR-REC-001–003; VT-01–15.

**Dependencies:** [18 — Durable outbox dispatch, bounded queues, and stale-worker fencing](18-durable-outbox-and-worker-leases.md); [23 — Service-specific gate evaluation and progress projections](23-gate-engine-and-projection-contract.md)

**Execution gate:** file 23 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe testing](https://docs.frappe.io/framework/user/en/testing); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/tests/test_r1_core.py`
- **Create:** `docs/production/r1-exit.md`
- **Modify:** `.github/workflows/production-ci.yml`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Build two-client/three-role fixtures using internal test setup; call actual session, generic REST, command, read, download and queue entrypoints. Fixtures must not enable professional writes for normal callers.

2. Use two independent database connections and barriers for simultaneous revision commands and linked engagement invalidation. Test process failure between commit and queue dispatch, expired worker lease and restart after remote success. A unit mock alone cannot pass a transaction boundary test.

3. Re-run install/migrate smoke against a clean database and a previous-schema fixture. Verify permission hooks on every installed custom DocType and absence of broad ignored-permission writes outside the audited command/bootstrap boundary.

4. Keep general integrations limited to approved non-production targets; release/report executors remain disabled. Publish evidence with tested commit, test IDs, environment and current provider capability revision. No claim that R2–R5 exists.

## Acceptance Criteria

- [ ] All R1 test modules run successfully under the pinned Frappe runner.
- [ ] Actual REST/Desk/import bypass tests reject protected mutations.
- [ ] Durable outbox and client-period race tests pass with independent connections.
- [ ] R1 exit records no unresolved critical isolation, authority or transaction finding.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_r1_core
./scripts/production/dev test-all
./scripts/production/dev build
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

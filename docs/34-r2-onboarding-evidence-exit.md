# 34 — R2 onboarding and evidence end-to-end acceptance

## Objective

Verify a complete two-client onboarding and evidence workflow before accounting and audit execution are added.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** Section 27/R2; FR-CL; FR-PBC; FR-COM; DOC-01–11.

**Dependencies:** [33 — Production staff workspace and restricted client portal](33-production-workspaces-and-client-portal.md)

**Execution gate:** file 33 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/tests/test_r2_onboarding.py`
- **Create:** `tests/production/onboarding.spec.js`
- **Create:** `docs/production/r2-exit.md`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Exercise lead/profile -> assessment -> acceptance -> estimate/fee -> quotation -> exact EL -> advance verification -> restricted onboarding -> PBC issue/upload/clarification/acceptance. Use client contributor, management approver, finance, Senior and Partner identities with distinct assignments.

2. Run missing-evidence hold, confirmed prohibition, rejected/revised EL, advance reversal, invitation replay, cross-client thread/upload and replacement evidence branches. Assert both UI feedback and authoritative record changes.

3. Verify DOC-01–08/11 are real versioned artifacts with correct visibility; DOC-09/10 planning artifacts remain pending future implementation, not falsely marked complete. Record that downstream G5–G10 cannot be forced by demo progress or empty providers.

4. Recheck same-key retries and Graph throttle/timeout behavior against controlled non-production resources. Update traceability with only executed scenario IDs, tested commit and real/mock distinction.

## Acceptance Criteria

- [ ] The happy path and each negative branch pass with isolated clients.
- [ ] Client users see no internal cost/review/other-client data.
- [ ] Every R2 gate decision names exact evidence and accountable actor.
- [ ] R2 exit has no unresolved critical onboarding/evidence defect.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_r2_onboarding
npx playwright test --config playwright.production.config.js tests/production/onboarding.spec.js
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

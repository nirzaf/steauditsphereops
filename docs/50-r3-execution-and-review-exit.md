# 50 — R3 accounting and audit execution acceptance gate

## Objective

Validate accounting-only, audit-only, combined and enabled internal-audit workflows before enabling release mechanisms.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** Section 27/R3; FR-E2E-002–005; AT-07–24; ET-23–35.

**Dependencies:** [41 — Accounting workspace, client responses, and audit handoff](41-accounting-workspace-and-linked-handoff.md); [49 — Planning, fieldwork, reviewer, partner, and EQR workspaces](49-audit-and-review-workspaces.md)

**Execution gate:** file 49 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/tests/test_r3_execution.py`
- **Create:** `tests/production/combined-cycle.spec.js`
- **Create:** `docs/production/r3-exit.md`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Run reference TB import, mapping, journal authorization/reflection, supporting schedules, exact FS, management response, planning, sample execution, submitted workpapers and independent review against real Frappe/MariaDB records.

2. Test audit-only consuming management-supplied accounts, accounting-only omitting opinion/EQR, combined engagement sharing guarded dependency handoffs, and internal-audit using its approved report profile. No irrelevant service gate may be silently coerced READY.

3. Exercise partial reflected journal, two revisions of one journal, contradictory evidence, changed materiality/population, old package approval, conditional client response and future remediation with evaluated reporting implications.

4. Cross-check implemented DOC-09–21 artifact inputs/owners/visibility and exact summary composition. DOC-22/23 issued states remain unavailable before R4. Record methodological/formula/template owner sign-off separately from software test output.

## Acceptance Criteria

- [ ] All supported service branches execute with correct applicability and professional authority.
- [ ] Source replacement invalidates linked completion even with impact worker paused.
- [ ] Expected arithmetic and risk/sample/review negative paths pass.
- [ ] No real report issuance path is reachable at the R3 checkpoint.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_r3_execution
npx playwright test --config playwright.production.config.js tests/production/combined-cycle.spec.js
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

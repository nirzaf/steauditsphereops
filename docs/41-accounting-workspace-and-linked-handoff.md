# 41 — Accounting workspace, client responses, and audit handoff

## Objective

Expose accounting workflows and their blockers through role-specific working surfaces and controlled linked-engagement handoffs.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-001–013; FR-NAV-006–007; FR-E2E-002–003; FR-COM-001.

**Dependencies:** [33 — Production staff workspace and restricted client portal](33-production-workspaces-and-client-portal.md); [40 — FS calculation, versioned drafts, MIR, and management response](40-financial-statements-and-management-response.md)

**Execution gate:** file 40 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md).

## Target Files

- **Create:** `production/audit_practice/audit_practice/public/js/accounting_workspace.js`
- **Create:** `tests/production/accounting.spec.js`
- **Create:** `production/audit_practice/audit_practice/application/handoffs.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_accounting_handoffs.py`
- **Modify:** `production/audit_practice/audit_practice/public/js/portal.js`
- **Modify:** `production/audit_practice/audit_practice/public/css/portal.css`
- **Modify:** `production/audit_practice/audit_practice/ui/routes.py`
- **Modify:** `production/audit_practice/audit_practice/api/accounting.py`
- **Modify:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement intake progress/validation, paginated TB/mapping, journal review, source bridge, schedule completeness, exact Draft FS preview and management response. Action button enablement explains blockers but authorization always occurs server-side.

2. Display original versus replacement source, journal reflection, approved plan and package revision; never mix amounts from different datasets. Upload failures and stale revisions retain the editable draft without reporting success.

3. Implement explicit same-client/period evidence handoff between linked accounting and audit engagements with recipient service, permitted purpose and snapshot manifest. Share no entire unrestricted ledger; reject wrong-client or wrong-period link requests.

4. On source/journal/disclosure changes, confirm the linked audit engagement sees generation/blocker changes immediately in authoritative reads even while the impact worker is paused. Do not register future audit UI routes until their implementation task.

5. Provide accountant, independent reviewer and client-management journeys with precise notification/next-action links. Protect journal export against CSV formula injection while preserving original data; use a safe export representation, not alteration of authoritative source values.

## Acceptance Criteria

- [ ] Users complete import -> review -> Draft FS -> management response from the UI.
- [ ] Action feedback names the exact resulting package/source revision.
- [ ] Wrong-client handoff and stale management approval are denied.
- [ ] Browser refresh shows authoritative current amounts and blockers, not local fixture fallback.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
npx playwright test --config playwright.production.config.js tests/production/accounting.spec.js
./scripts/production/dev test audit_practice.tests.test_accounting_handoffs
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

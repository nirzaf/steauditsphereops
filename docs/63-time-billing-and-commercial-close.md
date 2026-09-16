# 63 — Time capture, invoice allocation, and commercial close

## Objective

Complete firm time/cost/billing integration with one-time advance allocation and a distinct commercial-close gate.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-FIN-001–006; FR-INT-002; DOC-24–26; G9.

**Dependencies:** [29 — Cost estimates, fee review, and exact quotation acceptance](29-estimates-fees-and-quotation.md); [62 — R4 release fault-injection and recovery acceptance gate](62-r4-release-and-recovery-exit.md)

**Execution gate:** file 62 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/time_and_cost.py`
- **Create:** `production/audit_practice/audit_practice/application/billing.py`
- **Create:** `production/audit_practice/audit_practice/api/finance.py`
- **Create:** `production/audit_practice/audit_practice/public/js/finance_workspace.js`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/engagement_cost_summary.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_finance.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/ui/routes.py`
- **Modify:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Reuse supported ERPNext Timesheet, Sales Invoice and Payment Entry workflows; verify required resource/employee references against the pinned installed version rather than silently installing HR/payroll modules. Map staff/engagement/task/service with explicit permissions and preserve approval history.

2. Capture time date, hours, staff level, activity, rate snapshot and approval. Validate negative/overlapping/impossible entries and locked billing periods under policy. Preserve original estimate, revised budget and approved actual cost snapshots; corrections append authorized revisions.

3. Generate invoice only at the approved issued-release/commercial milestone with exact fee basis and scope. Fixed fee must not also generate time-based charges for the same work. Allocate the verified advance once with a unique source allocation identity and ledger reconciliation.

4. Handle partial payments, reversals, credits and disputed scope explicitly through native ERPNext financial records and controlled linking; no manual current-balance overwrite. A payment reversal changes commercial/eligibility evaluation, not historical professional opinion content.

5. Produce DOC-24–26 and finance-only cost/margin views. G9 evaluates required invoice/time/cost/advance exception resolution independently from G8 release/G10 records; no circular gate prerequisites or client-visible internal cost data.

## Acceptance Criteria

- [ ] Repeated invoice/allocation commands do not double-charge or allocate the advance twice.
- [ ] Fixed-fee and time-fee modes follow the approved mutually consistent rules.
- [ ] Time/cost totals reconcile to native ERPNext records and original/revised budgets remain separate.
- [ ] Client views exclude internal rates and margins.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_finance
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

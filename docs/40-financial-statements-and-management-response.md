# 40 — FS calculation, versioned drafts, MIR, and management response

## Objective

Generate reproducible FS packages and collect management responses bound to the exact draft and information request.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-007–011; FR-COM-001–005; FR-REV-005–007; DOC-17–19,23.

**Dependencies:** [27 — Approved artifact rendering and verified signature evidence](27-artifact-rendering-and-signature-adapter.md); [39 — Supporting schedules, comparatives, and disclosure completeness](39-comparatives-cashflow-and-disclosures.md)

**Execution gate:** file 39 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management).

## Target Files

- **Create:** `production/audit_practice/audit_practice/accounting/statements.py`
- **Create:** `production/audit_practice/audit_practice/accounting/management.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/financial_statements.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/management_information_request.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_financial_statements.py`
- **Modify:** `production/audit_practice/audit_practice/api/accounting.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Build a pure Decimal calculation result from current dataset/adjustment plan/mapping/schedules plus approved framework/taxonomy/template versions. Validate applicable statement of financial position, profit/loss/OCI, equity, cash-flow, comparatives and notes. Separate calculation output from rendering and preserve both in a manifest.

2. Create immutable draft package snapshots only after scoped review prerequisites pass. Dispatch Draft FS and MIR as distinct versioned artifacts in one linked conversation, with exact matching references; neither message status nor file download counts as approval.

3. Client management may approve, reject, conditionally approve or respond to the paired request. Record verified accepting authority and exact viewed package/request version. Conditional approval (for example subject to posting) cannot satisfy final approval until its condition is evaluated and a current final decision recorded.

4. Handle out-of-band Office edits: reconcile saved provider version, require financial figure changes to return to structured sources/approved adjustment, classify narrative edits and re-review. Do not continue claiming the original database calculation matches a manually altered spreadsheet.

5. For audit-only service, accept a separately versioned management-prepared package under its own intake/review contract; do not require the firm to produce accounts. Final issued FS must later be paired with the correct report for audit services, or released through the accounting-only path without an opinion.

## Acceptance Criteria

- [ ] Package manifest reproduces all calculation inputs and output totals.
- [ ] Stale or conditionally approved draft cannot satisfy final approval.
- [ ] Draft FS and MIR responses remain bound to their separate correct versions.
- [ ] Out-of-band content changes cannot retain a false current package approval.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_financial_statements
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

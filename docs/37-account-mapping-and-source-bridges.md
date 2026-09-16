# 37 — Versioned taxonomy mappings and source reconciliation

## Objective

Create reviewed account mapping and replacement-source bridges before adjustment plans consume client data.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-003,005,007,010; AT-09–10; ET-27; VT-16–17.

**Dependencies:** [36 — Bounded TB parsing, staging, and atomic promotion](36-safe-tb-import-and-validation.md)

**Execution gate:** file 36 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/accounting/mapping.py`
- **Create:** `production/audit_practice/audit_practice/accounting/bridges.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_mapping_and_bridges.py`
- **Modify:** `production/audit_practice/audit_practice/api/accounting.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement draft_mapping, submit_mapping and approve_mapping with pinned framework/taxonomy/service/period and exact dataset. Validate full applicable account coverage, many-to-one aggregation and approved splits. Small individually unmapped balances must not evade a significant aggregate unmapped total.

2. Replacement source creates a new dataset and bridge, never an in-place row edit. Compare old/new balances by dimensions and identify journal candidates without auto-asserting reflection from coincidentally matching totals.

3. A source bridge records reviewer-verified REFLECTED/NOT_REFLECTED/PARTIAL/UNKNOWN per logical journal revision, posting evidence, period/currency and rationale. PARTIAL/UNKNOWN blocks plan selection until a reviewed explicit treatment exists; no guessed residual entry.

4. Mapping or bridge approval uses the existing exact-version decision engine and synchronously advances relevant generations. Permission checks restrict customer-managed answers from becoming firm technical approval.

5. Register only typed mapping/bridge command handlers and evidence providers. Add a query returning source lineage, control totals and current blockers, without materializing a full unbounded dataset into the UI.

## Acceptance Criteria

- [ ] Unmapped aggregate balances block final mapping approval.
- [ ] Replacement preserves the old dataset, mapping and approval.
- [ ] Matching totals alone do not mark a journal reflected.
- [ ] Partial/unknown reflection and stale bridge revision block downstream plan selection.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_mapping_and_bridges
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

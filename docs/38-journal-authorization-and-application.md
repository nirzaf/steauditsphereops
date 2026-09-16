# 38 — Journal review, management authorization, and reflection-aware plans

## Objective

Implement adjustment plans that cannot double-count journals or post client audit data into the firm ledger.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-004–007,010–013; AT-10–11; ET-26–27; VT-16–17; P0-07.

**Dependencies:** [37 — Versioned taxonomy mappings and source reconciliation](37-account-mapping-and-source-bridges.md)

**Execution gate:** file 37 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database).

## Target Files

- **Create:** `production/audit_practice/audit_practice/accounting/journals.py`
- **Create:** `production/audit_practice/audit_practice/accounting/plans.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/journal_export.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_journals.py`
- **Modify:** `production/audit_practice/audit_practice/api/accounting.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Read / preserve:** `fixtures/replacement_tb_aj001_reflected.csv`
- **Read / preserve:** `fixtures/expected_results.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Commands create_journal, revise_journal, submit_journal, review_journal and record_management_authorization capture exact balanced lines, logical ID/revision, reason, accounts, period/currency and independent/management decisions. Technical review is not management authorization.

2. Build an immutable adjustment plan from approved base/mapping, one selected revision per logical journal and reviewed reflection bridge. REFLECTED contributes zero further application; NOT_REFLECTED applies the authorized amount; PARTIAL/UNKNOWN holds. Reversal/correction needs an explicit reviewed linked journal.

3. Calculate adjusted values with Decimal and persist unique application identities under the client-period guard. Concurrent plan application cannot create two postings or two current plan promotions. Capture plan/input/safety generations for downstream FS.

4. Management rejection retains an uncorrected-item record and later audit reporting evaluation; do not force a false correction. Initially provide a controlled journal export for the client accountant, not live posting credentials. Client ledger integration is out of scope unless separately approved.

5. Port the verified P0 fixture semantics into production tests: apply AJ-001, import replacement already containing it, independently confirm reflection, then apply zero again. Reject duplicate journal revisions, stale authorization and mismatched entity/period/currency.

## Acceptance Criteria

- [ ] The expected 175,000 fixture result remains unchanged after reflected replacement.
- [ ] Two concurrent application attempts produce one logical application.
- [ ] Rejected/unapproved journals never alter the adjusted dataset.
- [ ] No client adjustment creates an ERPNext firm Journal Entry/GL Entry.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_journals
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 36 — Bounded TB parsing, staging, and atomic promotion

## Objective

Implement safe, exact and resumable client accounting ingestion without posting anything to the firm ledger.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-001–002; FR-VAL-001–004; AT-07–08; ET-23–25; DOC-13–14.

**Dependencies:** [35 — Accounting datasets, journals, mappings, and FS schema](35-accounting-data-schema.md)

**Execution gate:** file 35 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database).

## Target Files

- **Create:** `production/audit_practice/audit_practice/accounting/__init__.py`
- **Create:** `production/audit_practice/audit_practice/accounting/parsers.py`
- **Create:** `production/audit_practice/audit_practice/accounting/imports.py`
- **Create:** `production/audit_practice/audit_practice/accounting/validation.py`
- **Create:** `production/audit_practice/audit_practice/api/accounting.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_tb_import.py`
- **Modify:** `production/audit_practice/pyproject.toml`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `infra/production/versions.json`
- **Read / preserve:** `fixtures/baseline_tb.csv`
- **Read / preserve:** `fixtures/expected_results.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use Python csv and openpyxl read-only XLSX parsing; use xlrd only for explicitly approved legacy XLS input. Pin dependencies in the toolchain record. Reject encrypted, malformed, macro-dependent/external-link/formula-only sources unless the approved intake policy defines a safe reviewed path. Do not evaluate workbook formulas or trust cached values without policy/evidence.

2. Validate byte and decompressed archive limits, sheet/row/column bounds, explicit column mapping, identity/period/currency, locale separators, leading-zero account codes, debit/credit convention, non-finite values and dimensioned duplicates. Convert strings to Decimal, never float -> Decimal; validation failures never become zero.

3. Store original receipt before parsing. Stage rows in bounded committed chunks linked to a noncurrent dataset, with checkpoint/progress and duplicate protection. Only after all controls pass, promote the dataset in one short guarded transaction that advances generation and creates impact intent. Partial staging cannot become current.

4. Provide start_import, get_import_status, inspect_validation and approve/promote commands with clear rights and idempotency. A crashed import resumes/discards its own staging, not an unrelated dataset; uncertain provider receipts reconcile before ingest.

5. Attach prior-year audited FS as versioned source evidence with period and visibility checks; do not infer financial figures from uploaded PDF narratives automatically. Audit-only can import management-provided inputs without enabling firm bookkeeping or client-ledger posting.

## Acceptance Criteria

- [ ] Baseline fixture parses exactly and remains outside ERPNext General Ledger.
- [ ] Unbalanced/ambiguous/formula-only/non-finite/oversized sources produce explicit validation reports.
- [ ] Failure halfway through staging leaves the previous current dataset intact.
- [ ] Repeat/resume does not create duplicate promoted datasets.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_tb_import
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

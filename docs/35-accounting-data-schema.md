# 35 — Accounting datasets, journals, mappings, and FS schema

## Objective

Create the accounting model and database constraints before import, adjustment or statement APIs are implemented.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-001–013; FR-REV-001–007; DOC-13–14,17–19,23.

**Dependencies:** [34 — R2 onboarding and evidence end-to-end acceptance](34-r2-onboarding-evidence-exit.md)

**Execution gate:** file 34 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_dataset/audit_tb_dataset.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_dataset/audit_tb_dataset.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_dataset/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_row/audit_tb_row.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_row/audit_tb_row.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_tb_row/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_set/audit_mapping_set.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_set/audit_mapping_set.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_set/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_line/audit_mapping_line.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_line/audit_mapping_line.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_mapping_line/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal/audit_journal.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal/audit_journal.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_line/audit_journal_line.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_line/audit_journal_line.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_line/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_source_bridge/audit_source_bridge.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_source_bridge/audit_source_bridge.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_source_bridge/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reflection_item/audit_reflection_item.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reflection_item/audit_reflection_item.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reflection_item/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_adjustment_plan/audit_adjustment_plan.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_adjustment_plan/audit_adjustment_plan.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_adjustment_plan/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_application/audit_journal_application.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_application/audit_journal_application.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_journal_application/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_supporting_schedule/audit_supporting_schedule.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_supporting_schedule/audit_supporting_schedule.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_supporting_schedule/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_fs_package/audit_fs_package.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_fs_package/audit_fs_package.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_fs_package/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_management_response/audit_management_response.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_management_response/audit_management_response.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_management_response/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/accounting.py`
- **Create:** `production/audit_practice/audit_practice/patches/v1_accounting_indexes.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_accounting_schema.py`
- **Modify:** `production/audit_practice/audit_practice/patches.txt`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. TB Dataset references client/engagement/period/currency/source receipt, parse profile, stage, row count, control totals, digest and predecessor. TB Row is a standalone scoped record linked to the dataset for chunked processing, not a huge inline child array. Unique account code/entity/dimension keys preserve leading zeroes.

2. Mapping Set/Line stores exact taxonomy/framework version and account/dimension classification. Journal/Line has stable logical journal ID, revision, balanced Decimal postings, preparer, rationale and management/technical approval references. Source Bridge/Reflection Item links old/new datasets to journal revisions with REFLECTED/NOT_REFLECTED/PARTIAL/UNKNOWN and reviewed evidence.

3. Adjustment Plan identifies base dataset, selected journal revisions and reflection bridge; Journal Application has unique plan/logical-journal identity and exact applied amount. Preserve reversals/corrections explicitly rather than accepting two active revisions of one logical journal.

4. Supporting Schedule stores typed cash-flow/comparative/disclosure/reconciliation inputs and version. FS Package captures framework, currencies, mapping, adjusted data, schedules, input manifest, engine/template versions and exact artifacts. Management Response binds a package/request snapshot and accept/reject/conditional/info-response decision.

5. Use policy-approved DECIMAL precision in MariaDB; validate that ORM/serialization does not route material arithmetic through binary float. Add unique indexes and bounded row-text fields. Schema test imports no future calculation engine and uses protected controllers with links created in this migration or earlier.

## Acceptance Criteria

- [ ] All 13 accounting DocTypes and indexes migrate before import endpoints.
- [ ] Same account code with distinct valid dimensions is supported; true duplicate dimension key rejects.
- [ ] Dataset replacement cannot overwrite original rows or approvals.
- [ ] Money round trips with the approved exact scale and no silent float drift.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_accounting_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 31 — PBC request, evidence association, and suitability schema

## Objective

Create PBC records and review history before upload or evidence-acceptance handlers are implemented.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-PBC-001–010; DOC-11; BT-04–06,18.

**Dependencies:** [30 — Engagement terms, verified advance, and restricted activation](30-terms-advance-and-portal-activation.md)

**Execution gate:** file 30 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_request/audit_pbc_request.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_request/audit_pbc_request.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_request/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_submission/audit_pbc_submission.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_submission/audit_pbc_submission.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_submission/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_review/audit_pbc_review.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_review/audit_pbc_review.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_pbc_review/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/pbc.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_pbc_schema.py`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. PBC Request includes engagement/period, category, requirement/criteria, owner, reviewer, due date, criticality, expected format, visibility and revision. Request drafts and formally issued requests are distinct.

2. PBC Submission references request revision and exact receipt snapshot, submitting identity, mode ELECTRONIC/HARD_COPY_READY/PHYSICAL_RECEIVED, custody evidence where applicable and replacement lineage. Hard-copy readiness has no invented bytes/digest or physical receipt timestamp.

3. PBC Review is append-only with exact submission, reviewer, suitability decision ACCEPT/CLARIFY/REJECT, reason, expected revision and timestamp. Capture status is independent from suitability and downstream completion.

4. Set one current submission relationship using guarded revision logic while retaining all historical submissions. Apply scope checks to every relationship and limited client field serialization. Do not add future audit-plan links until planning schemas exist.

## Acceptance Criteria

- [ ] Requests/submissions/reviews migrate before any PBC API.
- [ ] Hard-copy-ready state cannot falsely satisfy electronic receipt/custody evidence.
- [ ] Cross-engagement or wrong-period submission links are rejected.
- [ ] Prior submissions/reviews survive replacement.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_pbc_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

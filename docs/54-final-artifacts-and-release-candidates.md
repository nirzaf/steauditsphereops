# 54 — Final artifacts, signature lineage, and eligible release candidates

## Objective

Prepare exact final deliverables and create only eligible release candidates, without issuing or sending them.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-001–004,006,010–011; DOC-21–23; AT-25; ET-33–35.

**Dependencies:** [47 — Completion package, representations, EQR, opinion, and discussion](47-completion-eqr-opinion-and-final-discussion.md); [53 — Independent checkpoint storage and non-rollbackable epoch adapter](53-independent-checkpoint-and-epoch-store.md)

**Execution gate:** file 53 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/finalization.py`
- **Create:** `production/audit_practice/audit_practice/records/candidates.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/final_audit_report.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/final_accounting_package.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_finalization.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Render final report/FS from the approved completion/opinion and management-approved package, not mutable working files. Link report to the exact FS version, report date and required final discussion; validate service-specific outputs so accounting-only/internal-audit do not require an external opinion pair.

2. Use a separate finalization operation/draft while waiting for generation, signing or protection. Do not label this an eligible Release Candidate before the upstream controls required by FR-REL-001 are satisfied. It may expose clear missing-input/approval blockers without asserting readiness.

3. Collect authorized signatures through the existing adapter; signed bytes have distinct hashes and approved-input lineage. Verify no financial content changed unexpectedly during signing; protect the exact resulting report/FS snapshots and record observed protection.

4. Create the immutable candidate in a guarded transaction capturing current input/safety generations, exact signed manifest, completion references, recipients and policy versions. Reject mismatched report/FS pair, stale approval, missing required EQR or unknown protection.

5. No real issuance event, invoice trigger or external delivery is performed here. Approval/publish links expose only current safe candidate metadata to authorized roles; preserve invalidated candidates historically.

## Acceptance Criteria

- [ ] A report attached to the wrong FS version cannot become an eligible candidate.
- [ ] Missing final controls remain finalization blockers, not a falsely READY candidate.
- [ ] Signed/protected output bytes match the stored candidate manifest.
- [ ] Source change during preparation invalidates the candidate generation.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_finalization
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 45 — Procedure execution, frozen workpapers, and conclusion summary

## Objective

Implement preparation and exact-version workpaper submission with a complete conclusion-summary manifest.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUD-007–009; FR-REV-001–003; DOC-15–16; G6.

**Dependencies:** [44 — Risk-response coverage, reconciled populations, and sample plans](44-risks-populations-and-sampling.md)

**Execution gate:** file 44 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit/workpapers.py`
- **Create:** `production/audit_practice/audit_practice/audit/summaries.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/workpaper.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/conclusion_summary.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_workpapers.py`
- **Modify:** `production/audit_practice/audit_practice/api/audit.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Commands create_workpaper, save_draft, attach_evidence, record_procedure_result and submit_workpaper require assigned preparer authority, current revision and appropriate scope. Record procedure, assertion/risk, population/sample references, work performed, results and conclusion.

2. Submission captures saved exact Office/generated artifact bytes plus structured evidence manifest and author set. Unsaved Office work is not submitted by implication. The viewer must present the same snapshot identifier expected by reviewer commands.

3. Contradictory evidence creates a visible blocker and required additional-work/independent/partner disposition; no single pass checkbox closes it. Preserve prior evidence and conflicting items in lineage.

4. Build DOC-16 conclusion summary from exact workpaper submissions, relevant FS package, risk coverage and outstanding review/findings. Generating a summary aggregates facts; an authorized Senior submits it, and approval remains a separate professional action.

5. Register G6 only for the applicable current submission set and summary. A new submitted revision supersedes downstream review eligibility, not the old record. Incomplete or missing professional provider returns a blocker, never inferred completion.

## Acceptance Criteria

- [ ] Submitted workpaper and summary cannot be edited through generic APIs.
- [ ] Later working-file changes do not change the submitted snapshot.
- [ ] Contradictory evidence remains blocking until its documented disposition.
- [ ] Summary members match the current exact submission revisions and FS dependencies.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_workpapers
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

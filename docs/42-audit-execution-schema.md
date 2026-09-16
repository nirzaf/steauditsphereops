# 42 — Planning, risk, samples, workpapers, findings, and completion schema

## Objective

Create the audit execution and completion records before audit procedures, reviews or opinion APIs are enabled.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUD-001–012; FR-REV-001–008; DOC-09–10,12,15–16,20–21.

**Dependencies:** [41 — Accounting workspace, client responses, and audit handoff](41-accounting-workspace-and-linked-handoff.md)

**Execution gate:** file 41 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_plan/audit_plan.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_plan/audit_plan.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_plan/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_materiality/audit_materiality.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_materiality/audit_materiality.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_materiality/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_risk/audit_risk.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_risk/audit_risk.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_risk/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population/audit_population.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population/audit_population.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population_item/audit_population_item.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population_item/audit_population_item.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_population_item/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_plan/audit_sample_plan.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_plan/audit_sample_plan.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_plan/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_item/audit_sample_item.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_item/audit_sample_item.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_sample_item/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_programme/audit_programme.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_programme/audit_programme.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_programme/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper/audit_workpaper.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper/audit_workpaper.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper_submission/audit_workpaper_submission.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper_submission/audit_workpaper_submission.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_workpaper_submission/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_review_point/audit_review_point.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_review_point/audit_review_point.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_review_point/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_finding/audit_finding.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_finding/audit_finding.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_finding/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_remediation_action/audit_remediation_action.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_remediation_action/audit_remediation_action.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_remediation_action/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_completion/audit_completion.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_completion/audit_completion.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_completion/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_conclusion_summary/audit_conclusion_summary.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_conclusion_summary/audit_conclusion_summary.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_conclusion_summary/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/audit.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_audit_schema.py`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Plan records scope/timing/fieldwork mode/team-level allocation/deadlines and approved programme versions. Materiality records benchmark, rationale, thresholds, exact currency and version. Risk records assertion/area/significance/response ownership and dependencies.

2. Population and standalone Population Item provide bounded reconciled source rows and control totals; Sample Plan/Item records reviewed method, deterministic selection metadata, inclusion probabilities when applicable, selected identity and testing status. Never silently replace a missing selected item.

3. Programme and Workpaper capture tailored procedure, scope, author/preparer set, evidence and draft revision. Workpaper Submission freezes an exact manifest. Review Point targets submission/version with severity/owner/response/independent clearer and history.

4. Finding and Remediation Action separate audit conclusion, management action ownership/due date, progress and retest. Completion holds management representations, manager/partner/EQR decisions, opinion selection/reasons and final-discussion evidence. Conclusion Summary freezes member submissions/packages and unresolved issues.

5. Use protected controllers and explicit same-scope Link validation; add indexes for role/owner/due-state queues. Register all 15 DocTypes and precise view permissions. Client access to selected management-action fields does not expose private review points or draft opinions.

## Acceptance Criteria

- [ ] All audit schemas migrate before audit commands.
- [ ] Private reviews/opinions cannot be serialized into client-facing findings.
- [ ] Every submission and summary references exact evidence rather than a mutable URL.
- [ ] Sample item identity and history survive exception handling.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_audit_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

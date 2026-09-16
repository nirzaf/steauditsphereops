# 43 — Planning, materiality, team allocation, and announcement

## Objective

Implement approved engagement planning and formal client announcement with service-specific prerequisites.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUD-001–003; FR-GATE-003; DOC-09–10,12; G5.

**Dependencies:** [42 — Planning, risk, samples, workpapers, findings, and completion schema](42-audit-execution-schema.md)

**Execution gate:** file 42 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit/planning.py`
- **Create:** `production/audit_practice/audit_practice/audit/materiality.py`
- **Create:** `production/audit_practice/audit_practice/api/audit.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/audit_plan.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/audit_announcement.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_planning.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Commands draft_plan, tailor_programme, submit_plan and approve_plan capture service/industry, methodology version, remote/on-site execution, staffing by seniority, responsibility, fieldwork dates and deadline. Confirm G1–G4 eligibility and required resources; no work authorized by assigning a team alone.

2. Compute materiality thresholds using Decimal from an approved benchmark/rationale and policy, with independent review. Store thresholds and sources; a later decrease triggers impact evaluation of sampling/coverage/misstatements rather than automatically declaring previous testing sufficient.

3. Tailor approved programme templates without mutating the shared master version. Required risk/procedure coverage is validated against the supported service profile; missing evidence/risk responses become blockers rather than omitted sections.

4. Generate DOC-09/10 from the exact approved plan and current critical request manifest. The announcement explains commencement and required client preparations and uses the existing safe correspondence outbox. Its receipt/delivery status is not fieldwork-completion evidence.

5. Register G5 from approved plan, announcement, assigned competent team, critical request readiness and absence of applicable blocking hold. Interim planning can proceed with documented dependencies; do not force completion of all final FS before any planning work.

## Acceptance Criteria

- [ ] Plan approval requires current eligible scope and appropriate role.
- [ ] Materiality change invalidates affected sampling/completion evaluation.
- [ ] Announcement includes the exact approved plan/request references.
- [ ] G5 cannot pass with a missing required plan/critical readiness control.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_planning
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 47 — Completion package, representations, EQR, opinion, and discussion

## Objective

Implement the professional completion controls that must precede any final release candidate.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUD-009; FR-REV-006–007; FR-REL-001–003; DOC-18–21; G7.

**Dependencies:** [40 — FS calculation, versioned drafts, MIR, and management response](40-financial-statements-and-management-response.md); [46 — Independent review points, findings, responses, and follow-up](46-reviews-findings-and-remediation.md)

**Execution gate:** file 46 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit/completion.py`
- **Create:** `production/audit_practice/audit_practice/audit/opinions.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/review_record.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/opinion_record.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_completion.py`
- **Modify:** `production/audit_practice/audit_practice/api/reviews.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Assemble current conclusion summary, evaluated Draft FS/MIR responses, representations, consultation evidence, misstatement evaluation, manager recommendation, partner decision and required EQR into an exact completion manifest. Do not treat client FS approval as auditor approval.

2. Enforce independent EQR assignment/eligibility and completion before report dating/release where required. Store report date rules and actual decision timestamps; no backdating to bypass a missing EQR or representation.

3. Partner/signatory alone records professional opinion type/rationale under the approved methodology. Modified-opinion paths preserve unresolved facts and documented professional evaluation; the software cannot infer a professional opinion from a risk score or automatically select an unmodified opinion.

4. Record final discussion date, participants, issues and disposition evidence separately from report transmission. Ensure the current paired report/FS scope and material unresolved issues are reflected in the decision.

5. Register service-specific G7: accounting-only uses its technical/management completion policy and no auditor opinion/EQR. Any changed relevant input/version makes completion stale through the generation engine. Final report generation/delivery remains unavailable until R4.

## Acceptance Criteria

- [ ] Required incomplete EQR/representations blocks report dating and release readiness.
- [ ] Client/technical-admin/preparer cannot select or approve auditor opinion.
- [ ] Modified opinion route preserves evaluated unresolved misstatements.
- [ ] Stale completion manifest and missing final-discussion evidence remain visible blockers.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_completion
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 48 — Internal-audit engagements and continuing remediation

## Objective

Implement the approved internal-audit variant without incorrectly applying external statutory audit outputs or approval gates.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-SCOPE-001; FR-AUD-010–012; FR-E2E-001; service-specific applicability.

**Dependencies:** [47 — Completion package, representations, EQR, opinion, and discussion](47-completion-eqr-opinion-and-final-discussion.md)

**Execution gate:** file 47 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Internal-audit professional owner supplies signed methodology, reporting scope and cadence; automated tests cannot replace that approval.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit/internal_audit.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/internal_audit_report.html`
- **Create:** `production/audit_practice/audit_practice/tests/fixtures/internal_audit_profile.json`
- **Create:** `production/audit_practice/audit_practice/tests/test_internal_audit.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`
- **Modify:** `production/audit_practice/audit_practice/api/audit.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Load the signed internal-audit service contract defining engagement authority, scope/period/cadence, audit programme, control observations, reporting recipients and approved output set. Reuse shared evidence, workpaper/review and corrective-action services rather than a duplicate subsystem.

2. Apply internal-specific completion/report approval rules and mark external auditor opinion, statutory FS pair and unrelated financial gates N/A only where approved. N/A cannot arise merely because the corresponding record is missing.

3. Support agreed recurring visits/reviews and action follow-up via explicit schedules/tasks when in scope; do not invent weekly/monthly cadence. Findings retain owners, deadlines, management response and retest across engagement closure.

4. Record a controlled internal-audit report artifact with exact manifest and recipients for the later generic service-specific release mechanism. Do not reuse an external-audit opinion template under a different title.

5. Enable this service profile only after its functional tests and professional owner sign-off. If source methodology or templates are absent, return BLOCKED and leave the service disabled rather than silently claiming full service coverage.

## Acceptance Criteria

- [ ] Internal-audit journey uses its approved outputs and authority model.
- [ ] External-only gates are explicitly N/A without removing shared evidence/record controls.
- [ ] Outstanding follow-up survives engagement close and can be retested later.
- [ ] Unsupported/missing methodology prevents enabling the internal-audit profile.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_internal_audit
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

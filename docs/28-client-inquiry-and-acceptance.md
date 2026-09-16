# 28 — Inquiry, client profile, questionnaire, and acceptance commands

## Objective

Implement versioned client assessment and authorized acceptance/continuance without converting risk scores into autonomous decisions.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-CL-001–005; FR-SCOPE-001; FR-INT-009; DOC-01–04; AT-01–06.

**Dependencies:** [25 — Client assessment and commercial onboarding schema](25-onboarding-and-commercial-schema.md); [27 — Approved artifact rendering and verified signature evidence](27-artifact-rendering-and-signature-adapter.md)

**Execution gate:** file 27 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [OpenSanctions data licensing](https://www.opensanctions.org/licensing/).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/onboarding.py`
- **Create:** `production/audit_practice/audit_practice/domain/acceptance.py`
- **Create:** `production/audit_practice/audit_practice/integrations/screening.py`
- **Create:** `production/audit_practice/audit_practice/api/clients.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_acceptance.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use ERPNext Lead/Customer where available in the selected release and the custom Audit Client link; do not install a parallel CRM by default. Commands create_lead, submit_profile, revise_profile, respond_questionnaire and verify_answer preserve submissions and exact questionnaire versions.

2. Implement deterministic mandatory evidence, integrity, UBO, independence, conflict and service eligibility checks from approved policies. Multiple specialist triggers accumulate rather than replacing each other. Missing evidence remains HOLD even when numerical risk is low; confirmed prohibition has no admin/partner override.

3. Only authorized professional roles decide ACCEPT/CONTINUE/HOLD/DECLINE with rationale and current verified evidence. Client contributors respond but cannot verify their own professional clearance. New service or material fact requires reassessment under a new current decision.

4. Screening is an optional adapter with licensed, approved datasets; match candidates require human disposition and retained version/timestamp. Never automatically accuse a client or convert a possible match into a conclusive finding. If provider disabled, use an explicitly approved manual clearance and record its evidence.

5. Bind DOC-01–04 artifacts and G1 evidence to the current client/service/period. Do not activate full portal/work at acceptance alone. Initial client evidence is collected via staff or setup-only channels defined by policy, avoiding a circular dependency on the later G4 portal grant.

## Acceptance Criteria

- [ ] UNKNOWN answer or missing identity evidence blocks acceptance despite low risk score.
- [ ] Confirmed prohibition cannot be overridden by partner/admin.
- [ ] Revised profile retains the original; clearance identifies exact evidence version.
- [ ] Screening false-positive disposition is preserved and no automatic accusation is produced.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_acceptance
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

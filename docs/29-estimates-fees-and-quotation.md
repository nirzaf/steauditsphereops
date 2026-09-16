# 29 — Cost estimates, fee review, and exact quotation acceptance

## Objective

Implement commercial readiness with versioned estimates, independent fee approval and client-safe quotation output.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-FIN-001–003; FR-CL-006; DOC-05–07; G2.

**Dependencies:** [28 — Inquiry, client profile, questionnaire, and acceptance commands](28-client-inquiry-and-acceptance.md)

**Execution gate:** file 28 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/commercial.py`
- **Create:** `production/audit_practice/audit_practice/domain/commercial.py`
- **Create:** `production/audit_practice/audit_practice/api/commercial.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/quotation.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_commercial.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Calculate planned cost and selling basis with Decimal from approved staff-level hours/rates, travel, currency and fee basis. Preserve original estimate, revised budget and eventual actuals as different records; do not rewrite the first estimate when scope changes.

2. Commands create_estimate, revise_estimate, submit_fee, approve_fee and issue_quotation use exact commercial revision and established approval engine. Fee changes invalidate old approvals and prevent stale quotation issuance.

3. Quotation output includes approved fee, scope, assumptions, expiry, tax treatment and terms references but excludes internal cost rates, margin and staffing remuneration. Client management accepts/rejects the specific issued quotation; acceptance is not engagement activation.

4. Use existing ERPNext Quotation with explicit custom linkage to the current commercial case where the approved workflow fits. Do not invent a second ledger or duplicate sales records. Fixed-fee scope cannot later trigger an additional time-based invoice for the same work.

5. Register G2 predicates and DOC-05–07. Approved exemptions/fee changes require an immutable decision with authorized owner; no free-text toggle that waives a professional gate.

## Acceptance Criteria

- [ ] Rounding/cost/fee calculations match approved fixtures exactly.
- [ ] Changed fee/estimate makes the prior approval insufficient.
- [ ] Client quotation data contains no internal rates or margin.
- [ ] Repeated quotation issue produces one logical issued quotation.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_commercial
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

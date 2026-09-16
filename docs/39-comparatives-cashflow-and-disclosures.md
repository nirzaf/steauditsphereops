# 39 — Supporting schedules, comparatives, and disclosure completeness

## Objective

Implement the supplementary information required for defensible financial statements instead of assuming a TB is sufficient.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-ACC-007–008; AT-12,19; ET-28; DOC-17,23.

**Dependencies:** [38 — Journal review, management authorization, and reflection-aware plans](38-journal-authorization-and-application.md)

**Execution gate:** file 38 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Technical accounting owner supplies approved framework-specific formulae and disclosure/templates; the agent does not write accounting policy.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/accounting/schedules.py`
- **Create:** `production/audit_practice/audit_practice/accounting/comparatives.py`
- **Create:** `production/audit_practice/audit_practice/accounting/disclosures.py`
- **Create:** `production/audit_practice/audit_practice/accounting/decimal_policy.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_supporting_schedules.py`
- **Modify:** `production/audit_practice/audit_practice/api/accounting.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Store versioned cash-flow workings with reconciliation to opening/closing cash and approved movement classifications. Prohibit unexplained plug lines, silently rounded away differences and invented missing movements.

2. Create comparative bridges linking prior audited package/dataset to current presentation. Capture restatements, reclassifications, policies, currency and evidence. Prior data is historical input, not copied current management approval.

3. Require approved disclosure questionnaire content/framework/entity profile, narrative owner, sources and technical review. Missing commitments, contingencies, estimates, policies or other necessary information becomes an explicit task; do not infer it from a trial balance or generate fabricated text.

4. Implement shared Decimal quantization and currency/rounding policy using the signed business contract. Separate input precision, calculation precision and display precision; retain rounding adjustments only where explicitly approved and reconciled.

5. Changes to schedules, comparison treatment or disclosure responses advance the input generation and invalidate dependent package decisions via the existing impact service. Unsupported frameworks/group consolidation remain explicitly disabled rather than approximated.

## Acceptance Criteria

- [ ] Cash-flow does not pass with an unexplained balancing plug.
- [ ] Missing required disclosure/comparative information blocks final package completion.
- [ ] Rounding and currency boundary fixtures reconcile exactly.
- [ ] Changing a schedule makes the previous package approval stale.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_supporting_schedules
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

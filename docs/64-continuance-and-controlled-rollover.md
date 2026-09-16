# 64 — Next-period continuance, non-renewal, and controlled roll-forward

## Objective

Create next-period engagement shells and fresh continuance decisions without copying prior professional conclusions as current work.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-CL-009–010; FR-GATE-009; FR-E2E-008; FR-AUD-010–011; G10.

**Dependencies:** [58 — Archive assembly and purpose-scoped evidence exports](58-archive-manifests-and-controlled-exports.md); [63 — Time capture, invoice allocation, and commercial close](63-time-billing-and-commercial-close.md)

**Execution gate:** file 63 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/continuance.py`
- **Create:** `production/audit_practice/audit_practice/api/continuance.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_continuance.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/ui/routes.py`
- **Modify:** `production/audit_practice/audit_practice/public/js/portal.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Roll forward only approved standing client details, source references, programme templates and open remediation responsibilities into a new client-period/engagement identity. Explicitly reset current questionnaires, terms decisions, samples, conclusions, review approvals, signatures and release state.

2. A scheduled next-period shell may exist before continuance, but professional work and portal permissions remain gated by fresh service-specific assessment, terms and required commercial/access conditions. Do not inherit staff assignments indefinitely without current validity checks.

3. Retain prior issued report/FS/archive/checkpoint pointers as read-only history with authorized reference access. Preserve open follow-up actions with owners/due dates; closing a prior period cannot delete them.

4. Partner records CONTINUE/HOLD/NON_RENEW with rationale and current evidence. Non-renewal creates deletion-disabled closeout while preserving record retention/hold obligations. A different service requires its own acceptance/terms, not reuse of last year's service permission.

5. Use idempotent next-period shell key, transaction-scoped generation guards and accurate G10 substatus distinguishing archive completeness from renewal readiness. UI navigation selects the new period without overwriting the prior engagement.

## Acceptance Criteria

- [ ] Repeated rollover creates one next-period shell.
- [ ] No prior sample, conclusion or approval is current in the new period.
- [ ] New work remains blocked until fresh continuance/terms conditions pass.
- [ ] Non-renewal and archive preserve historical releases and open remediation.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_continuance
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

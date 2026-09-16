# 30 — Engagement terms, verified advance, and restricted activation

## Objective

Implement the ordered terms/advance/onboarding controls that authorize client access and engagement commencement.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-CL-006–008; FR-FIN-002–003; FR-AUTH-003; DOC-08; G3–G4.

**Dependencies:** [15 — Entra sign-in, stable identity mapping, and session revocation](15-entra-sessions-and-lifecycle.md); [29 — Cost estimates, fee review, and exact quotation acceptance](29-estimates-fees-and-quotation.md)

**Execution gate:** file 29 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/terms.py`
- **Create:** `production/audit_practice/audit_practice/application/activation.py`
- **Create:** `production/audit_practice/audit_practice/api/activation.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/engagement_letter.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_activation.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/security/identity.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Generate and review an EL from the accepted quotation/service scope, send the exact version through controlled correspondence and record client authorized-signatory acceptance using the signature/evidence service. Rejection opens a correction path; a newer EL makes the old acceptance insufficient for the changed scope.

2. Finance verifies an actual allocated advance against the proper client, engagement, currency and source Payment Entry/evidence. Wrong-client, insufficient, unallocated or reversed payment cannot satisfy G4. Record verification as a business control distinct from any ledger posting; final invoice allocation is handled later without charging twice.

3. Activation command validates current G1, G2, G3, verified advance, named identity, configured workspace and other approved holds under the scope guard. Issue short-lived single-use onboarding invitation only after eligibility; save only token digest, display/redeem secret once through the approved secure route.

4. Redeem to the pre-bound Entra identity and restricted setup flow; never accept requested roles, arbitrary user IDs or browser demo passwords. Record first-login setup completion and prohibit replay, revocation and expired token use. Client contributors cannot become client management approvers by choosing a field.

5. Advance reversal or material acceptance change synchronously reevaluates safety/eligibility and restricts the affected scope according to approved policy. Preserve old approvals as historical; do not silently delete account history or issued artifacts. Register G3/G4 evidence independently.

## Acceptance Criteria

- [ ] No full client portal activation before exact terms and verified advance.
- [ ] Replay/expiry/identity mismatch in invitation redemption is denied.
- [ ] Reversed or misallocated advance blocks/restricts eligibility with a visible reason.
- [ ] Terms acceptance, finance verification and access grant have separate events/authorities.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_activation
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 57 — Controlled distribution, delivery evidence, and uncertain-outcome recovery

## Objective

Implement final-deliverable distribution with current authorization, exact artifacts and truthful delivery states.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-005–007,011–012; FR-COM-003–006; ET-36–37; VT-11–13.

**Dependencies:** [26 — Scoped messages, notification outbox, and safe correspondence](26-portal-messaging-and-notification-services.md); [56 — Publish and verify the release checkpoint before delivery intent](56-checkpoint-publication-gate.md)

**Execution gate:** file 56 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Approved test sender/recipient resources; real professional report transmission is not authorized by completing this development task.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/delivery.py`
- **Create:** `production/audit_practice/audit_practice/records/delivery_reconciliation.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_delivery.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `production/audit_practice/audit_practice/integrations/microsoft/mail.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. FINAL_DELIVERY requires committed release, verified independent checkpoint, exact protected artifact hashes, permitted environment, current recipient-set/hold policy and valid epoch/fence. Resolve authorized attachments/portal access server-side; clients cannot substitute another report or external destination.

2. Record logical delivery identity per release/channel/recipient and append actual attempts. Distinguish SCHEDULED, SUBMITTING, PROVIDER_ACCEPTED, DELIVERY_CONFIRMED, ACKNOWLEDGED and OUTCOME_UNKNOWN. Graph 202 is provider acceptance, not proof of delivery.

3. On timeout-after-send do not blindly retry or mark failed; reconcile observable provider/message evidence using the same logical operation. If outcome cannot be proven, retain UNKNOWN for operator disposition. No exactly-once claim for email providers without that guarantee.

4. Recheck current recipients, holds and authorization policy immediately before dispatch. User-requested exports revoked in queue are denied; valid historical release approvals are not erased when the employee departs. Define the R0-approved dispatch linearization point and track in-flight sends that cannot be recalled after an intervening hold.

5. Expose client download only for authorized published exact artifacts, with server authorization on each request. No broad anonymous SharePoint sharing link. Use an allowlisted non-production mailbox/recipient to test; leave production sending disabled.

## Acceptance Criteria

- [ ] A forged/missing checkpoint or mismatched artifact blocks transmission.
- [ ] Provider accepted and delivery confirmed remain distinct.
- [ ] Uncertain send is reconciled or left UNKNOWN without blind duplicate send.
- [ ] Revoked user export and current applicable hold block queued distribution.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_delivery
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

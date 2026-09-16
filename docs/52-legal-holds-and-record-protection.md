# 52 — Legal holds and observed record-protection enforcement

## Objective

Implement applicable holds and real protection verification before final-package authorization can succeed.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-004,007–009; FR-REC-007–008; ET-38–40; VT-20,24.

**Dependencies:** [20 — Microsoft transport and trusted repository gateway](20-microsoft-document-gateway.md); [51 — Release, hold, checkpoint, delivery, archive, and recovery schema](51-release-records-and-recovery-schema.md)

**Execution gate:** file 51 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Records administrator authorizes policy operations against R0-approved non-production artifacts only; production retention/legal decisions remain human-owned.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/__init__.py`
- **Create:** `production/audit_practice/audit_practice/records/holds.py`
- **Create:** `production/audit_practice/audit_practice/records/protection.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/records.py`
- **Create:** `production/audit_practice/audit_practice/api/records.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_records_protection.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Records custodians apply/release a hold through scoped commands with rationale and authorized evidence; no delete/overwrite of the hold history. Increment safety generation for affected client-period/engagements and reevaluate release eligibility.

2. Implement the exact supported records-policy operations proven in R0 using separate restricted identity and trusted binding/profile IDs. Keep expected versus observed protection separate; failed/unsupported policy application leaves BLOCKED/PENDING. Never strip protection or widen permissions to make a test pass.

3. Verify the required exact immutable snapshot under the approved threat model, including ordinary edit/delete/unlock permissions and residual administrator powers. Record protection evidence freshness. Protect submitted/issued snapshots separately from mutable working copies to preserve legitimate editing workflows.

4. An applicable release-blocking hold prevents new delivery. Preservation/export required by an authorized hold may proceed under policy; disposal/destructive moves cannot. Do not turn any legal hold into a blanket ban on retaining evidence, or infer jurisdictional policy from prototype TTL.

5. General workers cannot invoke record-profile mutations; credentials and egress capabilities are restricted outside the queue naming convention. Provider failure or stale observation fails closed for release without corrupting safe local drafts.

## Acceptance Criteria

- [ ] An active applicable hold blocks release/delivery and prohibited disposal.
- [ ] Authorized preservation under hold remains possible and audited.
- [ ] A requested but unobserved record label cannot pass protection readiness.
- [ ] Live disposable-artifact edit/delete/unlock tests match the signed protection profile.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_records_protection
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

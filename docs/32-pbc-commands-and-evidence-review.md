# 32 — PBC requests, bounded uploads, replacements, and review

## Objective

Complete the client evidence request-to-review loop with integrity, safe retries and explicit suitability decisions.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-PBC-001–008; FR-COM-002–005; AT-13; BT-04–06,18; ET-09–14.

**Dependencies:** [26 — Scoped messages, notification outbox, and safe correspondence](26-portal-messaging-and-notification-services.md); [31 — PBC request, evidence association, and suitability schema](31-pbc-schema.md)

**Execution gate:** file 31 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/pbc.py`
- **Create:** `production/audit_practice/audit_practice/domain/pbc.py`
- **Create:** `production/audit_practice/audit_practice/api/pbc.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/document_request.html`
- **Create:** `production/audit_practice/audit_practice/tests/test_pbc.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement create_request, issue_request, submit_evidence, mark_hard_copy_ready, record_physical_receipt, review_submission and request_clarification using revisions/idempotency. Pre-fieldwork intake requests may be issued only under approved policy; formal audit announcement depends on the later approved planning module.

2. Enforce approved file allowlist, actual content/signature validation, byte/decompressed-size limits and upload quotas. Treat files as inert untrusted bytes; no formula/macro execution. Store only private authorized objects via evidence gateway; an interrupted or uncertain upload remains pending, not a receipt.

3. Record suitability separately from storage. An assigned reviewer verifies scope, period, completeness and criteria before acceptance; wrong-period files stay unaccepted. Replacement creates a new receipt/submission and invalidates dependent conclusions through the shared impact service.

4. Hard-copy readiness notifies the Senior and alerts the Manager without claiming custody. A separately authorized staff receipt records actual custody/location/evidence. Do not fabricate a file digest for an unscanned physical document.

5. Create deduplicated messages/tasks on issue/upload/clarification/review, with exact destinations and client-safe text. Critical unresolved requests become relevant gate blockers; optional/N_A items require explicit approved applicability.

## Acceptance Criteria

- [ ] Identical submission retry results in one receipt/submission/task set.
- [ ] Wrong period, oversized payload and cross-client request IDs fail.
- [ ] Replacement preserves old bytes/review and marks downstream evaluation stale.
- [ ] Senior task/Manager notification occurs once; readiness alone is not custody.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_pbc
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

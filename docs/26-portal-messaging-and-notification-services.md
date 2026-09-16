# 26 — Scoped messages, notification outbox, and safe correspondence

## Objective

Provide the engagement communication service used by onboarding, PBC, draft responses and role handoffs.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-COM-001–007; FR-NAV-009; BT-07,14,41–44.

**Dependencies:** [19 — Artifact, signature, communication, and notification schema](19-artifact-and-communication-schema.md); [25 — Client assessment and commercial onboarding schema](25-onboarding-and-commercial-schema.md)

**Execution gate:** file 25 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0); [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/communications.py`
- **Create:** `production/audit_practice/audit_practice/application/notifications.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/mail.py`
- **Create:** `production/audit_practice/audit_practice/api/communications.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_communications.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement create_thread, append_message, revise_message, mark_notification_read and list_threads with authorized participants, scope, expected revision and idempotency keys. Sanitize markup; reject arbitrary HTML/script content, cross-client attachments and protected workflow fields.

2. Create portal messages and notification intents with the workflow event transaction. Resolve recipients from active assignments and verified contacts, not a client-supplied arbitrary address. Dedupe per source event/recipient/channel while retaining distinct conversations.

3. General correspondence may carry only approved onboarding/request/draft artifact purposes; final report/FS delivery is a separate forbidden operation until R4. Link a notification to the exact message or snapshot. Do not imply that marking a message read grants approval or closes a review point.

4. Microsoft mail adapter uses the established transport and approved sender/recipient allowlist in test environments. Record provider acceptance separately from actual delivery evidence and acknowledgement. A timeout after submission is OUTCOME_UNKNOWN; no blind send replay or universal exactly-once promise.

5. Add due-date escalation using bounded scheduler jobs; suppress obsolete reminders after revision/reassignment and prevent notification storms. Keep email/WhatsApp channels disabled unless the approved policy and tested adapter exists; portal threads remain the authoritative communication record.

## Acceptance Criteria

- [ ] Same workflow event produces one notification per intended recipient/channel.
- [ ] A client cannot read an internal thread or attach another client's snapshot.
- [ ] Provider 202 acceptance does not set DELIVERED.
- [ ] General correspondence cannot send a final report or bypass the future checkpoint gate.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_communications
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

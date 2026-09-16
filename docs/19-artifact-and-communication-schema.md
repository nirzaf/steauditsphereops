# 19 — Artifact, signature, communication, and notification schema

## Objective

Create reusable artifact and communication records before generation, signature and messaging services are introduced.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-PBC-009–012; FR-COM-001–007; FR-CL-006–007; FR-REC-001–002.

**Dependencies:** [14 — Evidence, manifest, approval, and dependency schema](14-evidence-and-approval-schema.md); [18 — Durable outbox dispatch, bounded queues, and stale-worker fencing](18-durable-outbox-and-worker-leases.md)

**Execution gate:** file 18 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_artifact_template/audit_artifact_template.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_artifact_template/audit_artifact_template.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_artifact_template/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_generated_artifact/audit_generated_artifact.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_generated_artifact/audit_generated_artifact.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_generated_artifact/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_signature_envelope/audit_signature_envelope.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_signature_envelope/audit_signature_envelope.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_signature_envelope/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_communication_thread/audit_communication_thread.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_communication_thread/audit_communication_thread.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_communication_thread/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_portal_message/audit_portal_message.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_portal_message/audit_portal_message.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_portal_message/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_notification/audit_notification.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_notification/audit_notification.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_notification/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/communications.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_communication_schema.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_provider_sync_state/audit_provider_sync_state.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_provider_sync_state/audit_provider_sync_state.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_provider_sync_state/__init__.py`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Artifact Template stores DOC identity, applicable service/framework, version, required data contract, approved template digest and approver. Generated Artifact links exact input manifest, calculation/template versions, draft/final state, output snapshot and visibility. Template approval cannot be set by importing a JSON flag.

2. Signature Envelope references approved input snapshot, named recipient identity, purpose, provider/manual mode, status and signed-output snapshot. Input and signed output digests may differ; preserve their verified lineage. A signature envelope is not a professional approval.

3. Communication Thread belongs to client/engagement with explicit participants and client/internal visibility. Portal Message stores sanitized content, sender identity, attachment snapshot references, source revision and supersession; edits preserve the prior version.

4. Notification records source event ID, recipient binding/role, typed destination, channel, state and dedupe key. No raw secret, mutable file URL, private review text or bank details in client notification payloads. General messages and final-report delivery use different operation kinds.

5. Add bounded text lengths, attachment-count limits, cross-scope validation and unique source-event/recipient/channel keys. Register every new DocType in the deny-by-default permission policy; prove generic create/update still fails.

6. Also create Audit Provider Sync State keyed by provider/repository binding with last committed delta cursor/page checkpoint, lease/fence, reconciliation mode, observation time and error state. The Microsoft delta service uses this persisted table; do not store its authoritative cursor only in Redis or process memory.

## Acceptance Criteria

- [ ] Artifact/signature/message tables exist before their handlers.
- [ ] Duplicate event notifications are constrained without losing different recipients.
- [ ] Client-visible messages reject internal attachments and cross-client thread IDs.
- [ ] Signed bytes and approved input bytes are separate immutable references.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_communication_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 12 — Firm, client, period, engagement, assignment, and guard schema

## Objective

Create the foundational scope and identity tables before authentication, permission or workflow APIs use them.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-SCOPE-001–005; FR-AUTH-001–003; FR-GATE-004; VT-08.

**Dependencies:** [11 — Protected record base and schema conventions](11-protected-record-foundation.md)

**Execution gate:** file 11 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Frappe app scaffolding](https://docs.frappe.io/framework/user/en/tutorial/create-an-app).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_service_profile/audit_service_profile.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_service_profile/audit_service_profile.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_service_profile/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client/audit_client.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client/audit_client.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reporting_period/audit_reporting_period.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reporting_period/audit_reporting_period.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_reporting_period/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_engagement/audit_engagement.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_engagement/audit_engagement.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_engagement/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_identity_binding/audit_identity_binding.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_identity_binding/audit_identity_binding.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_identity_binding/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assignment/audit_assignment.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assignment/audit_assignment.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assignment/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_scope_guard/audit_scope_guard.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_scope_guard/audit_scope_guard.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_scope_guard/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_task/audit_task.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_task/audit_task.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_task/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/scope.py`
- **Create:** `production/audit_practice/audit_practice/patches/__init__.py`
- **Create:** `production/audit_practice/audit_practice/patches/v1_scope_indexes.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_scope_schema.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/__init__.py`
- **Modify:** `production/audit_practice/audit_practice/patches.txt`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Create Audit Service Profile (version, supported actions, enabled); Audit Client (firm Company, optional ERPNext Customer link, legal identity); Audit Reporting Period (client, start/end, currencies); Audit Engagement (client, period, service profile, optional linked engagement, state, revision). Use one Frappe site per operating firm initially; ERPNext multi-company is not cross-firm tenant isolation.

2. Create Audit Identity Binding keyed by approved tenant/subject with optional oid and Frappe User link, actor status and epoch; Audit Assignment links identity, engagement or allowed client scope, professional role, validity and revocation state. Email remains mutable display/contact metadata, never an identity merge key.

3. Create Audit Scope Guard keyed uniquely by firm/client/period with input_generation, safety_generation and revision. Every linked accounting/audit mutation must share this guard. Audit Task records owner/role, due time, typed target, state and source event identity; unrelated activities do not grant record access.

4. Use scoped unique indexes, date/period checks and controller validation rejecting cross-client links. Parent directories and JSON controllers come first; use protected base controllers, not future command services. Explicitly register only required installed ERPNext DocType links.

5. Write additive repeatable index patch with existence checks and preflight duplicate reporting. Do not drop/migrate production data automatically. Tests create two clients and verify invalid cross-scope links and duplicate guard/identity keys fail at the appropriate layer.

## Acceptance Criteria

- [ ] All eight DocTypes install and migrate twice on the disposable site.
- [ ] Two engagements for the same client/period share exactly one guard.
- [ ] Cross-client assignments/links and invalid periods are rejected.
- [ ] No identity is linked automatically by an email match.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_scope_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

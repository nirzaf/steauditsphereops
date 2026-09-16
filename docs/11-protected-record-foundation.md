# 11 — Protected record base and schema conventions

## Objective

Create the default-deny document foundation used by all subsequent DocType controllers. Prevent automatically generated CRUD routes from becoming an alternate professional command path.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-AUTH-005–009; FR-REC-001–002; VT-01–03.

**Dependencies:** [10 — Runtime configuration, secrets boundary, and diagnostic primitives](10-runtime-settings-and-telemetry.md)

**Execution gate:** file 10 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database).

## Target Files

- **Create:** `production/audit_practice/audit_practice/security/__init__.py`
- **Create:** `production/audit_practice/audit_practice/security/protected_document.py`
- **Create:** `production/audit_practice/audit_practice/security/write_context.py`
- **Create:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Create:** `production/audit_practice/audit_practice/tests/helpers.py`
- **Create:** `docs/production/schema-conventions.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_protected_records.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement ProtectedDocument and an internal transaction-scoped write context. The context must originate only in server application commands, not payload flags, request query parameters, browser roles or a publicly whitelisted context setter. Reject direct insert/update/delete of protected records by default.

2. Classify append-only decisions/events, immutable snapshot references and mutable drafts explicitly. Deny update/delete of historical decisions and submitted revisions; corrections are new records linked to the prior identity. Frappe Administrator privilege is not a professional approval role.

3. Define shared scope fields, internal UUID/name strategy, revision BIGINT policy, UTC timestamps, visibility enums and valid link checks. A nullable engagement on client-level onboarding records is deliberate; never require a future engagement to exist before a lead/client can be evaluated.

4. Specify DocType migration rules: JSON metadata/controllers precede APIs; Link options target only installed ERPNext/Frappe or already-created custom DocTypes; optional polymorphic references use a server-side type allowlist. Schema tasks may create validators but must not import later application services.

5. Provide minimal test helpers for internal writes and immutable-record assertions. Add tests ensuring client-supplied bypass flags do not create context; document that raw SQL/DB credentials are a trusted administrative boundary, not magically prevented by controller hooks.

## Acceptance Criteria

- [ ] Untrusted code paths cannot acquire the professional write context through HTTP inputs.
- [ ] Append-only updates/deletes are denied by the base policy.
- [ ] Schema conventions identify migration order and link ownership without forward references.
- [ ] No new production CRUD endpoint is enabled.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_protected_records
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

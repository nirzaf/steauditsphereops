# 16 — Role/assignment authorization across every access path

## Objective

Enforce the same client, engagement, period and professional authority checks for reads and writes across Desk, portal, API, exports and workers.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-AUTH-001–010; FR-PBC-008; FR-VAL-001–005; ET-03–08; VT-01–03,11,22.

**Dependencies:** [11 — Protected record base and schema conventions](11-protected-record-foundation.md); [15 — Entra sign-in, stable identity mapping, and session revocation](15-entra-sessions-and-lifecycle.md)

**Execution gate:** file 15 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/security/authorization.py`
- **Create:** `production/audit_practice/audit_practice/security/queries.py`
- **Create:** `production/audit_practice/audit_practice/security/action_policy.py`
- **Create:** `production/audit_practice/audit_practice/security/permission_reconciliation.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_authorization.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`
- **Modify:** `production/audit_practice/audit_practice/security/protected_document.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement authorize(actor, action, scope, target) using server-resolved role assignments, expiry, active actor and service applicability. Return a typed authorized context; no string role supplied by the browser confers authority. Author/preparer sets participate in independent-review denial.

2. Implement Frappe permission_query_conditions and has_permission hooks for all current custom DocTypes; protect related attachment/search/count/report paths. Do not use get_all for user-facing scoped reads. Scope injection is mandatory in custom query builders; metadata/count denial must not reveal another client.

3. Lock down generic REST writes, Desk save/import, workflow transitions, duplicate/copy, share and export entry points for protected fields and immutable records. Use explicit application commands; tests must invoke real generic endpoints and document controllers, not just call authorize in isolation.

4. Technical administrator can manage diagnostic access but cannot sign, approve or self-clear. Define narrowly scoped bootstrap exceptions outside professional workflows and log them. An existing valid historical signature remains evidence after departure; new decisions need current assignment.

5. Prepare an access-reconciliation service that compares approved repository rights to authoritative assignments using typed operations. Until the provider gateway is implemented, keep provider execution disabled; return a planned drift item, never claim revocation. Each new DocType must join this registry in its schema task.

## Acceptance Criteria

- [ ] Client A cannot obtain Client B content, counts, attachments or export URLs.
- [ ] Generic REST/import/Desk attempts to edit protected fields are denied.
- [ ] Preparer self-review and technical-admin professional approval both fail.
- [ ] Expired/revoked assignments are denied on direct and queued user-requested paths.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_authorization
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

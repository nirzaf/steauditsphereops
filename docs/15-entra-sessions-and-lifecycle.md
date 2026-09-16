# 15 — Entra sign-in, stable identity mapping, and session revocation

## Objective

Implement authenticated server-managed sessions and explicit identity lifecycle behavior before business command endpoints become reachable.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-AUTH-001,003,008–009; FR-INT-004; ET-01–02,05; VT-21.

**Dependencies:** [10 — Runtime configuration, secrets boundary, and diagnostic primitives](10-runtime-settings-and-telemetry.md); [14 — Evidence, manifest, approval, and dependency schema](14-evidence-and-approval-schema.md)

**Execution gate:** file 14 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Previously approved Entra test app, callback URI, identity bindings and MFA policy are provisioned by the tenant operator.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/security/identity.py`
- **Create:** `production/audit_practice/audit_practice/security/sessions.py`
- **Create:** `production/audit_practice/audit_practice/api/__init__.py`
- **Create:** `production/audit_practice/audit_practice/api/session.py`
- **Create:** `docs/production/identity-operations.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_identity.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use the pinned Frappe OAuth/OIDC integration and validated provider library flow, not custom token cryptography. Validate approved issuer/tenant, audience, signature, nonce/state, code exchange and expiry; use PKCE where supported by the chosen flow. Enforce secure HttpOnly SameSite session cookies and CSRF for cookie-authenticated mutations.

2. Map stable verified identity claims to Audit Identity Binding and a pre-authorized Frappe User; invitations/administrative provisioning establish the binding. Reject unknown tenant and email reuse rather than auto-assigning staff roles. Require the agreed MFA policy for privileged sessions and verify it in the test tenant.

3. Check actor status and epoch on protected requests. Disable/reassignment increments local epoch; queued user-requested actions must subsequently reauthorize. Record direct SharePoint permission drift as pending reconciliation, not instant remote revocation.

4. Add session/me and logout endpoints returning only the caller projection. Temporary onboarding identity is setup-only and cannot bypass advance/terms activation; the business eligibility handler comes later. Do not expose the demo persona selector or reusable sample passwords here.

5. Use internal bootstrap/provision paths restricted to approved operators. Separate endpoint tests from live federation tests, keep fixtures synthetic and restore session state after each test.

## Acceptance Criteria

- [ ] Wrong issuer/audience, nonce/state replay and an unbound reused email are denied.
- [ ] Disable/epoch rotation invalidates an existing protected session.
- [ ] Client identity receives no staff/partner role by default.
- [ ] Live non-production staff/client sign-in and local disable evidence are recorded; mocks are labeled.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_identity
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

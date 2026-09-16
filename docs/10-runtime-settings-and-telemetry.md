# 10 — Runtime configuration, secrets boundary, and diagnostic primitives

## Objective

Establish environment safety, redacted diagnostics and typed error contracts before business handlers are added.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-SCOPE-006–009; FR-VAL-002–004; FR-REC-001; section 26.2.

**Dependencies:** [09 — Scaffold the production app and executable test harness](09-production-app-and-test-harness.md)

**Execution gate:** file 09 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks).

## Target Files

- **Create:** `production/audit_practice/audit_practice/runtime/__init__.py`
- **Create:** `production/audit_practice/audit_practice/runtime/settings.py`
- **Create:** `production/audit_practice/audit_practice/runtime/errors.py`
- **Create:** `production/audit_practice/audit_practice/runtime/logging.py`
- **Create:** `production/audit_practice/audit_practice/runtime/clock.py`
- **Create:** `infra/production/env.example`
- **Create:** `production/audit_practice/audit_practice/tests/test_runtime.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use an explicit environment enum TEST/STAGING/PRODUCTION and feature flags with default-deny outward effects. Read secrets through the approved deployment secret mechanism or Frappe site configuration, never committed files. Example files contain variable names, not working credentials.

2. Define public error codes VALIDATION_FAILED, UNAUTHENTICATED, FORBIDDEN, VERSION_CONFLICT, INPUTS_NOT_EVALUATED, PROVIDER_UNAVAILABLE and OUTCOME_UNKNOWN with safe correlation IDs and retryability. Preserve HTTP class; never return success when a provider or transaction failed.

3. Provide structured logging using standard logging with action, scope IDs, operation ID, duration and result. Redact tokens, cookies, temporary invitations, raw documents, bank data and personal payloads. Restrict exception detail to authorized operational logs.

4. Provide injectable UTC clock and monotonic duration helpers for expiry/retry tests. Persist UTC instants; convert to user time only for presentation. No global mutable fake clock outside tests.

5. Expose a minimal health method reporting build/environment/dependency reachability without client records or secret values. A process-alive health check must not claim Microsoft or records readiness. Do not add a new observability server or configuration abstraction framework.

## Acceptance Criteria

- [ ] Missing production configuration keeps outward effects disabled.
- [ ] Logs from representative errors contain correlation metadata but no seeded test secrets.
- [ ] Unknown provider outcome remains distinct from denial, conflict and success.
- [ ] Health returns no client data to anonymous callers.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_runtime
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

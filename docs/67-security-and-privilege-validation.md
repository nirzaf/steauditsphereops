# 67 — Security regression, privilege-boundary, and secret-handling assessment

## Objective

Validate security controls across actual endpoints, direct provider access, queued work and privileged operations before pilot sign-off.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-AUTH; FR-VAL; FR-REC; ET-01–08,21–24,38–42; VT-01–03,11–15,20–24.

**Dependencies:** [66 — Scoped legacy-data inventory and migration rehearsal](66-legacy-migration-rehearsal.md)

**Execution gate:** file 66 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview).

## Target Files

- **Create:** `production/audit_practice/audit_practice/tests/test_security_matrix.py`
- **Create:** `tests/production/security.spec.js`
- **Create:** `docs/production/security-assessment.md`
- **Modify:** `.github/workflows/production-ci.yml`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Enumerate every custom DocType/whitelisted method/report/export/attachment/portal route and verify two-client negative access, including metadata/count leakage. Test generic Desk/import/share/copy paths, mass assignment of protected fields and direct provider links.

2. Exercise CSRF/session fixation/expiry/revocation, invitation replay, spoofed tenant/audience, callback validation, HTML/script injection, CSV formula export injection, SSRF/redirect targets and oversized input handling. Use synthetic payloads and a sanctioned test environment.

3. Verify separate document/records/checkpoint/delivery identities and runtime capability boundaries. An application DB compromise must not be described as unable to forge every control unless the independent boundary actually demonstrates that property; document residual administrative risk.

4. Scan dependency/secret/container configuration using the project's approved toolchain. Pin any added security tooling and keep untrusted PR runs credential-free. Address real findings minimally; do not introduce unrelated auth frameworks or unapproved scanning services.

5. Record manual review and, where required by the risk decision, an independent penetration-test sign-off separately from automated checks. No blanket compliance/security certification claim follows from a passing test suite.

## Acceptance Criteria

- [ ] All documented role/scope bypass attempts are denied or tracked as blocking findings.
- [ ] No secrets occur in bundles, logs, export packages or committed configuration.
- [ ] Critical/high exploitable findings have verified remediation before promotion.
- [ ] Residual independent-store/shared-admin limitations are honestly documented.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_security_matrix
npx playwright test --config playwright.production.config.js tests/production/security.spec.js
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

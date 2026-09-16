# 20 — Microsoft transport and trusted repository gateway

## Objective

Implement one typed Microsoft adapter for the document capabilities proven in R0, with no arbitrary destination or token exposure.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-INT-004–007,012; FR-PBC-003,008,011–012; ET-06,08–10,15–22.

**Dependencies:** [16 — Role/assignment authorization across every access path](16-scoped-action-authorization.md); [19 — Artifact, signature, communication, and notification schema](19-artifact-and-communication-schema.md)

**Execution gate:** file 19 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Use only R0-approved test resources and credentials; no new tenant grants or policy mutations are authorized by this task.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/integrations/__init__.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/__init__.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/token_provider.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/transport.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/documents.py`
- **Create:** `production/audit_practice/audit_practice/integrations/microsoft/delta.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_microsoft_gateway.py`
- **Modify:** `production/audit_practice/pyproject.toml`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `production/audit_practice/audit_practice/security/permission_reconciliation.py`
- **Modify:** `infra/production/versions.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use pinned msal application-token acquisition and one requests transport with verified TLS, connection pooling, bounded timeouts, response limits, correlation and redacted logs. Credentials and token caches stay server-side in the approved secret boundary; separate principals by capability, not a single tenant-wide administrator.

2. Expose typed operations get_metadata, upload, get_version_bytes, snapshot_copy and list_changes only where the R0 endpoint/auth-mode matrix proves support. Resolve site/drive/item through Repository Binding. Reject client-supplied full URLs, label IDs, redirects to unapproved hosts and unrelated repository targets.

3. Stream bounded uploads/downloads, resume only validated upload sessions and correlate a deterministic destination with operation identity and digest. Handle timeout-after-success by finding/verifying the same remote object, not generating a new random filename. Distinguish source metadata changes from content changes.

4. Persist delta progress atomically with processed change records, not before processing a page. Expired cursor triggers bounded full reconciliation; duplicate/out-of-order/missing notifications cannot directly mark evidence accepted. Do not treat Graph workbook application permissions as generally available.

5. Implement assignment-rights drift reconciliation using the approved site/library/group model, with explicit pending/revoked/failed observations. Do not add broader consent automatically. Bind access observations to timestamp and principal; local user disable and remote cleanup are different outcomes.

## Acceptance Criteria

- [ ] Unrelated sites and forged URLs are denied before transport.
- [ ] 429 respects Retry-After; 403 remains denied; uncertain upload reconciles the original object.
- [ ] Resume after a failed delta page neither skips committed changes nor creates duplicate effects.
- [ ] Required calls pass on the approved test tenant with exact auth-mode evidence.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_microsoft_gateway
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

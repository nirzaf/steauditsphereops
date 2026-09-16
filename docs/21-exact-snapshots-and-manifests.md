# 21 — Exact receipts, preserved snapshots, and canonical manifests

## Objective

Implement the exact-byte evidence substrate used by every later approval, accounting package and report.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-PBC-003–007,012; FR-REV-001,007; FR-REC-002; ET-11–16; VT-18–19.

**Dependencies:** [17 — Atomic command transactions, revisions, and idempotency](17-transactional-command-kernel.md); [20 — Microsoft transport and trusted repository gateway](20-microsoft-document-gateway.md)

**Execution gate:** file 20 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/evidence.py`
- **Create:** `production/audit_practice/audit_practice/domain/__init__.py`
- **Create:** `production/audit_practice/audit_practice/domain/manifests.py`
- **Create:** `production/audit_practice/audit_practice/domain/references.py`
- **Create:** `production/audit_practice/audit_practice/api/evidence.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_snapshots.py`
- **Modify:** `production/audit_practice/pyproject.toml`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `infra/production/versions.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Capture original upload bytes and digest before provider transformations, then record stored bytes/version separately. Request a saved exact provider version for submission. Preserve a protected snapshot independent of a mutable working URL and verify bytes after storage. A concurrent edit yields a precise retry/conflict, not an ambiguous approval target.

2. Build canonical manifest bytes using rfc8785 with a versioned schema. Encode money as fixed schema-defined decimal strings, UTC instants in one format, sorted member identities and stable typed references. Reject NaN, duplicate members, unknown types and nondeterministic metadata. Persist canonical bytes/digest, not only a reconstructed Python dict.

3. Evidence API returns authorized metadata and exact snapshot read access; it never accepts caller-provided storage credentials or arbitrary provider paths. Enforce expiration and permission on each served/download operation; use streamed access for sensitive files rather than long-lived bearer URLs.

4. Record replacement receipts as new lineage and preserve predecessor visibility/history. Receipt storage success is not evidence suitability and does not complete a PBC or professional gate. Expose pending-storage/reconciliation separately from committed receipt.

5. Use outbox transitions for provider work and short local completion transactions. If remote snapshot creation succeeds and local commit fails, reconcile expected hash/version using the same operation identity. Add saved/unsaved Office, rename, move, provider rewrite and old-version-pruned cases.

## Acceptance Criteria

- [ ] Repeated receipt command creates one receipt and exact snapshot identity.
- [ ] Retrieved submitted bytes match the digest after the working file changes.
- [ ] Reordering manifest input yields the same canonical digest; encoding violations fail.
- [ ] Snapshot URLs/content and metadata never cross client boundaries.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_snapshots
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

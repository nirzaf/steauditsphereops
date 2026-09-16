# 05 — P0 identity, isolation, and Microsoft document proofs

## Objective

Prove identity isolation and exact-version evidence behavior in an explicitly authorized test tenant. Establish the supported endpoint and protection matrix before designing production adapters.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** P0-02–05; P0-09; ET-01–22; FR-AUTH; FR-PBC.

**Dependencies:** [04 — Disposable feasibility environment, spike schema, and proof runner](04-poc-harness-and-schema.md)

**Execution gate:** file 04 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Security/tenant administrator supplies pre-authorized non-production identities, test sites, Selected grants and approved records profile; separate approval is required for tenant/retention mutations.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management); [Purview records-management setup and licensing](https://learn.microsoft.com/en-us/purview/get-started-with-records-management); [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `spikes/p0/test_identity.py`
- **Create:** `spikes/p0/test_documents.py`
- **Create:** `spikes/p0/test_records.py`
- **Create:** `docs/production/microsoft-capabilities.json`
- **Create:** `docs/production/sharepoint-boundaries.md`
- **Create:** `spikes/p0/audit_poc/audit_poc/permissions.py`
- **Modify:** `spikes/p0/audit_poc/audit_poc/hooks.py`
- **Modify:** `spikes/p0/audit_poc/audit_poc/poc/doctype/poc_record/poc_record.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use named staff, invited client, unrelated tenant, changed/reused email and disabled-user fixtures. Verify stable subject/tenant mapping; browser persona strings and email domains are not identity. Demonstrate Frappe-side denial and direct SharePoint access denial for a second client, including metadata/search/export paths.

2. With pre-provisioned least-privilege application/delegated grants, exercise metadata, upload, saved version retrieval, supported delta reconciliation, snapshot readback, and an unrelated repository denial. Record API/version/auth-mode/scopes/request shape/observed outcome/limitations. Do not broaden consent automatically after a 403.

3. Upload deterministic bytes; retain original digest; create a working copy; edit/save it; snapshot an exact version; edit again and verify the old snapshot remains reconstructable. Test unsaved Office changes, metadata updates, rename/move, version pruning, protected files and concurrent snapshot creation. Do not equate an ETag with SHA-256.

4. The records administrator applies the approved synthetic policy to disposable artifacts. Test ordinary editor, records custodian and administrative edit/delete/unlock attempts and record the residual privileged-admin risk. A retention label name is not proof of immutable bytes.

5. Document the browser/portal versus Office access boundary and required client-content, internal-workpaper and issued-record containers. Prefer inherited site/library/group boundaries over unbounded item-specific permissions. This task is allowed to be externally BLOCKED; mock-only success does not satisfy its live exit.

## Acceptance Criteria

- [ ] P0-02, P0-03, P0-04, P0-05 and P0-09 have genuine test-tenant observations and owner-reviewed residual limitations.
- [ ] Wrong tenant, wrong scope, revoked access and unrelated repository all deny data and metadata.
- [ ] A submitted snapshot remains the same retrievable bytes after the working file changes.
- [ ] The capability matrix explicitly distinguishes supported, denied, unsupported and not-run operations.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/p0/run.py --suite identity --mode mock
python3 scripts/p0/run.py --suite documents --mode mock
python3 scripts/p0/run.py --suite identity --mode live
python3 scripts/p0/run.py --suite documents --mode live
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

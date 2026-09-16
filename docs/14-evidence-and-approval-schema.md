# 14 — Evidence, manifest, approval, and dependency schema

## Objective

Create version-bound document and approval records so later services can implement evidence and stale-input controls without schema gaps.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-PBC-003–012; FR-REV-001–007; FR-ACC-010–011; FR-REC-002.

**Dependencies:** [13 — Command receipts, audit history, outbox, and worker-state schema](13-command-history-and-outbox-schema.md)

**Execution gate:** file 13 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_repository_binding/audit_repository_binding.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_repository_binding/audit_repository_binding.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_repository_binding/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_document_receipt/audit_document_receipt.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_document_receipt/audit_document_receipt.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_document_receipt/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_snapshot/audit_snapshot.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_snapshot/audit_snapshot.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_snapshot/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_manifest/audit_manifest.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_manifest/audit_manifest.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_manifest/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_approval_decision/audit_approval_decision.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_approval_decision/audit_approval_decision.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_approval_decision/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_dependency/audit_dependency.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_dependency/audit_dependency.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_dependency/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_impact_case/audit_impact_case.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_impact_case/audit_impact_case.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_impact_case/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/evidence.py`
- **Create:** `production/audit_practice/audit_practice/patches/v1_evidence_indexes.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_evidence_schema.py`
- **Modify:** `production/audit_practice/audit_practice/patches.txt`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Repository Binding contains server-owned site/drive/container identifiers, client scope, purpose (working/internal/issued) and approved operation capabilities. Client payloads cannot create repository bindings or redirect providers.

2. Document Receipt records origin, original/stored digests, byte length/type, provider item/version, receipt time, creator and supersedes receipt. Snapshot records exact retained bytes digest, provider version, source receipt and storage binding; manifest records canonical schema version, sorted typed members and digest.

3. Approval Decision stores decision kind, exact snapshot/manifest, target revision/generation, actor/role/assignment, condition/rationale and predecessor decision. Conditions make approval CONDITIONAL, never final. Preserve historically valid decisions even if the person later leaves.

4. Dependency links typed upstream/downstream IDs and versions within approved same-client/period handoffs. Impact Case stores changed input, affected scope, captured generation, processing state and evaluation version. The generation advances synchronously later; background impact discovery must not be needed to make release unsafe.

5. Use uniqueness for receipt replay/snapshot identity and dependency edge version. Permit only existing/custom-type registry references; service-specific handlers will register later types after their schemas exist. No future FS/Workpaper/Release Link fields at this stage.

## Acceptance Criteria

- [ ] Receipt, snapshot and approval identities remain separate in schema and test fixtures.
- [ ] Cross-client repository/approval/dependency references are denied.
- [ ] A condition and a stale generation can be represented without overwriting a prior decision.
- [ ] Migration twice preserves the first inserted historical records.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_evidence_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 66 — Scoped legacy-data inventory and migration rehearsal

## Objective

Create a reversible, auditable migration process for authorized legacy records without importing synthetic approvals as professional evidence.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-SCOPE-003–007; FR-REC-002,008; FR-TRACE-003; section 27/R5.

**Dependencies:** [65 — Production deployment packaging, telemetry, backups, and runbooks](65-operations-deployment-and-backups.md)

**Execution gate:** file 65 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Data owner supplies an allowlisted legacy dataset and approved mappings; live migration requires separate operator authorization.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Repository requirements manifest](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/requirements-manifest.md).

## Target Files

- **Create:** `production/audit_practice/audit_practice/migration/__init__.py`
- **Create:** `production/audit_practice/audit_practice/migration/mapping.py`
- **Create:** `production/audit_practice/audit_practice/migration/importer.py`
- **Create:** `scripts/production/migrate_legacy.py`
- **Create:** `docs/production/migration-plan.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_migration.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Inventory authorized legacy clients, engagements, files and financial references, with source owner, consent/scope, identity mapping and source-control totals. Use explicit schema mapping and stable source IDs; do not discover/import unrelated Drive/SharePoint content automatically.

2. Never migrate browser demo persona credentials, simulated approvals, synthetic report releases, invitation secrets or demo checkpoint evidence into production. If synthetic data is retained for testing, isolate and label it in non-production only.

3. Dry-run validates duplicates, links, client/period scope, file/version hashes, unsupported fields and excluded records. Import permitted historical evidence as historical with provenance, not new current approvals. Use existing application/invariant-preserving migration commands rather than ad hoc SQL bypass.

4. Process bounded batches with checkpoints/idempotency and reconcilable control totals. Preserve source files; use a staging rehearsal and backup/rollback plan before any live writes. Issued legacy decisions require a professionally approved provenance/import policy, not invented missing approvers or timestamps.

5. Define cutover freeze/delta window, exception handling, mapping sign-off and post-import reconciliation. A nonzero rejected/ambiguous required record count blocks cutover unless individually reviewed and approved.

## Acceptance Criteria

- [ ] Dry run changes no authoritative data or external files.
- [ ] Repeated approved rehearsal produces no duplicate clients/files.
- [ ] Source counts/totals/digests reconcile or exceptions are explicitly dispositioned.
- [ ] No demo credential, synthetic approval or fabricated professional signature appears in imported records.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/production/migrate_legacy.py --environment staging --dry-run
./scripts/production/dev test audit_practice.tests.test_migration
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

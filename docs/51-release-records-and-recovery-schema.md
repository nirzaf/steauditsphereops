# 51 — Release, hold, checkpoint, delivery, archive, and recovery schema

## Objective

Create all release and recovery persistence before any externally effective issuance handler is registered.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-001–012; FR-REC-004–008; DOC-22–23; G8–G10.

**Dependencies:** [50 — R3 accounting and audit execution acceptance gate](50-r3-execution-and-review-exit.md)

**Execution gate:** file 50 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_legal_hold/audit_legal_hold.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_legal_hold/audit_legal_hold.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_legal_hold/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_protection_observation/audit_protection_observation.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_protection_observation/audit_protection_observation.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_protection_observation/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_candidate/audit_release_candidate.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_candidate/audit_release_candidate.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_candidate/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_event/audit_release_event.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_event/audit_release_event.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_release_event/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_checkpoint_reference/audit_checkpoint_reference.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_checkpoint_reference/audit_checkpoint_reference.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_checkpoint_reference/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_delivery_attempt/audit_delivery_attempt.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_delivery_attempt/audit_delivery_attempt.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_delivery_attempt/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_archive_manifest/audit_archive_manifest.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_archive_manifest/audit_archive_manifest.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_archive_manifest/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_amendment_case/audit_amendment_case.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_amendment_case/audit_amendment_case.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_amendment_case/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_recovery_case/audit_recovery_case.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_recovery_case/audit_recovery_case.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_recovery_case/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_export_request/audit_export_request.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_export_request/audit_export_request.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_export_request/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/records.py`
- **Create:** `production/audit_practice/audit_practice/patches/v1_release_indexes.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_release_schema.py`
- **Modify:** `production/audit_practice/audit_practice/patches.txt`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Legal Hold stores scope/purpose, effective state, authority, rationale and append-only apply/release event lineage. Protection Observation records exact artifact/version/digest, requested/observed profile, timestamp, verification identity and provider evidence; a desired label is not observed protection.

2. Release Candidate stores service-specific exact package manifest, report/FS pair where applicable, signatures, completion references, current input/safety generations, recipient-set version and state. Release Event is append-only with one logical release identity and authorized decision; do not permit generic REST insert.

3. Checkpoint Reference binds release event, canonical digest, independently stored immutable object version, external epoch and verified time. Delivery Attempt links only an authorized release/checkpoint, intended recipient, sender/system-duty identity, provider accepted/delivered/acknowledged/unknown status and reconciliation evidence.

4. Archive Manifest freezes included snapshots/structured records, protection/hold observations and completion checks. Amendment Case links original release and reason/new revision without mutating issued artifacts. Recovery Case records restore generation, old/new epochs, checkpoints, quarantine and approval evidence.

5. Export Request records requestor, purpose (client/inspector/internal), scope, artifact selection, expiry and current authorization state. Add unique release identity, candidate lineage/checkpoint keys and per-recipient logical-delivery constraints. API services arrive only after this migration.

## Acceptance Criteria

- [ ] All ten DocTypes and uniqueness controls migrate before release services.
- [ ] No delivery record can omit its release/checkpoint linkage.
- [ ] Hold, protection, release, checkpoint, delivery and archive remain separate states.
- [ ] Generic write/import cannot insert or rewrite issued history.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_release_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

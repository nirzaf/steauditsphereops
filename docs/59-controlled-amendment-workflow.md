# 59 — Post-issue amendments and supersession lineage

## Objective

Implement post-issue correction as a new controlled workflow rather than overwriting an issued report or statement.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-010; FR-E2E-007; FR-REC-002,007; AT-27.

**Dependencies:** [58 — Archive assembly and purpose-scoped evidence exports](58-archive-manifests-and-controlled-exports.md)

**Execution gate:** file 58 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/amendments.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_amendments.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Authorized partner opens an Amendment Case with original release identity, triggering fact, affected outputs/scope, reason and distribution implications. Preserve all original report/FS bytes, approval timestamps and archive references.

2. Create revised working/package/candidate lineage with fresh applicable technical/management/partner/EQR reviews. Reuse the established finalization -> release authorization -> independent checkpoint -> delivery path; do not create a bypass amendment send endpoint.

3. Record explicitly whether a new release supersedes an earlier one and how recipients are informed under the approved policy. Historical client portal access distinguishes superseded versus current but does not erase original history.

4. Apply holds, generations, idempotency and current authority to amendment commands. Material new inputs invalidate pending amended candidates; future facts never mutate the original approved manifest.

## Acceptance Criteria

- [ ] Attempting to overwrite or delete an issued output is denied.
- [ ] Amendment has its own version/approval/release/checkpoint lineage linked to the original.
- [ ] No amended report can be delivered without the same release controls.
- [ ] Original bytes and historical decisions remain reconstructable.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_amendments
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

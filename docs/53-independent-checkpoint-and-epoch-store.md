# 53 — Independent checkpoint storage and non-rollbackable epoch adapter

## Objective

Implement the independently administered checkpoint and recovery-epoch substrate selected and proven in R0.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-004–006; FR-REC-004–007; VT-13,23–24.

**Dependencies:** [06 — P0 transaction, privileged execution, retry, and recovery proofs](06-poc-release-and-recovery-proofs.md); [52 — Legal holds and observed record-protection enforcement](52-legal-holds-and-record-protection.md)

**Execution gate:** file 52 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Independently administered store and narrowly scoped credentials from R0 must exist; infrastructure privilege changes need operator approval.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py).

## Target Files

- **Create:** `production/audit_practice/audit_practice/integrations/checkpoints.py`
- **Create:** `production/audit_practice/audit_practice/records/checkpoint_payload.py`
- **Create:** `production/audit_practice/audit_practice/records/epochs.py`
- **Create:** `infra/production/checkpoint-policy.json`
- **Create:** `docs/production/checkpoint-operations.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_checkpoint_store.py`
- **Modify:** `production/audit_practice/pyproject.toml`
- **Modify:** `production/audit_practice/audit_practice/jobs/leases.py`
- **Modify:** `infra/production/versions.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement one provider adapter from docs/production/checkpoint-provider-decision.md with create_once, get_exact_version, verify_digest, read_epoch and advance_epoch(expected_epoch) operations. Use the provider SDK pinned for the approved store; for an approved Azure Blob store use azure-storage-blob/azure-identity. Do not create a new checkpoint microservice or store authoritative epochs in the application database.

2. Separate immutable release checkpoints from the conditional-update epoch register as required by the selected provider. The epoch is monotonic and outside the restored DB/backup set; do not overwrite immutable objects to increment it.

3. Canonical checkpoint payload includes release identity, event digest, artifact manifest/hash/version identities, source generations, policy/version, intended recipient-set digest and observed protection evidence. Sign/authenticate it using the approved independent control, and verify on read.

4. A same release/checkpoint key with equal bytes returns the original object; unequal bytes conflicts and alerts. A local cached success is insufficient; read back exact provider identity/version/digest before recording VERIFIED.

5. Restrict credentials/admin rights separately from ordinary app workers and document residual shared-admin risk. Integrate epoch checks before privileged work and local result publication; no claim that an epoch token cancels a remote request already in flight.

## Acceptance Criteria

- [ ] Database rollback cannot lower the independent epoch or erase a prior checkpoint.
- [ ] Identical checkpoint replay returns one immutable object; changed bytes fail.
- [ ] Wrong signature/digest/object version is rejected.
- [ ] Records executor has only the capabilities proved by the approved boundary.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_checkpoint_store
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

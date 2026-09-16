# 06 — P0 transaction, privileged execution, retry, and recovery proofs

## Objective

Prove the failure-sensitive release and recovery invariants against real transactions and controlled external artifacts. Reject designs that only work when every request succeeds once.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** P0-06; P0-08; P0-10–11; VT-04–15; VT-23–24.

**Dependencies:** [05 — P0 identity, isolation, and Microsoft document proofs](05-poc-identity-and-document-capabilities.md)

**Execution gate:** file 05 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Independent records/security operator controls the approved checkpoint store and authorizes the disposable restore exercise.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `spikes/p0/test_transactions.py`
- **Create:** `spikes/p0/test_privileged.py`
- **Create:** `spikes/p0/test_recovery.py`
- **Create:** `docs/production/release-linearization.md`
- **Create:** `docs/production/checkpoint-provider-decision.md`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use the earlier spike tables, never future DocTypes. Run two independent MariaDB connections with synchronization barriers: pause impact processing, mutate a linked accounting input and race a release authorization. Use one client-period guard before engagement locks, a deterministic lock order and expected revision/generation checks. Record the linearization point and prove a stale candidate cannot win after the input change commits.

2. Commit durable outbox intent with business state. Simulate upload success followed by local commit failure, duplicate delivery work, reused idempotency key with changed payload, process restart and expired worker lease. Reconcile the same deterministic artifact and hash; a stale fence must reject local completion.

3. Test forged URL, label, action and document IDs against a typed privileged executor whose destinations come from trusted bindings. Document that DB access or a queue label alone is not an independent privilege boundary. All outward effects use synthetic artifacts and allowlisted recipients.

4. Choose and prove one independently administered checkpoint/epoch store outside the application database and backup set. Define create-once checkpoint, read/verify, durable monotonic recovery epoch and conditional update semantics. An Azure Blob implementation is a candidate only if its actual immutable/conditional capabilities are approved and tested; do not assume a local JSON file is an independent checkpoint.

5. Restore the spike database to before an already externally checkpointed release. Quarantine outside the restored database, invalidate/retire old worker credentials or egress, reconcile issued identities and uncertain operations, and verify no duplicate issue/send. A local fencing token does not prevent an already-started provider side effect; require credential/egress isolation and bounded in-flight reconciliation.

## Acceptance Criteria

- [ ] P0-06/08/10/11 evidence includes barrier-based concurrency and real restore observations, not sleeps or fabricated log assertions.
- [ ] A same-key/different-payload retry conflicts; identical replay produces one business effect.
- [ ] The chosen external store can verify retained checkpoints and survive database rollback without resetting the recovery epoch.
- [ ] No production report, invoice, tenant policy or real recipient was used.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/p0/run.py --suite transactions --mode live
python3 scripts/p0/run.py --suite privileged --mode live
python3 scripts/p0/run.py --suite recovery --mode live
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

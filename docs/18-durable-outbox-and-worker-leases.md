# 18 — Durable outbox dispatch, bounded queues, and stale-worker fencing

## Objective

Deliver retryable background execution without losing committed intent or claiming universal exactly-once external effects.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-INT-012; FR-REC-003–005; FR-VAL-002; ET-09,17–20; VT-13–15.

**Dependencies:** [17 — Atomic command transactions, revisions, and idempotency](17-transactional-command-kernel.md)

**Execution gate:** file 17 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling); [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0).

## Target Files

- **Create:** `production/audit_practice/audit_practice/jobs/__init__.py`
- **Create:** `production/audit_practice/audit_practice/jobs/dispatcher.py`
- **Create:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Create:** `production/audit_practice/audit_practice/jobs/leases.py`
- **Create:** `production/audit_practice/audit_practice/jobs/retry.py`
- **Create:** `production/audit_practice/audit_practice/jobs/reconciliation.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_outbox.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Dispatch due durable outbox rows into bounded Frappe queues (general, processing, restricted records) and rescan after restart. enqueue_after_commit can reduce premature execution but is not the durable source of truth; Redis flush/crash must not lose pending operations.

2. Claim operations with atomic expected-state/revision changes, attempt record, expiry and monotonically increasing fence. Validate local and externally supplied environment epoch before effects and before publishing results. The independent provider epoch adapter arrives in R4; outward report delivery remains unregistered/disabled meanwhile.

3. Implement typed executor registry accepting only known operation kinds and trusted target IDs. Provider calls use bounded timeouts/concurrency and Retry-After/backoff/jitter; 403 does not trigger broadened consent. OUTCOME_UNKNOWN goes to reconciliation rather than blind retry.

4. Differentiate user-requested exports from committed system-duty notifications/delivery. Reauthorize current user requests; retain valid historical professional approval when its original employee leaves. Apply current recipient, hold, epoch and artifact policy for system duties.

5. Use injected transports and deterministic lease clocks in tests. Simulate process death after remote success and before local completion, duplicate queue message, expired worker, poison job and clock boundary. A fence prevents stale local publication, not a provider request already in flight; retain explicit uncertainty and operator recovery.

## Acceptance Criteria

- [ ] An outbox row survives queue loss and is redispatched without a second business event.
- [ ] Expired/stale workers cannot publish current success.
- [ ] An uncertain side effect is reconciled with the same operation identity and digest.
- [ ] Report delivery is unavailable before the release/checkpoint executor tasks exist.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_outbox
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

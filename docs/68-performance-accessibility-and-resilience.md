# 68 — Capacity, accessibility, and degraded-mode validation

## Objective

Verify the agreed workload and user-interaction targets under realistic data volume and provider degradation.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-UX-008–009; FR-NAV; FR-VAL-002–007; section 25 bottlenecks and NFRs.

**Dependencies:** [67 — Security regression, privilege-boundary, and secret-handling assessment](67-security-and-privilege-validation.md)

**Execution gate:** file 67 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `scripts/production/load_test.py`
- **Create:** `tests/production/accessibility.spec.js`
- **Create:** `production/audit_practice/audit_practice/tests/test_performance_contracts.py`
- **Create:** `docs/production/performance-results.md`
- **Create:** `docs/production/accessibility-results.md`
- **Modify:** `infra/production/versions.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Generate bounded synthetic datasets at the approved client/engagement/TB-row/file scales and concurrency. Use a pinned load-test library only when standard scripting is inadequate; record that dependency and environment. Measure p95 latency, memory, query counts, queue age and throughput rather than estimating capacity from the tiny arithmetic fixture.

2. Identify N+1 queries, unscoped counts, large child-array hydration, report-rendering saturation and provider throttling. Verify compound indexes, pagination, bounded background concurrency and per-provider retry limits. Dashboard projections may lag within target, but release must read authoritative state.

3. Inject Graph outage/429, queue loss, stalled worker, expired session, interrupted upload and database contention. Show accurate pending/error/stale status; safe drafts remain available without false server save or automatic replay.

4. Test keyboard-only traversal, focus management, accessible names/error relationships, status announcements, reduced motion and mobile/tablet/desktop widths. Use existing Playwright plus optional pinned axe-core tooling; manual screen-reader checks are separate evidence and no automated scan alone proves full conformance.

5. Document targets versus measured results, workload, tested image/commit and limitations. Optimize only observed bottlenecks; capacity/availability promises cannot exceed the exercised topology.

## Acceptance Criteria

- [ ] Approved latency/queue/memory/workload targets pass at the stated tested scale.
- [ ] No uncontrolled retry storm or missing-scope performance shortcut is introduced.
- [ ] Principal portal/staff workflows are keyboard-operable and responsive.
- [ ] Unmet mandatory NFR/accessibility findings prevent pilot acceptance.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/production/load_test.py --environment staging --validate-only
./scripts/production/dev test audit_practice.tests.test_performance_contracts
npx playwright test --config playwright.production.config.js tests/production/accessibility.spec.js
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

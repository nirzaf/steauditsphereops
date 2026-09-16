# 69 — Preserve the demo shell, shared invitations, and repeatable walkthrough

## Objective

Verify the existing Vue/Cloudflare demonstrator still satisfies its separate presentation and synthetic-state contract.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-SCOPE-006–009; FR-AUTH-004; FR-NAV-001–012; FR-STATE-004–010; FR-DEMO-001–010; FR-UX-002–009; AC-DEMO-001–012.

**Dependencies:** [68 — Capacity, accessibility, and degraded-mode validation](68-performance-accessibility-and-resilience.md)

**Execution gate:** file 68 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [Existing prototype scripts and dependencies](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/package.json); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `tests/wbs-demo-regression.test.js`
- **Create:** `tests/production/demo-preservation.spec.js`
- **Create:** `docs/production/demo-preservation.md`
- **Modify:** `playwright.production.config.js`
- **Modify:** `playwright.config.js`
- **Read / preserve:** `src/App.vue`
- **Read / preserve:** `src/auth.js`
- **Read / preserve:** `src/demoContext.js`
- **Read / preserve:** `src/localState.js`
- **Read / preserve:** `src/sharedDemo.js`
- **Read / preserve:** `src/navigation/registry.js`
- **Read / preserve:** `src/components/DemoNavigator.vue`
- **Read / preserve:** `src/components/WorkflowGuide.vue`
- **Read / preserve:** `src/domain/scenario.js`
- **Read / preserve:** `worker/index.js`
- **Read / preserve:** `worker/schema.sql`
- **Read / preserve:** `package.json`
- **Read / preserve:** `playwright.config.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Treat this as regression/preservation first: inspect existing controls and reuse tests. Root demo remains Vue/Vite with LOCAL_ONLY authoritative synthetic scenario and SHARED_DEMO Worker/D1 truth. New production app code must not make the demo depend on a live Frappe tenant.

2. Verify presenter-only persona/client/engagement/period/scenario switching, exact next actions, visible derived progress, notification/activity results, deterministic reset and stale-selection correction. Presentation preference cannot waive a professional gate. Invitation client never sees staff/presenter reset/switch controls.

3. Exercise two separate invitation runs and second-browser shared state, scoped thread/evidence separation, seven-day invitation limit and current source-defined upload allowlist/10 MB bound/24-hour download expiry. Worker authorization/expiry blocks access even if asynchronous object cleanup is delayed. Verify fail-closed shared configuration and safe local storage errors.

4. Register the demo-preservation browser test with the existing demo Playwright setup, explicitly excluding it from production config. Use local test bindings/mocks unless an operator authorizes an isolated shared-demo check. Never execute remote quadrate-db migration or purge existing R2 objects as part of a regression test.

5. Correct only demonstrated regressions in the relevant existing file after adding that path to the task diff plan; do not refactor the entire shell or migrate synthetic records to production. Preserve SIMULATION/NOT_RUN/N_A evidence distinctions and do not claim the 160 scenario inventory all ran.

## Acceptance Criteria

- [ ] All 12 AC-DEMO observations have a passing test or honest reviewed manual evidence.
- [ ] LOCAL_ONLY makes no unauthorized provider call and labels local drafts accurately.
- [ ] Invitation scope, expiry and presenter-control denial pass.
- [ ] Demo and production builds/tests remain separate and independently runnable.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
npm test
npm run build
npm run test:e2e -- tests/production/demo-preservation.spec.js
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# 71 — Pilot UAT, training, and cutover rehearsal

## Objective

Obtain operational and professional pilot acceptance on the exact tested build before any production enablement.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** Section 27/R5; FR-E2E-001–008; FR-TRACE; all approved operating targets.

**Dependencies:** [70 — Complete functional, acceptance, and P0 traceability](70-full-requirement-and-test-traceability.md)

**Execution gate:** file 70 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Named pilot and control owners review/sign their own acceptance; production change-window approval remains an operator responsibility.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `docs/production/pilot-uat.md`
- **Create:** `docs/production/training-and-support.md`
- **Create:** `docs/production/cutover-rehearsal.md`
- **Create:** `scripts/production/check_release_readiness.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Run a bounded pilot with authorized synthetic or explicitly approved pilot data and all required real actor roles. Walk the supported service cycles, financial/accounting calculations, exact evidence/approval chain and client-safe output visibility; each professional owner signs its own control acceptance.

2. Train staff/client support on next actions, version conflicts, conditional decisions, provider uncertainty, holds, amendments and recovery quarantine. Provide operator runbooks with escalation owners, not AI-generated stand-in approvals.

3. Rehearse deployment/migration, smoke validation, restore/fencing and rollback/forward-fix on staging using the exact image digest and configuration policy. Reconcile migration totals and confirm production sending is still disabled during the rehearsal.

4. Implement release readiness checker that consumes baseline, R0–R4 exits, security/NFR results, traceability, backup/drill evidence and UAT sign-offs. Require zero unresolved critical defects and explicit treatment of other risks; block on stale tested image or missing independent approval.

5. Record go/no-go, staged rollout scope, monitored SLOs, support owners and stop/rollback criteria. Technical success is not permission for the agent to perform a production cutover or issue professional reports.

## Acceptance Criteria

- [ ] Professional, security/records, finance and operating owners provide genuine acceptance for their scope.
- [ ] Staging cutover rehearsal meets approved safety and recovery targets.
- [ ] Readiness checker rejects missing/stale evidence or altered image digest.
- [ ] No production grant, migration, email/report issue or policy change occurs without explicit authorization.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/production/check_release_readiness.py --root . --environment staging
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

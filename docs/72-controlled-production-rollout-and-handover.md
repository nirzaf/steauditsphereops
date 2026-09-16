# 72 — Controlled production rollout, verification, and handover

## Objective

Provide the final operator-gated rollout and handover procedure for the accepted build. Keep production side effects disabled until independently verified readiness and explicit authorization exist.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** Section 27/R5; FR-REC-004–008; FR-TRACE-003; final delivery control.

**Dependencies:** [71 — Pilot UAT, training, and cutover rehearsal](71-pilot-acceptance-and-cutover-rehearsal.md)

**Execution gate:** file 71 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Explicit production change approval, independent records/security verification and the user-selected confirmation codeword; absent approval means BLOCKED, not completed.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management).

## Target Files

- **Create:** `docs/production/production-release-record.md`
- **Create:** `docs/production/handover.md`
- **Create:** `scripts/production/post_deploy_verify.py`
- **Modify:** `docs/production/operations-runbook.md`
- **Modify:** `docs/production/execution-status.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. First run read-only readiness/deployment plans and compare the approved image digest, migration set, environment bindings, credentials and service feature profile. Any material change after acceptance requires affected regression/capability checks and new review; do not deploy floating latest.

2. A human operator obtains the required change approval and user-specified confirmation codeword before live deployment, migrations, grants, policy changes or externally effective sends. Execute only the scoped approved operations; the autonomous coding agent must not infer these permissions from completing this task file.

3. Use a controlled rollout with explicit initial recipients/clients, backups, runtime epoch and independent checkpoint validation. Enable outbound capabilities separately only after direct scope/protection/records smoke checks. Do not promote synthetic invitations, decisions or release records into production.

4. Run non-destructive post-deploy checks on version, health, permission denial, queue recovery, checkpoint reachability, telemetry and client portal isolation. Use designated non-professional test records where needed; never issue a real audit opinion merely to smoke-test deployment.

5. Monitor agreed service/error/queue/records targets during the approved stabilization period; follow documented stop/rollback or forward-fix conditions. Complete handover with support owners, recovery evidence, known limitations, tested refs and per-task actual status; retain future remediation follow-up.

## Acceptance Criteria

- [ ] Released image/configuration matches the accepted evidence and recorded operator authorization.
- [ ] Post-deploy verification demonstrates isolation and independent checkpoint readiness without issuing an unauthorized report.
- [ ] Outward capabilities are enabled only through explicit approved control steps.
- [ ] Handover records real support/recovery ownership and no task is marked ACCEPTED without its evidence.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/production/check_release_readiness.py --root . --environment production
python3 scripts/production/deploy_plan.py --environment production --validate-only
python3 scripts/production/post_deploy_verify.py --environment production --read-only
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

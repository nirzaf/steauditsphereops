# 08 — R0 evidence reconciliation and feasibility exit

## Objective

Close the feasibility milestone using the real P0 evidence and approved unresolved decisions. Establish the go/no-go boundary before production app construction.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** P0-01–12; FR-TRACE-002–006; section 27/R0.

**Dependencies:** [07 — P0 accounting bridge and representative capacity proof](07-poc-accounting-and-capacity.md)

**Execution gate:** file 07 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Sponsor, professional lead and security/records owners provide actual R0 acceptance; the agent cannot manufacture sign-off.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Repository requirements manifest](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/requirements-manifest.md).

## Target Files

- **Create:** `docs/production/r0-exit.md`
- **Create:** `scripts/wbs/check_p0_exit.py`
- **Modify:** `docs/production/decision-register.md`
- **Modify:** `docs/production/p0-index.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Reconcile all twelve source experiment IDs: build (01), identity (02), isolation (03), Microsoft capability (04), snapshots (05), release race (06), accounting bridge (07), privileged execution (08), records (09), retry/revocation (10), release/recovery (11) and scope/economics (12). Attach actual proof outputs and artifact/environment revisions; do not count an unexecuted test definition as evidence.

2. Obtain the professional lead/sponsor decision on the supported service profiles, method/template scope, licensing exception, NFRs, external checkpoint boundary and staffing/cost unknowns. Reuse existing approval records rather than asking to approve already-agreed architecture again; only missing decisions need resolution.

3. Treat unsupported required provider features, false records-immutability assumptions, unresolved authorization leakage, unreconciled release races and unmet recovery requirements as release-blocking findings. Record affected downstream task IDs and a bounded corrective action.

4. Implement check_p0_exit.py so absent, mock-only, waived-without-owner or stale evidence for a required live experiment returns nonzero. An approved change in requirement/scope must update baseline and dependency mapping; never silently skip a MUST requirement.

5. Production construction can proceed only after R0 exit is accepted. This WBS generation does not assert that R0 has passed; subsequent tasks describe what to implement after it does.

6. This is a feasibility gate based on isolated spike implementations, not certification of future production code. Preserve P0 identities and rerun their production equivalents at R1/R3/R4 and on relevant upgrades; platform-spike build evidence cannot substitute for building the final app.

## Acceptance Criteria

- [ ] The R0 record has a named decision owner, source references, applicable experiment results and explicit go/no-go.
- [ ] check_p0_exit.py rejects a deliberately removed/altered required result.
- [ ] No critical feasibility dependency remains hidden in a future task.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/wbs/check_p0_exit.py --root .
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

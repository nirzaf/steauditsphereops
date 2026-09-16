# 23 — Service-specific gate evaluation and progress projections

## Objective

Implement the authoritative gate evaluation contract before feature modules register their evidence providers.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-GATE-001–009; FR-STATE-001–003,009; FR-NAV-005–007; FR-VAL-005–007.

**Dependencies:** [02 — Service contracts, gates, outputs, and operating targets](02-business-contracts-and-operating-targets.md); [22 — Version-bound decisions and synchronous invalidation](22-versioned-approval-and-impact-engine.md)

**Execution gate:** file 22 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/domain/gates.py`
- **Create:** `production/audit_practice/audit_practice/application/projections.py`
- **Create:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Create:** `production/audit_practice/audit_practice/api/workspace.py`
- **Create:** `production/audit_practice/audit_practice/tests/fixtures/__init__.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_gates.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Load the approved versioned service/gate contract into a bounded registry, not a user-programmable workflow engine. Return gate_id, applicability, status, blocker codes, record references, accountable roles, evaluated_generation and next actionable destination.

2. Missing feature providers return NOT_IMPLEMENTED/BLOCKED, never READY. Keep future production gate registrations absent until their tasks pass. G8 depends only on its approved prerequisites, never G9/G10; UNKNOWN applicability fails closed instead of being counted as N/A.

3. Compute progress from applicable requirements with distinct task, approval and gate measures; a denominator of zero yields N/A, not misleading 100%. A selected client/context cannot reuse cached data from another client or period.

4. Expose GET workspace/context and record-specific next-action projection using existing domain evidence. Never expose a set_gate_status or editable percentage command. Include projection revision/freshness and a safe stale-state response for unavailable authoritative reads.

5. Use a shared route/target contract that UI tasks can implement later. Only link to registered implemented destinations; for upcoming surfaces show the blocker and responsible role without a dead link. Gate commands must re-read authoritative transaction state, not trust dashboard caches.

## Acceptance Criteria

- [ ] No public API can force a gate READY or change completion percentage.
- [ ] Missing provider and stale generation are blocked; N/A cannot waive an applicable control.
- [ ] Test contracts reject cycles and G8 dependencies on commercial close/renewal.
- [ ] Two-client projections expose no cross-scope records or counts.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_gates
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

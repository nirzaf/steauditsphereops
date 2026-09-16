# 44 — Risk-response coverage, reconciled populations, and sample plans

## Objective

Implement traceable risk-to-procedure and population-to-sample controls using approved methodology rather than unvalidated sampling shortcuts.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUD-002–006; AT-14–17; ET-29; DOC-12.

**Dependencies:** [43 — Planning, materiality, team allocation, and announcement](43-audit-planning-and-announcement.md)

**Execution gate:** file 43 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Professional audit lead approves methods and reference expected outputs before the method is enabled.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit/risks.py`
- **Create:** `production/audit_practice/audit_practice/audit/populations.py`
- **Create:** `production/audit_practice/audit_practice/audit/sampling.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_sampling.py`
- **Modify:** `production/audit_practice/audit_practice/api/audit.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Link each risk/assertion to procedure owner, evidence requirements and planned response. Significant risks cannot be marked covered without an applicable procedure and eventual supported conclusion; record any professional disposition explicitly.

2. Import populations in bounded batches with source snapshot, period/currency, row identity, inclusion/exclusion rules and reconciled totals. Unreconciled or incomplete populations cannot support an approved sample plan.

3. Implement only the sampling methods approved in R0. Preserve method/version, seed where reproducibility applies, parameters, population digest and selected IDs; require reviewer validation against reference fixtures. Statistical claims need professionally validated algorithms, not a random.sample wrapper labeled representative.

4. Missing/contradictory evidence for a selected item cannot cause silent resampling. Record alternative procedures, exception, rationale and required independent review. A changed population/materiality makes dependent samples and coverage evaluation stale.

5. Expose bounded sample/procedure queries and exact source/evidence links. Manual judgement selection remains an explicit supported method with rationale, not a hidden fallback pretending to satisfy statistical sampling.

## Acceptance Criteria

- [ ] Unreconciled population and uncovered significant risk block approval.
- [ ] Same pinned method/seed/input yields the approved selection fixture.
- [ ] A missing sample item remains visible with alternative-work/exception history.
- [ ] Changed population/materiality invalidates old sampling evaluation.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_sampling
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

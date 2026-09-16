# 07 — P0 accounting bridge and representative capacity proof

## Objective

Validate exact arithmetic, replacement-source reconciliation and a representative workload before committing to the financial-statement pipeline. Supply measured evidence for the scope/economics decision.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** P0-07; P0-12 engineering input; AT-07–12; ET-23–28; VT-16–18.

**Dependencies:** [06 — P0 transaction, privileged execution, retry, and recovery proofs](06-poc-release-and-recovery-proofs.md)

**Execution gate:** file 06 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py).

## Target Files

- **Create:** `spikes/p0/test_accounting.py`
- **Create:** `spikes/p0/accounting_reference.py`
- **Create:** `docs/production/p0-capacity-results.json`
- **Read / preserve:** `fixtures/baseline_tb.csv`
- **Read / preserve:** `fixtures/replacement_tb_aj001_reflected.csv`
- **Read / preserve:** `fixtures/expected_results.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Read the checked-in arithmetic fixtures; do not copy expected numbers from memory or rewrite fixtures to fit a failed result. Parse monetary values from strings into Decimal, preserve leading-zero account codes and maintain explicit sign/currency/dimension conventions.

2. Run base import, AJ-001 authorization/application and replacement source already reflecting AJ-001. Assert the source expected 175,000 result and zero additional application when reflection is independently verified; test PARTIAL/UNKNOWN reflection and selecting two revisions of the same logical journal. No inferred residual adjustment.

3. Exercise non-finite values, ambiguous locale separators, zero/sign anomalies, duplicate dimensioned codes, unbalanced TB, formula-only cells, external links and oversized decompressed spreadsheets. Use bounded streaming; no workbook formula execution and no zero-defaulting of failed parses.

4. Measure representative owner-specified TB sizes, upload/snapshot sizes, two-client workloads and memory/latency against approved targets. Report synthetic fixture scale honestly and identify the serial/provider-bound bottlenecks. Do not treat the tiny fixture as capacity proof.

5. Keep this a small reference implementation and evidence task, not a second production accounting engine. Production code will reuse the fixtures and published invariants, not blindly promote spike code.

## Acceptance Criteria

- [ ] The provided arithmetic expectations pass exactly; reflected replacement does not double-count.
- [ ] Duplicate revision, partial reflection and ambiguous numeric inputs fail explicitly.
- [ ] Capacity results include dataset size, environment, measured duration/memory, target comparison and uncertainty.
- [ ] P0-07 is recorded separately from P0-12 professional scope/economics approval.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/p0/run.py --suite accounting --mode mock
python3 scripts/p0/run.py --suite accounting --mode live
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

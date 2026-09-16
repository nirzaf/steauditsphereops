# 02 — Service contracts, gates, outputs, and operating targets

## Objective

Turn the approved business model into versioned, unambiguous implementation contracts. Resolve policy and capacity inputs before schemas or release logic are designed.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** FR-GATE-001–009; FR-SCOPE-001–005; FR-ACC-003–011; FR-AUD-001–012; FR-FIN-001–006; FR-INT-011; sections 25.1 and 27/R0.

**Dependencies:** [01 — Execution contract, source baseline, and WBS index](01-execution-contract-and-baseline.md)

**Execution gate:** file 01 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Professional lead, security/records owner and sponsor provide or confirm detailed policy, licensing and operating-target decisions.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Purview records-management setup and licensing](https://learn.microsoft.com/en-us/purview/get-started-with-records-management); [OpenSanctions data licensing](https://www.opensanctions.org/licensing/).

## Target Files

- **Create:** `docs/production/service-profiles.json`
- **Create:** `docs/production/gate-contracts.json`
- **Create:** `docs/production/output-catalog.json`
- **Create:** `docs/production/nfr-targets.json`
- **Create:** `docs/production/decision-register.md`
- **Create:** `scripts/wbs/validate_contracts.py`
- **Read / preserve:** `src/v5Data.js`
- **Read / preserve:** `src/domain/traceability.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Encode service profiles ACCOUNTING_ONLY, EXTERNAL_AUDIT_ONLY, COMBINED and INTERNAL_AUDIT. Mark unsupported variants disabled until their test/sign-off task is accepted; an accounting-only package must never require an auditor opinion. Linked accounting/audit engagements share an explicit client-period dependency group, not a merged ledger.

2. Use the current v5 labels: G0 Firm ready; G1 Accept/continue; G2 Commercial ready; G3 Terms accepted; G4 Portal eligible; G5 Fieldwork ready; G6 Review submission ready; G7 Completion ready; G8 Release ready; G9 Commercial close; G10 Archive/renewal. Do not import the older v3/v4 gate numbering. Define applicability, authoritative inputs, owner, blocker codes, invalidation triggers and prerequisite gates for each profile. Reject cycles; G9/G10 must not become prerequisites for G8.

3. Enumerate DOC-01–DOC-26 from src/v5Data.js with an owner, visibility, trigger, required fields, template version and producing WBS task. Record the paired Draft FS/MIR response, opinion, final discussion, final report/FS pairing, advance allocation, time and cost close requirements. Workpaper conclusion-summary generation is not itself professional approval.

4. Get approval for decimal scales, exchange-rate sources, rounding, journal reflection including PARTIAL/UNKNOWN, applicable financial frameworks, non-applicable evidence rules, report date rules, and materiality/sampling policies. Every final output must be reproducible from structured inputs and pinned templates; no cash-flow plug or invented disclosure.

5. Record existing approvals or unresolved dispositions for Microsoft/Purview licensing, screening data rights, identity guest model, record threat model, independently administered checkpoint storage and data residency. Define measured acceptance targets: expected clients/engagements, active users, peak concurrency, p95 command latency, progress freshness, TB row/file limits, availability, retention, RPO, RTO and budget. These are owner inputs, not values to guess.

6. Build validate_contracts.py using json, pathlib and graphlib to reject duplicate/missing gates or output IDs, invalid dependency DAGs, missing scope/applicability and unresolved critical decision entries. Optional Documenso/OpenSanctions/Insights choices must not create hidden mandatory integration dependencies.

## Acceptance Criteria

- [ ] All eleven gates and 26 outputs are represented with explicit ownership and applicability.
- [ ] A negative fixture where G8 depends on G10 fails validation; accounting-only does not require audit-only approvals.
- [ ] The required licensing exception and NFR targets have verifiable owner dispositions; unresolved values block their dependent live proofs.
- [ ] No specific legal/regulatory compliance or platform capacity is asserted without evidence.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/wbs/validate_contracts.py --root .
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

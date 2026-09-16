# Production source baseline

**Status:** `BLOCKED`

**Repository:** `nirzaf/steauditsphereops`

**Target branch:** `main`
**WBS:** [01 — Execution contract, source baseline, and WBS index](../01-execution-contract-and-baseline.md)

This record separates the existing read-only demonstrator from the proposed production target. It records observable references only; it does not copy the demonstrator, create a Bench, or claim production readiness.

## Repository and path mapping

| Concern | Recorded value | Status |
| --- | --- | --- |
| Production execution repository | `nirzaf/steauditsphereops` | Current task repository |
| Production application target | `production/audit_practice/` with Python package `production/audit_practice/audit_practice/` | Proposed path; no application exists yet |
| Read-only reference demonstrator | `nirzaf/steauditqts` | Separate repository; no writes performed |
| Demonstrator planning commit | `2898e44f6732c8b37c31ddfbeab0e322d7574ffe` | Observed public commit |
| Current execution-repository commit at task start | `265817a0b1792e839fe5f77f07e2eb9b8898c842` | Documentation-only base |
| Owner-approved mapping from inherited task-01 target to this repository | Not supplied | **BLOCKER** |

The inherited task text says to work in `steauditqts`, while the approved repository contract names `steauditsphereops` as the execution repository. This mismatch must be resolved by an owner/source-custodian approval recorded here before task 01 can be accepted. No production path is redirected silently.

### Demonstrator boundary for later tasks

- **WBS 09:** the production app, test wrapper, and production CI are created under `steauditsphereops`; the Vue/Cloudflare demonstrator remains untouched.
- **WBS 69:** demo-shell preservation and walkthrough regression run against the separately pinned `steauditqts` checkout; its synthetic state, credentials, and deployment are never promoted into production.

These two task IDs are part of the repository-mapping disposition and must retain separate evidence and ownership.

## Controlled baseline references

| Reference | Revision or identity | Observation |
| --- | --- | --- |
| Approved functional requirements and architecture | [Google Doc](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs), revision `ANLCKQmu2G_lj5urAbbPvWKjY81cbKLwI_hulbiCl-vh367JYEms9Jcaq5Y9kM-iL4CUE9FkPfmtnXVhku8UHNGRwblC9TWu9u20eVplsnU` | Revision recorded in WBS 01; owner disposition still required |
| Demonstrator source commit | `2898e44f6732c8b37c31ddfbeab0e322d7574ffe` | Public Git commit observed on 2026-09-16 |
| Requirements manifest | `docs/requirements-manifest.md`, blob `cc20087acee6813b43c7d72edc123402e25316ed` | Reference only; not copied |
| v5 gates/data catalogue | `src/v5Data.js`, blob `2b9270e806ad83871e481d24e49b9533592d371f` | Reference only; not copied |
| Traceability scenarios/P0 experiments | `src/domain/traceability.js`, blob `1e65880eb3809dc3caf7bc0b0994510f4951718f` | Reference only; not copied |
| Demo-shell boundaries | `docs/demo-shell-architecture.md`, blob `80412d3aef032d8ea05143acd067fdabe38e5524` | Reference only; not copied |
| Prototype dependency manifest | `package.json`, blob `62de2d105a7b43228a84ff9373c02ef66d5d9d4c` | Reference only; not copied |

## Approval and missing source material

```text
owner_approval: MISSING
approval_reference: none
controlled_v5_source: unresolved
```

The WBS identifies the consolidated Google Doc as the execution baseline but also notes that the externally controlled v5 manifest has not been retrieved in this execution. The owner/source custodian must either provide the controlled v5 material or explicitly confirm that the recorded Google Doc revision governs. Missing questionnaire wording, methodology, templates, licensing, capacity targets, credentials, and professional approvals remain unresolved rather than being invented here.

## Boundaries preserved

- The demonstrator's Vue/Vite application, `shared/`, worker, D1 database, R2 storage, synthetic data, credentials, and deployment settings remain outside this repository.
- The proposed Frappe application is not implemented by this baseline record.
- No tenant mutation, production migration, provider write, external send, deployment, merge, or acceptance publication is authorized by this record.
- Evidence in this file contains no passwords, tokens, client data, or private source text.

## Resolution required

Record an owner/source-custodian decision by replacing the `owner_approval: MISSING` marker with an approved disposition and adding the approval reference. Re-run `scripts/wbs/validate_baseline.py --root .` after the decision; until then task 01 remains `BLOCKED` and later WBS tasks cannot start.

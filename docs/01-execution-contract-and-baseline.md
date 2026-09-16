# 01 — Execution contract, source baseline, and WBS index

## Objective

Establish the exact implementation baseline and the autonomous-agent execution contract. Freeze the source revision and distinguish executable engineering work from external approvals and production operations.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** FR-SCOPE-001–009; FR-TRACE-001–006; sections 25–27.

**Dependencies:** None — entry task.

**External prerequisites:** Owner/source-custodian supplies the controlled v5 source or confirms the consolidated Google Doc as the governing baseline. Prior architectural approval is not re-requested; unresolved detailed contracts remain explicit.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Repository requirements manifest](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/requirements-manifest.md); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [Existing prototype scripts and dependencies](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/package.json).

## Target Files

- **Create:** `docs/production/source-baseline.md`
- **Create:** `docs/production/execution-status.json`
- **Create:** `scripts/wbs/validate_baseline.py`
- **Read / preserve:** `README.md`
- **Read / preserve:** `docs/requirements-manifest.md`
- **Read / preserve:** `docs/implementation-status.md`
- **Read / preserve:** `docs/demo-shell-architecture.md`
- **Read / preserve:** `src/domain/traceability.js`
- **Read / preserve:** `src/v5Data.js`
- **Read / preserve:** `package.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Work in nirzaf/steauditqts. Preserve the existing root Vue/Vite application, shared/, worker/, D1 quadrate-db, private demo R2 bucket, and demo data boundaries. The new production Frappe app is proposed under production/audit_practice/; this is a new path convention, not a claim that production code already exists. Do not mix in the separate Merconiq/.NET ERP project.

2. Read applicable AGENTS.md files and inspect git status, the current branch, existing issues and overlapping changes before editing. Implement one numbered file at a time on one branch per task; review the minimal diff and relevant tests before moving on. Do not autonomously merge, deploy, change tenant consent/retention, or perform irreversible operations; obtain the user-specified confirmation codeword for those operations. Never invent a codeword.

3. Record the Google Doc URL/revision, repository commit, source hashes, and requirement IDs. The retrieved Google Doc is the execution baseline. The manifest names an externally controlled v5 document not retrieved in this session: obtain it or record explicit owner approval that the consolidated baseline governs. Do not fabricate missing questionnaire wording, methodology, template content, or approvals.

4. Create execution-status.json with task_id, state (NOT_STARTED/IN_PROGRESS/BLOCKED/ACCEPTED), commit, tests, evidence_path and blocker. Initial status is NOT_STARTED for every task. Record only observable results, not agent intention. A dependency is complete only when its acceptance criteria and required external evidence are satisfied.

5. Implement validate_baseline.py using Python standard library only: validate the source-baseline references, sequential task identities in the status file, and legal state values; exit nonzero on missing required baseline approval. Evidence must not contain passwords, tokens, real client data, or private source text beyond the authorized repository scope.

6. The archive is a build plan, not implemented application code or permission to execute future operational steps. Commands below and in later files are acceptance commands for the future implementing agent; scripts/modules explicitly listed as new must first be implemented in their owning task.


**Execution order and command ownership**

Unpack this folder, start with this file, and complete files in ascending order. Dependencies are acceptance gates, not merely files that exist. Every task has a backward-only technical dependency set plus the immediately preceding execution gate; this deliberately serializes shared-file changes. Do not parallelize these task files without revalidating dependencies and path ownership. All paths are relative to the existing repository root unless stated otherwise.

The ZIP contains task specifications only. Its future target scripts, schemas and APIs are not implemented by downloading it. The dependency graph is validated internally; external tenant credentials, licensing, methodology, capacity targets and operator approvals remain explicit gates rather than fabricated guarantees of blocker-free execution.

**Resolved planning snapshot:** Google Doc revision `ANLCKQmu2G_lj5urAbbPvWKjY81cbKLwI_hulbiCl-vh367JYEms9Jcaq5Y9kM-iL4CUE9FkPfmtnXVhku8UHNGRwblC9TWu9u20eVplsnU`; repository commit `2898e44f6732c8b37c31ddfbeab0e322d7574ffe`; compiled 2026-09-16. The current document is authoritative for this WBS; repository evidence explains existing behavior, not proof of production readiness.

**Minimal architecture contract:** one Frappe/ERPNext modular monolith with `audit_practice`; MariaDB stores workflow and durable outbox intent; Redis/Frappe workers execute bounded tasks; Entra supplies identity; SharePoint stores canonical documents; records protection and independent checkpoints gate delivery. No initial FastAPI service, general workflow engine, Kafka, new DMS or .NET rewrite. Optional signature/screening/analytics integrations need approved capability and license disposition; native/manual approved paths must remain honest.

**Path and command contract:** production app source `production/audit_practice/`; Python package `production/audit_practice/audit_practice/`; module `audit_operations`; custom DocTypes under `audit_operations/doctype/`. Task 04 creates the P0 runner; task 09 creates the `./scripts/production/dev` wrapper and disposable Frappe test site; task 33 creates the production Playwright configuration. Commands run from REPO_ROOT and the wrapper changes into its ignored Bench. Production credentials are never needed for ordinary unit tests. Live acceptance gates require explicitly allowed staging resources.

**Per-task completion contract:** inspect previous accepted commits; implement schemas/patches before corresponding handlers, then APIs/UI/tests; use exact source-approved business rules; run the named checks; record actual evidence and limitations. Never add a stub that reports success, widen permissions to clear a failure, weaken a negative test, or mark skipped live proof as passed. New files named by this WBS are proposals; reuse an equivalent existing implementation when verified, recording the path mapping without duplicating it.

| File | Milestone | Work package |
|---|---|---|
| [01](01-execution-contract-and-baseline.md) | R0 | Execution contract, source baseline, and WBS index |
| [02](02-business-contracts-and-operating-targets.md) | R0 | Service contracts, gates, outputs, and operating targets |
| [03](03-toolchain-and-version-contract.md) | R0 | Pin the toolchain and command conventions |
| [04](04-poc-harness-and-schema.md) | R0 | Disposable feasibility environment, spike schema, and proof runner |
| [05](05-poc-identity-and-document-capabilities.md) | R0 | P0 identity, isolation, and Microsoft document proofs |
| [06](06-poc-release-and-recovery-proofs.md) | R0 | P0 transaction, privileged execution, retry, and recovery proofs |
| [07](07-poc-accounting-and-capacity.md) | R0 | P0 accounting bridge and representative capacity proof |
| [08](08-r0-feasibility-exit.md) | R0 | R0 evidence reconciliation and feasibility exit |
| [09](09-production-app-and-test-harness.md) | R1 | Scaffold the production app and executable test harness |
| [10](10-runtime-settings-and-telemetry.md) | R1 | Runtime configuration, secrets boundary, and diagnostic primitives |
| [11](11-protected-record-foundation.md) | R1 | Protected record base and schema conventions |
| [12](12-scope-and-identity-schema.md) | R1 | Firm, client, period, engagement, assignment, and guard schema |
| [13](13-command-history-and-outbox-schema.md) | R1 | Command receipts, audit history, outbox, and worker-state schema |
| [14](14-evidence-and-approval-schema.md) | R1 | Evidence, manifest, approval, and dependency schema |
| [15](15-entra-sessions-and-lifecycle.md) | R1 | Entra sign-in, stable identity mapping, and session revocation |
| [16](16-scoped-action-authorization.md) | R1 | Role/assignment authorization across every access path |
| [17](17-transactional-command-kernel.md) | R1 | Atomic command transactions, revisions, and idempotency |
| [18](18-durable-outbox-and-worker-leases.md) | R1 | Durable outbox dispatch, bounded queues, and stale-worker fencing |
| [19](19-artifact-and-communication-schema.md) | R1 | Artifact, signature, communication, and notification schema |
| [20](20-microsoft-document-gateway.md) | R1 | Microsoft transport and trusted repository gateway |
| [21](21-exact-snapshots-and-manifests.md) | R1 | Exact receipts, preserved snapshots, and canonical manifests |
| [22](22-versioned-approval-and-impact-engine.md) | R1 | Version-bound decisions and synchronous invalidation |
| [23](23-gate-engine-and-projection-contract.md) | R1 | Service-specific gate evaluation and progress projections |
| [24](24-r1-secure-core-exit.md) | R1 | R1 secure-core integration and bypass regression gate |
| [25](25-onboarding-and-commercial-schema.md) | R2 | Client assessment and commercial onboarding schema |
| [26](26-portal-messaging-and-notification-services.md) | R2 | Scoped messages, notification outbox, and safe correspondence |
| [27](27-artifact-rendering-and-signature-adapter.md) | R2 | Approved artifact rendering and verified signature evidence |
| [28](28-client-inquiry-and-acceptance.md) | R2 | Inquiry, client profile, questionnaire, and acceptance commands |
| [29](29-estimates-fees-and-quotation.md) | R2 | Cost estimates, fee review, and exact quotation acceptance |
| [30](30-terms-advance-and-portal-activation.md) | R2 | Engagement terms, verified advance, and restricted activation |
| [31](31-pbc-schema.md) | R2 | PBC request, evidence association, and suitability schema |
| [32](32-pbc-commands-and-evidence-review.md) | R2 | PBC requests, bounded uploads, replacements, and review |
| [33](33-production-workspaces-and-client-portal.md) | R2 | Production staff workspace and restricted client portal |
| [34](34-r2-onboarding-evidence-exit.md) | R2 | R2 onboarding and evidence end-to-end acceptance |
| [35](35-accounting-data-schema.md) | R3 | Accounting datasets, journals, mappings, and FS schema |
| [36](36-safe-tb-import-and-validation.md) | R3 | Bounded TB parsing, staging, and atomic promotion |
| [37](37-account-mapping-and-source-bridges.md) | R3 | Versioned taxonomy mappings and source reconciliation |
| [38](38-journal-authorization-and-application.md) | R3 | Journal review, management authorization, and reflection-aware plans |
| [39](39-comparatives-cashflow-and-disclosures.md) | R3 | Supporting schedules, comparatives, and disclosure completeness |
| [40](40-financial-statements-and-management-response.md) | R3 | FS calculation, versioned drafts, MIR, and management response |
| [41](41-accounting-workspace-and-linked-handoff.md) | R3 | Accounting workspace, client responses, and audit handoff |
| [42](42-audit-execution-schema.md) | R3 | Planning, risk, samples, workpapers, findings, and completion schema |
| [43](43-audit-planning-and-announcement.md) | R3 | Planning, materiality, team allocation, and announcement |
| [44](44-risks-populations-and-sampling.md) | R3 | Risk-response coverage, reconciled populations, and sample plans |
| [45](45-workpapers-submission-and-summary.md) | R3 | Procedure execution, frozen workpapers, and conclusion summary |
| [46](46-reviews-findings-and-remediation.md) | R3 | Independent review points, findings, responses, and follow-up |
| [47](47-completion-eqr-opinion-and-final-discussion.md) | R3 | Completion package, representations, EQR, opinion, and discussion |
| [48](48-internal-audit-service-profile.md) | R3 | Internal-audit engagements and continuing remediation |
| [49](49-audit-and-review-workspaces.md) | R3 | Planning, fieldwork, reviewer, partner, and EQR workspaces |
| [50](50-r3-execution-and-review-exit.md) | R3 | R3 accounting and audit execution acceptance gate |
| [51](51-release-records-and-recovery-schema.md) | R4 | Release, hold, checkpoint, delivery, archive, and recovery schema |
| [52](52-legal-holds-and-record-protection.md) | R4 | Legal holds and observed record-protection enforcement |
| [53](53-independent-checkpoint-and-epoch-store.md) | R4 | Independent checkpoint storage and non-rollbackable epoch adapter |
| [54](54-final-artifacts-and-release-candidates.md) | R4 | Final artifacts, signature lineage, and eligible release candidates |
| [55](55-guarded-release-authorization.md) | R4 | Transactional release authorization and single release identity |
| [56](56-checkpoint-publication-gate.md) | R4 | Publish and verify the release checkpoint before delivery intent |
| [57](57-controlled-delivery-and-reconciliation.md) | R4 | Controlled distribution, delivery evidence, and uncertain-outcome recovery |
| [58](58-archive-manifests-and-controlled-exports.md) | R4 | Archive assembly and purpose-scoped evidence exports |
| [59](59-controlled-amendment-workflow.md) | R4 | Post-issue amendments and supersession lineage |
| [60](60-quarantined-restore-and-recovery.md) | R4 | Quarantined restore, reconciliation, and safe recovery resume |
| [61](61-release-records-and-recovery-ui.md) | R4 | Signatory, records, delivery, and recovery workspaces |
| [62](62-r4-release-and-recovery-exit.md) | R4 | R4 release fault-injection and recovery acceptance gate |
| [63](63-time-billing-and-commercial-close.md) | R5 | Time capture, invoice allocation, and commercial close |
| [64](64-continuance-and-controlled-rollover.md) | R5 | Next-period continuance, non-renewal, and controlled roll-forward |
| [65](65-operations-deployment-and-backups.md) | R5 | Production deployment packaging, telemetry, backups, and runbooks |
| [66](66-legacy-migration-rehearsal.md) | R5 | Scoped legacy-data inventory and migration rehearsal |
| [67](67-security-and-privilege-validation.md) | R5 | Security regression, privilege-boundary, and secret-handling assessment |
| [68](68-performance-accessibility-and-resilience.md) | R5 | Capacity, accessibility, and degraded-mode validation |
| [69](69-demo-preservation-and-walkthrough-regression.md) | R5 | Preserve the demo shell, shared invitations, and repeatable walkthrough |
| [70](70-full-requirement-and-test-traceability.md) | R5 | Complete functional, acceptance, and P0 traceability |
| [71](71-pilot-acceptance-and-cutover-rehearsal.md) | R5 | Pilot UAT, training, and cutover rehearsal |
| [72](72-controlled-production-rollout-and-handover.md) | R5 | Controlled production rollout, verification, and handover |

**Sources and implementation references**

- `spec` — [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs)
- `manifest` — [Repository requirements manifest](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/requirements-manifest.md)
- `gates` — [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js)
- `trace` — [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js)
- `demo` — [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md)
- `pkg` — [Existing prototype scripts and dependencies](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/package.json)
- `frappe-db` — [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database)
- `frappe-jobs` — [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs)
- `frappe-test` — [Frappe testing](https://docs.frappe.io/framework/user/en/testing)
- `frappe-app` — [Frappe app scaffolding](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- `frappe-hooks` — [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
- `graph-selected` — [Microsoft Graph Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview)
- `graph-throttle` — [Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling)
- `graph-mail` — [Graph sendMail response semantics](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0)
- `records` — [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management)
- `licenses` — [Purview records-management setup and licensing](https://learn.microsoft.com/en-us/purview/get-started-with-records-management)
- `screen-license` — [OpenSanctions data licensing](https://www.opensanctions.org/licensing/)
- `msal` — [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens)
- `canonical` — [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py)

## Acceptance Criteria

- [ ] The source baseline identifies the existing demo and the separate production target without renaming or deleting either.
- [ ] Every file in this WBS has a distinct task ID; all dependency links point to earlier existing files.
- [ ] Missing external v5 material has an owner-approved disposition rather than an invented substitute.
- [ ] Working-tree changes are limited to baseline/status/validator artifacts; production, tenant and repository writes have not been triggered by this planning step.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
git status --short
git rev-parse HEAD
python3 scripts/wbs/validate_baseline.py --root .
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

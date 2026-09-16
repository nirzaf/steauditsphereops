# 70 — Complete functional, acceptance, and P0 traceability

## Objective

Reconcile every requirement and acceptance scenario to implemented code and genuine test evidence before declaring the solution complete.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** FR-TRACE-001–006; all FR families; AT-01–28; ET-01–44; BT-01–64; VT-01–24; P0-01–12.

**Dependencies:** [69 — Preserve the demo shell, shared invitations, and repeatable walkthrough](69-demo-preservation-and-walkthrough-regression.md)

**Execution gate:** file 69 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Repository requirements manifest](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/requirements-manifest.md); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js).

## Target Files

- **Create:** `docs/production/requirement-traceability.json`
- **Create:** `docs/production/test-evidence-index.json`
- **Create:** `scripts/wbs/validate_traceability.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_full_cycle.py`
- **Create:** `tests/production/full-cycle.spec.js`
- **Read / preserve:** `src/domain/traceability.js`
- **Read / preserve:** `docs/requirements-manifest.md`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Extract the exact FR IDs from the frozen approved Google Doc and AT/ET/BT/VT/P0 identities and meanings from the pinned repository source. Preserve 28 AT + 44 ET + 64 BT + 24 VT = 160 acceptance scenarios and track 12 P0 experiments separately; never invent replacement titles or count source rows as passing tests.

2. For every requirement/scenario record WBS task, applicable service, source, target code, focused test ID/command, tested commit/environment, outcome and evidence path. Distinguish IMPLEMENTED, TESTED_LOCAL, TESTED_TENANT, BLOCKED, N_A with owner-approved reason; a mock cannot satisfy live records/recovery evidence.

3. Implement validate_traceability.py using standard library to reject duplicate/missing IDs, nonexistent test modules, unchecked MUST requirements and absent evidence. Optional capabilities require an explicit disabled/approved manual-path disposition, not silent omission or fake test status.

4. Run full cycles for all enabled services, replacement/accounting impact, independent review, blocked release, checkpoint/delivery/archive/amendment and next-period continuance; also preserve the demo acceptance contract. All 26 output definitions need an implementation or valid service-specific N_A with ownership, version, visibility and tested production trigger.

5. The task-to-requirement allocation below is a planning crosswalk, not evidence of completed implementation. Reconcile it against live source at execution; approval of this WBS does not automatically accept changed scope or missing mandatory tests.


**Planning allocation — every baseline functional requirement**

The range in each row includes every numbered ID, not a sample. These are task allocations, not implementation/pass claims. Tasks 67–71 provide cross-cutting validation; additional owner/test links must be recorded during execution.

| Requirement IDs | Implementation / control task IDs |
|---|---|
| FR-SCOPE-001–009 | [01](01-execution-contract-and-baseline.md), [02](02-business-contracts-and-operating-targets.md), [09](09-production-app-and-test-harness.md), [12](12-scope-and-identity-schema.md), [16](16-scoped-action-authorization.md), [38](38-journal-authorization-and-application.md), [48](48-internal-audit-service-profile.md), [65](65-operations-deployment-and-backups.md), [66](66-legacy-migration-rehearsal.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-AUTH-001–010 | [11](11-protected-record-foundation.md), [12](12-scope-and-identity-schema.md), [15](15-entra-sessions-and-lifecycle.md), [16](16-scoped-action-authorization.md), [22](22-versioned-approval-and-impact-engine.md), [30](30-terms-advance-and-portal-activation.md), [33](33-production-workspaces-and-client-portal.md), [47](47-completion-eqr-opinion-and-final-discussion.md), [53](53-independent-checkpoint-and-epoch-store.md), [67](67-security-and-privilege-validation.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-NAV-001–012 | [23](23-gate-engine-and-projection-contract.md), [33](33-production-workspaces-and-client-portal.md), [41](41-accounting-workspace-and-linked-handoff.md), [49](49-audit-and-review-workspaces.md), [61](61-release-records-and-recovery-ui.md), [68](68-performance-accessibility-and-resilience.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-CL-001–010 | [25](25-onboarding-and-commercial-schema.md), [28](28-client-inquiry-and-acceptance.md), [29](29-estimates-fees-and-quotation.md), [30](30-terms-advance-and-portal-activation.md), [64](64-continuance-and-controlled-rollover.md) |
| FR-GATE-001–009 | [02](02-business-contracts-and-operating-targets.md), [12](12-scope-and-identity-schema.md), [17](17-transactional-command-kernel.md), [22](22-versioned-approval-and-impact-engine.md), [23](23-gate-engine-and-projection-contract.md), [28](28-client-inquiry-and-acceptance.md), [29](29-estimates-fees-and-quotation.md), [30](30-terms-advance-and-portal-activation.md), [43](43-audit-planning-and-announcement.md), [45](45-workpapers-submission-and-summary.md), [47](47-completion-eqr-opinion-and-final-discussion.md), [48](48-internal-audit-service-profile.md), [55](55-guarded-release-authorization.md), [63](63-time-billing-and-commercial-close.md), [64](64-continuance-and-controlled-rollover.md) |
| FR-PBC-001–012 | [14](14-evidence-and-approval-schema.md), [19](19-artifact-and-communication-schema.md), [20](20-microsoft-document-gateway.md), [21](21-exact-snapshots-and-manifests.md), [27](27-artifact-rendering-and-signature-adapter.md), [31](31-pbc-schema.md), [32](32-pbc-commands-and-evidence-review.md), [33](33-production-workspaces-and-client-portal.md), [58](58-archive-manifests-and-controlled-exports.md) |
| FR-ACC-001–013 | [35](35-accounting-data-schema.md), [36](36-safe-tb-import-and-validation.md), [37](37-account-mapping-and-source-bridges.md), [38](38-journal-authorization-and-application.md), [39](39-comparatives-cashflow-and-disclosures.md), [40](40-financial-statements-and-management-response.md), [41](41-accounting-workspace-and-linked-handoff.md) |
| FR-AUD-001–012 | [42](42-audit-execution-schema.md), [43](43-audit-planning-and-announcement.md), [44](44-risks-populations-and-sampling.md), [45](45-workpapers-submission-and-summary.md), [46](46-reviews-findings-and-remediation.md), [47](47-completion-eqr-opinion-and-final-discussion.md), [48](48-internal-audit-service-profile.md), [49](49-audit-and-review-workspaces.md) |
| FR-REV-001–008 | [14](14-evidence-and-approval-schema.md), [16](16-scoped-action-authorization.md), [21](21-exact-snapshots-and-manifests.md), [22](22-versioned-approval-and-impact-engine.md), [45](45-workpapers-submission-and-summary.md), [46](46-reviews-findings-and-remediation.md), [47](47-completion-eqr-opinion-and-final-discussion.md), [49](49-audit-and-review-workspaces.md) |
| FR-REL-001–012 | [51](51-release-records-and-recovery-schema.md), [52](52-legal-holds-and-record-protection.md), [53](53-independent-checkpoint-and-epoch-store.md), [54](54-final-artifacts-and-release-candidates.md), [55](55-guarded-release-authorization.md), [56](56-checkpoint-publication-gate.md), [57](57-controlled-delivery-and-reconciliation.md), [58](58-archive-manifests-and-controlled-exports.md), [59](59-controlled-amendment-workflow.md), [60](60-quarantined-restore-and-recovery.md), [61](61-release-records-and-recovery-ui.md), [62](62-r4-release-and-recovery-exit.md) |
| FR-FIN-001–006 | [25](25-onboarding-and-commercial-schema.md), [29](29-estimates-fees-and-quotation.md), [30](30-terms-advance-and-portal-activation.md), [63](63-time-billing-and-commercial-close.md) |
| FR-COM-001–007 | [19](19-artifact-and-communication-schema.md), [26](26-portal-messaging-and-notification-services.md), [27](27-artifact-rendering-and-signature-adapter.md), [30](30-terms-advance-and-portal-activation.md), [32](32-pbc-commands-and-evidence-review.md), [33](33-production-workspaces-and-client-portal.md), [40](40-financial-statements-and-management-response.md), [46](46-reviews-findings-and-remediation.md), [57](57-controlled-delivery-and-reconciliation.md) |
| FR-STATE-001–010 | [12](12-scope-and-identity-schema.md), [17](17-transactional-command-kernel.md), [18](18-durable-outbox-and-worker-leases.md), [22](22-versioned-approval-and-impact-engine.md), [23](23-gate-engine-and-projection-contract.md), [33](33-production-workspaces-and-client-portal.md), [41](41-accounting-workspace-and-linked-handoff.md), [49](49-audit-and-review-workspaces.md), [61](61-release-records-and-recovery-ui.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-DEMO-001–010 | [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-UX-001–009 | [23](23-gate-engine-and-projection-contract.md), [33](33-production-workspaces-and-client-portal.md), [41](41-accounting-workspace-and-linked-handoff.md), [49](49-audit-and-review-workspaces.md), [61](61-release-records-and-recovery-ui.md), [68](68-performance-accessibility-and-resilience.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-INT-001–012 | [02](02-business-contracts-and-operating-targets.md), [03](03-toolchain-and-version-contract.md), [09](09-production-app-and-test-harness.md), [10](10-runtime-settings-and-telemetry.md), [15](15-entra-sessions-and-lifecycle.md), [20](20-microsoft-document-gateway.md), [27](27-artifact-rendering-and-signature-adapter.md), [28](28-client-inquiry-and-acceptance.md), [52](52-legal-holds-and-record-protection.md), [53](53-independent-checkpoint-and-epoch-store.md), [63](63-time-billing-and-commercial-close.md), [65](65-operations-deployment-and-backups.md), [70](70-full-requirement-and-test-traceability.md) |
| FR-REC-001–008 | [11](11-protected-record-foundation.md), [13](13-command-history-and-outbox-schema.md), [14](14-evidence-and-approval-schema.md), [17](17-transactional-command-kernel.md), [18](18-durable-outbox-and-worker-leases.md), [21](21-exact-snapshots-and-manifests.md), [22](22-versioned-approval-and-impact-engine.md), [51](51-release-records-and-recovery-schema.md), [52](52-legal-holds-and-record-protection.md), [53](53-independent-checkpoint-and-epoch-store.md), [55](55-guarded-release-authorization.md), [56](56-checkpoint-publication-gate.md), [57](57-controlled-delivery-and-reconciliation.md), [58](58-archive-manifests-and-controlled-exports.md), [59](59-controlled-amendment-workflow.md), [60](60-quarantined-restore-and-recovery.md), [65](65-operations-deployment-and-backups.md), [66](66-legacy-migration-rehearsal.md) |
| FR-VAL-001–008 | [10](10-runtime-settings-and-telemetry.md), [11](11-protected-record-foundation.md), [16](16-scoped-action-authorization.md), [17](17-transactional-command-kernel.md), [18](18-durable-outbox-and-worker-leases.md), [20](20-microsoft-document-gateway.md), [22](22-versioned-approval-and-impact-engine.md), [23](23-gate-engine-and-projection-contract.md), [36](36-safe-tb-import-and-validation.md), [38](38-journal-authorization-and-application.md), [52](52-legal-holds-and-record-protection.md), [55](55-guarded-release-authorization.md), [57](57-controlled-delivery-and-reconciliation.md), [60](60-quarantined-restore-and-recovery.md), [67](67-security-and-privilege-validation.md), [68](68-performance-accessibility-and-resilience.md), [69](69-demo-preservation-and-walkthrough-regression.md) |
| FR-E2E-001–008 | [34](34-r2-onboarding-evidence-exit.md), [41](41-accounting-workspace-and-linked-handoff.md), [50](50-r3-execution-and-review-exit.md), [59](59-controlled-amendment-workflow.md), [62](62-r4-release-and-recovery-exit.md), [64](64-continuance-and-controlled-rollover.md), [70](70-full-requirement-and-test-traceability.md), [71](71-pilot-acceptance-and-cutover-rehearsal.md) |
| FR-TRACE-001–006 | [01](01-execution-contract-and-baseline.md), [02](02-business-contracts-and-operating-targets.md), [04](04-poc-harness-and-schema.md), [08](08-r0-feasibility-exit.md), [24](24-r1-secure-core-exit.md), [34](34-r2-onboarding-evidence-exit.md), [50](50-r3-execution-and-review-exit.md), [62](62-r4-release-and-recovery-exit.md), [70](70-full-requirement-and-test-traceability.md), [71](71-pilot-acceptance-and-cutover-rehearsal.md), [72](72-controlled-production-rollout-and-handover.md) |
| AC-DEMO-001–012 | [69](69-demo-preservation-and-walkthrough-regression.md), [70](70-full-requirement-and-test-traceability.md) |

**Named output allocation — v5 catalogue**

| Output | Exact catalogue title | Producer / control tasks |
|---|---|---|
| DOC-01 | Client Acceptance Form | [25](25-onboarding-and-commercial-schema.md), [27](27-artifact-rendering-and-signature-adapter.md), [28](28-client-inquiry-and-acceptance.md) |
| DOC-02 | Client Acceptance Questionnaire | [25](25-onboarding-and-commercial-schema.md), [27](27-artifact-rendering-and-signature-adapter.md), [28](28-client-inquiry-and-acceptance.md) |
| DOC-03 | Client Continuation Form | [25](25-onboarding-and-commercial-schema.md), [28](28-client-inquiry-and-acceptance.md), [64](64-continuance-and-controlled-rollover.md) |
| DOC-04 | Client Continuation Questionnaire | [25](25-onboarding-and-commercial-schema.md), [28](28-client-inquiry-and-acceptance.md), [64](64-continuance-and-controlled-rollover.md) |
| DOC-05 | Estimated Cost of Service Sheet | [25](25-onboarding-and-commercial-schema.md), [29](29-estimates-fees-and-quotation.md) |
| DOC-06 | Fee Approval Record | [25](25-onboarding-and-commercial-schema.md), [29](29-estimates-fees-and-quotation.md) |
| DOC-07 | Quotation | [27](27-artifact-rendering-and-signature-adapter.md), [29](29-estimates-fees-and-quotation.md) |
| DOC-08 | Audit Engagement Letter | [27](27-artifact-rendering-and-signature-adapter.md), [30](30-terms-advance-and-portal-activation.md) |
| DOC-09 | Audit Planning Record | [42](42-audit-execution-schema.md), [43](43-audit-planning-and-announcement.md) |
| DOC-10 | Audit Announcement Letter | [43](43-audit-planning-and-announcement.md) |
| DOC-11 | Client Document Request / Submission Record | [31](31-pbc-schema.md), [32](32-pbc-commands-and-evidence-review.md) |
| DOC-12 | Audit Programmes | [42](42-audit-execution-schema.md), [43](43-audit-planning-and-announcement.md), [44](44-risks-populations-and-sampling.md) |
| DOC-13 | Trial Balance Import | [35](35-accounting-data-schema.md), [36](36-safe-tb-import-and-validation.md) |
| DOC-14 | Prior-Year Audited FS | [36](36-safe-tb-import-and-validation.md), [39](39-comparatives-cashflow-and-disclosures.md) |
| DOC-15 | Audit Working Papers | [42](42-audit-execution-schema.md), [45](45-workpapers-submission-and-summary.md) |
| DOC-16 | Working Paper Conclusion Summary | [45](45-workpapers-submission-and-summary.md) |
| DOC-17 | Draft Financial Statements | [39](39-comparatives-cashflow-and-disclosures.md), [40](40-financial-statements-and-management-response.md) |
| DOC-18 | Management Information Request Letter | [26](26-portal-messaging-and-notification-services.md), [40](40-financial-statements-and-management-response.md) |
| DOC-19 | Client Response Record | [33](33-production-workspaces-and-client-portal.md), [40](40-financial-statements-and-management-response.md) |
| DOC-20 | Manager / Partner Review Record | [46](46-reviews-findings-and-remediation.md), [47](47-completion-eqr-opinion-and-final-discussion.md) |
| DOC-21 | Audit Opinion | [47](47-completion-eqr-opinion-and-final-discussion.md) |
| DOC-22 | Final Audit Report | [54](54-final-artifacts-and-release-candidates.md), [55](55-guarded-release-authorization.md), [56](56-checkpoint-publication-gate.md), [57](57-controlled-delivery-and-reconciliation.md) |
| DOC-23 | Final Financial Statements | [40](40-financial-statements-and-management-response.md), [54](54-final-artifacts-and-release-candidates.md), [55](55-guarded-release-authorization.md), [56](56-checkpoint-publication-gate.md), [57](57-controlled-delivery-and-reconciliation.md) |
| DOC-24 | Invoice | [63](63-time-billing-and-commercial-close.md) |
| DOC-25 | Staff Time Record | [63](63-time-billing-and-commercial-close.md) |
| DOC-26 | Engagement Cost Summary | [63](63-time-billing-and-commercial-close.md) |

**P0 allocation and production revalidation**

| P0 ID | Source experiment | Feasibility / revalidation tasks |
|---|---|---|
| P0-01 | Build | [04](04-poc-harness-and-schema.md), [08](08-r0-feasibility-exit.md), [09](09-production-app-and-test-harness.md), [24](24-r1-secure-core-exit.md), [65](65-operations-deployment-and-backups.md) |
| P0-02 | Identity | [05](05-poc-identity-and-document-capabilities.md), [15](15-entra-sessions-and-lifecycle.md), [16](16-scoped-action-authorization.md), [67](67-security-and-privilege-validation.md) |
| P0-03 | Isolation | [05](05-poc-identity-and-document-capabilities.md), [16](16-scoped-action-authorization.md), [33](33-production-workspaces-and-client-portal.md), [67](67-security-and-privilege-validation.md) |
| P0-04 | Microsoft capability | [05](05-poc-identity-and-document-capabilities.md), [20](20-microsoft-document-gateway.md), [52](52-legal-holds-and-record-protection.md) |
| P0-05 | Receipt / snapshot | [05](05-poc-identity-and-document-capabilities.md), [21](21-exact-snapshots-and-manifests.md) |
| P0-06 | Local release race | [06](06-poc-release-and-recovery-proofs.md), [17](17-transactional-command-kernel.md), [22](22-versioned-approval-and-impact-engine.md), [55](55-guarded-release-authorization.md), [62](62-r4-release-and-recovery-exit.md) |
| P0-07 | Accounting bridge | [07](07-poc-accounting-and-capacity.md), [37](37-account-mapping-and-source-bridges.md), [38](38-journal-authorization-and-application.md), [50](50-r3-execution-and-review-exit.md) |
| P0-08 | Privileged execution | [06](06-poc-release-and-recovery-proofs.md), [18](18-durable-outbox-and-worker-leases.md), [52](52-legal-holds-and-record-protection.md), [53](53-independent-checkpoint-and-epoch-store.md), [67](67-security-and-privilege-validation.md) |
| P0-09 | Records | [05](05-poc-identity-and-document-capabilities.md), [52](52-legal-holds-and-record-protection.md), [58](58-archive-manifests-and-controlled-exports.md), [62](62-r4-release-and-recovery-exit.md) |
| P0-10 | Retry / revocation | [06](06-poc-release-and-recovery-proofs.md), [18](18-durable-outbox-and-worker-leases.md), [20](20-microsoft-document-gateway.md), [57](57-controlled-delivery-and-reconciliation.md), [67](67-security-and-privilege-validation.md) |
| P0-11 | Release / recovery | [06](06-poc-release-and-recovery-proofs.md), [53](53-independent-checkpoint-and-epoch-store.md), [56](56-checkpoint-publication-gate.md), [60](60-quarantined-restore-and-recovery.md), [62](62-r4-release-and-recovery-exit.md) |
| P0-12 | Scope / economics | [02](02-business-contracts-and-operating-targets.md), [07](07-poc-accounting-and-capacity.md), [08](08-r0-feasibility-exit.md), [71](71-pilot-acceptance-and-cutover-rehearsal.md) |

AT-01–28, ET-01–44, BT-01–64 and VT-01–24 retain their exact meanings from the linked source inventory. Map each individual scenario to its focused test during this task; assigning a family to a phase is not sufficient evidence. A real critical-scope production test cannot be replaced by an unrelated demo smoke test.

## Acceptance Criteria

- [ ] All baseline FR IDs and 12 demo acceptance criteria are allocated with verifiable evidence/disposition.
- [ ] The exact 160 scenario IDs and 12 separate P0 IDs are retained without double counting.
- [ ] All enabled service end-to-end cycles pass; critical requirements cannot be silently waived.
- [ ] A deliberately missing or mock-only required live result causes validator failure.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_full_cycle
npx playwright test --config playwright.production.config.js tests/production/full-cycle.spec.js
python3 scripts/wbs/validate_traceability.py --root .
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

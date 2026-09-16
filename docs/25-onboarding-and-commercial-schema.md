# 25 — Client assessment and commercial onboarding schema

## Objective

Create client assessment, commercial revision and portal-eligibility records before onboarding services use them.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-CL-001–010; FR-FIN-001–003; DOC-01–08.

**Dependencies:** [24 — R1 secure-core integration and bypass regression gate](24-r1-secure-core-exit.md)

**Execution gate:** file 24 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_questionnaire_template/audit_questionnaire_template.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_questionnaire_template/audit_questionnaire_template.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_questionnaire_template/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client_assessment/audit_client_assessment.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client_assessment/audit_client_assessment.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_client_assessment/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assessment_answer/audit_assessment_answer.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assessment_answer/audit_assessment_answer.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_assessment_answer/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_commercial_case/audit_commercial_case.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_commercial_case/audit_commercial_case.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_commercial_case/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_cost_line/audit_cost_line.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_cost_line/audit_cost_line.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_cost_line/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_terms_record/audit_terms_record.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_terms_record/audit_terms_record.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_terms_record/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_advance_verification/audit_advance_verification.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_advance_verification/audit_advance_verification.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_advance_verification/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_onboarding_invitation/audit_onboarding_invitation.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_onboarding_invitation/audit_onboarding_invitation.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/doctype/audit_onboarding_invitation/__init__.py`
- **Create:** `production/audit_practice/audit_practice/schema/onboarding.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_onboarding_schema.py`
- **Create:** `production/audit_practice/audit_practice/fixtures/custom_field.json`
- **Create:** `production/audit_practice/audit_practice/setup/__init__.py`
- **Create:** `production/audit_practice/audit_practice/setup/custom_fields.py`
- **Create:** `production/audit_practice/audit_practice/security/erpnext_links.py`
- **Modify:** `production/audit_practice/audit_practice/security/schema_policy.py`
- **Modify:** `production/audit_practice/audit_practice/security/action_policy.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Questionnaire Template is versioned/approved and contains exact source questions, directionality, evidence requirements, prohibitions and specialist triggers. Assessment references client/service/period, template version, acceptance/continuance mode and prior assessment. Answers preserve UNKNOWN/YES/NO/N_A, evidence snapshot, responder/verifier and current status; N_A needs an approved reason.

2. Commercial Case links a client/engagement shell to versioned cost/fee basis, original estimate, revisions, quotation and fee approvals. Cost Line includes staff level, hours, internal cost/sell rates, expenses and currency encoded according to the approved decimal policy. Internal cost rates are never client-visible.

3. Terms Record links exact generated EL/quotation scope, firm review, client signatory and acceptance evidence. Advance Verification references an ERPNext Payment Entry or reviewed payment evidence, currency, verified amount, reversal state and business eligibility; it does not post a second ledger payment.

4. Onboarding Invitation stores only a digest of a high-entropy redeem secret, intended identity/client/scope, expiry, redemption/revocation and setup-only status. Never store a reusable plaintext password or allow a new invitation to choose a staff persona.

5. Add child-table/order validation and unique external financial IDs/idempotency fields. Preserve prior submissions, fee revisions and invitations rather than overwriting. The schema links only to existing DocTypes; billing close uses installed ERPNext later.

6. Before commercial APIs, install version-controlled ERPNext Custom Fields for audit engagement/commercial/source-operation links on Quotation, Sales Invoice, Payment Entry and Timesheet using create_custom_fields and idempotent migration hooks. Future release IDs are validated typed Data references until the release schema exists, not forward Link options. Protect audit-linked provenance/amount-allocation fields through doc_events and the internal command context while preserving ordinary unrelated ERPNext functionality. Include verified/unallocated/allocated/reversed advance fields and a unique allocation identity for the later billing task.

## Acceptance Criteria

- [ ] All eight DocTypes migrate before services are exposed.
- [ ] Question direction and UNKNOWN state are representable without an assumed favorable default.
- [ ] Client serialization cannot include internal cost rates or token digests.
- [ ] Terms, advance verification and access eligibility remain separate records.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_onboarding_schema
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

# Business-contract decision register

This register records the decisions required before schemas, release logic, or live feasibility proofs can claim readiness. `BLOCKED_PENDING_OWNER` is a deliberate disposition: it identifies the accountable owner and prevents dependent proof from being reported as passed. It is not an invented policy value or a substitute for professional, security, records, or sponsor approval.

The v5 demonstrator data is a read-only reference. It supplies labels and illustrative fixture values; it does not supply production policy, licensing, capacity, retention, or approval authority.

```json
{
  "schema": "steauditsphereops/decision-register@1",
  "version": "v5",
  "decisions": [
    {"id":"DEC-ACCOUNTING-DECIMAL","topic":"accounting_decimal_scale","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve scale, currency precision, and source-approved rounding policy before accounting proofs.","blocks":["P0-07","R0_ACCOUNTING_EXIT"]},
    {"id":"DEC-ACCOUNTING-FX","topic":"exchange_rate_source","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve exchange-rate source, date selection, and fallback treatment.","blocks":["P0-07","R0_ACCOUNTING_EXIT"]},
    {"id":"DEC-JOURNAL-REFLECTION","topic":"journal_reflection_policy","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve PARTIAL and UNKNOWN reflection treatment; no silent duplicate or cash-flow plug is permitted.","blocks":["P0-07","R0_ACCOUNTING_EXIT"]},
    {"id":"DEC-FRAMEWORK","topic":"applicable_financial_frameworks","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve the framework catalogue and engagement-level applicability rule.","blocks":["P0-07","R0_ACCOUNTING_EXIT"]},
    {"id":"DEC-EVIDENCE-APPLICABILITY","topic":"non_applicable_evidence_rules","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve how non-applicable evidence is justified, reviewed, and preserved.","blocks":["P0-05","P0-07","R0_EVIDENCE_EXIT"]},
    {"id":"DEC-REPORT-DATE","topic":"report_date_rules","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve report-date prerequisites and prohibit backdating around incomplete gates.","blocks":["P0-11","R0_RELEASE_EXIT"]},
    {"id":"DEC-MATERIALITY-SAMPLING","topic":"materiality_and_sampling_policy","owner_role":"PROFESSIONAL_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve methodology references, thresholds, overrides, and population/sample documentation.","blocks":["P0-07","R0_ACCOUNTING_EXIT"]},
    {"id":"DEC-PURVIEW-LICENSE","topic":"purview_records_license_and_capability","owner_role":"RECORDS_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":"https://learn.microsoft.com/en-us/purview/get-started-with-records-management","required_action":"Confirm licensed capability, tenant configuration, observed protection evidence, and manual fallback. Do not claim retention or immutability from a label alone.","blocks":["P0-04","P0-09","P0-11","R0_RECORDS_EXIT"]},
    {"id":"DEC-SCREENING-LICENSE","topic":"screening_data_rights","owner_role":"SECURITY_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":"https://www.opensanctions.org/licensing/","required_action":"Confirm permitted data source, licence, geography, freshness, false-positive handling, and manual fallback; keep optional until approved.","blocks":["P0-02","P0-12","R0_IDENTITY_EXIT"]},
    {"id":"DEC-IDENTITY-GUEST","topic":"identity_guest_model","owner_role":"SECURITY_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Confirm Entra guest/invite model, stable identity mapping, revocation, and tenant boundary.","blocks":["P0-02","P0-03","R0_IDENTITY_EXIT"]},
    {"id":"DEC-RECORD-THREAT","topic":"record_threat_model","owner_role":"RECORDS_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve record classes, hold/disposal profile, protected-role model, and observed verification method.","blocks":["P0-09","P0-11","R0_RECORDS_EXIT"]},
    {"id":"DEC-CHECKPOINT","topic":"independent_checkpoint_storage","owner_role":"SECURITY_OWNER","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve independently administered checkpoint/epoch store, access boundary, residency, and recovery operator.","blocks":["P0-08","P0-11","R0_RELEASE_EXIT"]},
    {"id":"DEC-RESIDENCY","topic":"data_residency","owner_role":"SPONSOR","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":null,"required_action":"Approve client/firm residency constraints for application, SharePoint, records, telemetry, backups, and checkpoint data.","blocks":["P0-04","P0-11","R0_CAPACITY_EXIT"]},
    {"id":"DEC-NFR-TARGETS","topic":"capacity_and_nfr_targets","owner_role":"SPONSOR","status":"BLOCKED_PENDING_OWNER","decision":null,"evidence":"docs/production/nfr-targets.json","required_action":"Approve expected scale, latency, freshness, file/row limits, availability, retention, RPO, RTO, and budget values; null values block dependent proofs.","blocks":["P0-01","P0-04","P0-07","P0-09","P0-11","P0-12","R0_FEASIBILITY_EXIT"]}
  ]
}
```

No entry above authorizes a provider, tenant, external send, deployment, professional conclusion, legal determination, or irreversible operation. A later owner decision must preserve the entry history and identify the exact evidence and effective revision.

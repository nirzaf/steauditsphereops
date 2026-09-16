# 58 — Archive assembly and purpose-scoped evidence exports

## Objective

Assemble a retained engagement record and bounded exports without altering issued artifacts or conflating client and inspector access.

## Context/Dependencies

**Milestone:** R4. **Requirement scope:** FR-REL-008–011; FR-REC-002,007–008; ET-40,42; G10 archive component.

**Dependencies:** [52 — Legal holds and observed record-protection enforcement](52-legal-holds-and-record-protection.md); [57 — Controlled distribution, delivery evidence, and uncertain-outcome recovery](57-controlled-delivery-and-reconciliation.md)

**Execution gate:** file 57 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py).

## Target Files

- **Create:** `production/audit_practice/audit_practice/records/archive.py`
- **Create:** `production/audit_practice/audit_practice/records/exports.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_archive_and_exports.py`
- **Modify:** `production/audit_practice/audit_practice/api/records.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/application/gate_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Freeze a canonical Archive Manifest containing approved source/evidence snapshots, structured workpapers/decisions, exact release/checkpoint/delivery records and required protection/hold observations. Verify completeness under the service profile; missing retained member or protection proof leaves archive pending.

2. Archive assembly may follow issue administratively, but checkpoint before delivery remains mandatory. Do not let G9 commercial state automatically rewrite professional issue/archive history; evaluate current independent gate applicability.

3. Create controlled exports by explicit purpose: client gets approved published outputs; inspector/internal authorized role may access defined wider evidence. Reauthorize queued export requester, selected members and destination at execution and publication; no unrestricted all-record dump.

4. Stream bounded archive packaging with safe member paths, file count/size limits and manifest digests. Prevent path traversal, duplicate ambiguous names and metadata leakage. If generated CSVs are present, neutralize executable formulas in the export representation without mutating source records.

5. Legal hold blocks prohibited disposal/destructive changes but allows authorized preservation. Retention/disposal follows the signed records policy with separate human authority; no auto-deletion based on demo 24-hour TTL.

## Acceptance Criteria

- [ ] Every archive member resolves to the exact retained version/digest.
- [ ] Client export cannot contain internal workpapers/review points or other-client metadata.
- [ ] Revocation while export queued prevents unauthorized publication.
- [ ] Archive stays incomplete when protection or member verification is missing.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_archive_and_exports
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.

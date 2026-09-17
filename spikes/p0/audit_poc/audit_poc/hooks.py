app_name = "audit_poc"
app_title = "Audit POC"
app_publisher = "STE AuditSphere Ops"
app_description = "Disposable P0 feasibility spike; not production code."
app_email = "engineering@example.invalid"
app_license = "MIT"

# POC-only hooks: generic API/Desk access must not bypass the scoped experiment.
doc_events = {
    "POC Record": {
        "validate": "audit_poc.permissions.validate_record",
    }
}
permission_query_conditions = {
    "POC Record": "audit_poc.permissions.poc_record_query",
}
has_permission = {
    "POC Record": "audit_poc.permissions.poc_record_has_permission",
}

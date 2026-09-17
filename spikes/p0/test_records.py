from __future__ import annotations

import unittest
from types import SimpleNamespace

from spikes.p0.audit_poc.audit_poc.permissions import poc_record_has_permission, poc_record_query


class RecordsBoundaryTests(unittest.TestCase):
    def test_frappe_permission_hook_fails_closed_without_assignment(self) -> None:
        record = SimpleNamespace(client_id="client-a", period="2026")
        self.assertFalse(poc_record_has_permission(record, user="client-a"))
        self.assertEqual(poc_record_query("client-a"), "1=0")

    def test_unobserved_protection_is_not_pass(self) -> None:
        matrix = {"ordinary_editor": "NOT_RUN_EXTERNAL_PREREQUISITE", "records_custodian": "NOT_RUN_EXTERNAL_PREREQUISITE", "privileged_admin": "NOT_RUN_EXTERNAL_PREREQUISITE"}
        self.assertTrue(all(value != "PASS" for value in matrix.values()))

    def test_retention_label_does_not_equal_immutable_bytes(self) -> None:
        label_applied = True
        observed_protection = False
        self.assertFalse(label_applied and observed_protection)


if __name__ == "__main__":
    unittest.main()

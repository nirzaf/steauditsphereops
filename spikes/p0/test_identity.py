from __future__ import annotations

import unittest

from spikes.p0.audit_poc.audit_poc.permissions import access_decision, subject_key


class IdentityIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client_a = {"tenant_id": "tenant-a", "client_id": "client-a", "subject_id": "subject-1", "email": "same@example.invalid", "role": "client"}
        self.record_a = {"tenant_id": "tenant-a", "client_id": "client-a"}

    def test_subject_mapping_does_not_use_email(self) -> None:
        self.assertEqual(subject_key("tenant-a", "subject-1"), "tenant-a:subject-1")
        changed_email = {**self.client_a, "email": "reused@example.invalid"}
        self.assertEqual(subject_key(changed_email["tenant_id"], changed_email["subject_id"]), "tenant-a:subject-1")
        self.assertNotEqual(subject_key("tenant-a", "subject-1"), subject_key("tenant-a", "subject-2"))

    def test_wrong_tenant_scope_and_revocation_deny(self) -> None:
        self.assertEqual(access_decision(self.client_a, self.record_a), (True, "ALLOW"))
        wrong_tenant = {**self.client_a, "tenant_id": "tenant-b"}
        wrong_client = {**self.client_a, "client_id": "client-b"}
        revoked = {**self.client_a, "revoked": True}
        disabled = {**self.client_a, "disabled": True}
        self.assertEqual(access_decision(wrong_tenant, self.record_a)[0], False)
        self.assertEqual(access_decision(wrong_client, self.record_a)[0], False)
        self.assertEqual(access_decision(revoked, self.record_a)[0], False)
        self.assertEqual(access_decision(disabled, self.record_a), (False, "ACTOR_DISABLED"))

    def test_missing_actor_identity_fails_closed(self) -> None:
        for field in ("tenant_id", "client_id", "subject_id"):
            actor_without_field = dict(self.client_a)
            actor_without_field.pop(field)
            with self.subTest(field=field, state="missing"):
                self.assertEqual(
                    access_decision(actor_without_field, self.record_a),
                    (False, "ACTOR_IDENTITY_INCOMPLETE"),
                )
            actor_with_blank_field = {**self.client_a, field: " "}
            with self.subTest(field=field, state="blank"):
                self.assertEqual(
                    access_decision(actor_with_blank_field, self.record_a),
                    (False, "ACTOR_IDENTITY_INCOMPLETE"),
                )

    def test_missing_record_scope_fails_closed(self) -> None:
        for record in (
            {},
            {"tenant_id": "tenant-a"},
            {"client_id": "client-a"},
            {"tenant_id": "tenant-a", "client_id": " "},
        ):
            with self.subTest(record=record):
                self.assertEqual(
                    access_decision(self.client_a, record),
                    (False, "RECORD_SCOPE_INCOMPLETE"),
                )

    def test_client_cannot_export(self) -> None:
        self.assertEqual(access_decision(self.client_a, self.record_a, "export"), (False, "ACTION_NOT_ASSIGNED"))

    def test_unknown_action_fails_closed(self) -> None:
        self.assertEqual(
            access_decision(self.client_a, self.record_a, "delete"),
            (False, "ACTION_NOT_SUPPORTED"),
        )


if __name__ == "__main__":
    unittest.main()

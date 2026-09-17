from __future__ import annotations

import hashlib
import unittest


class DocumentSnapshotTests(unittest.TestCase):
    def test_exact_snapshot_survives_working_copy_change(self) -> None:
        original = b"deterministic-poc-bytes-v1\n"
        original_digest = hashlib.sha256(original).hexdigest()
        working = bytearray(original)
        submitted = bytes(working)
        submitted_digest = hashlib.sha256(submitted).hexdigest()
        working.extend(b"unsaved-edit\n")
        changed_digest = hashlib.sha256(bytes(working)).hexdigest()
        self.assertEqual(original_digest, submitted_digest)
        self.assertNotEqual(submitted_digest, changed_digest)
        self.assertEqual(hashlib.sha256(submitted).hexdigest(), submitted_digest)

    def test_etag_is_not_a_content_hash(self) -> None:
        etag = "W/\"provider-version-7\""
        content_digest = hashlib.sha256(b"bytes").hexdigest()
        self.assertNotEqual(etag, content_digest)


if __name__ == "__main__":
    unittest.main()

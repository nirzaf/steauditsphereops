from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BuildSpikeTests(unittest.TestCase):
    def test_schema_declares_scope_and_receipt_tables(self) -> None:
        schema = (ROOT / "spikes/p0/schema.sql").read_text(encoding="utf-8")
        for table in ("scope_guard", "poc_package", "command_receipt", "poc_outbox", "checkpoint_reference", "poc_audit_event"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", schema)

    def test_p0_index_has_exact_twelve_ids(self) -> None:
        index = json.loads((ROOT / "docs/production/p0-index.json").read_text(encoding="utf-8"))
        ids = [item["id"] for item in index["experiments"]]
        self.assertEqual(ids, [f"P0-{number:02d}" for number in range(1, 13)])

    def test_mock_build_is_not_live_pass(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/p0/run.py"), "--suite", "build", "--mode", "mock"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"status": "MOCK_PASS"', result.stdout)


if __name__ == "__main__":
    unittest.main()

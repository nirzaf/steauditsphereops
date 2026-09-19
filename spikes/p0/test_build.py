from __future__ import annotations

import importlib.util
import json
import os
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

    def test_runner_suite_registry_matches_p0_index(self) -> None:
        spec = importlib.util.spec_from_file_location("p0_run", ROOT / "scripts/p0/run.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)

        index = json.loads((ROOT / "docs/production/p0-index.json").read_text(encoding="utf-8"))
        expected: dict[str, list[str]] = {}
        for experiment in index["experiments"]:
            expected.setdefault(experiment["suite"], []).append(experiment["id"])
        self.assertEqual(runner.P0_BY_SUITE, expected)
        self.assertEqual(runner.SUITES, set(expected))

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

    def test_live_wbs05_suites_fail_closed_without_authorized_fixture_inputs(self) -> None:
        for suite, experiment in (
            ("identity", "P0-02"),
            ("isolation", "P0-03"),
            ("microsoft", "P0-04"),
            ("documents", "P0-05/P0-09"),
        ):
            with self.subTest(suite=suite):
                env = os.environ.copy()
                env.pop("AUDIT_P0_GRAPH_ACCESS_TOKEN", None)
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/p0/run.py"), "--suite", suite, "--mode", "live"],
                    cwd=ROOT,
                    env=env,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                evidence = json.loads(result.stdout)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertIn(experiment, evidence["outcome"])
                self.assertIn("provider-call:none", evidence["trace"])
                if suite == "documents":
                    observation = evidence["provider_observation"]
                    self.assertEqual(observation["p0_05_status"], "BLOCKED")
                    self.assertEqual(observation["p0_09_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")


if __name__ == "__main__":
    unittest.main()

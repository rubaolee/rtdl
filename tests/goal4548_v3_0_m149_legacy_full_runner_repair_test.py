from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4548_v3_0_m149_legacy_full_runner_repair_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4548_v3_0_m149_legacy_full_runner_repair_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
EMBREE_API = ROOT / "src/native/embree/rtdl_embree_api.cpp"


class Goal4548V30M149LegacyFullRunnerRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4548_m149_legacy_full_runner_repair")
        cls.packet = cls.module.build_packet(ROOT, run_suite=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_repair_checks_pass_without_running_suite(self) -> None:
        self.assertEqual("rtdl.v3_0.legacy_full_runner_repair.goal4548.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_full_runner_passed(self) -> None:
        suite = self.checked_in["suite_run"]
        self.assertTrue(suite["ok"])
        self.assertEqual(41, suite["module_count"])
        self.assertTrue(self.checked_in["suite_summary"]["contains_ran_296"])
        self.assertIn("OK", suite["output"])

    def test_legacy_symbols_are_private_to_goal15_shim(self) -> None:
        api = EMBREE_API.read_text(encoding="utf-8")
        self.assertNotIn("rtdl_embree_run_lsi", api)
        self.assertNotIn("rtdl_embree_run_pip", api)
        self.assertFalse(self.checked_in["claim_boundary"]["native_public_abi_restored"])

    def test_report_and_index_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4548 / V3 M149", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4548 legacy full runner repair", INDEX.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

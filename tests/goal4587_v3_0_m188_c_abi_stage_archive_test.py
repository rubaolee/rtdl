from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4587V30M188CAbiStageArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4587_m188_v3_c_abi_stage_archive")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_stage_archive_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_stage_archive.goal4587.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_archive_builds_extracts_compiles_and_runs(self) -> None:
        smoke = self.checked_in["stage_archive_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["make_result"]["ok"])
        self.assertTrue(smoke["archive_exists"])
        self.assertGreater(smoke["archive_size_bytes"], 0)
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4587 / V3 M188", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4587 C ABI stage archive", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

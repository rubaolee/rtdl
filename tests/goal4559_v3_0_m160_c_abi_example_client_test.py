from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/c_api_aabb2_overlap_client.c"
PACKET = ROOT / "docs/reports/goal4559_v3_0_m160_c_abi_example_client_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4559_v3_0_m160_c_abi_example_client_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4559V30M160CAbiExampleClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4559_m160_v3_c_abi_example_client")
        cls.packet = cls.module.build_packet(ROOT, run_build=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_example_source_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_example_client.goal4559.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_pod_example_run_passed(self) -> None:
        run_result = self.checked_in["run_result"]
        self.assertTrue(run_result["ok"])
        self.assertTrue(run_result["compile_result"]["ok"])
        self.assertTrue(run_result["run_result"]["ok"])
        self.assertIn("hit_count=1", run_result["run_result"]["stdout"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        example = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("RTDL_QUERY_AABB_OVERLAP", example)
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4559 / V3 M160", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4559 C ABI example client", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

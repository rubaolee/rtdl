from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4579_v3_0_m180_c_abi_direct_link_example_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4579_v3_0_m180_c_abi_direct_link_example_2026-06-17.md"
EXAMPLE = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/c_api_direct_link_client.c"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4579V30M180CAbiDirectLinkExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4579_m180_v3_c_abi_direct_link_example")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_direct_link_example_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_direct_link_example.goal4579.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_stage_smoke_compiles_and_runs_example(self) -> None:
        smoke = self.checked_in["direct_link_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])

    def test_example_report_index_and_boundaries_are_wired(self) -> None:
        source = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("rtdl_backend_is_supported", source)
        self.assertIn("rtdl_route_is_supported", source)
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4579 / V3 M180", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4579 C ABI direct-link example", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

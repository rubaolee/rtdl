from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4589V30M190EmbeddabilityShippingReadinessRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4589_m190_v3_embeddability_shipping_readiness_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_shipping_readiness_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_shipping_readiness_refresh.goal4589.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_keeps_archive_ready_and_sdk_blocked(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated_extract_compile_run", matrix["source_tree_stage_archive"])
        self.assertEqual("validated_after_directory_move", matrix["relocatable_pkg_config_stage"])
        self.assertEqual("blocked", matrix["packaged_sdk"])
        self.assertEqual("blocked_until_1_0_gates", matrix["stable_abi"])
        self.assertEqual("blocked", matrix["optix_embree_c_abi_queries"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4589 / V3 M190", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4589 embeddability shipping readiness refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

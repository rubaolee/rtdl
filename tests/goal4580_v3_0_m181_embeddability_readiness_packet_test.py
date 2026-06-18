from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4580_v3_0_m181_embeddability_readiness_packet_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4580_v3_0_m181_embeddability_readiness_packet_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4580V30M181EmbeddabilityReadinessPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4580_m181_v3_embeddability_readiness_packet")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_readiness_packet_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_readiness_packet.goal4580.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_preserves_ready_and_blocked_boundaries(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated_source_tree_stage", matrix["staged_pkg_config"])
        self.assertEqual("validated", matrix["direct_link_example"])
        self.assertEqual("blocked_until_1_0_gates", matrix["stable_abi"])
        self.assertEqual("blocked", matrix["optix_embree_c_abi_queries"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4580 / V3 M181", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4580 embeddability readiness packet", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

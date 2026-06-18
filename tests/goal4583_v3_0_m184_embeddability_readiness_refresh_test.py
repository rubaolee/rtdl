from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4583_v3_0_m184_embeddability_readiness_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4583_v3_0_m184_embeddability_readiness_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4583V30M184EmbeddabilityReadinessRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4583_m184_v3_embeddability_readiness_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_readiness_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_readiness_refresh.goal4583.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_reflects_python_ctypes_progress_and_remaining_blocks(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated_source_tree_stage", matrix["python_ctypes_lifecycle_example"])
        self.assertEqual("validated_source_tree_stage", matrix["python_ctypes_host_aabb2_query_example"])
        self.assertEqual("minimal_ctypes_examples_validated_no_generated_binding", matrix["language_binding_base"])
        self.assertEqual("blocked", matrix["generated_language_bindings"])
        self.assertEqual("blocked_until_1_0_gates", matrix["stable_abi"])
        self.assertEqual("blocked", matrix["optix_embree_c_abi_queries"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4583 / V3 M184", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4583 embeddability readiness refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

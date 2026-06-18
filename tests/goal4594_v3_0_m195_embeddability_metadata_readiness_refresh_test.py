from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4594V30M195EmbeddabilityMetadataReadinessRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4594_m195_v3_embeddability_metadata_readiness_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_metadata_readiness_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_metadata_readiness.goal4594.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_keeps_descriptor_and_execution_separate(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated", matrix["host_external_runtime_metadata"])
        self.assertEqual("validated_metadata_only", matrix["cuda_buffer_descriptor_import_export"])
        self.assertEqual("validated", matrix["python_ctypes_cuda_metadata_bridge"])
        self.assertEqual("rejected_invalid_argument", matrix["cuda_descriptor_host_aabb2_query_route"])
        self.assertEqual("blocked", matrix["device_buffer_query_route"])
        self.assertEqual("blocked", matrix["public_true_zero_copy_claim"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4594 / V3 M195", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4594 embeddability metadata readiness refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

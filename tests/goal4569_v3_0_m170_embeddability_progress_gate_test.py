from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4569_v3_0_m170_embeddability_progress_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4569_v3_0_m170_embeddability_progress_gate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4569V30M170EmbeddabilityProgressGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4569_m170_v3_embeddability_progress_gate")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_progress_gate_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_progress_gate.goal4569.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_keeps_ready_and_blocked_surfaces_separate(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated", matrix["non_python_c_client"])
        self.assertEqual("validated", matrix["negative_and_layout_runtime"])
        self.assertEqual("blocked", matrix["c_abi_device_buffers"])
        self.assertEqual("blocked", matrix["packaged_sdk"])
        self.assertEqual("readiness_contract_only", matrix["dlpack_cuda_array_interface_runtime"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4569 / V3 M170", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4569 embeddability progress gate", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

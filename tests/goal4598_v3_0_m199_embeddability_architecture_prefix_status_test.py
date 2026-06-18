from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4598_v3_0_m199_embeddability_architecture_prefix_status_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4598_v3_0_m199_embeddability_architecture_prefix_status_2026-06-17.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4598V30M199EmbeddabilityArchitecturePrefixStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4598_m199_v3_embeddability_architecture_prefix_status_refresh"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_architecture_prefix_status_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_architecture_prefix_status.goal4598.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_architecture_doc_is_current_at_or_beyond_goal4597(self) -> None:
        text = ARCHITECTURE_DOC.read_text(encoding="utf-8")
        self.assertIn("As of Goal4602", text)
        self.assertIn("make stage-c-api-prefix", text)
        self.assertIn("Prefix-stage Python `ctypes` smoke", text)
        self.assertIn("not a generated package or stable public binding", text)

    def test_status_matrix_keeps_prefix_progress_and_release_blocks_separate(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated", matrix["prefix_layout_stage"])
        self.assertEqual("validated", matrix["prefix_python_ctypes_examples"])
        self.assertEqual("blocked", matrix["generated_language_bindings"])
        self.assertEqual("blocked", matrix["packaged_sdk"])
        self.assertEqual("blocked", matrix["release"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4598 / V3 M199", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4598 embeddability architecture prefix status", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

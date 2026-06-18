from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4549_v3_0_m150_embeddability_strategy_intake_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4549_v3_0_m150_embeddability_strategy_intake_2026-06-17.md"
DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
ROOT_DRAFT = ROOT / "rtdl_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4549V30M150EmbeddabilityStrategyIntakeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4549_m150_v3_embeddability_strategy_intake")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_strategy_intake_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_strategy_intake.goal4549.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doc_is_tracked_design_input_not_root_draft(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertTrue(DOC.exists())
        self.assertFalse(ROOT_DRAFT.exists())
        self.assertIn("not a frozen ABI contract", text)
        self.assertIn("does not by itself authorize", text)
        self.assertIn("DLPack", text)
        self.assertIn("Numba-only", text)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4549 / V3 M150", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4549 embeddability strategy intake", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

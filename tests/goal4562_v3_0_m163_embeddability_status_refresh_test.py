from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / "docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md"
PACKET = ROOT / "docs/reports/goal4562_v3_0_m163_embeddability_status_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4562_v3_0_m163_embeddability_status_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4562V30M163EmbeddabilityStatusRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4562_m163_v3_embeddability_status_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_status_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_status_refresh.goal4562.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_strategy_names_progress_and_boundaries(self) -> None:
        strategy = STRATEGY.read_text(encoding="utf-8")
        self.assertIn("Current Implementation Progress", strategy)
        self.assertIn("host `F32` AABB2 overlap query proof", strategy)
        self.assertIn("Still not authorized", strategy)
        self.assertIn("OptiX/Embree query", strategy)
        self.assertIn("execution through the C ABI", strategy)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4562 / V3 M163", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4562 embeddability status refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

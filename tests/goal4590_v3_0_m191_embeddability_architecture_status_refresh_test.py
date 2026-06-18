from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4590_v3_0_m191_embeddability_architecture_status_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4590_v3_0_m191_embeddability_architecture_status_refresh_2026-06-17.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4590V30M191EmbeddabilityArchitectureStatusRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4590_m191_v3_embeddability_architecture_status_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_architecture_status_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_architecture_status_refresh.goal4590.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_architecture_doc_has_current_progress_and_boundaries(self) -> None:
        doc = ARCHITECTURE_DOC.read_text(encoding="utf-8")
        self.assertIn("As of Goal4602", doc)
        self.assertIn("make package-c-api-stage", doc)
        self.assertIn("make stage-c-api-prefix", doc)
        self.assertIn("Python `ctypes` lifecycle", doc)
        self.assertIn("Prefix-stage Python `ctypes` smoke", doc)
        self.assertIn("Host external-runtime metadata validation", doc)
        self.assertIn("CUDA buffer metadata import/export validation", doc)
        self.assertIn("Python `ctypes` bridge", doc)
        self.assertIn("generated language bindings", doc)
        self.assertIn("minimal binding base", doc)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4590 / V3 M191", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4590 embeddability architecture status refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

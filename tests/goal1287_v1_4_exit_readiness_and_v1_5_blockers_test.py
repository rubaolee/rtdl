from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1287_v1_4_exit_readiness_and_v1_5_blockers_2026-05-05.md"
INVENTORY = ROOT / "docs" / "reports" / "goal1285_v1_4_contract_inventory_export_2026-05-05.json"
GATE = ROOT / "docs" / "reports" / "goal1286_v1_4_contract_inventory_gate_2026-05-05.json"


class Goal1287V14ExitReadinessAndV15BlockersTest(unittest.TestCase):
    def test_report_preserves_local_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not a public release gate", text)
        self.assertIn("not a pod evidence packet", text)
        self.assertIn("not public RTX wording authorization", text)
        self.assertIn("Public wording remains blocked", text)

    def test_report_keeps_backend_scope_and_frozen_policy(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Embree, OptiX", text)
        self.assertIn("Frozen-before-v2.1 backends", text)
        self.assertIn("Vulkan", text)
        self.assertIn("HIPRT", text)
        self.assertIn("Apple RT", text)
        self.assertIn("must not be promoted", text)

    def test_report_lists_required_v1_5_blockers(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Generic native primitive ABI",
            "Reduction implementation",
            "Same-contract backend parity",
            "Fresh NVIDIA performance evidence",
            "Jaccard promotion remains blocked",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_matches_inventory_gate_state(self) -> None:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        gate = json.loads(GATE.read_text(encoding="utf-8"))

        self.assertEqual(inventory["contract_count"], 20)
        self.assertEqual(inventory["active_contract_count"], 8)
        self.assertEqual(inventory["frozen_contract_count"], 12)
        self.assertFalse(inventory["public_wording_authorized"])
        self.assertTrue(gate["valid"])
        self.assertEqual(gate["failure_count"], 0)

    def test_recommended_first_v1_5_slice_is_graph_anyhit_count(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("recommended first slice", text)
        self.assertIn("ANY_HIT", text)
        self.assertIn("COUNT_HITS", text)
        self.assertIn("graph", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3094_v2_7_primitive_discovery_orchestration_closeout_2026-06-03.md"


class Goal3094V27PrimitiveDiscoveryOrchestrationCloseoutTest(unittest.TestCase):
    def test_closeout_maps_all_design_items(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for item in ("D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8"):
            with self.subTest(item=item):
                self.assertIn(item, text)

        self.assertIn("Goal3070", text)
        self.assertIn("Goal3073", text)
        self.assertIn("Goal3077", text)
        self.assertIn("Goal3081", text)
        self.assertIn("Goal3084", text)
        self.assertIn("Goal3087", text)
        self.assertIn("Goal3090", text)
        self.assertIn("Deferred", text)

    def test_current_validation_snapshot_matches_runtime_contracts(self) -> None:
        hierarchy = rt.validate_primitive_hierarchy(require_discovery_metadata=True)
        recipes = rt.validate_composition_recipes()
        planner = rt.validate_primitive_advisory_planner()

        self.assertTrue(hierarchy["valid"], hierarchy)
        self.assertTrue(recipes["valid"], recipes)
        self.assertEqual(planner["status"], "accept")
        self.assertFalse(planner["executes"])
        self.assertFalse(planner["automatic_partner_selection_allowed"])

    def test_closeout_preserves_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        required_phrases = (
            "release readiness",
            "public speedup wording",
            "zero-copy wording",
            "broad RT-core claims",
            "paper-reproduction claims",
            "stable primitive promotion",
            "hidden auto-dispatch",
            "hidden auto partner selection",
            "app-specific native engine logic",
        )

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_closeout_states_planner_is_explain_only(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False", text)
        self.assertIn("PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False", text)
        self.assertIn("explain-only", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3102_v2_7_post_semantic_search_current_closeout_2026-06-03.md"
HISTORICAL_REPORT = ROOT / "docs" / "reports" / "goal3094_v2_7_primitive_discovery_orchestration_closeout_2026-06-03.md"
HISTORICAL_2AI = ROOT / "docs" / "reports" / "goal3096_v2_7_discovery_orchestration_closeout_2ai_consensus_2026-06-03.md"
HISTORICAL_3AI = ROOT / "docs" / "reports" / "goal3098_v2_7_discovery_orchestration_closeout_3ai_consensus_2026-06-03.md"


class Goal3102V27PostSemanticSearchCurrentCloseoutTest(unittest.TestCase):
    def test_current_closeout_marks_all_design_items_done(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for item in ("D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8"):
            with self.subTest(item=item):
                self.assertIn(item, text)

        self.assertIn("D-8 | Optional semantic search", text)
        self.assertIn("Done as preview", text)
        self.assertIn("Goal3099", text)
        self.assertIn("Goal3100", text)
        self.assertIn("Goal3101", text)

    def test_current_runtime_boundaries_match_report(self) -> None:
        semantic = rt.validate_primitive_semantic_search()
        planner = rt.validate_primitive_advisory_planner()
        hierarchy = rt.validate_primitive_hierarchy(require_discovery_metadata=True)
        recipes = rt.validate_composition_recipes()

        self.assertTrue(hierarchy["valid"], hierarchy)
        self.assertTrue(recipes["valid"], recipes)
        self.assertTrue(semantic["valid"], semantic)
        self.assertFalse(semantic["executes"])
        self.assertFalse(semantic["uses_embeddings"])
        self.assertFalse(semantic["automatic_partner_selection_allowed"])
        self.assertEqual(planner["status"], "accept")
        self.assertFalse(planner["executes"])
        self.assertFalse(planner["automatic_partner_selection_allowed"])

    def test_current_closeout_preserves_claim_boundaries(self) -> None:
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
            "ML/embedding-backed semantic search",
            "telemetry-backed ranking",
            "execution-coupled orchestration",
        )

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_historical_closeout_points_to_current_closeout(self) -> None:
        for path in (HISTORICAL_REPORT, HISTORICAL_2AI, HISTORICAL_3AI):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")

                self.assertIn("Postscript", text)
                self.assertIn("goal3102_v2_7_post_semantic_search_current_closeout", text)
                self.assertIn("D-8", text)
                self.assertIn("correctly deferred", text)


if __name__ == "__main__":
    unittest.main()

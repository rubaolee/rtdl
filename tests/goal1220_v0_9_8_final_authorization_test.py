from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1220V098FinalAuthorizationTest(unittest.TestCase):
    def test_final_authorization_record_is_prepared_not_mutating(self) -> None:
        text = (
            ROOT / "docs" / "reports" / "goal1220_v0_9_8_final_authorization_2026-05-01.md"
        ).read_text(encoding="utf-8")
        self.assertIn("AUTHORIZED_FOR_RELEASE_ACTION_AFTER_THIS_GOAL_HAS_2_AI_CONSENSUS", text)
        self.assertIn("does not perform the release action", text)
        self.assertIn("Do not tag, push,\npublish, upload packages, or bump `VERSION`", text)

    def test_final_authorization_preserves_claim_boundaries(self) -> None:
        text = (
            ROOT / "docs" / "reports" / "goal1220_v0_9_8_final_authorization_2026-05-01.md"
        ).read_text(encoding="utf-8")
        self.assertIn("reviewed public RTX wording rows: `11`", text)
        self.assertIn("road_hazard_screening / prepared_native_compact_summary_40k", text)
        self.assertIn("database_analytics` public speedup wording remains `blocked`", text)
        self.assertIn("polygon_set_jaccard` public speedup wording remains `blocked`", text)
        self.assertIn("no broad app-suite, whole-app, or all-OptiX RT-core speedup claim", text)

    def test_tag_preparation_reflects_goal1219_review(self) -> None:
        text = (
            ROOT / "docs" / "release_reports" / "v0_9_8" / "tag_preparation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Goal1219 release package review: accepted by Codex and Gemini", text)
        self.assertIn("Goal1220 final authorization: accepted by Codex and Gemini", text)
        self.assertNotIn("External review of this v0.9.8 release package.", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1950_gemini_final_v2_release_review_2026-05-13.md"
SKELETON = ROOT / "docs" / "reports" / "goal1909_v2_release_packet_skeleton_2026-05-13.md"


class Goal1950GeminiFinalV2ReleaseReviewTest(unittest.TestCase):
    def test_gemini_final_review_is_complete(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer Identity", text)
        self.assertIn("Independence from Codex", text)
        self.assertIn("docs/reports/goal1909_v2_release_packet_skeleton_2026-05-13.md", text)
        self.assertIn("docs/reports/goal1946_all_app_v2_perf_deep_dive_2026-05-13.md", text)
        self.assertIn("docs/reports/goal1947_v2_source_tree_only_policy_consensus_2026-05-13.md", text)
        self.assertIn("docs/reports/goal1948_user_owned_native_continuation_example_2026-05-13.md", text)
        self.assertIn("**Verdict:** `accept-with-boundary`", text)
        self.assertNotIn("(Answer to be inserted here)", text)
        self.assertNotIn("(Verdict to be inserted here)", text)
        self.assertNotIn("To be populated", text)

    def test_release_skeleton_tracks_remaining_claude_consensus_slot(self) -> None:
        text = SKELETON.read_text(encoding="utf-8")

        self.assertIn("Goal1950 Gemini review", text)
        self.assertIn("Claude still required for 3-AI consensus", text)
        self.assertIn("Final v2.0 release consensus", text)


if __name__ == "__main__":
    unittest.main()

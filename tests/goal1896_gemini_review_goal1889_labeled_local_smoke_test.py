from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1896_gemini_review_goal1889_labeled_local_smoke_2026-05-13.md"


class Goal1896GeminiReviewGoal1889LabeledLocalSmokeTest(unittest.TestCase):
    def test_review_accepts_with_boundary_and_blocks_rtx_claims(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini / Antigravity", text)
        self.assertIn("Verdict:** `accept-with-boundary`", text)
        self.assertIn("goal_extension", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("a63c706b7a0488c161d6f8e090de5e441a710f7f", text)
        self.assertIn("GTX 1070", text)
        self.assertIn("RTX 3090 pod timing evidence is still pending", text)
        self.assertIn("rtx_pod_timing_authorized", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("whole_app_speedup_claim_authorized", text)


if __name__ == "__main__":
    unittest.main()

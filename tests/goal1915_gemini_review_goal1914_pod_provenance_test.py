from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1915_gemini_review_goal1914_pod_provenance_2026-05-13.md"


class Goal1915GeminiReviewGoal1914PodProvenanceTest(unittest.TestCase):
    def test_review_accepts_goal1914_with_claim_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini/Antigravity review", text)
        self.assertIn("distinct from Codex", text)
        self.assertIn("**Verdict:** accept", text)
        self.assertIn("RTX GPU provenance", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("whole_app_speedup_claim_authorized", text)
        self.assertIn("broad_rt_core_speedup_claim_authorized", text)
        self.assertIn("still requiring actual pod artifacts and post-pod review", text)


if __name__ == "__main__":
    unittest.main()

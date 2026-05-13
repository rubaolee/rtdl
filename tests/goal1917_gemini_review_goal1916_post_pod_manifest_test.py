from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1917_gemini_review_goal1916_post_pod_manifest_2026-05-13.md"


class Goal1917GeminiReviewGoal1916PostPodManifestTest(unittest.TestCase):
    def test_review_accepts_manifest_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini/Antigravity review", text)
        self.assertIn("distinct from Codex", text)
        self.assertIn("**Verdict:** `accept`", text)
        self.assertIn("missing artifacts", text)
        self.assertIn("RTX", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("review aid", text)


if __name__ == "__main__":
    unittest.main()

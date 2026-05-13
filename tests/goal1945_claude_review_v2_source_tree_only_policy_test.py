from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1945_claude_review_v2_source_tree_only_policy_2026-05-13.md"


class Goal1945ClaudeReviewV2SourceTreeOnlyPolicyTest(unittest.TestCase):
    def test_claude_accepts_source_tree_only_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Claude", text)
        self.assertIn("Anthropic", text)
        self.assertIn("independent of Codex and Gemini", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("source-tree-only", text)
        self.assertIn("package-install support", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("No packaging metadata exists", text)

    def test_claude_conditions_do_not_authorize_release(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Scanner coverage", text)
        self.assertIn("Final consensus file", text)
        self.assertIn("No release authorization", text)
        self.assertIn("authorize v2.0 release", text)
        self.assertIn("blocked-wording list", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1944_gemini_review_v2_source_tree_only_policy_2026-05-13.md"


class Goal1944GeminiReviewV2SourceTreeOnlyPolicyTest(unittest.TestCase):
    def test_gemini_accepts_source_tree_only_with_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini CLI", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("source-tree-only", text)
        self.assertIn("package-install support explicitly out of scope", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("pyproject.toml", text)
        self.assertIn("setup.py", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("does not broaden any other performance claims", text)


if __name__ == "__main__":
    unittest.main()

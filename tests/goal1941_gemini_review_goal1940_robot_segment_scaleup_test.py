from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1941_GEMINI_REVIEW_GOAL1940_ROBOT_SEGMENT_SCALEUP.md"
REVIEW = ROOT / "docs" / "reviews" / "goal1941_gemini_review_goal1940_robot_segment_scaleup_2026-05-13.md"


class Goal1941GeminiReviewGoal1940RobotSegmentScaleupTest(unittest.TestCase):
    def test_handoff_and_review_are_present(self) -> None:
        self.assertTrue(HANDOFF.exists())
        self.assertTrue(REVIEW.exists())

    def test_review_accepts_goal1940_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review, distinct from Codex", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("segment any-hit", text)
        self.assertIn("1,048,576", text)
        self.assertIn("8,388,608", text)
        self.assertIn("v1.8 baseline remains subsecond", text)
        self.assertIn("does not authorize v2.0", text)
        self.assertIn("package-install", text)
        self.assertIn("broad RT-core", text)
        self.assertIn("whole-app", text)
        self.assertIn("arbitrary PyTorch/CuPy", text)

    def test_review_tracks_log_and_json_provenance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("robot_8388608x16384_run.log", text)
        self.assertIn("segment_1048576_run.log", text)
        self.assertIn("primary artifacts for numeric assertions", text)
        self.assertIn("visible-progress provenance", text)
        self.assertNotIn("No `.log` files were found", text)
        self.assertNotIn("were not located", text)


if __name__ == "__main__":
    unittest.main()

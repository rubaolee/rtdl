from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2170_gemini_review_goal2169_optix_lsi_device_filter_2026-05-16.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2169_OPTIX_LSI_DEVICE_FILTER_REVIEW_2026-05-16.md"


class Goal2170GeminiReviewGoal2169OptixLsiDeviceFilterTest(unittest.TestCase):
    def test_review_records_independent_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex authoring", text)
        self.assertIn("does not by itself authorize v2.0 release", text)
        self.assertIn("`accept`", text)

    def test_review_confirms_bounded_device_filter_evidence(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("generic/app-agnostic", text)
        self.assertIn("host exact refinement", text)
        self.assertIn("all_parity_vs_cpu_python_reference: true", text)
        self.assertIn("not a full RayJoin-paper-speedup result", text)
        self.assertIn("No blocking issues", text)

    def test_handoff_named_expected_review_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn(
            "docs/reviews/goal2170_gemini_review_goal2169_optix_lsi_device_filter_2026-05-16.md",
            text,
        )
        self.assertIn("Goal2169", text)


if __name__ == "__main__":
    unittest.main()

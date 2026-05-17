from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_GEMINI_GOAL2175_LARGER_RAYJOIN_OVERLAY_REVIEW_2026-05-16.md"
)
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2176_gemini_review_goal2175_larger_rayjoin_overlay_2026-05-16.md"
)


class Goal2176GeminiReviewGoal2175LargerRayjoinOverlayTest(unittest.TestCase):
    def test_review_accepts_current_shared_reference_artifact(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini Review: Goal2175", text)
        self.assertIn("Gemini Agent", text)
        self.assertIn("`accept`", text)
        self.assertIn("9a4b8ae1ef054406eeda8475a51f24ed3f225459", text)
        self.assertIn("goal2175_overlay_count256_shared_reference_pod_2026-05-16.json", text)
        self.assertNotIn("de6caced016b2631ab21cb20ef69e0b6b760fca0", text)

    def test_review_verifies_numbers_and_narrow_claim(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("2.1851774686947465", text)
        self.assertIn("0.13478228449821472", text)
        self.assertIn("0.07310969196259975", text)
        self.assertIn("0.07800947688519955", text)
        self.assertIn("1.844x", text)
        self.assertIn("1.728x", text)
        self.assertIn("all four backends parity-clean", text)
        self.assertIn("prepared OptiX is not always faster", text)

    def test_review_and_handoff_keep_release_claims_blocked(self) -> None:
        review_text = REVIEW.read_text(encoding="utf-8")
        handoff_text = HANDOFF.read_text(encoding="utf-8")

        for text in (review_text, handoff_text):
            self.assertIn("no full RayJoin paper reproduction", text)
            self.assertIn("no broad RT-core speedup", text)
            self.assertIn("no v2.0 release authorization", text)
            self.assertIn("no whole-app RayJoin speedup", text)
            self.assertIn("stronger CUDA/CuPy spatial-prefilter baselines", text)


if __name__ == "__main__":
    unittest.main()

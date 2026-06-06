from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3591_gemini_review_goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md"


class Goal3591GeminiReviewGoal3589RayJoinCupyBaselineTest(unittest.TestCase):
    def test_review_accepts_with_boundary_and_records_key_values(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        self.assertIn("Goal3591: Gemini Review", text)
        self.assertIn("`accept-with-boundary`", text)
        for phrase in (
            "PIP: RTDL/OptiX speedup vs CuPy: `0.041x`",
            "LSI: RTDL/OptiX speedup vs CuPy: `6.261x`",
            "Overlay: RTDL/OptiX speedup vs CuPy: `0.095x`",
            "public RayJoin RT-core speedup wording",
            "public_speedup_claim_authorized: false",
            "No Measurement-Contract Problems",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

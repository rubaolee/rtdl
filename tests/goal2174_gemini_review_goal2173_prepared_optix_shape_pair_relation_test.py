from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_GEMINI_GOAL2173_PREPARED_OPTIX_SHAPE_PAIR_RELATION_REVIEW_2026-05-16.md"
)
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2174_gemini_review_goal2173_prepared_optix_shape_pair_relation_2026-05-16.md"
)


class Goal2174GeminiReviewPreparedOptixShapePairRelationTest(unittest.TestCase):
    def test_review_records_independent_gemini_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2174 Gemini Review", text)
        self.assertIn("Reviewer:** Gemini Agent", text)
        self.assertIn("`accept`", text)
        self.assertIn("generic, app-agnostic", text)
        self.assertIn("rtdl_optix_prepare_shape_pair_relation_flags", text)
        self.assertIn("rtdl_optix_run_prepared_shape_pair_relation_flags", text)
        self.assertIn("rtdl_optix_destroy_prepared_shape_pair_relation_flags", text)

    def test_review_verifies_exact_pod_numbers_and_parity(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("0.021841061301529408", text)
        self.assertIn("0.0248165475204587", text)
        self.assertIn("0.019190984778106213", text)
        self.assertIn("0.009707760997116566", text)
        self.assertIn("14036", text)
        self.assertIn("7ab56c1fe382c58f2500ce7aed98696c065d9323", text)
        self.assertIn("all_parity_vs_cpu_python_reference", text)
        self.assertIn("`true`", text)

    def test_review_keeps_claim_boundary_narrow(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("does not overclaim", text)
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("broad RT-core speedup claims", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("stronger CUDA/CuPy spatial-prefilter baselines", text)

    def test_handoff_requested_conservative_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("This is performance/public-claim-adjacent work", text)
        self.assertIn("be conservative", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("needs-more-evidence", text)


if __name__ == "__main__":
    unittest.main()

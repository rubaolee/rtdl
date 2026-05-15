from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md"
TABLE = ROOT / "docs" / "reports" / "goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json"
GEMINI_DELTA_REVIEW = ROOT / "docs" / "reviews" / "goal2087_gemini_review_goal2086_extended_streaming_witness_pod_2026-05-15.md"


class Goal2088V2ReleasePrepAfterStreamingWitnessTest(unittest.TestCase):
    def test_release_prep_report_replaces_stale_mixed_witness_row(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("release-prep-candidate", text)
        self.assertIn("Goal2073", text)
        self.assertIn("supersede that stale part", text)
        self.assertIn("streaming exact witness-column", text)
        self.assertIn("remaining mixed rows in the current OptiX/RT table: `[]`", text)
        self.assertIn("not yet a release authorization", text)

    def test_current_optix_table_has_no_ratio_regressions_under_documented_contracts(self) -> None:
        payload = json.loads(TABLE.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_cells_filled"])
        optix_rows = payload["optix_rt_rows"]
        self.assertEqual(16, len(optix_rows))
        self.assertTrue(all(row["v2_over_v1_8_ratio"] < 1.0 for row in optix_rows))
        segment = {row["app"]: row for row in optix_rows}["segment_polygon_anyhit_rows"]
        self.assertIn("streaming_exact_witness_page", segment["scale"])
        self.assertLess(segment["v2_over_v1_8_ratio"], 0.01)

    def test_boundaries_keep_release_and_broad_claims_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Still not allowed", text)
        self.assertIn("v2.0 is released", text)
        self.assertIn("arbitrary PyTorch/CuPy acceleration", text)
        self.assertIn("package-install support", text)
        self.assertIn("old full Python witness-row materialization is fast", text)

    def test_delta_gemini_review_exists_but_final_reviews_are_still_required(self) -> None:
        review = GEMINI_DELTA_REVIEW.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Verdict: accept-with-boundary", review)
        self.assertIn("Get a fresh Claude review", report)
        self.assertIn("Get a fresh Gemini final-release review", report)
        self.assertIn("Write a new final consensus file", report)


if __name__ == "__main__":
    unittest.main()

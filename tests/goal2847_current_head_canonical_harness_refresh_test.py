from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2847_current_head_canonical_harness_pod"
REPORT = ROOT / "docs" / "reports" / "goal2847_current_head_canonical_harness_refresh_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2848_gemini_review_goal2847_current_head_canonical_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2848_goal2847_current_head_canonical_harness_consensus_2026-05-31.md"
EXPECTED_COMMIT = "23b047e5d44bfda7e535ca7ba78d94f195e2be86"
EXPECTED_ARTIFACTS = {
    "goal2797_triangle_counting.json",
    "goal2798_librts.json",
    "goal2799_spatial_rayjoin.json",
    "goal2800_rtnn.json",
    "goal2801_hausdorff_xhd.json",
    "goal2802_rt_dbscan.json",
    "goal2803_barnes_hut.json",
}


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2847CurrentHeadCanonicalHarnessRefreshTest(unittest.TestCase):
    def test_all_expected_artifacts_are_present_and_pass(self) -> None:
        self.assertTrue(ARTIFACT_DIR.exists(), ARTIFACT_DIR)
        self.assertEqual(
            EXPECTED_ARTIFACTS | {"goal2847_summary.json"},
            {path.name for path in ARTIFACT_DIR.glob("*.json")},
        )

        summary = _load("goal2847_summary.json")
        self.assertTrue(summary["all_pass"])
        self.assertEqual("Goal2847", summary["goal"])
        self.assertEqual(EXPECTED_COMMIT, summary["source_commit"])
        self.assertEqual(EXPECTED_ARTIFACTS, set(summary["artifacts"]))

        for name in EXPECTED_ARTIFACTS:
            payload = _load(name)
            self.assertEqual("pass", payload["status"], name)
            self.assertEqual(EXPECTED_COMMIT, payload["source_commit"], name)
            self.assertEqual([], payload["source_dirty"], name)
            self.assertIn("NVIDIA RTX A5000", payload["gpu"], name)

    def test_claim_boundaries_remain_fail_closed(self) -> None:
        false_keys = {
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "paper_reproduction_claim_authorized",
        }
        for name in EXPECTED_ARTIFACTS:
            boundary = _load(name).get("claim_boundary", {})
            for key in false_keys & set(boundary):
                self.assertIs(boundary[key], False, f"{name}:{key}")

        hausdorff = _load("goal2801_hausdorff_xhd.json")
        self.assertTrue(hausdorff["rtdl"]["uses_rt_cores"])
        self.assertGreater(hausdorff["rtdl_over_cupy_grid_elapsed_ratio"], 1.0)
        self.assertFalse(hausdorff["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

        rtnn = _load("goal2800_rtnn.json")
        self.assertFalse(rtnn["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])
        self.assertFalse(rtnn["claim_boundary"]["public_speedup_claim_authorized"])

    def test_current_head_metrics_keep_expected_boundaries(self) -> None:
        rayjoin = _load("goal2799_spatial_rayjoin.json")
        self.assertEqual(3, rayjoin["row_count"])
        self.assertTrue(all(row["matches_cpu_reference"] for row in rayjoin["rows"]))
        self.assertTrue(all(row["uses_prepared_optix_rt_backend"] for row in rayjoin["rows"]))

        rtnn = _load("goal2800_rtnn.json")
        ratios = {row["distribution"]: row["cupy_grid_over_rtdl_elapsed_ratio"] for row in rtnn["rows"]}
        self.assertLess(ratios["uniform"], 1.0)
        self.assertGreater(ratios["clustered"], 2.0)
        self.assertGreater(ratios["shell"], 2.0)

        dbscan = _load("goal2802_rt_dbscan.json")
        self.assertGreater(dbscan["min_grouped_stream_speedup_vs_prepared_cupy_grid"], 3.0)
        self.assertTrue(dbscan["grouped_stream_rt_core_accelerated"])

        barnes_hut = _load("goal2803_barnes_hut.json")
        self.assertGreater(barnes_hut["max_optix_membership_speedup_vs_embree"], 100.0)
        self.assertGreater(barnes_hut["vector_sum"]["triton_over_torch_ratio"], 1.0)
        self.assertFalse(barnes_hut["triton_vector_sum_auto_selection_allowed"])

    def test_report_records_current_head_verdict_and_debt(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        required = [
            "Goal2847",
            EXPECTED_COMMIT,
            "accept-with-boundary",
            "seven canonical v2.5 harnesses",
            "source_dirty: []",
            "not a v2.5 release authorization",
            "Hausdorff remains slower",
            "RTNN remains distribution-dependent",
            "Barnes-Hut needs better progress logging",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_external_review_and_consensus_record_the_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in [
            "independent Gemini review",
            "accept-with-boundary",
            EXPECTED_COMMIT,
            "source_dirty: []",
            "no stale public-speedup or release-authorization claims",
        ]:
            self.assertIn(phrase, review)

        for phrase in [
            "Consensus verdict: **accept-with-boundary**",
            "Codex",
            "Gemini",
            "not a v2.5 release authorization",
            "must not be used alone as release consensus",
        ]:
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()

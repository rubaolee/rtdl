from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2813_rtnn_unsorted_topk_summary_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2813_rtnn_unsorted_topk_summary_pod"
ARTIFACT_32768 = ARTIFACT_DIR / "rtnn_unsorted_topk_median_f32_32768.json"
ARTIFACT_65536 = ARTIFACT_DIR / "rtnn_unsorted_topk_median_f32_65536.json"
GOAL2812_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2812_rtnn_prepared_query_aggregate_pod"
GOAL2812_32768 = GOAL2812_ARTIFACT_DIR / "rtnn_prepared_query_median_f32_32768.json"
GOAL2812_65536 = GOAL2812_ARTIFACT_DIR / "rtnn_prepared_query_median_f32_65536.json"
EXPECTED_COMMIT = "73270996cdeaff24cc7f90c7773818cccec73a8b"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2813RtnnUnsortedTopKSummaryTest(unittest.TestCase):
    def test_summary_only_f32_paths_use_unsorted_bounded_topk(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("frn_ranked_insert_unsorted_f32", core)
        self.assertIn("frn_ranked_f32_less", core)
        self.assertIn("frn_ranked_f32_worse", core)
        self.assertIn("worst_distance_sq", core)
        self.assertIn("nearest_index", core)
        self.assertIn("kth_index", core)

        summary_start = core.index("fixed_radius_neighbors_3d_grid_ranked_summary_f32")
        direct_start = core.index("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct")
        aggregate_start = core.index("fixed_radius_neighbors_3d_grid_compact", direct_start)
        summary_body = core[summary_start:direct_start]
        direct_body = core[direct_start:aggregate_start]

        self.assertIn("frn_ranked_insert_unsorted_f32", summary_body)
        self.assertIn("frn_ranked_insert_unsorted_f32", direct_body)
        self.assertNotIn("frn_ranked_insert_f32(d2", summary_body)
        self.assertNotIn("frn_ranked_insert_f32(d2", direct_body)
        self.assertNotIn("rtnn", core.lower())

    def test_clean_pod_artifacts_record_controlled_same_contract_wins(self) -> None:
        wins = 0
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = _load(artifact)
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertIn("prepared_query_aggregate_float32_median", payload["harness_version"])
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])
                for row in payload["rows"]:
                    phase = row["rtdl_phase_summary"]
                    self.assertEqual(row["status"], "pass")
                    self.assertEqual(row["contract"]["mode"], "ranked-summary-aggregate-prepared-query-float32")
                    self.assertEqual(row["rtdl_elapsed_statistic"], "median")
                    self.assertEqual(row["cupy_grid_elapsed_statistic"], "median")
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    self.assertEqual(float(phase["upload_sec"]), 0.0)
                    self.assertTrue(all(mode.startswith("prepared_query_uniform_cell") for mode in phase["modes"]))
                    if float(row["cupy_grid_over_rtdl_elapsed_ratio"]) > 1.0:
                        wins += 1
        self.assertGreaterEqual(wins, 4)

    def test_unsorted_summary_path_improves_over_goal2812_for_dense_and_shell_rows(self) -> None:
        previous_by_key = {}
        for artifact in (GOAL2812_32768, GOAL2812_65536):
            payload = _load(artifact)
            for row in payload["rows"]:
                previous_by_key[(payload["point_count"], row["distribution"])] = float(row["rtdl_elapsed_sec"])

        improvements = {}
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = _load(artifact)
            for row in payload["rows"]:
                key = (payload["point_count"], row["distribution"])
                improvements[key] = previous_by_key[key] / float(row["rtdl_elapsed_sec"])

        self.assertGreater(improvements[(32768, "clustered")], 3.0)
        self.assertGreater(improvements[(32768, "shell")], 2.0)
        self.assertGreater(improvements[(65536, "uniform")], 2.0)
        self.assertGreater(improvements[(65536, "clustered")], 3.0)
        self.assertGreater(improvements[(65536, "shell")], 7.0)

    def test_report_keeps_external_review_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("unsorted bounded top-k", report)
        self.assertIn("summary-only", report)
        self.assertIn("RTDL is faster than the CuPy grid opponent in 4 of 6 rows", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized before external review", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)


if __name__ == "__main__":
    unittest.main()

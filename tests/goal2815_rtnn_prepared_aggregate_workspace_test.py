from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2815_rtnn_prepared_aggregate_workspace_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2815_rtnn_prepared_aggregate_workspace_pod"
OLD_32768 = ARTIFACT_DIR / "rtnn_workspace_baseline_median_f32_32768.json"
OLD_65536 = ARTIFACT_DIR / "rtnn_workspace_baseline_median_f32_65536.json"
NEW_32768 = ARTIFACT_DIR / "rtnn_workspace_median_f32_32768.json"
NEW_65536 = ARTIFACT_DIR / "rtnn_workspace_median_f32_65536.json"
OLD_COMMIT = "8dacc429105d33f1e08bb43fef4c843d266bba75"
NEW_COMMIT = "95218cf43094ee3fdc2826c4f5ea07cb175bbeb4"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2815RtnnPreparedAggregateWorkspaceTest(unittest.TestCase):
    def test_prepared_fixed_radius_handle_owns_reusable_aggregate_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("std::unique_ptr<DevPtr> d_ranked_aggregate", workloads)
        self.assertIn(
            "d_ranked_aggregate = std::make_unique<DevPtr>(sizeof(RtdlFixedRadiusRankedNeighborAggregate))",
            workloads,
        )

        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        prepared_query_body = workloads[start:end]

        self.assertIn("prepared->d_ranked_aggregate->ptr", prepared_query_body)
        self.assertIn("CUdeviceptr d_aggregate", prepared_query_body)
        self.assertIn("cuMemsetD8(d_aggregate", prepared_query_body)
        self.assertNotIn("DevPtr d_aggregate", prepared_query_body)
        self.assertNotIn("rtnn", prepared_query_body.lower())

    def test_non_resident_query_aggregate_path_uses_same_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        start = workloads.index("aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix", start)
        aggregate_body = workloads[start:end]

        self.assertIn("prepared->d_ranked_aggregate->ptr", aggregate_body)
        self.assertIn("CUdeviceptr d_aggregate", aggregate_body)
        self.assertIn("cuMemsetD8(d_aggregate", aggregate_body)
        self.assertNotIn("DevPtr d_aggregate", aggregate_body)
        self.assertNotIn("rtnn", aggregate_body.lower())

    def test_ab_artifacts_show_bounded_small_row_improvement(self) -> None:
        old_by_key = {}
        for artifact in (OLD_32768, OLD_65536):
            payload = _load(artifact)
            self.assertEqual(payload["source_commit"], OLD_COMMIT)
            self.assertEqual(payload["source_dirty"], [])
            for row in payload["rows"]:
                old_by_key[(payload["point_count"], row["distribution"])] = float(row["rtdl_elapsed_sec"])

        improvements = {}
        wins = 0
        for artifact in (NEW_32768, NEW_65536):
            payload = _load(artifact)
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], NEW_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
                for row in payload["rows"]:
                    self.assertEqual(row["rtdl_elapsed_statistic"], "median")
                    self.assertEqual(row["cupy_grid_elapsed_statistic"], "median")
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    self.assertEqual(float(row["rtdl_phase_summary"]["upload_sec"]), 0.0)
                    key = (payload["point_count"], row["distribution"])
                    improvements[key] = old_by_key[key] / float(row["rtdl_elapsed_sec"])
                    if float(row["cupy_grid_over_rtdl_elapsed_ratio"]) > 1.0:
                        wins += 1

        self.assertGreater(improvements[(32768, "uniform")], 1.1)
        self.assertGreater(improvements[(65536, "uniform")], 1.1)
        self.assertGreater(improvements[(65536, "clustered")], 1.1)
        self.assertGreaterEqual(wins, 4)

    def test_report_keeps_boundary_and_names_remaining_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("reusable prepared-handle aggregate workspace", report)
        self.assertIn("32K and 65K uniform rows still do not beat CuPy", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized before external review", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2817_rtnn_block_partial_aggregate_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2817_rtnn_block_partial_aggregate_pod"
ARTIFACT_32768 = ARTIFACT_DIR / "rtnn_block_partial_median_f32_32768.json"
ARTIFACT_65536 = ARTIFACT_DIR / "rtnn_block_partial_median_f32_65536.json"
GOAL2815_DIR = ROOT / "docs" / "reports" / "goal2815_rtnn_prepared_aggregate_workspace_pod"
GOAL2815_32768 = GOAL2815_DIR / "rtnn_workspace_median_f32_32768.json"
GOAL2815_65536 = GOAL2815_DIR / "rtnn_workspace_median_f32_65536.json"
EXPECTED_COMMIT = "578cfe947037fff476c81b84a11e36ac6ac8fe45"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2817RtnnBlockPartialAggregateTest(unittest.TestCase):
    def test_block_partial_kernel_is_generic_summary_path(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks", core)
        self.assertIn("FrnRankedAggregate* partials_out", core)
        self.assertIn("partials_out[blockIdx.x].query_count", core)
        self.assertNotIn("rtnn", core.lower())

    def test_prepared_query_handle_owns_partial_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("size_t aggregate_block_count", workloads)
        self.assertIn("std::unique_ptr<DevPtr> d_aggregate_partials", workloads)
        self.assertIn("aggregate_block_count = (count + 255u) / 256u", workloads)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks", workloads)
        self.assertIn("use_block_partial_direct", workloads)
        self.assertIn("prepared_queries->query_count <= 65536u", workloads)

    def test_python_phase_label_names_block_partial_mode(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn(
            '15: "prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials"',
            runtime,
        )

    def test_pod_artifacts_show_65k_uniform_crossing_and_preserve_correctness(self) -> None:
        wins = 0
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = _load(artifact)
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
                for row in payload["rows"]:
                    self.assertEqual(row["rtdl_elapsed_statistic"], "median")
                    self.assertEqual(row["cupy_grid_elapsed_statistic"], "median")
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    if row["distribution"] in {"uniform", "shell"}:
                        self.assertIn("block_partials", row["rtdl_phase_summary"]["modes"][0])
                    if float(row["cupy_grid_over_rtdl_elapsed_ratio"]) > 1.0:
                        wins += 1
        self.assertGreaterEqual(wins, 5)

    def test_block_partial_path_improves_uniform_rows_over_goal2815(self) -> None:
        previous = {}
        for artifact in (GOAL2815_32768, GOAL2815_65536):
            payload = _load(artifact)
            for row in payload["rows"]:
                previous[(payload["point_count"], row["distribution"])] = float(row["rtdl_elapsed_sec"])

        current = {}
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = _load(artifact)
            for row in payload["rows"]:
                current[(payload["point_count"], row["distribution"])] = float(row["rtdl_elapsed_sec"])

        self.assertGreater(previous[(32768, "uniform")] / current[(32768, "uniform")], 1.1)
        self.assertGreater(previous[(65536, "uniform")] / current[(65536, "uniform")], 1.1)
        self.assertLess(current[(65536, "uniform")], _load(ARTIFACT_65536)["rows"][0]["cupy_grid_elapsed_sec"])

    def test_report_keeps_boundary_and_names_remaining_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("block-partial", report)
        self.assertIn("65K uniform improves by about 1.12x and crosses parity", report)
        self.assertIn("32K uniform improves by about 1.15x but still trails CuPy", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized before external review", report)


if __name__ == "__main__":
    unittest.main()

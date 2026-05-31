from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2810_rtnn_ranked_summary_aggregate_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2810_rtnn_ranked_summary_aggregate_pod"
ARTIFACT_32768 = ARTIFACT_DIR / "rtnn_aggregate_f32_32768.json"
ARTIFACT_65536 = ARTIFACT_DIR / "rtnn_aggregate_f32_65536.json"
OLD_32768 = ROOT / "docs" / "reports" / "goal2808_current_head_canonical_harness_pod" / "goal2800_rtnn.json"
OLD_65536 = ROOT / "docs" / "reports" / "goal2800_pod_artifacts" / "rtnn_v25_live_ranked_summary_65536_clean_from_git.json"
EXPECTED_COMMIT = "734488a92f7a2a8e9c3fa18598c621558f6a1630"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2810RtnnRankedSummaryAggregateTest(unittest.TestCase):
    def test_native_and_python_surfaces_are_generic_aggregate_paths(self) -> None:
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        runner = (ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py").read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate", core)
        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_f32", core)
        self.assertIn("rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d", api)
        self.assertIn("rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d_f32", api)
        self.assertIn("def aggregate_ranked_summary(", runtime)
        self.assertIn("precision: str = \"float64\"", runtime)
        self.assertIn("ranked-summary-aggregate-float32", runner)
        self.assertNotIn("rtnn_aggregate", core.lower())

    def test_clean_pod_artifacts_pass_and_keep_claims_closed(self) -> None:
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = _load(artifact)
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertIn("NVIDIA RTX A5000", payload["gpu"])
                for row in payload["rows"]:
                    self.assertEqual(row["status"], "pass")
                    self.assertEqual(row["contract"]["mode"], "ranked-summary-aggregate-float32")
                    self.assertEqual(row["contract"]["precision"], "float32")
                    self.assertFalse(row["contract"]["exact"])
                    self.assertTrue(row["candidate_count_within_tolerance"])
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    self.assertIsNotNone(row["rtdl_ranked_aggregate_summary"])
                    self.assertIn("prepared_uniform_cell_ranked_summary_aggregate_f32", row["rtdl_phase_summary"]["modes"])
                for key, value in payload["claim_boundary"].items():
                    if "claim_authorized" in key:
                        self.assertFalse(value)
                self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_goal2810_improves_rtdl_path_without_claiming_cupy_win(self) -> None:
        old_32768 = _load(OLD_32768)
        new_32768 = _load(ARTIFACT_32768)
        old_65536 = _load(OLD_65536)
        new_65536 = _load(ARTIFACT_65536)

        for old_payload, new_payload, minimum in (
            (old_32768, new_32768, 1.7),
            (old_65536, new_65536, 1.4),
        ):
            for old_row, new_row in zip(old_payload["rows"], new_payload["rows"]):
                with self.subTest(point_count=new_payload["point_count"], distribution=new_row["distribution"]):
                    improvement = float(old_row["rtdl_elapsed_sec"]) / float(new_row["rtdl_elapsed_sec"])
                    self.assertGreater(improvement, minimum)
                    self.assertLess(float(new_row["cupy_grid_over_rtdl_elapsed_ratio"]), 1.0)

    def test_report_records_boundary_and_remaining_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("device-side aggregate", report)
        self.assertIn("No RTDL-beats-CuPy claim is authorized", report)
        self.assertIn("precision=\"float32\"", report)
        self.assertIn("generic tiled/cooperative top-k reducer", report)


if __name__ == "__main__":
    unittest.main()

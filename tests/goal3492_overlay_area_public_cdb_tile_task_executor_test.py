from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3492_overlay_area_public_cdb_tile_task_executor_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3492_overlay_area_public_cdb_tile_task_executor_pod_2026-06-05.json"


class Goal3492OverlayAreaPublicCdbTileTaskExecutorTest(unittest.TestCase):
    def test_script_documents_public_cdb_tile_task_pipeline(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "prepare_rayjoin_optix_shape_pair_active_count",
            "active_relation_device_columns",
            "plan_prepared_overlay_area_tile_tasks",
            "evaluate_prepared_overlay_area_tile_tasks_cupy",
            "max_triangle_pairs_per_task",
            "cupy_tile_task_executor",
            "largest_error_rows",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_keeps_claim_boundary_and_progress_contract(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "public-CDB active relation stream",
            "Shapely/GEOS oracle",
            "max_triangle_pairs_per_task",
            "phase progress",
            "NVIDIA RTX A5000",
            "9,653,005",
            "0.48830951377749443",
            "not a release authorization",
            "public speedup",
            "not the final native runtime path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_public_cdb_tile_task_result(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3492.overlay_area_public_cdb_tile_task_executor.v1")
        self.assertTrue(data["rtdl_commit"].startswith("2bdf1064"))
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertIn("NVIDIA RTX A5000", data["gpu"])
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["supported_relation_row_count"], 4539)
        self.assertEqual(data["unsupported_relation_row_count"], 4)
        self.assertEqual(data["component_pair_row_count"], 39947)
        self.assertEqual(data["tile_task_count"], 54232)
        self.assertEqual(data["planned_triangle_pair_count"], 9653005)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 9653005)
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 54232})
        self.assertAlmostEqual(data["observed_total_area"], 26.083217672086707)
        self.assertAlmostEqual(data["exact_total_area"], 26.08321766231046)
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        self.assertEqual(data["observed_positive_row_count"], 1086)
        self.assertEqual(data["exact_positive_row_count"], 1086)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor"], 1.0)
        self.assertGreater(data["timing_sec"]["payload_build"], 10.0)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_goal3492_as_public_cdb_run(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3492", spatial["evidence_refs"])
        self.assertIn("Goal3492 executed the public-CDB full-stream tile-task executor", spatial["current_bottleneck"])
        self.assertIn("payload construction", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()

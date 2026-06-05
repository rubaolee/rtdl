from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3492_overlay_area_public_cdb_tile_task_executor_2026-06-05.md"


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
            "not a release authorization",
            "public speedup",
            "not the final native runtime path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_spatial_rayjoin_gap_row_records_goal3492_as_public_cdb_run(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3492", spatial["evidence_refs"])
        self.assertIn("public-CDB full-stream tile-task executor", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()

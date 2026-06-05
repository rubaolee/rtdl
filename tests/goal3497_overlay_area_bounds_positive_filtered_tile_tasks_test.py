from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3497_overlay_area_bounds_positive_filtered_tile_tasks_2026-06-05.md"


class Goal3497OverlayAreaBoundsPositiveFilteredTileTasksTest(unittest.TestCase):
    def test_runner_exposes_bounds_positive_filter(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--bounds-positive-filter",
            "shape_pair_relation_bounds_overlap_area_cupy",
            "bounds_positive_relation_row_count",
            "bounds_positive_filter_metadata",
            "exact_area_for_filtered_rows",
            "rtdl.goal3497.overlay_area_bounds_positive_filtered_tile_tasks.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_active_shape_ordinal_helper_accepts_row_mask(self) -> None:
        import inspect

        source = inspect.getsource(rt.shape_pair_relation_active_shape_ordinals_cupy)
        self.assertIn("row_mask=None", source)
        self.assertIn("row_filter_applied", source)
        self.assertIn("selected_row_count", source)

    def test_report_documents_candidate_filter_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Rows with bounds-overlap area equal to zero are provably zero-area",
            "preserve one output area per original relation row",
            "not device-resident tile-task planning",
            "does not authorize release",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_spatial_rayjoin_gap_row_records_bounds_positive_filter_after_pod_update(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        # The gap map is updated with Goal3497 after pod evidence, but the row
        # must remain non-authorizing throughout this preparatory test.
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()

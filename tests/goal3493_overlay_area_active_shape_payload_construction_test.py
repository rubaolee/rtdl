from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3493_overlay_area_active_shape_payload_construction_2026-06-05.md"


class Goal3493OverlayAreaActiveShapePayloadConstructionTest(unittest.TestCase):
    def test_runner_exposes_active_shape_only_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--active-shapes-only",
            "active_shapes_only",
            "prepared_left_shape_count",
            "prepared_right_shape_count",
            "_build_oracle_geometry_map",
            "_prepare_payload_from_geometry_map",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_explains_payload_construction_bottleneck(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "payload construction/triangulation",
            "1,261",
            "15,700",
            "first discover active relation ordinals",
            "same component-pair rows",
            "does not authorize release",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_spatial_rayjoin_gap_row_records_active_shape_payload_work(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3493", spatial["evidence_refs"])
        self.assertIn("active-shape-only payload construction", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3493_overlay_area_active_shape_payload_construction_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3493_overlay_area_active_shape_payload_construction_pod_2026-06-05.json"


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
            "7.8638s",
            "0.2811s",
            "does not authorize release",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_active_shape_improvement(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3493.overlay_area_active_shape_payload_construction.v1")
        self.assertEqual(data["goal"], 3493)
        self.assertTrue(data["active_shapes_only"])
        self.assertTrue(data["rtdl_commit"].startswith("6193a493"))
        self.assertEqual(data["prepared_left_shape_count"], 1261)
        self.assertEqual(data["left_shape_count"], 15700)
        self.assertLess(data["prepared_left_shape_count"], data["left_shape_count"])
        self.assertEqual(data["prepared_right_shape_count"], 949)
        self.assertEqual(data["left_payload_triangle_count"], 46297)
        self.assertEqual(data["right_payload_triangle_count"], 32087)
        self.assertEqual(data["planned_triangle_pair_count"], 9653005)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 9653005)
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 54232})
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        self.assertLess(data["timing_sec"]["payload_build"], 9.5)
        self.assertLess(data["timing_sec"]["geometry_build"], 1.5)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor"], 0.5)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_active_shape_payload_work(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3493", spatial["evidence_refs"])
        self.assertIn("active-shape-only payload construction", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3502_overlay_area_single_triangulation_payload_construction_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3502_overlay_area_single_triangulation_payload_construction_pod_2026-06-05.json"


class Goal3502OverlayAreaSingleTriangulationPayloadConstructionTest(unittest.TestCase):
    def test_pretriangulated_payload_matches_regular_payload(self) -> None:
        components = (
            ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)),
            ((5.0, 5.0), (7.0, 5.0), (7.0, 7.0), (5.0, 7.0)),
        )
        regular = rt.prepare_simple_polygon_component_payload(components, source_shape_ids=(10, 11))
        triangles = tuple(triangulate_simple_polygon_ear_clip(component) for component in components)
        bounds = tuple(
            (
                min(point[0] for point in component),
                min(point[1] for point in component),
                max(point[0] for point in component),
                max(point[1] for point in component),
            )
            for component in components
        )

        prepared = rt.prepare_simple_polygon_component_payload_from_triangles(
            triangles,
            source_shape_ids=(10, 11),
            component_vertex_counts=tuple(len(component) for component in components),
            component_bounds=bounds,
        )

        self.assertEqual(prepared.triangles, regular.triangles)
        self.assertEqual(
            tuple(record.to_metadata() for record in prepared.components),
            tuple(record.to_metadata() for record in regular.components),
        )

    def test_pretriangulated_payload_does_not_call_ear_clip_again(self) -> None:
        triangles = (
            (
                ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0)),
                ((0.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
            ),
        )

        with mock.patch(
            "rtdsl.v2_8_overlay_area_prepared_payload.triangulate_simple_polygon_ear_clip",
            side_effect=AssertionError("constructor must not triangulate pretriangulated input"),
        ):
            prepared = rt.prepare_simple_polygon_component_payload_from_triangles(
                triangles,
                source_shape_ids=(3,),
                component_vertex_counts=(4,),
                component_bounds=((0.0, 0.0, 2.0, 2.0),),
            )

        self.assertEqual(prepared.triangle_count, 2)
        self.assertEqual(prepared.components[0].source_shape_id, 3)
        self.assertEqual(prepared.components[0].input_vertex_count, 4)
        self.assertEqual(prepared.components[0].to_metadata()["bounds"], (0.0, 0.0, 2.0, 2.0))

    def test_runner_uses_single_triangulation_payload_path(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("_component_payload_parts_for_prepared_geometry", text)
        self.assertIn("prepare_simple_polygon_component_payload_from_triangles", text)
        self.assertIn("--single-triangulation-payload-evidence", text)
        self.assertIn("rtdl.goal3502.overlay_area_single_triangulation_payload_construction.v1", text)
        self.assertNotIn("component_vertices_for_prepared_geometry", text)

    def test_report_documents_single_triangulation_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "removes duplicated CPU triangulation",
            "6.887s -> 3.951s",
            "about 1.74x",
            "does not construct polygon payloads",
            "native code",
            "does not authorize public speedup or release wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_payload_construction_improvement(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3502.overlay_area_single_triangulation_payload_construction.v1")
        self.assertEqual(data["goal"], 3502)
        self.assertTrue(data["rtdl_commit"].startswith("314f3eec"))
        self.assertTrue(data["single_triangulation_payload_construction"])
        self.assertTrue(data["single_triangulation_payload_evidence"])
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["supported_relation_row_count"], 2149)
        self.assertEqual(data["component_pair_row_count"], 4524)
        self.assertEqual(data["tile_task_count"], 11617)
        self.assertEqual(data["planned_triangle_pair_count"], 4070240)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 4070240)
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        self.assertLess(data["timing_sec"]["payload_build"], 4.1)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.02)
        self.assertLess(data["timing_sec"]["device_tile_task_planning_best_repeat"], 0.05)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"


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


if __name__ == "__main__":
    unittest.main()

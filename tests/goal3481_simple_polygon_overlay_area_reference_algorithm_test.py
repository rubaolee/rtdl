from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.simple_polygon_overlay_area_reference import convex_polygon_overlap_area
from rtdsl.simple_polygon_overlay_area_reference import simple_polygon_overlap_area_by_triangulation
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "rtdsl" / "simple_polygon_overlay_area_reference.py"
REPORT = ROOT / "docs" / "reports" / "goal3481_simple_polygon_overlay_area_reference_algorithm_2026-06-05.md"


class Goal3481SimplePolygonOverlayAreaReferenceAlgorithmTest(unittest.TestCase):
    def test_convex_triangle_clip_matches_square_overlap(self) -> None:
        left = ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))
        right = ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0))

        self.assertAlmostEqual(convex_polygon_overlap_area(left, right), 1.0, places=12)

    def test_ear_clip_triangulates_concave_l_shape(self) -> None:
        l_shape = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        triangles = triangulate_simple_polygon_ear_clip(l_shape)

        self.assertEqual(len(triangles), 4)

    def test_triangulated_overlap_matches_known_concave_case(self) -> None:
        l_shape = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))

        result = simple_polygon_overlap_area_by_triangulation(l_shape, square)

        self.assertAlmostEqual(result.area, 1.75, places=12)
        self.assertEqual(result.left_triangle_count, 4)
        self.assertEqual(result.right_triangle_count, 2)
        self.assertEqual(result.triangle_pair_count, 8)

    def test_triangulated_overlap_handles_containment_disjoint_and_reversed_winding(self) -> None:
        outer = ((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))
        inner = ((1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0))
        disjoint = ((10.0, 10.0), (11.0, 10.0), (11.0, 11.0), (10.0, 11.0))

        self.assertAlmostEqual(simple_polygon_overlap_area_by_triangulation(outer, inner).area, 1.0, places=12)
        self.assertAlmostEqual(simple_polygon_overlap_area_by_triangulation(tuple(reversed(outer)), inner).area, 1.0, places=12)
        self.assertAlmostEqual(simple_polygon_overlap_area_by_triangulation(outer, disjoint).area, 0.0, places=12)

    def test_module_and_report_keep_boundary(self) -> None:
        module_text = MODULE.read_text(encoding="utf-8")
        report_text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "ear_clip_triangulation_plus_triangle_pair_convex_clip",
            "simple polygons only",
            "not the production GPU continuation",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, module_text + report_text)


if __name__ == "__main__":
    unittest.main()

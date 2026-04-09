import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference
from rtdsl.baseline_runner import load_representative_case


class Goal110SegmentPolygonHitcountSemanticsTest(unittest.TestCase):
    def _rows(self, *, segments, polygons):
        return rt.run_cpu_python_reference(
            segment_polygon_hitcount_reference,
            segments=segments,
            polygons=polygons,
        )

    def test_segment_fully_inside_polygon_counts_as_hit(self) -> None:
        rows = self._rows(
            segments=(rt.Segment(id=1, x0=1.0, y0=1.0, x1=2.0, y1=2.0),),
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),),
        )
        self.assertEqual(rows, ({"segment_id": 1, "hit_count": 1},))

    def test_segment_touching_polygon_boundary_counts_as_hit(self) -> None:
        rows = self._rows(
            segments=(rt.Segment(id=1, x0=-1.0, y0=0.0, x1=0.0, y1=0.0),),
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),),
        )
        self.assertEqual(rows, ({"segment_id": 1, "hit_count": 1},))

    def test_segment_crossing_polygon_boundary_counts_as_hit(self) -> None:
        rows = self._rows(
            segments=(rt.Segment(id=1, x0=-1.0, y0=2.0, x1=5.0, y1=2.0),),
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),),
        )
        self.assertEqual(rows, ({"segment_id": 1, "hit_count": 1},))

    def test_segment_with_zero_hits_is_preserved(self) -> None:
        rows = self._rows(
            segments=(rt.Segment(id=1, x0=10.0, y0=10.0, x1=12.0, y1=12.0),),
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),),
        )
        self.assertEqual(rows, ({"segment_id": 1, "hit_count": 0},))

    def test_overlapping_polygons_count_independently(self) -> None:
        rows = self._rows(
            segments=(rt.Segment(id=1, x0=1.0, y0=1.0, x1=3.0, y1=3.0),),
            polygons=(
                rt.Polygon(id=10, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),
                rt.Polygon(id=11, vertices=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0))),
            ),
        )
        self.assertEqual(rows, ({"segment_id": 1, "hit_count": 2},))

    def test_derived_case_loader_produces_four_x_scale(self) -> None:
        case = load_representative_case("segment_polygon_hitcount", "derived/br_county_subset_segment_polygon_tiled_x4")
        fixture = load_representative_case("segment_polygon_hitcount", "tests/fixtures/rayjoin/br_county_subset.cdb")
        self.assertEqual(len(case.inputs["segments"]), 4 * len(fixture.inputs["segments"]))
        self.assertEqual(len(case.inputs["polygons"]), 4 * len(fixture.inputs["polygons"]))


if __name__ == "__main__":
    unittest.main()

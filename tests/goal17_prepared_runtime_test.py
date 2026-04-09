import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference
from goal15_compare_embree import build_lsi_dataset
from goal15_compare_embree import build_pip_dataset
from goal17_compare_prepared_embree import compare_goal17
from tests._embree_support import embree_available


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal17PreparedRuntimeTest(unittest.TestCase):
    def test_prepare_embree_accepts_overlay_after_goal18_extension(self) -> None:
        from examples.reference.rtdl_language_reference import county_soil_overlay_reference

        prepared = rt.prepare_embree(county_soil_overlay_reference)
        self.assertEqual(prepared.predicate_name, "overlay_compose")

    def test_prepared_lsi_matches_current_embree(self) -> None:
        left, right = build_lsi_dataset(build_count=12, probe_count=8, distribution="uniform")
        prepared = rt.prepare_embree(county_zip_join_reference)
        left_packed = rt.pack_segments(records=left)
        right_packed = rt.pack_segments(records=right)

        current_rows = rt.run_embree(county_zip_join_reference, left=left, right=right)
        prepared_rows = prepared.run(left=left_packed, right=right_packed)
        raw_rows = prepared.bind(left=left_packed, right=right_packed).run_raw()
        try:
            raw_dict_rows = raw_rows.to_dict_rows()
        finally:
            raw_rows.close()

        self.assertEqual(current_rows, prepared_rows)
        self.assertEqual(current_rows, raw_dict_rows)

    def test_prepared_pip_matches_current_embree(self) -> None:
        points, polygons = build_pip_dataset(build_count=16, probe_count=10, distribution="uniform")
        prepared = rt.prepare_embree(point_in_counties_reference)
        points_packed = rt.pack_points(records=points)
        polygon_ids = [polygon.id for polygon in polygons]
        offsets = []
        counts = []
        vertices_xy = []
        offset = 0
        for polygon in polygons:
            offsets.append(offset)
            counts.append(len(polygon.vertices))
            for x, y in polygon.vertices:
                vertices_xy.extend((x, y))
            offset += len(polygon.vertices)
        polygons_packed = rt.pack_polygons(
            ids=polygon_ids,
            vertex_offsets=offsets,
            vertex_counts=counts,
            vertices_xy=vertices_xy,
        )

        current_rows = rt.run_embree(point_in_counties_reference, points=points, polygons=polygons)
        prepared_rows = prepared.run(points=points_packed, polygons=polygons_packed)
        raw_rows = prepared.bind(points=points_packed, polygons=polygons_packed).run_raw()
        try:
            raw_dict_rows = raw_rows.to_dict_rows()
        finally:
            raw_rows.close()

        self.assertEqual(current_rows, prepared_rows)
        self.assertEqual(current_rows, raw_dict_rows)

    def test_pack_segments_rejects_mismatched_arrays(self) -> None:
        with self.assertRaisesRegex(ValueError, "identical lengths"):
            rt.pack_segments(ids=[1, 2], x0=[0.0], y0=[0.0, 1.0], x1=[1.0, 2.0], y1=[1.0, 2.0])

    def test_pack_polygons_rejects_invalid_offsets(self) -> None:
        with self.assertRaisesRegex(ValueError, "exceed the provided vertices_xy data"):
            rt.pack_polygons(
                ids=[1],
                vertex_offsets=[1],
                vertex_counts=[4],
                vertices_xy=[0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
            )

    def test_goal17_compare_reports_speedup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = compare_goal17(Path(tmpdir), repeats=5)
        self.assertTrue(payload["workloads"]["lsi"]["prepared_matches_current"])
        self.assertTrue(payload["workloads"]["pip"]["prepared_matches_current"])
        self.assertGreater(payload["workloads"]["lsi"]["speedup_vs_current_raw_hot"], 1.0)
        self.assertGreater(payload["workloads"]["pip"]["speedup_vs_current_raw_hot"], 1.0)


if __name__ == "__main__":
    unittest.main()

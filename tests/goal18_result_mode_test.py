import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from rtdsl.baseline_runner import load_representative_case
from tests._embree_support import embree_available


CASES = (
    ("lsi", county_zip_join_reference, "authored_lsi_minimal"),
    ("pip", point_in_counties_reference, "authored_pip_minimal"),
    ("overlay", county_soil_overlay_reference, "authored_overlay_minimal"),
    ("ray_tri_hitcount", ray_triangle_hitcount_reference, "authored_ray_tri_minimal"),
    ("segment_polygon_hitcount", segment_polygon_hitcount_reference, "authored_segment_polygon_minimal"),
    ("point_nearest_segment", point_nearest_segment_reference, "authored_point_nearest_segment_minimal"),
)


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal18ResultModeTest(unittest.TestCase):
    def test_run_embree_rejects_invalid_result_mode(self) -> None:
        case = load_representative_case("lsi", "authored_lsi_minimal")
        with self.assertRaisesRegex(ValueError, "result_mode"):
            rt.run_embree(county_zip_join_reference, result_mode="bogus", **case.inputs)

    def test_raw_result_mode_matches_dict_rows_for_all_workloads(self) -> None:
        for workload, kernel, dataset in CASES:
            with self.subTest(workload=workload):
                case = load_representative_case(workload, dataset)
                expected = rt.run_embree(kernel, **case.inputs)
                rows = rt.run_embree(kernel, result_mode="raw", **case.inputs)
                try:
                    self.assertIsInstance(rows, rt.EmbreeRowView)
                    self.assertEqual(expected, rows.to_dict_rows())
                    self.assertEqual(len(expected), len(rows))
                finally:
                    rows.close()

    def test_prepared_raw_supports_goal18_extended_workloads(self) -> None:
        for workload, kernel, dataset in CASES[2:]:
            with self.subTest(workload=workload):
                case = load_representative_case(workload, dataset)
                prepared = rt.prepare_embree(kernel)
                rows = prepared.bind(**case.inputs).run_raw()
                try:
                    self.assertEqual(rt.run_embree(kernel, **case.inputs), rows.to_dict_rows())
                finally:
                    rows.close()

    def test_pack_triangles_and_pack_rays_match_reference_path(self) -> None:
        case = load_representative_case("ray_tri_hitcount", "authored_ray_tri_minimal")
        packed_rays = rt.pack_rays(records=case.inputs["rays"])
        packed_triangles = rt.pack_triangles(records=case.inputs["triangles"])

        expected = rt.run_embree(
            ray_triangle_hitcount_reference,
            rays=case.inputs["rays"],
            triangles=case.inputs["triangles"],
        )
        rows = rt.run_embree(
            ray_triangle_hitcount_reference,
            result_mode="raw",
            rays=packed_rays,
            triangles=packed_triangles,
        )
        try:
            self.assertEqual(expected, rows.to_dict_rows())
        finally:
            rows.close()


if __name__ == "__main__":
    unittest.main()

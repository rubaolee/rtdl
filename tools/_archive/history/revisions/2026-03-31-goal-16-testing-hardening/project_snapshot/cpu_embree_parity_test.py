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
from tests._embree_support import embree_available


WORKLOAD_CASES = (
    ("lsi", county_zip_join_reference, "authored_lsi_minimal"),
    ("pip", point_in_counties_reference, "authored_pip_minimal"),
    ("overlay", county_soil_overlay_reference, "authored_overlay_minimal"),
    ("ray_tri_hitcount", ray_triangle_hitcount_reference, "authored_ray_tri_minimal"),
    ("segment_polygon_hitcount", segment_polygon_hitcount_reference, "authored_segment_polygon_minimal"),
    ("point_nearest_segment", point_nearest_segment_reference, "authored_point_nearest_segment_minimal"),
)


class CpuEmbreeParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not embree_available():
            raise unittest.SkipTest("Embree is not installed in the current environment")

    def test_authored_cases_match_for_all_workloads(self) -> None:
        for workload, kernel, dataset in WORKLOAD_CASES:
            with self.subTest(workload=workload, dataset=dataset):
                payload = rt.run_baseline_case(kernel, dataset, backend="both")
                self.assertTrue(payload["parity"])
                self.assertTrue(
                    rt.compare_baseline_rows(workload, payload["cpu_rows"], payload["embree_rows"])
                )


if __name__ == "__main__":
    unittest.main()

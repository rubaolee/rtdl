import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference
from tests.rtdl_sorting_test import optix_available


class Goal110BaselineRunnerBackendTest(unittest.TestCase):
    def test_segment_polygon_representative_datasets_include_goal110_derived_case(self) -> None:
        datasets = rt.representative_dataset_names("segment_polygon_hitcount")
        self.assertIn("authored_segment_polygon_minimal", datasets)
        self.assertIn("tests/fixtures/rayjoin/br_county_subset.cdb", datasets)
        self.assertIn("derived/br_county_subset_segment_polygon_tiled_x4", datasets)

    def test_cpu_python_reference_backend_runs_baseline_case(self) -> None:
        payload = rt.run_baseline_case(
            segment_polygon_hitcount_reference,
            "authored_segment_polygon_minimal",
            backend="cpu_python_reference",
        )
        self.assertEqual(payload["workload"], "segment_polygon_hitcount")
        self.assertIn("cpu_python_reference_rows", payload)
        self.assertEqual(payload["cpu_python_reference_rows"][0]["segment_id"], 1)

    @unittest.skipUnless(optix_available(), "OptiX is not available in the current environment")
    def test_optix_backend_runs_baseline_case(self) -> None:
        payload = rt.run_baseline_case(
            segment_polygon_hitcount_reference,
            "authored_segment_polygon_minimal",
            backend="optix",
        )
        self.assertEqual(payload["workload"], "segment_polygon_hitcount")
        self.assertIn("optix_rows", payload)


if __name__ == "__main__":
    unittest.main()

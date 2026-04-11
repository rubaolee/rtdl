import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.baseline_runner as baseline_runner
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_workload_reference import point_nearest_segment_reference


class Goal223VulkanHarnessIntegrationTest(unittest.TestCase):
    def test_baseline_runner_accepts_vulkan_backend_for_fixed_radius_neighbors(self) -> None:
        with mock.patch.object(baseline_runner, "run_vulkan", return_value=({"query_id": 1, "neighbor_id": 2, "distance": 0.5},)):
            with mock.patch.object(
                baseline_runner,
                "run_cpu_python_reference",
                return_value=({"query_id": 1, "neighbor_id": 2, "distance": 0.5},),
            ):
                payload = baseline_runner.run_baseline_case(
                    fixed_radius_neighbors_reference,
                    "authored_fixed_radius_neighbors_minimal",
                    backend="vulkan",
                )
        self.assertIn("vulkan_rows", payload)
        self.assertIn("parity", payload)

    def test_baseline_runner_accepts_vulkan_backend_for_knn_rows(self) -> None:
        with mock.patch.object(
            baseline_runner,
            "run_vulkan",
            return_value=({"query_id": 1, "neighbor_id": 2, "distance": 0.5, "neighbor_rank": 1},),
        ):
            with mock.patch.object(
                baseline_runner,
                "run_cpu_python_reference",
                return_value=({"query_id": 1, "neighbor_id": 2, "distance": 0.5, "neighbor_rank": 1},),
            ):
                payload = baseline_runner.run_baseline_case(
                    knn_rows_reference,
                    "authored_knn_rows_minimal",
                    backend="vulkan",
                )
        self.assertIn("vulkan_rows", payload)
        self.assertIn("parity", payload)

    def test_baseline_runner_rejects_vulkan_backend_for_unsupported_workload(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Vulkan baseline backend is currently implemented only for fixed_radius_neighbors and knn_rows",
        ):
            baseline_runner.run_baseline_case(
                point_nearest_segment_reference,
                "authored_point_nearest_segment_minimal",
                backend="vulkan",
            )

    def test_cli_parser_accepts_vulkan_choice_for_nearest_neighbor_workloads(self) -> None:
        with mock.patch.object(
            baseline_runner,
            "run_baseline_case",
            return_value={"workload": "fixed_radius_neighbors", "dataset": "authored_fixed_radius_neighbors_minimal"},
        ) as patched:
            rc = baseline_runner.main(
                [
                    "fixed_radius_neighbors",
                    "--dataset",
                    "authored_fixed_radius_neighbors_minimal",
                    "--backend",
                    "vulkan",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertEqual(patched.call_args.kwargs["backend"], "vulkan")


if __name__ == "__main__":
    unittest.main()

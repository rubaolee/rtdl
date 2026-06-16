from __future__ import annotations

import unittest

import numpy as np

from examples.current.research_benchmarks.robot_collision import (
    rtdl_robot_collision_benchmark_app as robot,
)
from rtdsl import prepare_grouped_segment_query_3d


class Goal4446V30M50RobotNumpyLoweringTest(unittest.TestCase):
    def test_grouped_segment_query_accepts_numpy_endpoint_arrays(self) -> None:
        starts = np.asarray(
            [
                [0.25, 0.25, 1.0],
                [2.5, 2.5, 1.0],
                [2.5, 0.25, 1.0],
            ],
            dtype=np.float64,
        )
        ends = starts.copy()
        ends[:, 2] = -1.0
        offsets = np.asarray([0, 1, 3], dtype=np.uint32)

        query = prepare_grouped_segment_query_3d(starts, ends, offsets)
        descriptor = query.descriptor()

        self.assertEqual(query.segment_count, 3)
        self.assertEqual(query.group_count, 2)
        self.assertEqual(query.segments[0].id, 0)
        self.assertEqual(query.segments[1].id, 1)
        self.assertAlmostEqual(query.segments[1].x0, 2.5)
        self.assertAlmostEqual(query.segments[1].y0, 2.5)
        self.assertAlmostEqual(query.segments[1].z0, 1.0)
        self.assertAlmostEqual(query.segments[1].z1, -1.0)
        self.assertEqual(query.group_offsets[0], 0)
        self.assertEqual(query.group_offsets[1], 1)
        self.assertEqual(query.group_offsets[2], 3)
        self.assertEqual(descriptor["query_buffer_kind"], "numpy_structured_host_rtdl_segment3d_array")
        self.assertEqual(descriptor["group_offsets_buffer_kind"], "numpy_host_uint32_offsets")
        self.assertEqual(descriptor["copy_boundary"], "python_ctypes_host_buffer")
        self.assertFalse(descriptor["true_zero_copy_authorized"])

    def test_robot_numpy_lowering_can_skip_large_group_metadata_for_summary_probe(self) -> None:
        case = robot.make_robot_collision_case("scaled", pose_count=8, obstacle_count=4, link_count=3)

        contract = robot.build_segment_probe_contract(
            case,
            lowering_mode="numpy_arrays",
            include_group_metadata=False,
        )

        self.assertIsInstance(contract.segment_start_xyz, np.ndarray)
        self.assertIsInstance(contract.segment_end_xyz, np.ndarray)
        self.assertIsInstance(contract.segment_group_offsets, np.ndarray)
        self.assertEqual(contract.segment_start_xyz.shape, (8 * 3 * 9, 3))
        self.assertEqual(contract.segment_end_xyz.shape, (8 * 3 * 9, 3))
        self.assertEqual(len(contract.segment_group_offsets), 8 * 3 + 1)
        self.assertEqual(contract.groups, ())
        self.assertIn("numpy_vectorized", contract.lowering_policy)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import struct
import unittest
from dataclasses import replace
from types import SimpleNamespace

import numpy as np

from experiments.goal5848_strong_baseline.packed_partner_inputs import (
    relation_host_inputs,
    triangle_host_inputs,
)
from experiments.goal5848_strong_baseline.workloads import (
    relation_workload,
    triangle_workload,
)


class Goal5848PackedPartnerInputsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        box_dtype = np.dtype([
            ("lower_x", "f4"),
            ("lower_y", "f4"),
            ("lower_z", "f4"),
            ("upper_x", "f4"),
            ("upper_y", "f4"),
            ("upper_z", "f4"),
            ("item_id", "u4"),
        ], align=True)
        ray_dtype = np.dtype([
            ("origin_x", "f4"),
            ("origin_y", "f4"),
            ("origin_z", "f4"),
            ("direction_x", "f4"),
            ("direction_y", "f4"),
            ("direction_z", "f4"),
        ], align=True)
        cls.baseline = SimpleNamespace(
            np=np,
            BOX_DTYPE=box_dtype,
            RAY_DTYPE=ray_dtype,
        )

    def test_relation_packed_authority_matches_pyoptix_abi(self):
        workload = relation_workload()
        result = relation_host_inputs(self.baseline, workload)
        indexed, sources = result.checked_arrays(self.baseline)
        self.assertTrue(np.array_equal(indexed, sources))
        self.assertFalse(indexed.flags.writeable)
        self.assertEqual(indexed.dtype.itemsize, 28)
        self.assertEqual(indexed[4095]["lower_x"], np.float32(8190.0))
        self.assertEqual(indexed[4095]["upper_x"], np.float32(8191.0))
        self.assertEqual(indexed[4095]["item_id"], np.uint32(4095))
        self.assertEqual(result.receipt()["python_row_assignment_count"], 0)

    def test_relation_mutated_bound_is_rejected(self):
        workload = relation_workload()
        bounds = bytearray(workload.indexed_bounds_f32le)
        bounds[0:4] = struct.pack("<f", 2.0)
        bounds[8:12] = struct.pack("<f", 1.0)
        mutated = replace(workload, indexed_bounds_f32le=bytes(bounds))
        with self.assertRaisesRegex(ValueError, "inverted"):
            relation_host_inputs(self.baseline, mutated)

    def test_triangle_packed_authority_matches_pyoptix_abi(self):
        workload = triangle_workload()
        result = triangle_host_inputs(self.baseline, workload)
        vertices, rays, weights, maximum = result.checked_arrays(
            self.baseline
        )
        self.assertFalse(vertices.flags.writeable)
        self.assertFalse(rays.flags.writeable)
        self.assertFalse(weights.flags.writeable)
        self.assertEqual(vertices.shape, (3 * 16384, 3))
        self.assertEqual(rays.shape, (16384,))
        self.assertEqual(weights.shape, (16384,))
        self.assertEqual(int(weights.sum()), 65530)
        self.assertEqual(maximum, np.float32(2.0))
        self.assertEqual(result.receipt()["python_ray_assignment_count"], 0)

    def test_triangle_mutated_index_and_zero_direction_are_rejected(self):
        workload = triangle_workload()
        indices = bytearray(workload.triangles_u32le)
        indices[0:4] = struct.pack("<I", 1)
        with self.assertRaisesRegex(ValueError, "consecutive"):
            triangle_host_inputs(
                self.baseline,
                replace(workload, triangles_u32le=bytes(indices)),
            )

        rays = bytearray(workload.rays_interleaved_6f_le)
        rays[12:24] = b"\0" * 12
        with self.assertRaisesRegex(ValueError, "nonzero"):
            triangle_host_inputs(
                self.baseline,
                replace(workload, rays_interleaved_6f_le=bytes(rays)),
            )


if __name__ == "__main__":
    unittest.main()

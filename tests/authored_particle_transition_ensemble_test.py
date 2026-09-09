from __future__ import annotations

import unittest

import numpy as np

from scripts.generate_authored_particle_transition_ensemble import (
    _generate_chunk,
    _strict_barycentric_weights,
)
from scripts.goal5776_prepare_particle_mesh import _faces_like_author


class AuthoredParticleTransitionEnsembleTest(unittest.TestCase):
    def test_weights_are_deterministic_strict_and_sum_to_one(self):
        indices = np.arange(10_000, dtype=np.uint64)
        first = _strict_barycentric_weights(indices)
        second = _strict_barycentric_weights(indices)
        np.testing.assert_array_equal(first, second)
        self.assertGreater(float(first.min()), 0.0)
        np.testing.assert_allclose(first.sum(axis=1), 1.0, rtol=0.0, atol=2e-16)

    def test_generated_queries_are_distinct_and_match_topology_oracle(self):
        vertices = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ], dtype=np.float32)
        cells = np.asarray([[0, 1, 2, 3]], dtype=np.uint32)
        triangles, front, back, cell_faces, oriented = _faces_like_author(
            vertices, cells)
        (queries, expected, query_cells, minimum,
         exit_minimum, rejected) = _generate_chunk(
            start=0,
            stop=10_000,
            eligible=np.asarray([0], dtype=np.int64),
            vertices=vertices.astype(np.float64),
            cells=oriented,
            triangles=triangles,
            front=front,
            back=back,
            cell_faces=cell_faces,
            tmax=2.0,
        )
        self.assertGreater(minimum, 0.0)
        self.assertGreater(exit_minimum, 1.0e-3)
        self.assertGreaterEqual(rejected, 0)
        self.assertEqual(np.unique(queries[:, :3], axis=0).shape[0], 10_000)
        np.testing.assert_array_equal(expected[:, 0], query_cells)
        self.assertTrue(np.all(expected[:, 2] < len(triangles)))


if __name__ == "__main__":
    unittest.main()

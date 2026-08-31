from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

from rtdsl.v4_typed_physical_schema import (
    PhysicalSchemaError,
    verify_reference_triangle_contents,
)


class Goal5776RealScaleTriangleColumnsTest(unittest.TestCase):
    def test_vectorized_author_face_orientation_matches_application_fixture(self):
        root = Path(__file__).resolve().parents[1]

        def load(name: str, path: Path):
            spec = importlib.util.spec_from_file_location(name, path)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module

        converter = load(
            "goal5776_prepare_particle_mesh",
            root / "scripts" / "goal5776_prepare_particle_mesh.py",
        )
        app = load(
            "goal5776_particle_v4_app",
            root
            / "Paper-reproduction-apps"
            / "goal5753-held-out-particle-tracking"
            / "v4_whole_app.py",
        )
        data = app.build_v4_input()
        triangles, front, back, _, _ = converter._faces_like_author(
            np.asarray(data["vertices"], dtype=np.float32),
            np.asarray(data["cells"], dtype=np.uint32),
        )
        observed = {
            tuple(map(int, triangle)): (int(front[index]), int(back[index]))
            for index, triangle in enumerate(triangles)
        }
        expected = {
            tuple(sorted(map(int, triangle))): (
                int(data["front_values"][index]),
                int(data["back_values"][index]),
            )
            for index, triangle in enumerate(data["triangles"])
        }
        self.assertEqual(observed, expected)

    def test_contiguous_numpy_columns_apply_every_f32_triangle_check(self):
        vertices = np.asarray(
            ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
            dtype=np.float32,
        )
        triangles = np.asarray(((0, 1, 2), (0, 3, 1)), dtype=np.uint32)
        verify_reference_triangle_contents(vertices, triangles)

        attacked = triangles.copy(); attacked[1] = (0, 1, 1)
        with self.assertRaisesRegex(PhysicalSchemaError, "distinct indices"):
            verify_reference_triangle_contents(vertices, attacked)
        attacked = triangles.copy(); attacked[1, 2] = 99
        with self.assertRaisesRegex(PhysicalSchemaError, "outside vertex domain"):
            verify_reference_triangle_contents(vertices, attacked)
        attacked_vertices = vertices.copy(); attacked_vertices[0, 0] = np.nan
        with self.assertRaisesRegex(PhysicalSchemaError, "must be finite"):
            verify_reference_triangle_contents(attacked_vertices, triangles)

    def test_large_column_path_is_not_sampled(self):
        count = 300_001  # crosses the verifier's bounded-memory chunk size
        base = np.arange(count, dtype=np.float32)
        vertices = np.column_stack((
            np.repeat(base, 3),
            np.tile(np.asarray((0.0, 1.0, 0.0), dtype=np.float32), count),
            np.tile(np.asarray((0.0, 0.0, 1.0), dtype=np.float32), count),
        ))
        triangles = np.arange(count * 3, dtype=np.uint32).reshape(count, 3)
        verify_reference_triangle_contents(vertices, triangles)
        # Corrupt only the final primitive.  A prefix sample would miss it.
        triangles[-1, 2] = triangles[-1, 1]
        with self.assertRaisesRegex(PhysicalSchemaError, "distinct indices"):
            verify_reference_triangle_contents(vertices, triangles)


if __name__ == "__main__":
    unittest.main()

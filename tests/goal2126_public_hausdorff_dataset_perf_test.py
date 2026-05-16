from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from scripts import goal2126_public_hausdorff_dataset_perf as goal2126


class PublicHausdorffDatasetPerfHarnessTest(unittest.TestCase):
    def test_ascii_ply_parser_loads_xyz_vertices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ply = Path(tmp) / "mini.ply"
            ply.write_text(
                "\n".join(
                    [
                        "ply",
                        "format ascii 1.0",
                        "element vertex 3",
                        "property float x",
                        "property float y",
                        "property float z",
                        "element face 0",
                        "property list uchar int vertex_indices",
                        "end_header",
                        "1.0 2.0 3.0",
                        "4.0 5.0 6.0",
                        "7.0 8.0 9.0",
                    ]
                )
                + "\n",
                encoding="ascii",
            )
            points = goal2126.load_ply_xyz(ply)
        self.assertEqual(points.shape, (3, 3))
        np.testing.assert_allclose(points[1], np.asarray([4.0, 5.0, 6.0]))

    def test_binary_little_endian_parser_loads_xyz_with_extra_property(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ply = Path(tmp) / "mini_binary.ply"
            header = (
                "ply\n"
                "format binary_little_endian 1.0\n"
                "element vertex 2\n"
                "property float x\n"
                "property float y\n"
                "property float z\n"
                "property uchar confidence\n"
                "end_header\n"
            ).encode("ascii")
            import struct

            payload = struct.pack("<fffBfffB", 1.0, 2.0, 3.0, 9, 4.0, 5.0, 6.0, 8)
            ply.write_bytes(header + payload)
            points = goal2126.load_ply_xyz(ply)
        self.assertEqual(points.shape, (2, 3))
        np.testing.assert_allclose(points[0], np.asarray([1.0, 2.0, 3.0]))
        np.testing.assert_allclose(points[1], np.asarray([4.0, 5.0, 6.0]))

    def test_sampling_and_projection_are_deterministic(self) -> None:
        points = np.asarray([[float(i), float(i * 2), float(i * 3)] for i in range(100)], dtype=np.float64)
        first = goal2126.normalize_project_xy(goal2126.deterministic_sample(points, 20, seed=7))
        second = goal2126.normalize_project_xy(goal2126.deterministic_sample(points, 20, seed=7))
        self.assertEqual(first.shape, (20, 2))
        np.testing.assert_allclose(first, second)
        self.assertGreaterEqual(float(first.min()), 0.0)
        self.assertLessEqual(float(first.max()), 1.0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"

import sys

sys.path.insert(0, str(SCRIPT_DIR))

from xhd_input_loader import load_ascii_ply_vertex_matrix
from xhd_input_loader import load_ascii_ply_vertices
from xhd_input_loader import load_points_matrix


def _write_ply_with_extra_vertex_property(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "ply",
                "format ascii 1.0",
                "element vertex 3",
                "property float intensity",
                "property float x",
                "property float y",
                "property float z",
                "element face 0",
                "property list uchar int vertex_indices",
                "end_header",
                "9.0 -1.0 2.0 3.0",
                "8.0 4.5 5.5 6.5",
                "7.0 8.0 9.0 10.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_binary_big_endian_ply_with_extra_vertex_property(path: Path) -> None:
    header = "\n".join(
        [
            "ply",
            "format binary_big_endian 1.0",
            "element vertex 2",
            "property uchar intensity",
            "property float x",
            "property float y",
            "property float z",
            "element face 0",
            "property list uchar int vertex_indices",
            "end_header",
        ]
    ).encode("ascii") + b"\n"
    payload = b"".join(
        [
            struct.pack(">Bfff", 9, -1.0, 2.0, 3.0),
            struct.pack(">Bfff", 8, 4.5, 5.5, 6.5),
        ]
    )
    path.write_bytes(header + payload)


class Goal5205FastAsciiPlyMatrixLoaderTest(unittest.TestCase):
    def test_numpy_ascii_ply_matrix_loader_uses_coordinate_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "extra_property.ply"
            _write_ply_with_extra_vertex_property(path)

            matrix = load_ascii_ply_vertex_matrix(path, n_dims=3)

        self.assertEqual(matrix.dtype, np.float64)
        self.assertEqual(matrix.shape, (3, 3))
        np.testing.assert_allclose(
            matrix,
            np.asarray([(-1.0, 2.0, 3.0), (4.5, 5.5, 6.5), (8.0, 9.0, 10.0)], dtype=np.float64),
        )

    def test_legacy_row_loader_matches_fast_matrix_loader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "extra_property.ply"
            _write_ply_with_extra_vertex_property(path)

            matrix = load_ascii_ply_vertex_matrix(path, n_dims=3)
            rows = load_ascii_ply_vertices(path, n_dims=3)

        self.assertEqual(rows, [tuple(float(value) for value in row) for row in matrix])

    def test_binary_ply_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "binary.ply"
            path.write_text(
                "\n".join(
                    [
                        "ply",
                        "format binary_little_endian 1.0",
                        "element vertex 1",
                        "property float x",
                        "property float y",
                        "property float z",
                        "end_header",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "must be ASCII PLY"):
                load_ascii_ply_vertex_matrix(path, n_dims=3)

    def test_generic_ply_matrix_loader_reads_binary_big_endian_vertices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "binary_be.ply"
            _write_binary_big_endian_ply_with_extra_vertex_property(path)

            matrix = load_points_matrix(path, n_dims=3, input_type="ply")

        self.assertEqual(matrix.dtype, np.float64)
        self.assertEqual(matrix.shape, (2, 3))
        np.testing.assert_allclose(
            matrix,
            np.asarray([(-1.0, 2.0, 3.0), (4.5, 5.5, 6.5)], dtype=np.float64),
        )

    def test_loader_remains_app_owned_not_rtdl_core(self) -> None:
        source = (SCRIPT_DIR / "xhd_input_loader.py").read_text(encoding="utf-8").lower()
        self.assertIn("np.loadtxt", source)
        self.assertIn("usecols", source)
        for forbidden in ("rtdsl", "optix", "native_generic_symbol", "x-hd algorithm"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

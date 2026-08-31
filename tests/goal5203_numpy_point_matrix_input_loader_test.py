from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from xhd_input_loader import load_ascii_ply_vertex_matrix
from xhd_input_loader import load_ascii_ply_vertices
from xhd_input_loader import translate_point_matrix_to_min_bound


def _write_ascii_ply(path: Path, points: list[tuple[float, float, float]]) -> None:
    rows = [
        "ply",
        "format ascii 1.0",
        f"element vertex {len(points)}",
        "property float x",
        "property float y",
        "property float z",
        "element face 0",
        "property list uchar int vertex_indices",
        "end_header",
    ]
    rows.extend(f"{x} {y} {z}" for x, y, z in points)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _load_route_module():
    route_path = SCRIPT_DIR / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate_goal5203", route_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5203NumpyPointMatrixInputLoaderTest(unittest.TestCase):
    def test_ascii_ply_matrix_loader_matches_legacy_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "points.ply"
            points = [(-2.0, 1.0, 5.0), (3.0, 4.0, 7.0)]
            _write_ascii_ply(path, points)

            matrix = load_ascii_ply_vertex_matrix(path, n_dims=3)

            self.assertEqual(matrix.dtype, np.float64)
            self.assertEqual(matrix.shape, (2, 3))
            self.assertEqual(load_ascii_ply_vertices(path, n_dims=3), points)
            np.testing.assert_allclose(matrix, np.asarray(points, dtype=np.float64))

    def test_translate_point_matrix_to_min_bound_operates_on_matrix(self) -> None:
        matrix = np.asarray([(-2.0, 1.0, 5.0), (3.0, 4.0, 7.0)], dtype=np.float64)
        translated = translate_point_matrix_to_min_bound(matrix, copy=False)

        self.assertIs(translated, matrix)
        np.testing.assert_allclose(translated, np.asarray([(0.0, 0.0, 0.0), (5.0, 3.0, 2.0)]))

    def test_cell_mbr_route_accepts_matrix_inputs_without_tuple_repack(self) -> None:
        route = _load_route_module()
        matrix = np.asarray([(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)], dtype=np.float64)

        columns = route._columns_3d(matrix)

        self.assertIs(columns["coordinate_matrix"], matrix)
        self.assertTrue(np.shares_memory(matrix[:, 0], columns["x"]))
        self.assertTrue(np.shares_memory(matrix[:, 1], columns["y"]))
        self.assertTrue(np.shares_memory(matrix[:, 2], columns["z"]))

    def test_route_summary_records_numpy_matrix_input_representation(self) -> None:
        route = _load_route_module()
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.ply"
            b = Path(tmp) / "b.ply"
            _write_ascii_ply(a, [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)])
            _write_ascii_ply(b, [(0.0, 0.0, 0.0)])

            summary = route.build_summary(
                argparse.Namespace(
                    input1=str(a),
                    input2=str(b),
                    n_dims=3,
                    input_type="ply",
                    translate_each_input_to_min_bound=False,
                    backend="numpy",
                    grid_shape="2,2,2",
                    radius=None,
                    max_inline_points=64,
                    initial_state="nearest-cell-mbr",
                    seed_cell_budget=4,
                    frontier_nearest_executor="auto",
                    local_grid_seed_executor="auto",
                    frontier_row_order="sorted",
                    frontier_inline_nearest=False,
                    collect_inline_stats=False,
                    collect_frontier_native_phase_timings=False,
                    frontier_row_capacity=None,
                    direction_mode="directed-a-to-b",
                    validation_mode="none",
                    author_json=None,
                    tolerance=1e-9,
                )
            )

        self.assertEqual(summary["point_input_representation"], "numpy_coordinate_matrix")
        self.assertEqual(summary["point_count_a"], 2)
        self.assertEqual(summary["point_count_b"], 1)
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_route_input_loader_window_is_app_owned_not_core_primitive(self) -> None:
        source = (SCRIPT_DIR / "xhd_input_loader.py").read_text(encoding="utf-8").lower()
        self.assertIn("load_points_matrix", source)
        self.assertIn("load_ascii_ply_vertex_matrix", source)
        for forbidden in ("rtdsl", "optix", "native_generic_symbol"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

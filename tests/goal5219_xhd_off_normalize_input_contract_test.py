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

from xhd_input_loader import load_ascii_off_vertex_matrix
from xhd_input_loader import normalize_point_matrix_to_author_float32_unit_box
from xhd_input_loader import normalize_point_matrix_to_author_unit_box


def _write_off(path: Path, points: list[tuple[float, float, float]]) -> None:
    rows = ["OFF", f"{len(points)} 0 0"]
    rows.extend(f"{x} {y} {z}" for x, y, z in points)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _load_route_module():
    route_path = SCRIPT_DIR / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate_goal5219", route_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5219XhdOffNormalizeInputContractTest(unittest.TestCase):
    def test_ascii_off_vertex_matrix_reads_vertices_and_ignores_faces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "points.off"
            path.write_text(
                "\n".join(
                    [
                        "OFF",
                        "3 1 0",
                        "0 1 2",
                        "3 4 5",
                        "6 7 8",
                        "3 0 1 2",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            matrix = load_ascii_off_vertex_matrix(path, n_dims=3)

        self.assertEqual(matrix.dtype, np.float64)
        np.testing.assert_allclose(
            matrix,
            np.asarray([(0.0, 1.0, 2.0), (3.0, 4.0, 5.0), (6.0, 7.0, 8.0)], dtype=np.float64),
        )

    def test_author_unit_box_normalize_subtracts_lower_and_divides_by_max_extent(self) -> None:
        matrix = np.asarray([(-1.0, 2.0, 0.0), (3.0, 6.0, 2.0)], dtype=np.float64)

        normalized = normalize_point_matrix_to_author_unit_box(matrix, copy=True)

        np.testing.assert_allclose(normalized, np.asarray([(0.0, 0.0, 0.0), (1.0, 1.0, 0.5)]))
        np.testing.assert_allclose(matrix, np.asarray([(-1.0, 2.0, 0.0), (3.0, 6.0, 2.0)]))

    def test_author_float32_unit_box_normalize_matches_float_coordinate_semantics(self) -> None:
        matrix = np.asarray(
            [
                (0.0, 0.0, 0.0),
                (1.0000001192092896, 0.5, 0.25),
            ],
            dtype=np.float64,
        )

        normalized64 = normalize_point_matrix_to_author_unit_box(matrix, copy=True)
        normalized32 = normalize_point_matrix_to_author_float32_unit_box(matrix, copy=True)

        self.assertEqual(normalized32.dtype, np.float64)
        self.assertNotEqual(float(normalized64[1, 1]), float(normalized32[1, 1]))
        np.testing.assert_allclose(normalized32, normalized32.astype(np.float32).astype(np.float64))

    def test_route_gate_accepts_off_and_records_author_normalize_preprocessing(self) -> None:
        route = _load_route_module()
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.off"
            b = Path(tmp) / "b.off"
            _write_off(a, [(-1.0, 2.0, 0.0), (3.0, 6.0, 2.0)])
            _write_off(b, [(0.0, 0.0, 0.0)])

            summary = route.build_summary(
                argparse.Namespace(
                    input1=str(a),
                    input2=str(b),
                    n_dims=3,
                    input_type="off",
                    normalize_each_input_to_author_unit_box=True,
                    author_float32_normalization=False,
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

        self.assertEqual(summary["input_type"], "off")
        self.assertEqual(summary["reference_preprocessing"], ["normalize_each_input_to_author_unit_box"])
        self.assertEqual(summary["point_count_a"], 2)
        self.assertEqual(summary["point_count_b"], 1)
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_route_gate_records_author_float32_normalize_preprocessing(self) -> None:
        route = _load_route_module()
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.off"
            b = Path(tmp) / "b.off"
            _write_off(a, [(0.0, 0.0, 0.0), (1.0000001192092896, 0.5, 0.25)])
            _write_off(b, [(0.0, 0.0, 0.0)])

            summary = route.build_summary(
                argparse.Namespace(
                    input1=str(a),
                    input2=str(b),
                    n_dims=3,
                    input_type="off",
                    normalize_each_input_to_author_unit_box=True,
                    author_float32_normalization=True,
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

        self.assertEqual(summary["reference_preprocessing"], ["normalize_each_input_to_author_float32_unit_box"])

    def test_loader_remains_app_owned_not_rtdl_core(self) -> None:
        source = (SCRIPT_DIR / "xhd_input_loader.py").read_text(encoding="utf-8").lower()
        self.assertIn("load_ascii_off_vertex_matrix", source)
        self.assertIn("normalize_point_matrix_to_author_unit_box", source)
        self.assertIn("normalize_point_matrix_to_author_float32_unit_box", source)
        for forbidden in ("rtdsl", "optix", "native_generic_symbol"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

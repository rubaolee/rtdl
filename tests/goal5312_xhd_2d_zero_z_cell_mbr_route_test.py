from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_DIR = APP_DIR / "scripts"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))


def _load_cell_mbr_runner():
    script = SCRIPT_DIR / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_hd_exec_runner():
    script = SCRIPT_DIR / "run_xhd_rtdl_hd_exec.py"
    spec = importlib.util.spec_from_file_location("run_xhd_rtdl_hd_exec", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5312Xhd2dZeroZCellMbrRouteTest(unittest.TestCase):
    def _write_directed_2d_fixture(self, tmp: str) -> tuple[Path, Path]:
        input_a = Path(tmp) / "a.wkt"
        input_b = Path(tmp) / "b.wkt"
        input_a.write_text("POINT (0 0)\nPOINT (10 0)\n", encoding="utf-8")
        input_b.write_text("POINT (0.5 0)\nPOINT (1.0 0)\n", encoding="utf-8")
        return input_a, input_b

    def test_zero_z_lift_helper_preserves_xy_and_appends_zero_z(self) -> None:
        from xhd_input_loader import lift_point_matrix_2d_to_3d_zero_z

        lifted = lift_point_matrix_2d_to_3d_zero_z(np.asarray([[1.0, 2.0], [3.0, 4.0]]))
        self.assertEqual(lifted.shape, (2, 3))
        np.testing.assert_allclose(lifted[:, :2], [[1.0, 2.0], [3.0, 4.0]])
        np.testing.assert_allclose(lifted[:, 2], [0.0, 0.0])

        with self.assertRaisesRegex(ValueError, "Nx2 point matrix"):
            lift_point_matrix_2d_to_3d_zero_z(np.asarray([[1.0, 2.0, 3.0]]))

    def test_streaming_wkt_matrix_loader_matches_row_loader(self) -> None:
        from xhd_input_loader import load_wkt_point_matrix
        from xhd_input_loader import load_wkt_points

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mixed.wkt"
            path.write_text(
                "\n".join(
                    [
                        "POINT (0 0)",
                        "LINESTRING (1 1, 2 2)",
                        "POLYGON ((3 3, 4 3, 4 4, 3 3), (99 99, 100 99, 99 99))",
                        "MULTIPOLYGON (((5 5, 6 5, 5 5)), ((7 7, 8 7, 7 7)))",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            rows = load_wkt_points(path, n_dims=2)
            matrix = load_wkt_point_matrix(path, n_dims=2)

        self.assertEqual(matrix.shape, (len(rows), 2))
        np.testing.assert_allclose(matrix, np.asarray(rows, dtype=np.float64))
        self.assertNotIn((99.0, 99.0), rows)

    def test_2d_cell_mbr_route_requires_explicit_zero_z_lift(self) -> None:
        runner = _load_cell_mbr_runner()
        with tempfile.TemporaryDirectory() as tmp:
            input_a, input_b = self._write_directed_2d_fixture(tmp)
            args = argparse.Namespace(
                input1=str(input_a),
                input2=str(input_b),
                n_dims=2,
                input_type="wkt",
                lift_2d_to_3d_zero_z=False,
                normalize_each_input_to_author_unit_box=False,
                author_float32_normalization=False,
                translate_each_input_to_min_bound=False,
                backend="numpy",
                grid_shape="2,2,1",
                radius=None,
                max_inline_points=64,
                initial_state="none",
                author_json=None,
                summary="",
                tolerance=1e-6,
                direction_mode="directed-a-to-b",
            )
            with self.assertRaisesRegex(ValueError, "--lift-2d-to-3d-zero-z"):
                runner.build_summary(args)

    def test_2d_wkt_zero_z_lift_matches_exact_directed_value_on_numpy_cell_mbr_route(self) -> None:
        runner = _load_cell_mbr_runner()
        with tempfile.TemporaryDirectory() as tmp:
            input_a, input_b = self._write_directed_2d_fixture(tmp)
            args = argparse.Namespace(
                input1=str(input_a),
                input2=str(input_b),
                n_dims=2,
                input_type="wkt",
                lift_2d_to_3d_zero_z=True,
                normalize_each_input_to_author_unit_box=False,
                author_float32_normalization=False,
                translate_each_input_to_min_bound=False,
                backend="numpy",
                grid_shape="2,2,1",
                radius=None,
                max_inline_points=64,
                initial_state="none",
                author_json=None,
                summary="",
                tolerance=1e-6,
                direction_mode="directed-a-to-b",
            )

            summary = runner.build_summary(args)

        self.assertEqual(summary["input_n_dims"], 2)
        self.assertEqual(summary["execution_n_dims"], 3)
        self.assertTrue(summary["lift_2d_to_3d_zero_z"])
        self.assertIn("lift_2d_to_3d_zero_z_for_cell_mbr", summary["reference_preprocessing"])
        self.assertEqual(summary["rtdl_route"]["directed_a_to_b"]["distance"], 9.0)
        self.assertTrue(summary["rtdl_matches_exact_reference"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])
        self.assertIn("2-D inputs are embedded into z=0", summary["rtdl_route"]["route_contract"])

    def test_hd_exec_cell_mbr_route_rejects_2d_without_lift_before_backend_work(self) -> None:
        runner = _load_hd_exec_runner()
        with tempfile.TemporaryDirectory() as tmp:
            input_a, input_b = self._write_directed_2d_fixture(tmp)
            parser = runner.build_parser()
            args = parser.parse_args(
                [
                    "-input1",
                    str(input_a),
                    "-input2",
                    str(input_b),
                    "-n_dims",
                    "2",
                    "-input_type",
                    "wkt",
                    "-variant",
                    "rt",
                    "-execution",
                    "gpu",
                    "-json",
                    str(Path(tmp) / "unused.json"),
                    "--rtdl-route",
                    "cell-mbr-fast-scalar",
                ]
            )
            with self.assertRaisesRegex(ValueError, "--lift-2d-to-3d-zero-z"):
                runner.run_rtdl_hd_exec(args)


if __name__ == "__main__":
    unittest.main()

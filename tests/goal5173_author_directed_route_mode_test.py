from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_route_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5173AuthorDirectedRouteModeTest(unittest.TestCase):
    def test_directed_mode_runs_only_author_contract_direction(self) -> None:
        runner = _load_route_runner()
        fixtures = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"
        results = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
        args = argparse.Namespace(
            input1=str(fixtures / "bounded3d_a.wkt"),
            input2=str(fixtures / "bounded3d_b.wkt"),
            n_dims=3,
            input_type="wkt",
            translate_each_input_to_min_bound=False,
            backend="numpy",
            grid_shape="2,1,1",
            radius=None,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            frontier_nearest_executor="numpy",
            frontier_row_order="sorted",
            frontier_inline_nearest=False,
            direction_mode="directed-a-to-b",
            validation_mode="exact-and-author",
            author_json=str(results / "bounded3d_author_hd_exec_output_pod.json"),
            summary="",
            tolerance=1e-6,
        )

        summary = runner.build_summary(args)

        self.assertEqual(summary["direction_mode"], "directed-a-to-b")
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertEqual(summary["rtdl_route"]["exact_reference_key"], "directed_a_to_b")
        self.assertIsNone(summary["rtdl_route"]["directed_b_to_a"])
        self.assertIsNone(summary["rtdl_route"]["hausdorff"])
        self.assertEqual(summary["author_hd_result"], 2.0)
        self.assertEqual(summary["author_comparison_distance"], 2.0)
        self.assertEqual(summary["rtdl_exact_abs_diff"], 0.0)

    def test_symmetric_diagnostic_mode_preserves_b_to_a(self) -> None:
        runner = _load_route_runner()
        fixtures = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"
        args = argparse.Namespace(
            input1=str(fixtures / "bounded3d_a.wkt"),
            input2=str(fixtures / "bounded3d_b.wkt"),
            n_dims=3,
            input_type="wkt",
            translate_each_input_to_min_bound=False,
            backend="numpy",
            grid_shape="2,1,1",
            radius=None,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            frontier_nearest_executor="numpy",
            frontier_row_order="sorted",
            frontier_inline_nearest=False,
            direction_mode="symmetric-diagnostic",
            validation_mode="none",
            author_json=None,
            summary="",
            tolerance=1e-6,
        )

        summary = runner.build_summary(args)

        self.assertEqual(summary["direction_mode"], "symmetric-diagnostic")
        self.assertIsNotNone(summary["rtdl_route"]["directed_b_to_a"])
        self.assertEqual(summary["rtdl_route"]["exact_reference_key"], "hausdorff")
        self.assertIsNotNone(summary["rtdl_route"]["hausdorff"])

    def test_matrix_and_route_expose_direction_mode_cli(self) -> None:
        route_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        matrix_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_seeded_performance_matrix.py"
        ).read_text(encoding="utf-8")
        for text in (route_script, matrix_script):
            self.assertIn("--direction-mode", text)
            self.assertIn("directed-a-to-b", text)
            self.assertIn("symmetric-diagnostic", text)


if __name__ == "__main__":
    unittest.main()

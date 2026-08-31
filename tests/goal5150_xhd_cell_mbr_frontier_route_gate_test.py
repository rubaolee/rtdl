from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5150XhdCellMbrFrontierRouteGateTest(unittest.TestCase):
    def test_numpy_cell_mbr_frontier_route_matches_existing_bounded3d_author_json(self) -> None:
        runner = _load_runner()
        fixtures = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"
        results = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
        summary_path = results / "_tmp_goal5150_bounded3d_cell_mbr_route.json"
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
            initial_state="none",
            author_json=str(results / "bounded3d_author_hd_exec_output_pod.json"),
            summary=str(summary_path),
            tolerance=1e-6,
        )
        summary = runner.build_summary(args)

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.cell_mbr_frontier_route_gate.v1")
        self.assertEqual(summary["backend"], "numpy")
        self.assertEqual(summary["author_hd_result"], 2.0)
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertTrue(summary["matched"])
        self.assertTrue(summary["rtdl_matches_exact_reference"])
        self.assertIn("cell_mbr_frontier", summary["rtdl_route"]["route"])
        self.assertIn("not full X-HD paper reproduction", summary["boundary"])
        self.assertIn("not the author's fused RT algorithm", summary["boundary"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])

    def test_script_keeps_route_gate_boundaries_visible(self) -> None:
        text = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        self.assertIn("full X-HD paper reproduction", text)
        self.assertIn("fused RT algorithm", text)
        self.assertIn("not a performance claim", text)
        self.assertIn("nearest_witness_from_cell_mbr_frontier_numpy_columns", text)
        self.assertIn("cell_mbr_nearest_frontier_native_3d_optix_columns", text)
        self.assertIn("np.isfinite(finite_seed_distances)", text)
        self.assertIn("finite_seed_distances.size == len(current_best_distances)", text)
        self.assertIn("_fill_missing_nearest_with_pairwise_fallback", text)
        self.assertIn("missing_nearest_fallback_count", text)
        self.assertIn("pairwise_l2_distance_candidate_rows_numpy_columns", text)


if __name__ == "__main__":
    unittest.main()

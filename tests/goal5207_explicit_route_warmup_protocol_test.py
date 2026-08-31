from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_full_public_subset_scaling_gate.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_xhd_full_public_subset_scaling_gate_goal5207", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_ply(path: Path, points):
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


def _base_namespace(root: Path, bridge_path: Path, profile_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        bridge=bridge_path,
        profile=profile_path,
        output=root / "summary.json",
        backend="numpy",
        grid_shape="2,2,1",
        source_limits="all",
        route_warmup_source_limit="2",
        run_goal="Goal5207",
        source_selection_policy="evenly-spaced",
        translate_each_input_to_min_bound=False,
        max_inline_points=64,
        initial_state="nearest-cell-mbr",
        seed_cell_budget=4,
        local_grid_seed_executor="auto",
        frontier_nearest_executor="numpy",
        frontier_row_order="native",
        frontier_inline_nearest=False,
        collect_inline_stats=False,
        collect_frontier_native_phase_timings=False,
        frontier_row_capacity=None,
        max_exact_pair_evaluations=1,
        skip_exact_oracle=True,
        author_summary=None,
        author_hd_result=3.0,
        author_tolerance=1e-9,
        tolerance=1e-9,
    )


class Goal5207ExplicitRouteWarmupProtocolTest(unittest.TestCase):
    def test_warmup_case_is_recorded_and_excluded_from_measured_statistics(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            _write_ply(source, [(0, 0, 0), (10, 0, 0), (0, 10, 0), (20, 0, 0)])
            _write_ply(target, [(0, 0, 0), (2, 0, 0), (10, 1, 0), (0, 10, 2), (20, 3, 0)])
            bridge_path.write_text(
                """
{
  "target": "graphics_dragon_happy_buddha",
  "public_same_source_candidates": {
    "dragon.ply": {"path": "%SOURCE%"},
    "happy_buddha.ply": {"path": "%TARGET%"}
  }
}
""".replace("%SOURCE%", str(source).replace("\\", "\\\\")).replace(
                    "%TARGET%", str(target).replace("\\", "\\\\")
                ),
                encoding="utf-8",
            )
            profile_path.write_text(
                """
{
  "pairwise_estimate": {
    "pair_count": 20,
    "pairwise_exact_route_allowed": false
  }
}
""",
                encoding="utf-8",
            )

            summary = module.build_summary(_base_namespace(root, bridge_path, profile_path))

        self.assertEqual(summary["source_limits"], [4])
        self.assertEqual(summary["route_warmup_source_limit"], 2)
        self.assertTrue(summary["summary_statistics"]["route_warmup_used"])
        self.assertTrue(summary["route_feasibility"]["route_warmup_excluded_from_summary_statistics"])
        self.assertIsNotNone(summary["route_warmup"])
        warmup = summary["route_warmup"]
        self.assertEqual(warmup["source_limit"], 2)
        self.assertEqual(warmup["case_role"], "warmup")
        self.assertTrue(warmup["source_subset_materialized"])
        self.assertEqual(warmup["source_subset_selection_contract"], "deterministic_indexed_subset_copy")
        self.assertTrue(warmup["excluded_from_summary_statistics"])
        self.assertTrue(warmup["matched"])
        self.assertEqual(summary["cases"][0]["case_role"], "measured")
        self.assertFalse(summary["cases"][0]["excluded_from_summary_statistics"])
        self.assertEqual(summary["cases"][0]["source_limit"], 4)
        self.assertFalse(summary["cases"][0]["source_subset_materialized"])
        self.assertEqual(summary["cases"][0]["source_subset_selection_contract"], "all_source_no_copy_view")
        self.assertEqual(summary["cases"][0]["selected_indices_head"], [0, 1, 2, 3])
        self.assertEqual(summary["cases"][0]["selected_indices_tail"], [0, 1, 2, 3])
        self.assertAlmostEqual(summary["summary_statistics"]["median_route_wall_sec"], summary["cases"][0]["phase_timings_sec"]["rtdl_route_wall"])
        self.assertGreater(summary["phase_timings_sec"]["route_warmup"], 0.0)
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_warmup_source_limit_rejects_out_of_range(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            _write_ply(source, [(0, 0, 0), (10, 0, 0)])
            _write_ply(target, [(0, 0, 0), (2, 0, 0)])
            bridge_path.write_text(
                """
{
  "target": "graphics_dragon_happy_buddha",
  "public_same_source_candidates": {
    "dragon.ply": {"path": "%SOURCE%"},
    "happy_buddha.ply": {"path": "%TARGET%"}
  }
}
""".replace("%SOURCE%", str(source).replace("\\", "\\\\")).replace(
                    "%TARGET%", str(target).replace("\\", "\\\\")
                ),
                encoding="utf-8",
            )
            profile_path.write_text('{"pairwise_estimate": {"pair_count": 4}}', encoding="utf-8")
            args = _base_namespace(root, bridge_path, profile_path)
            args.source_limits = "1"
            args.route_warmup_source_limit = "3"

            with self.assertRaisesRegex(ValueError, "route-warmup-source-limit"):
                module.build_summary(args)


if __name__ == "__main__":
    unittest.main()

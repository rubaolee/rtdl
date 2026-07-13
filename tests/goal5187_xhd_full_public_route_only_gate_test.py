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
    spec = importlib.util.spec_from_file_location("run_xhd_full_public_subset_scaling_gate", SCRIPT)
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


class Goal5187XhdFullPublicRouteOnlyGateTest(unittest.TestCase):
    def test_all_source_route_only_compares_to_author_without_exact_oracle(self):
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
            args = argparse.Namespace(
                bridge=bridge_path,
                profile=profile_path,
                output=root / "summary.json",
                backend="numpy",
                grid_shape="2,2,1",
                source_limits="all",
                run_goal="Goal5187",
                source_selection_policy="evenly-spaced",
                translate_each_input_to_min_bound=False,
                max_inline_points=64,
                frontier_nearest_executor="numpy",
                frontier_row_order="native",
                frontier_inline_nearest=False,
                frontier_row_capacity=None,
                max_exact_pair_evaluations=1,
                skip_exact_oracle=True,
                author_summary=None,
                author_hd_result=3.0,
                author_tolerance=1e-9,
                tolerance=1e-9,
            )

            summary = module.build_summary(args)

        self.assertEqual(summary["source_limits"], [4])
        self.assertTrue(summary["summary_statistics"]["all_matched"])
        self.assertTrue(summary["summary_statistics"]["full_all_source_route_run"])
        self.assertTrue(summary["route_feasibility"]["full_all_source_route_run"])
        self.assertFalse(summary["route_feasibility"]["exact_oracle_used"])
        self.assertTrue(summary["claim_boundary"]["full_all_source_route_run_claimed"])
        self.assertFalse(summary["claim_boundary"]["exact_oracle_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertEqual(summary["cases"][0]["match_basis"], "author_hd_result")
        self.assertTrue(summary["cases"][0]["matched"])
        self.assertIsNone(summary["cases"][0]["exact_subset_reference"])
        self.assertFalse(summary["cases"][0]["exact_oracle_used"])
        self.assertAlmostEqual(summary["cases"][0]["author_abs_diff"], 0.0, delta=1e-12)

    def test_skip_exact_oracle_requires_author_comparator(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            _write_ply(source, [(0, 0, 0)])
            _write_ply(target, [(0, 0, 0)])
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
            profile_path.write_text('{"pairwise_estimate": {"pair_count": 1}}', encoding="utf-8")
            args = argparse.Namespace(
                bridge=bridge_path,
                profile=profile_path,
                output=root / "summary.json",
                backend="numpy",
                grid_shape="1,1,1",
                source_limits="all",
                run_goal="Goal5187",
                source_selection_policy="evenly-spaced",
                translate_each_input_to_min_bound=False,
                max_inline_points=64,
                frontier_nearest_executor="numpy",
                frontier_row_order="native",
                frontier_inline_nearest=False,
                frontier_row_capacity=None,
                max_exact_pair_evaluations=1,
                skip_exact_oracle=True,
                author_summary=None,
                author_hd_result=None,
                author_tolerance=1e-9,
                tolerance=1e-9,
            )

            with self.assertRaises(ValueError):
                module.build_summary(args)


if __name__ == "__main__":
    unittest.main()

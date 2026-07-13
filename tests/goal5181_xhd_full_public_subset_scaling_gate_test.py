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


class Goal5181XhdFullPublicSubsetScalingGateTest(unittest.TestCase):
    def test_subset_scaling_matrix_matches_exact_oracles(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            output_path = root / "summary.json"
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
                output=output_path,
                backend="numpy",
                grid_shape="2,2,1",
                source_limits="2,3",
                source_selection_policy="evenly-spaced",
                translate_each_input_to_min_bound=False,
                max_inline_points=64,
                frontier_nearest_executor="numpy",
                frontier_row_order="native",
                frontier_inline_nearest=False,
                max_exact_pair_evaluations=100,
                tolerance=1e-9,
            )

            summary = module.build_summary(args)

        self.assertEqual(
            summary["schema"],
            "rtdl.paper_reproduction.xhd.full_public_subset_scaling_gate.v1",
        )
        self.assertEqual(summary["source_limits"], [2, 3])
        self.assertTrue(summary["summary_statistics"]["all_matched"])
        self.assertEqual(len(summary["cases"]), 2)
        self.assertTrue(all(case["matched"] for case in summary["cases"]))
        self.assertGreater(summary["summary_statistics"]["max_frontier_row_count"], 0)
        self.assertGreater(summary["capacity_planning"]["suggested_next_explicit_row_capacity"], 0)
        self.assertFalse(summary["route_feasibility"]["full_all_source_route_run"])
        self.assertFalse(summary["route_feasibility"]["full_pairwise_rows_materialized"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_source_limits_parse_and_pair_evaluation_guard(self):
        module = _load_module()
        self.assertEqual(module._parse_source_limits("1, 2;3"), [1, 2, 3])
        with self.assertRaises(ValueError):
            module._parse_source_limits("1,1")

    def test_bridge_path_resolution_uses_author_basename_order(self):
        module = _load_module()
        bridge = {
            "target": "graphics_dragon_asian_dragon",
            "author_basename_order": ["dragon.ply", "asian_dragon.ply"],
            "source_basename": "dragon.ply",
            "target_basename": "asian_dragon.ply",
            "public_same_source_candidates": {
                "dragon.ply": {"path": "C:/data/dragon.ply"},
                "asian_dragon.ply": {"path": "C:/data/asian_dragon.ply"},
                "happy_buddha.ply": {"path": "C:/data/should_not_be_used.ply"},
            },
        }

        source, target = module.feasibility_gate._resolve_bridge_paths(bridge)

        self.assertEqual(source.as_posix(), "C:/data/dragon.ply")
        self.assertEqual(target.as_posix(), "C:/data/asian_dragon.ply")


if __name__ == "__main__":
    unittest.main()

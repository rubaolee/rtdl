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
    / "run_xhd_full_public_feasibility_gate.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_xhd_full_public_feasibility_gate", SCRIPT)
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


class Goal5180XhdFullPublicFeasibilityGateTest(unittest.TestCase):
    def test_bounded_subset_route_matches_exact_subset_oracle(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            output_path = root / "summary.json"
            _write_ply(source, [(0, 0, 0), (10, 0, 0), (0, 10, 0)])
            _write_ply(target, [(0, 0, 0), (2, 0, 0), (10, 1, 0), (0, 10, 2)])
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
    "pair_count": 12,
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
                source_limit=2,
                source_selection_policy="evenly-spaced",
                translate_each_input_to_min_bound=False,
                max_inline_points=64,
                frontier_nearest_executor="numpy",
                frontier_row_order="native",
                frontier_inline_nearest=False,
                tolerance=1e-9,
            )

            summary = module.build_summary(args)

        self.assertEqual(
            summary["schema"],
            "rtdl.paper_reproduction.xhd.full_public_feasibility_gate.v1",
        )
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["source_subset"]["selected_indices"], [0, 2])
        self.assertEqual(summary["full_point_counts"], {"source": 3, "target": 4})
        self.assertEqual(summary["exact_subset_reference"]["pair_evaluations"], 8)
        self.assertAlmostEqual(summary["exact_subset_reference"]["distance"], 2.0)
        self.assertAlmostEqual(summary["rtdl_route"]["distance"], 2.0)
        self.assertFalse(summary["route_feasibility"]["full_pairwise_rows_materialized"])
        self.assertFalse(summary["route_feasibility"]["full_all_source_route_run"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_source_selection_is_deterministic_and_fail_closed(self):
        module = _load_module()
        self.assertEqual(
            module._select_source_indices(10, limit=4, policy="evenly-spaced"),
            [0, 3, 6, 9],
        )
        self.assertEqual(module._select_source_indices(10, limit=4, policy="first"), [0, 1, 2, 3])
        with self.assertRaises(ValueError):
            module._select_source_indices(3, limit=4, policy="evenly-spaced")


if __name__ == "__main__":
    unittest.main()

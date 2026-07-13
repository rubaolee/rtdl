import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE_SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_cell_mbr_frontier_route_gate.py"
)
SCALING_SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_full_public_subset_scaling_gate.py"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
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


class Goal5182XhdExplicitFrontierCapacityTest(unittest.TestCase):
    def test_directed_route_capacity_is_explicit_and_fail_closed(self):
        route = _load_module("run_xhd_cell_mbr_frontier_route_gate", ROUTE_SCRIPT)
        source_points = [(0, 0, 0), (2, 0, 0)]
        target_points = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)]
        kwargs = dict(
            label="capacity_probe",
            backend="numpy",
            grid_shape=(2, 1, 1),
            radius=None,
            fallback_radius=route._full_cover_radius(source_points, target_points),
            max_inline_points=1,
            initial_state="none",
            frontier_nearest_executor="numpy",
            frontier_row_order="native",
            frontier_inline_nearest=False,
        )
        baseline = route._directed_cell_mbr_route(
            source_points,
            target_points,
            frontier_row_capacity=None,
            **kwargs,
        )
        self.assertEqual(baseline["frontier_row_count"], 4)
        with self.assertRaisesRegex(RuntimeError, "fail_closed_overflow"):
            route._directed_cell_mbr_route(
                source_points,
                target_points,
                frontier_row_capacity=3,
                **kwargs,
            )
        exact_capacity = route._directed_cell_mbr_route(
            source_points,
            target_points,
            frontier_row_capacity=4,
            **kwargs,
        )
        self.assertEqual(exact_capacity["frontier_row_count"], 4)
        self.assertEqual(exact_capacity["frontier_row_capacity_requested"], 4)
        self.assertEqual(exact_capacity["frontier_row_capacity"], 4)
        self.assertEqual(exact_capacity["frontier_row_capacity_policy"], "explicit")
        self.assertEqual(exact_capacity["frontier_row_capacity_attempts"], [4])
        self.assertAlmostEqual(exact_capacity["distance"], baseline["distance"])

    def test_full_public_subset_scaling_carries_capacity_metadata(self):
        scaling = _load_module("run_xhd_full_public_subset_scaling_gate", SCALING_SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge_path = root / "bridge.json"
            profile_path = root / "profile.json"
            output_path = root / "summary.json"
            _write_ply(source, [(0, 0, 0), (2, 0, 0)])
            _write_ply(target, [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)])
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
    "pair_count": 8,
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
                grid_shape="2,1,1",
                source_limits="2",
                source_selection_policy="first",
                translate_each_input_to_min_bound=False,
                max_inline_points=1,
                frontier_nearest_executor="numpy",
                frontier_row_order="native",
                frontier_inline_nearest=False,
                frontier_row_capacity=4,
                max_exact_pair_evaluations=100,
                tolerance=1e-9,
            )

            summary = scaling.build_summary(args)

        self.assertTrue(summary["summary_statistics"]["all_matched"])
        self.assertEqual(summary["route_feasibility"]["frontier_row_capacity_requested"], 4)
        case_route = summary["cases"][0]["rtdl_route"]
        self.assertEqual(case_route["frontier_row_capacity_requested"], 4)
        self.assertEqual(case_route["frontier_row_capacity"], 4)
        self.assertEqual(case_route["frontier_row_capacity_policy"], "explicit")
        self.assertLessEqual(case_route["frontier_row_count"], 4)
        self.assertGreater(case_route["frontier_row_count"], 0)
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()

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
    / "profile_xhd_priority_input_scale.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("profile_xhd_priority_input_scale", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_ply(path: Path, points):
    path.parent.mkdir(parents=True, exist_ok=True)
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
    path.write_text("\n".join(rows) + "\n")


class Goal5179PriorityInputScaleProfileTest(unittest.TestCase):
    def test_profile_estimates_pairwise_scale_and_refuses_route_claim(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dragon = root / "dragon.ply"
            happy = root / "happy.ply"
            _write_ply(dragon, [(0, 0, 0), (1, 0, 0), (0, 1, 0)])
            _write_ply(happy, [(0, 0, 1), (2, 0, 1)])
            bridge = {
                "target": "graphics_dragon_happy_buddha",
                "status": "fixture_bridge",
                "public_same_source_candidates": {
                    "dragon.ply": {"path": str(dragon)},
                    "happy_buddha.ply": {"path": str(happy)},
                },
            }

            profile = module.build_profile(bridge=bridge, grid_shapes=[(2, 2, 1)])

        self.assertEqual(
            profile["schema"],
            "rtdl.paper_reproduction.xhd.priority_input_scale_profile.v1",
        )
        self.assertEqual(profile["pairwise_estimate"]["pair_count"], 6)
        self.assertFalse(profile["pairwise_estimate"]["pairwise_exact_route_allowed"])
        self.assertTrue(profile["route_feasibility"]["do_not_run_naive_pairwise_exact"])
        self.assertTrue(profile["route_feasibility"]["requires_scalable_route"])
        self.assertFalse(profile["claim_boundary"]["route_run_claimed"])
        self.assertFalse(profile["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(profile["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertEqual(
            profile["input_profiles"]["dragon.ply"]["header"]["vertex_count"],
            3,
        )
        occupancy = profile["grid_occupancy_profiles"]["dragon.ply"][0]
        self.assertEqual(occupancy["total_cells"], 4)
        self.assertGreaterEqual(occupancy["occupied_cells"], 1)


if __name__ == "__main__":
    unittest.main()

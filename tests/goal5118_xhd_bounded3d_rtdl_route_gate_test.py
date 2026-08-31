from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_rtdl_route_gate.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "bounded3d_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "bounded3d_b.wkt"
AUTHOR_JSON = APP_DIR / "results" / "bounded3d_author_hd_exec_output_pod.json"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_route_gate", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5118XhdBounded3dRtdlRouteGateTest(unittest.TestCase):
    def test_bounded3d_rtdl_route_matches_author_json_when_present(self) -> None:
        gate = _load_gate_module()
        if not AUTHOR_JSON.exists():
            self.skipTest("bounded3d author JSON not produced yet")

        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "bounded3d_rtdl_route_summary.json"
            rc = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--n-dims",
                    "3",
                    "--author-json",
                    str(AUTHOR_JSON),
                    "--summary",
                    str(summary_path),
                    "--tolerance",
                    "1e-6",
                ]
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.rtdl_route_gate.v1")
        self.assertEqual(summary["n_dims"], 3)
        self.assertEqual(summary["point_count_a"], 9)
        self.assertEqual(summary["point_count_b"], 8)
        self.assertEqual(summary["rtdl_route"]["route"], "rtdl_numpy_columns_3d")
        self.assertTrue(summary["rtdl_matches_exact_reference"])
        self.assertTrue(summary["matched"])
        self.assertAlmostEqual(summary["rtdl_route"]["hausdorff"], 2.0, delta=1e-12)
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertAlmostEqual(summary["author_comparison_distance"], 2.0, delta=1e-12)
        self.assertAlmostEqual(summary["author_hd_result"], 2.0, delta=1e-6)
        self.assertLessEqual(summary["author_abs_diff"], summary["tolerance"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])
        self.assertFalse(summary["author_performance_parity_claimed"])
        self.assertIn("generic RTDL 2D or 3D columnar Hausdorff route", summary["boundary"])


if __name__ == "__main__":
    unittest.main()

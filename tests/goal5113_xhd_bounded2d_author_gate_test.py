from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_author_json_gate.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "bounded2d_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "bounded2d_b.wkt"
EXPECTED = APP_DIR / "data" / "fixtures" / "bounded2d_expected.json"
POD_SUMMARY = APP_DIR / "results" / "bounded2d_author_gate_summary_pod.json"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("xhd_author_json_gate", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5113XhdBounded2dAuthorGateTest(unittest.TestCase):
    def test_bounded2d_fixture_exact_reference(self) -> None:
        gate = _load_gate_module()
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

        points_a = gate.load_wkt_points(FIXTURE_A, n_dims=2)
        points_b = gate.load_wkt_points(FIXTURE_B, n_dims=2)
        exact = gate.exact_hausdorff(points_a, points_b)

        self.assertEqual(len(points_a), expected["point_count_a"])
        self.assertEqual(len(points_b), expected["point_count_b"])
        self.assertAlmostEqual(exact["directed_a_to_b"], expected["directed_a_to_b"], delta=1e-12)
        self.assertAlmostEqual(exact["directed_b_to_a"], expected["directed_b_to_a"], delta=1e-12)
        self.assertAlmostEqual(exact["hausdorff"], expected["hausdorff"], delta=1e-12)

    def test_pod_author_gate_summary_matches_when_present(self) -> None:
        if not POD_SUMMARY.exists():
            self.skipTest("POD author summary not produced yet")
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.author_json_gate.v1")
        self.assertEqual(summary["point_count_a"], 10)
        self.assertEqual(summary["point_count_b"], 9)
        self.assertEqual(summary["author_run"]["returncode"], 0)
        self.assertFalse(summary["author_run_failed"])
        self.assertTrue(summary["matched"])
        self.assertAlmostEqual(summary["author_hd_result"], 2.0, delta=1e-6)
        self.assertAlmostEqual(summary["rtdl_reference"]["hausdorff"], 2.0, delta=1e-12)
        self.assertLessEqual(summary["abs_diff"], summary["tolerance"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])


if __name__ == "__main__":
    unittest.main()

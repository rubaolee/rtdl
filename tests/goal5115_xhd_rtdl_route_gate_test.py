from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_rtdl_route_gate.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "bounded2d_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "bounded2d_b.wkt"
AUTHOR_JSON = APP_DIR / "results" / "bounded2d_author_hd_exec_output_pod.json"
DIRECTED_FIXTURE_A = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_a.wkt"
DIRECTED_FIXTURE_B = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_b.wkt"
DIRECTED_AUTHOR_JSON = APP_DIR / "results" / "directed2d_asymmetric_author_hd_exec_output_pod.json"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_route_gate", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5115XhdRtdlRouteGateTest(unittest.TestCase):
    def test_bounded2d_rtdl_route_matches_author_json_when_present(self) -> None:
        gate = _load_gate_module()
        if not AUTHOR_JSON.exists():
            self.skipTest("bounded2d author JSON not produced yet")

        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "rtdl_route_summary.json"
            rc = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--n-dims",
                    "2",
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
        self.assertEqual(summary["rtdl_route"]["route"], "rtdl_numpy_columns_2d")
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
        self.assertFalse(summary["existing_hausdorff_xhd_benchmark_reclassified_as_paper_reproduction"])
        self.assertIn("generic RTDL 2D or 3D columnar Hausdorff route", summary["boundary"])

    def test_reference_only_route_has_no_author_match_claim(self) -> None:
        gate = _load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "rtdl_route_summary.json"
            rc = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--n-dims",
                    "2",
                    "--summary",
                    str(summary_path),
                ]
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertIsNone(summary["author_hd_result"])
        self.assertIsNone(summary["author_abs_diff"])
        self.assertIsNone(summary["matched"])
        self.assertTrue(summary["rtdl_matches_exact_reference"])

    def test_directed_asymmetric_rtdl_route_matches_author_directed_not_symmetric(self) -> None:
        gate = _load_gate_module()
        if not DIRECTED_AUTHOR_JSON.exists():
            self.skipTest("directed asymmetric author JSON not produced yet")

        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "directed_rtdl_route_summary.json"
            rc = gate.main(
                [
                    "--input1",
                    str(DIRECTED_FIXTURE_A),
                    "--input2",
                    str(DIRECTED_FIXTURE_B),
                    "--n-dims",
                    "2",
                    "--author-json",
                    str(DIRECTED_AUTHOR_JSON),
                    "--summary",
                    str(summary_path),
                    "--tolerance",
                    "1e-6",
                ]
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertAlmostEqual(summary["author_comparison_distance"], 0.5, delta=1e-12)
        self.assertAlmostEqual(summary["author_hd_result"], 0.5, delta=1e-6)
        self.assertAlmostEqual(summary["exact_reference"]["directed_b_to_a"], 9.0, delta=1e-12)
        self.assertAlmostEqual(summary["exact_reference"]["hausdorff"], 9.0, delta=1e-12)
        self.assertAlmostEqual(summary["rtdl_route"]["hausdorff"], 9.0, delta=1e-12)
        self.assertNotEqual(
            summary["author_comparison_distance"],
            summary["rtdl_route"]["hausdorff"],
        )

    def test_unsupported_dimension_is_rejected(self) -> None:
        gate = _load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "supports only public 2D and 3D Hausdorff APIs"):
                gate.main(
                    [
                        "--input1",
                        str(FIXTURE_A),
                        "--input2",
                        str(FIXTURE_B),
                        "--n-dims",
                        "4",
                        "--summary",
                        str(Path(tmp) / "unused.json"),
                    ]
                )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_author_json_gate.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "tiny2d_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "tiny2d_b.wkt"
EXPECTED = APP_DIR / "data" / "fixtures" / "tiny2d_expected.json"
DIRECTED_FIXTURE_A = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_a.wkt"
DIRECTED_FIXTURE_B = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_b.wkt"
DIRECTED_AUTHOR_SUMMARY = APP_DIR / "results" / "directed2d_asymmetric_author_gate_summary_pod.json"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("xhd_author_json_gate", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5111XhdAuthorJsonGateTest(unittest.TestCase):
    def test_tiny_fixture_has_exact_hausdorff_one(self) -> None:
        gate = _load_gate_module()
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

        points_a = gate.load_wkt_points(FIXTURE_A, n_dims=2)
        points_b = gate.load_wkt_points(FIXTURE_B, n_dims=2)
        exact = gate.exact_hausdorff(points_a, points_b)

        self.assertEqual(len(points_a), 3)
        self.assertEqual(len(points_b), 3)
        self.assertAlmostEqual(exact["directed_a_to_b"], expected["directed_a_to_b"], delta=1e-12)
        self.assertAlmostEqual(exact["directed_b_to_a"], expected["directed_b_to_a"], delta=1e-12)
        self.assertAlmostEqual(exact["hausdorff"], expected["hausdorff"], delta=1e-12)

    def test_reference_only_summary_makes_no_author_claim(self) -> None:
        gate = _load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "summary.json"
            rc = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--summary",
                    str(summary_path),
                ]
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.author_json_gate.v1")
        self.assertEqual(summary["point_count_a"], 3)
        self.assertEqual(summary["point_count_b"], 3)
        self.assertAlmostEqual(summary["rtdl_reference"]["hausdorff"], 1.0, delta=1e-12)
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertAlmostEqual(summary["author_comparison_reference_value"], 1.0, delta=1e-12)
        self.assertIsNone(summary["author_hd_result"])
        self.assertIsNone(summary["matched"])
        self.assertFalse(summary["author_run_failed"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])
        self.assertIn("not exact paper input reproduction", summary["boundary"])

    def test_directed_asymmetric_fixture_distinguishes_author_contract_from_symmetric(self) -> None:
        gate = _load_gate_module()
        if not DIRECTED_AUTHOR_SUMMARY.exists():
            self.skipTest("directed asymmetric POD author summary not produced yet")

        points_a = gate.load_wkt_points(DIRECTED_FIXTURE_A, n_dims=2)
        points_b = gate.load_wkt_points(DIRECTED_FIXTURE_B, n_dims=2)
        exact = gate.exact_hausdorff(points_a, points_b)
        summary = json.loads(DIRECTED_AUTHOR_SUMMARY.read_text(encoding="utf-8"))

        self.assertAlmostEqual(exact["directed_a_to_b"], 0.5, delta=1e-12)
        self.assertAlmostEqual(exact["directed_b_to_a"], 9.0, delta=1e-12)
        self.assertAlmostEqual(exact["hausdorff"], 9.0, delta=1e-12)
        self.assertNotEqual(exact["directed_a_to_b"], exact["hausdorff"])

        self.assertTrue(summary["matched"])
        self.assertEqual(summary["author_comparison_reference"], "directed_a_to_b")
        self.assertAlmostEqual(summary["author_comparison_reference_value"], 0.5, delta=1e-12)
        self.assertAlmostEqual(summary["author_hd_result"], 0.5, delta=1e-6)
        self.assertAlmostEqual(summary["abs_diff"], 0.0, delta=1e-12)

    def test_fake_author_json_match_and_mismatch_are_explicit(self) -> None:
        gate = _load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            matching_author_json = tmp_path / "author_match.json"
            matching_summary = tmp_path / "summary_match.json"
            matching_author_json.write_text(json.dumps({"HDResult": 1.0}), encoding="utf-8")

            rc_match = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--author-json",
                    str(matching_author_json),
                    "--summary",
                    str(matching_summary),
                    "--tolerance",
                    "1e-9",
                ]
            )
            match_summary = json.loads(matching_summary.read_text(encoding="utf-8"))

            mismatching_author_json = tmp_path / "author_mismatch.json"
            mismatching_summary = tmp_path / "summary_mismatch.json"
            mismatching_author_json.write_text(json.dumps({"HDResult": 1.25}), encoding="utf-8")

            rc_mismatch = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--author-json",
                    str(mismatching_author_json),
                    "--summary",
                    str(mismatching_summary),
                    "--tolerance",
                    "1e-9",
                ]
            )
            mismatch_summary = json.loads(mismatching_summary.read_text(encoding="utf-8"))

        self.assertEqual(rc_match, 0)
        self.assertTrue(match_summary["matched"])
        self.assertEqual(match_summary["author_hd_result"], 1.0)
        self.assertEqual(match_summary["abs_diff"], 0.0)

        self.assertEqual(rc_mismatch, 1)
        self.assertFalse(mismatch_summary["matched"])
        self.assertFalse(mismatch_summary["author_run_failed"])
        self.assertEqual(mismatch_summary["author_hd_result"], 1.25)
        self.assertAlmostEqual(mismatch_summary["abs_diff"], 0.25, delta=1e-12)

    def test_author_binary_failure_fails_closed_but_keeps_summary(self) -> None:
        gate = _load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            if os.name == "nt":
                failing_author = tmp_path / "failing_author.cmd"
                failing_author.write_text("@echo off\r\nexit /b 7\r\n", encoding="utf-8")
            else:
                failing_author = tmp_path / "failing_author.sh"
                failing_author.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
                failing_author.chmod(0o755)
            summary_path = tmp_path / "summary_failed_author.json"

            rc = gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--author-bin",
                    str(failing_author),
                    "--author-json",
                    str(tmp_path / "missing_author_output.json"),
                    "--summary",
                    str(summary_path),
                ]
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 2)
        self.assertTrue(summary["author_run_failed"])
        self.assertFalse(summary["matched"])
        self.assertEqual(summary["author_run"]["returncode"], 7)
        self.assertIsNone(summary["author_hd_result"])

    def test_author_bin_requires_author_json_output_path(self) -> None:
        gate = _load_gate_module()
        with self.assertRaises(ValueError):
            gate.main(
                [
                    "--input1",
                    str(FIXTURE_A),
                    "--input2",
                    str(FIXTURE_B),
                    "--author-bin",
                    str(APP_DIR / "missing_hd_exec"),
                    "--summary",
                    str(APP_DIR / "results" / "unused.json"),
                ]
            )


if __name__ == "__main__":
    unittest.main()

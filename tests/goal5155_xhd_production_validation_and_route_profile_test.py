from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_route_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_matrix_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_seeded_performance_matrix.py"
    spec = importlib.util.spec_from_file_location("run_xhd_seeded_performance_matrix", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5155XhdProductionValidationAndRouteProfileTest(unittest.TestCase):
    def test_author_only_mode_skips_exact_reference_but_keeps_author_gate(self) -> None:
        runner = _load_route_runner()
        fixtures = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"
        results = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
        args = argparse.Namespace(
            input1=str(fixtures / "bounded3d_a.wkt"),
            input2=str(fixtures / "bounded3d_b.wkt"),
            n_dims=3,
            input_type="wkt",
            translate_each_input_to_min_bound=False,
            backend="numpy",
            grid_shape="2,1,1",
            radius=None,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            validation_mode="author-only",
            author_json=str(results / "bounded3d_author_hd_exec_output_pod.json"),
            summary="",
            tolerance=1e-6,
        )

        summary = runner.build_summary(args)

        self.assertEqual(summary["validation_mode"], "author-only")
        self.assertIsNone(summary["exact_reference"])
        self.assertIsNone(summary["rtdl_exact_abs_diff"])
        self.assertIsNone(summary["rtdl_matches_exact_reference"])
        self.assertIsNone(summary["run_phases"]["exact_reference_sec"])
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["author_hd_result"], 2.0)

    def test_route_summary_exposes_seeded_subphase_timings(self) -> None:
        runner = _load_route_runner()
        fixtures = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"
        args = argparse.Namespace(
            input1=str(fixtures / "bounded3d_a.wkt"),
            input2=str(fixtures / "bounded3d_b.wkt"),
            n_dims=3,
            input_type="wkt",
            translate_each_input_to_min_bound=False,
            backend="numpy",
            grid_shape="2,1,1",
            radius=None,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            validation_mode="none",
            author_json=None,
            summary="",
            tolerance=1e-6,
        )

        summary = runner.build_summary(args)
        timings = summary["rtdl_route"]["directed_a_to_b"]["phase_timings_sec"]

        expected = {
            "source_columns",
            "target_columns",
            "grid_cell_mbrs",
            "initial_state_seed",
            "radius_selection",
            "frontier_rows",
            "nearest_continuation",
            "max_nearest_reduction",
            "direction_total",
        }
        self.assertEqual(set(timings), expected)
        self.assertGreaterEqual(timings["direction_total"], 0.0)
        self.assertGreaterEqual(timings["frontier_rows"], 0.0)
        self.assertGreaterEqual(timings["nearest_continuation"], 0.0)
        self.assertIsNone(summary["matched"])

    def test_performance_matrix_supports_skipped_exact_reference_medians(self) -> None:
        matrix = _load_matrix_runner()

        self.assertIsNone(matrix._median_optional([None, None]))
        self.assertEqual(matrix._median_optional([None, 1.0, 3.0]), 2.0)

    def test_production_matrix_artifact_keeps_validation_and_profile_boundaries(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_production_author_only_matrix_pod.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.seeded_performance_matrix.v1")
        self.assertEqual(payload["phase_policy"]["validation_mode"], "author-only")
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"sample256", "sample1024"})
        for case in cases.values():
            self.assertTrue(case["matched"])
            self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
            self.assertIsNone(case["rtdl"]["exact_reference_sec_median"])
            self.assertTrue(all(value is None for value in case["rtdl"]["exact_reference_sec_runs"]))
            self.assertIsNone(case["rtdl"]["rtdl_matches_exact_reference"])
            timings = case["rtdl"]["directed_a_to_b"]["phase_timings_sec_last_run"]
            self.assertIn("initial_state_seed", timings)
            self.assertIn("frontier_rows", timings)
            self.assertIn("nearest_continuation", timings)
            self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)


if __name__ == "__main__":
    unittest.main()

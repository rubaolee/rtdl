from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "build_xhd_hd_exec_entrypoint_performance_matrix.py"
MATRIX = APP_DIR / "results" / "xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json"
HD_EXEC_BATCH = APP_DIR / "results" / "xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json"
AUTHOR_BASELINE = APP_DIR / "results" / "xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location("xhd_hd_exec_perf_matrix", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5261XhdHdExecEntrypointPerformanceMatrixTest(unittest.TestCase):
    def test_all400_matrix_denominators_and_ratios(self) -> None:
        if not MATRIX.exists():
            self.skipTest(f"missing Goal5261 matrix artifact: {MATRIX}")
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.hd_exec_entrypoint_performance_matrix.v1")
        self.assertEqual(payload["case_count"], 400)
        self.assertEqual(payload["matched_case_count"], 400)
        self.assertEqual(payload["per_source_witness_exact_case_count"], 400)
        self.assertTrue(payload["all_cases_matched"])
        self.assertTrue(payload["all_cases_per_source_witness_exact"])
        self.assertLessEqual(payload["correctness"]["max_author_abs_diff"], 1e-6)

        stats = payload["statistics"]
        self.assertAlmostEqual(stats["rtdl_hd_exec_route_wall_ms"]["sum"], 420310.53318828344)
        self.assertAlmostEqual(stats["rtdl_hd_exec_case_wall_sec"]["sum"], 600.8750001639128)
        self.assertAlmostEqual(stats["author_process_wall_sec"]["sum"], 255.03741998970509)
        self.assertAlmostEqual(stats["author_internal_running_avg_time_ms"]["sum"], 2794.7910000000006)

        ratios = payload["denominator_separated_ratios"]
        self.assertAlmostEqual(ratios["rtdl_route_sum_sec_over_author_process_wall_sum_sec"], 1.648034759782505)
        self.assertAlmostEqual(ratios["rtdl_case_wall_sum_sec_over_author_process_wall_sum_sec"], 2.356026814371663)
        self.assertAlmostEqual(ratios["rtdl_route_sum_ms_over_author_internal_avgtime_sum_ms"], 150.3906850953375)
        self.assertAlmostEqual(ratios["hd_exec_route_sum_sec_over_legacy_goal5253_route_sum_sec"], 0.9899840755927131)

        semantics = payload["timing_semantics"]
        self.assertIn("not author internal AvgTime parity", semantics["rtdl_hd_exec_route_wall_ms"])
        self.assertIn("different denominator", semantics["author_internal_running_avg_time_ms"])
        claim = payload["claim_boundary"]
        self.assertFalse(claim["performance_parity_claimed"])
        self.assertFalse(claim["speedup_claimed"])
        self.assertFalse(claim["author_internal_avgtime_comparable_without_phase_review"])
        self.assertFalse(claim["exact_paper_dataset_identity_proved"])
        self.assertFalse(claim["full_xhd_paper_reproduction_claimed"])

    def test_builder_rejects_case_set_mismatch(self) -> None:
        builder = _load_builder()
        batch = {
            "cases": [
                {
                    "case_name": "a",
                    "rtdl_hd_result": 1.0,
                    "matched_author": True,
                    "per_source_witness_exact": True,
                    "running_avg_time_ms": 10.0,
                    "case_wall_sec": 0.1,
                }
            ]
        }
        baseline = {
            "cases": [
                {
                    "case_name": "b",
                    "author_normalized": {"hd_result": 1.0, "process_wall_sec": 0.2, "running_avg_time_ms": 5.0},
                    "rtdl_normalized_route": {"route_wall_sec": 0.01, "total_sec": 0.02},
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "case_name sets differ"):
            builder.build_matrix(batch, baseline)

    def test_cli_rebuilds_matrix_from_real_artifacts(self) -> None:
        if not HD_EXEC_BATCH.exists() or not AUTHOR_BASELINE.exists():
            self.skipTest("missing real Goal5253/Goal5260 artifacts")
        builder = _load_builder()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "matrix.json"
            rc = builder.main(
                [
                    "--hd-exec-batch",
                    str(HD_EXEC_BATCH),
                    "--author-baseline",
                    str(AUTHOR_BASELINE),
                    "--output",
                    str(out),
                ]
            )
            rebuilt = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(rebuilt["case_count"], 400)
        self.assertTrue(rebuilt["all_cases_matched"])
        self.assertAlmostEqual(
            rebuilt["denominator_separated_ratios"]["rtdl_route_sum_sec_over_author_process_wall_sum_sec"],
            1.648034759782505,
        )


if __name__ == "__main__":
    unittest.main()

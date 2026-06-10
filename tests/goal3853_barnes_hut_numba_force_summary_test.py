from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/apps/simulation/rtdl_barnes_hut_force_app.py"
BENCHMARK = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
REPORT = ROOT / "docs/reports/goal3853_barnes_hut_numba_force_summary_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3853_barnes_hut_numba_force_summary_a5000"
DIRECT_ARTIFACT = ARTIFACT_DIR / "barnes_hut_numba_force_summary_8192.json"
RUNNER_SUMMARY = ARTIFACT_DIR / "scale_profile_summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3853BarnesHutNumbaForceSummaryTest(unittest.TestCase):
    def test_force_summary_path_reuses_partner_columns_and_avoids_python_rows(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("_run_partner_exact_force_summary", text)
        self.assertIn("prepared_partner_columns_reused", text)
        self.assertIn("materializes_python_force_rows", text)
        self.assertIn("force_summary_materialization_sec", text)
        self.assertIn("prepared_force_repeat_protocol", text)
        self.assertIn("rt.pairwise_inverse_square_force_2d_partner_columns", text)

    def test_benchmark_forwards_repeat_and_warmup_to_partner_exact_force(self) -> None:
        text = BENCHMARK.read_text(encoding="utf-8")

        self.assertIn('"partner_exact_force"', text)
        self.assertIn("query_repeat=query_repeat", text)
        self.assertIn("warmup=warmup", text)

    def test_report_documents_kernel_startup_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3853",
            "0.008967613",
            "materializes Python force rows | `false`",
            "cold-process",
            "kernel caching",
            "not a public speedup claim",
            "not release authorization",
        ):
            self.assertIn(phrase, text)

    def test_a5000_direct_artifact_records_hot_kernel_and_no_row_summary(self) -> None:
        payload = _load(DIRECT_ARTIFACT)
        metadata = payload["partner_metadata"]

        self.assertEqual(payload["body_count"], 8192)
        self.assertEqual(payload["partner"], "numba")
        self.assertEqual(payload["output_mode"], "force_summary")
        self.assertFalse(metadata["materializes_python_force_rows"])
        self.assertTrue(metadata["prepared_partner_columns_reused"])
        self.assertEqual(metadata["prepared_force_repeat_protocol"]["repeat"], 3)
        self.assertEqual(metadata["prepared_force_repeat_protocol"]["warmup"], 1)
        self.assertLess(metadata["prepared_force_repeat_protocol"]["median_force_kernel_sec"], 0.02)
        self.assertLess(metadata["force_summary_materialization_sec"], 0.01)
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_a5000_runner_row_passes_and_keeps_process_boundary_visible(self) -> None:
        summary = _load(RUNNER_SUMMARY)

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["json_pass_count"], 1)
        row = summary["rows"][0]
        self.assertEqual(row["row_id"], "barnes_hut_numba_scale_default_8192")
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["stderr_bytes"], 0)
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])
        self.assertGreater(row["elapsed_sec"], 1.0)

        payload = _load(ROOT / row["stdout_path"])
        metadata = payload["partner_metadata"]
        self.assertLess(metadata["prepared_force_repeat_protocol"]["median_force_kernel_sec"], 0.02)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()

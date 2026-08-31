from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3215_claude_review_intake_fused_count_hardening_2026-06-03.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3214_claude_review_fused_segment_pair_count_chain_2026-06-03.md"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
GOAL3213_TEST = ROOT / "tests" / "goal3213_rayjoin_dense_left_id_count_route_timing_test.py"
CLI_SMOKE = ROOT / "docs" / "reports" / "goal3212_dense_count_cli_smoke_2026-06-03.json"


class Goal3215ClaudeReviewIntakeFusedCountHardeningTest(unittest.TestCase):
    def test_claude_review_and_intake_report_are_present(self) -> None:
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("L1: Overflow flag written without atomics", review)
        self.assertIn("L2: Dense count columns reuse the general release symbol", review)
        self.assertIn("L3: Timing comparison chain cannot be fully verified", review)
        self.assertIn("Goal3215 closes those review findings", report)
        self.assertIn("does not authorize release", report)

    def test_low_severity_findings_are_machine_guarded(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        timing_test = GOAL3213_TEST.read_text(encoding="utf-8")

        self.assertIn("atomicOr(params.overflow, 1u)", workloads)
        self.assertIn("rtdl_optix_release_segment_pair_left_id_count_device_columns", prelude)
        self.assertIn("rtdl_optix_release_segment_pair_left_id_count_device_columns", api)
        self.assertIn("OPTIX_RELEASE_SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("release_symbol_name=OPTIX_RELEASE_SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn('self.assertFalse(baseline["include_rows_measured"])', timing_test)
        self.assertIn('self.assertTrue(baseline["validation_pass_include_rows"])', timing_test)

    def test_dense_count_cli_smoke_artifact_is_recorded(self) -> None:
        artifact = CLI_SMOKE.read_text(encoding="utf-8")

        self.assertIn("prepared_optix_left_id_dense_count_reuse", artifact)
        self.assertIn("segment_segment_intersection_count_by_left_id_dense_device_column", artifact)
        self.assertIn("rtdl_optix_prepared_segment_pair_left_id_count_device_columns", artifact)
        self.assertNotIn('"rows"', artifact)


if __name__ == "__main__":
    unittest.main()

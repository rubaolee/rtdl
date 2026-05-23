import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2520_raydb_style_partner_resident_closeout_2026-05-23.md"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"
GOAL2519_ARTIFACT = ROOT / "docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json"
GOAL2518_ARTIFACT = ROOT / "docs/reports/goal2518_partner_resident_fused_sum_count_timing_pod_2026-05-23.json"


class Goal2520RaydbStylePartnerResidentCloseoutTest(unittest.TestCase):
    def test_closeout_verdict_finishes_reconstruction_harness_not_raydb(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("complete as an RTDL language/runtime\nreconstruction harness", text)
        self.assertIn("not a RayDB reproduction", text)
        self.assertIn("not a SQL engine", text)
        self.assertIn("not a RayDB-specific engine", text)

    def test_closeout_records_completed_partner_resident_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "CPU oracle for grouped `count`, `sum`, `min`, `max`, and",
            "Embree count/sum parity",
            "OptiX count/sum parity",
            "Experimental OptiX partner-resident CUDA tensor descriptor path",
            "Native partner-resident grouped i64 `count`, `sum`, `min`, and `max`",
            "Explicit dense non-negative `group_capacity` contract",
            "Compact grouped output materialization",
            "Generic fused native `sum_count` grouped reduction",
            "run_optix_partner_resident_columnar_grouped_i64_reduction",
            "app dispatches by generic reduction names",
        ):
            self.assertIn(phrase, text)

    def test_closeout_backend_status_table_includes_final_modes_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("| CPU Python reference | Complete | `count`, `sum`, `min`, `max`, `avg_as_sum_count` |", text)
        self.assertIn("| Embree | Complete for parity slice | `count`, `sum` |", text)
        self.assertIn("| OptiX compatibility path | Complete for parity slice | `count`, `sum` |", text)
        self.assertIn(
            "| OptiX partner-resident experimental | Complete for benchmark slice | `count`, `sum`, `min`, `max`, `avg_as_sum_count` |",
            text,
        )

    def test_closeout_records_evidence_and_preserves_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("145 tests passed, 4 skipped", text)
        self.assertIn("goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json", text)
        self.assertIn("app direct low-level grouped symbols absent: `true`", text)
        self.assertIn("about `5.018x`", text)
        for blocked in (
            "public speedup",
            "whole-app speedup",
            "SQL",
            "DBMS",
            "authors-code",
            "true zero-copy",
        ):
            self.assertIn(blocked, text)

    def test_closeout_defers_authors_code_comparison_to_feasibility_gate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Authors-code performance comparison is a separate goal", text)
        self.assertIn("Goal2521", text)
        self.assertIn("same input/query/result contract", text)
        self.assertIn('"not comparable"', text)

    def test_readme_marks_slice_closed_and_separates_authors_code(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("As of Goal2520", text)
        self.assertIn("closed as an RTDL reconstruction\nharness", text)
        self.assertIn("one runtime dispatcher", text)
        self.assertIn("Authors-code performance comparison is intentionally separate", text)

    def test_referenced_artifacts_support_final_status(self) -> None:
        goal2519 = json.loads(GOAL2519_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(goal2519["status"], "ok")
        self.assertEqual(goal2519["dispatcher_reductions"], ["count", "sum", "min", "max", "sum_count"])
        self.assertIs(goal2519["app_uses_dispatcher"], True)
        self.assertIs(goal2519["app_direct_low_level_symbols_absent"], True)
        self.assertIs(goal2519["direct_dispatch_all_match_cpu_reference"], True)
        self.assertIs(goal2519["app_suite_all_match_cpu_reference"], True)

        goal2518 = json.loads(GOAL2518_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(goal2518["status"], "ok")
        self.assertIs(goal2518["rows_match_two_launch_reference"], True)
        self.assertGreater(goal2518["internal_fused_speedup_ratio_mean"], 1.0)
        self.assertIs(goal2518["public_speedup_claim_authorized"], False)
        self.assertIs(goal2518["true_zero_copy_claim_authorized"], False)


if __name__ == "__main__":
    unittest.main()

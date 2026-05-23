import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "docs/reports/goal2527_large_same_contract_external_pod_2026-05-23.json"
RTDL = ROOT / "docs/reports/goal2527_large_same_contract_rtdl_optix_pod_2026-05-23.json"
MATRIX = ROOT / "docs/reports/goal2527_large_same_contract_performance_matrix_pod_2026-05-23.json"
REPORT = ROOT / "docs/reports/goal2527_large_same_contract_performance_matrix_2026-05-23.md"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


class Goal2527LargeSameContractPerformanceMatrixTest(unittest.TestCase):
    def test_artifacts_record_large_same_contract_success(self) -> None:
        external = json.loads(EXTERNAL.read_text(encoding="utf-8"))
        rtdl = json.loads(RTDL.read_text(encoding="utf-8"))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(external["status"], "ok")
        self.assertEqual(rtdl["status"], "ok")
        self.assertEqual(matrix["status"], "ok")
        self.assertEqual(matrix["row_counts"], [1_000_000, 5_000_000, 10_000_000])
        self.assertEqual(matrix["group_capacity"], 1024)
        self.assertTrue(external["all_available_results_match_expected"])
        self.assertTrue(rtdl["all_available_results_match_expected"])
        self.assertTrue(matrix["all_available_results_match_expected"])
        self.assertFalse(matrix["performance_claim_authorized"])

    def test_performance_matrix_contains_expected_medians(self) -> None:
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        by_rows = {row["row_count"]: row for row in matrix["row_count_matrix"]}
        self.assertEqual(set(by_rows), {1_000_000, 5_000_000, 10_000_000})
        self.assertAlmostEqual(by_rows[1_000_000]["postgresql_ms"], 6.241950)
        self.assertAlmostEqual(by_rows[1_000_000]["duckdb_ms"], 4.087197)
        self.assertAlmostEqual(by_rows[1_000_000]["cudf_ms"], 42.533734)
        self.assertAlmostEqual(by_rows[1_000_000]["rtdl_full_contract_ms"], 1.601686)
        self.assertAlmostEqual(by_rows[5_000_000]["rtdl_full_contract_ms"], 1.986026)
        self.assertAlmostEqual(by_rows[10_000_000]["rtdl_full_contract_ms"], 2.425149)
        self.assertAlmostEqual(by_rows[10_000_000]["rtdl_three_launch_full_contract_ms"], 6.138255)
        self.assertGreater(by_rows[10_000_000]["rtdl_fused_vs_three_launch_speedup"], 2.0)
        self.assertGreater(by_rows[10_000_000]["postgresql_ms"], by_rows[10_000_000]["rtdl_full_contract_ms"])
        self.assertGreater(by_rows[10_000_000]["duckdb_ms"], by_rows[10_000_000]["rtdl_full_contract_ms"])
        self.assertGreater(by_rows[10_000_000]["cudf_ms"], by_rows[10_000_000]["rtdl_full_contract_ms"])

    def test_indexing_boundary_is_explicit(self) -> None:
        external = json.loads(EXTERNAL.read_text(encoding="utf-8"))
        pg_10m = external["systems"]["postgresql"]["10000000"]
        duckdb_10m = external["systems"]["duckdb"]["10000000"]
        self.assertIn("partial covering index", pg_10m["index_strategy"])
        self.assertIn("Index Only Scan using rtdl_goal2527_partial_group_cover_idx", pg_10m["explain_plan"])
        self.assertIn("ART indexes", duckdb_10m["index_strategy"])
        self.assertIn("PERFECT_HASH_GROUP_BY", duckdb_10m["explain_plan"])

    def test_partner_resident_large_row_guard_was_raised(self) -> None:
        source = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("kDeviceColumnGroupedMaxRowsPerJob = 100000000", source)
        self.assertIn("device-column grouped execution row_count must be in 1..100000000", source)
        self.assertIn("kColumnarMaxRowsPerJob = 1000000", source)

    def test_fused_stats_path_is_generic_and_exported(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL", runtime)
        self.assertIn("run_optix_partner_resident_columnar_grouped_stats_i64", runtime)
        self.assertIn('"stats"', runtime)
        self.assertIn("struct RtdlGroupedStatsRow", prelude)
        self.assertIn("using RtdlDbGroupedStatsRow = RtdlGroupedStatsRow;", prelude)
        self.assertIn("rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity", api)
        self.assertIn("RTDL_GROUPED_OP_STATS", workloads)
        self.assertNotIn("raydb", runtime.lower())

    def test_report_preserves_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Large Same-Contract Performance Matrix", report)
        self.assertIn("does not authorize public", report)
        self.assertIn("Parallel Index Only Scan", report)
        self.assertIn("RTDL full-contract is the fastest recorded full result path", report)
        self.assertIn("fused native `stats` launch", report)

    def test_closeout_and_readme_mark_app_complete_without_paper_claims(self) -> None:
        closeout = CLOSEOUT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        for text in (closeout, readme):
            self.assertIn("closed", text.lower())
            self.assertIn("fused", text)
            self.assertIn("1.601686", text)
        self.assertIn("not a RayDB paper reproduction", closeout)
        self.assertIn("No more work is required", closeout)
        self.assertIn("Goal2528", readme)


if __name__ == "__main__":
    unittest.main()
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"
CLOSEOUT = ROOT / "docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md"

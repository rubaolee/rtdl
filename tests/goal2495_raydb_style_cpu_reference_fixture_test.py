from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2495_raydb_style_cpu_reference_fixture_2026-05-22.md"
GENERIC_REF = ROOT / "src/rtdsl/columnar_aggregate_reference.py"


class Goal2495RaydbStyleCpuReferenceFixtureTest(unittest.TestCase):
    def test_generic_columnar_reference_is_exported(self) -> None:
        self.assertIsNotNone(rt.ColumnarRecordSet)
        self.assertIsNotNone(rt.ColumnarAggregatePlan)
        self.assertIsNotNone(rt.ColumnarAggregateResult)
        self.assertIsNotNone(rt.evaluate_columnar_grouped_aggregate)
        self.assertIsNotNone(rt.columnar_record_set_to_row_mappings)
        self.assertIsNotNone(rt.columnar_plan_to_grouped_query)
        self.assertIn("count", rt.SUPPORTED_AGGREGATES)

    def test_count_and_sum_outputs_match_fixture_oracle(self) -> None:
        count = app.run_result_mode("count")
        total = app.run_result_mode("sum")
        self.assertEqual(
            count["rows"],
            [
                {"region_id": 0, "count": 2},
                {"region_id": 1, "count": 1},
                {"region_id": 2, "count": 1},
            ],
        )
        self.assertEqual(
            total["rows"],
            [
                {"region_id": 0, "sum": 190},
                {"region_id": 1, "sum": 200},
                {"region_id": 2, "sum": 80},
            ],
        )

    def test_min_max_and_avg_as_sum_count_outputs_match_fixture_oracle(self) -> None:
        self.assertEqual(
            app.run_result_mode("min")["rows"],
            [
                {"region_id": 0, "min": 90},
                {"region_id": 1, "min": 200},
                {"region_id": 2, "min": 80},
            ],
        )
        self.assertEqual(
            app.run_result_mode("max")["rows"],
            [
                {"region_id": 0, "max": 100},
                {"region_id": 1, "max": 200},
                {"region_id": 2, "max": 80},
            ],
        )
        self.assertEqual(
            app.run_result_mode("avg_as_sum_count")["rows"],
            [
                {"region_id": 0, "sum": 190, "count": 2},
                {"region_id": 1, "sum": 200, "count": 1},
                {"region_id": 2, "sum": 80, "count": 1},
            ],
        )

    def test_cli_suite_runs_without_native_backends(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
                "--mode",
                "all",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn('"all_match_cpu_reference": true', proc.stdout)
        self.assertIn('"rt_core_accelerated": false', proc.stdout)

    def test_generic_reference_source_avoids_app_vocabulary(self) -> None:
        text = GENERIC_REF.read_text().lower()
        for forbidden in ("raydb", "sql", "database", "ssb"):
            self.assertNotIn(forbidden, text)

    def test_report_records_claim_boundary(self) -> None:
        text = REPORT.read_text()
        self.assertIn("CPU-only RayDB-style benchmark slice", text)
        self.assertIn("does not use Embree, OptiX", text)
        self.assertIn("native database-specific ABI", text)


if __name__ == "__main__":
    unittest.main()

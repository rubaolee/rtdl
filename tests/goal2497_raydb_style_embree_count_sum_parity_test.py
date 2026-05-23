from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2497_raydb_style_embree_count_sum_parity_2026-05-22.md"


def _require_embree() -> None:
    try:
        rt.embree_version()
    except Exception as exc:
        raise unittest.SkipTest(f"Embree backend unavailable: {exc}") from exc


class Goal2497RaydbStyleEmbreeCountSumParityTest(unittest.TestCase):
    def test_columnar_conversion_helpers_preserve_fixture_shape(self) -> None:
        rows = rt.columnar_record_set_to_row_mappings(app.make_fixture())
        query = rt.columnar_plan_to_grouped_query(app.make_plan("sum"))
        self.assertEqual(rows[0]["row_id"], 1)
        self.assertEqual(rows[0]["region_id"], 0)
        self.assertEqual(query["group_keys"], ("region_id",))
        self.assertEqual(query["value_field"], "revenue")

    def test_embree_unsupported_modes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "supports only count and sum"):
            app.run_result_mode("min", backend="embree")

    def test_report_records_no_new_native_abi_boundary(self) -> None:
        text = REPORT.read_text()
        self.assertIn("Goal2497 does not add native code", text)
        self.assertIn("transfer=\"columnar\"", text)
        self.assertIn("without\nadding a RayDB-specific native ABI", text)
        self.assertIn("Goal2498 should add OptiX parity", text)

    def test_embree_count_and_sum_match_cpu_oracle_when_available(self) -> None:
        _require_embree()
        count = app.run_result_mode("count", backend="embree")
        total = app.run_result_mode("sum", backend="embree")
        self.assertTrue(count["matches_cpu_reference"])
        self.assertTrue(total["matches_cpu_reference"])
        self.assertEqual(count["rows"], app.run_result_mode("count")["rows"])
        self.assertEqual(total["rows"], app.run_result_mode("sum")["rows"])

    def test_embree_cli_suite_runs_when_available(self) -> None:
        _require_embree()
        proc = subprocess.run(
            [
                sys.executable,
                "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
                "--backend",
                "embree",
                "--mode",
                "all",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn('"backend": "embree"', proc.stdout)
        self.assertIn('"matches_cpu_reference": true', proc.stdout)
        self.assertIn('"native_abi_added": false', proc.stdout)


if __name__ == "__main__":
    unittest.main()

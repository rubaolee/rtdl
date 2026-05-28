from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2498_raydb_style_optix_count_sum_parity_2026-05-22.md"
APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"


def _require_optix() -> None:
    try:
        rt.optix_version()
    except Exception as exc:
        raise unittest.SkipTest(f"OptiX backend unavailable: {exc}") from exc


class Goal2498RaydbStyleOptixCountSumParityTest(unittest.TestCase):
    def test_optix_backend_is_exposed_by_app(self) -> None:
        self.assertEqual(app.OPTIX_RESULT_MODES, ("count", "sum"))
        self.assertIn("optix", app.BACKENDS)
        source = APP.read_text(encoding="utf-8")
        self.assertIn("choices=BACKENDS", source)
        self.assertIn("rt.prepare_optix_columnar_record_set", source)
        self.assertIn('contract="columnar_grouped_aggregate_optix_columnar_payload"', source)

    def test_optix_unsupported_modes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "supports only count and sum"):
            app.run_result_mode("min", backend="optix")

    def test_optix_reuses_existing_generic_columnar_payload_symbols(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_columnar_payload_create_from_columns",
            "rtdl_optix_columnar_payload_grouped_reduction_count",
            "rtdl_optix_columnar_payload_grouped_reduction_sum",
        ):
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)

    def test_report_records_no_new_native_abi_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2498 does not add native code", text)
        self.assertIn("does not add any RayDB-specific native", text)
        self.assertIn("Fresh pod evidence is still required", text)
        self.assertIn("Authors-code timing or comparison.", text)

    def test_optix_count_and_sum_match_cpu_oracle_when_available(self) -> None:
        _require_optix()
        count = app.run_result_mode("count", backend="optix")
        total = app.run_result_mode("sum", backend="optix")
        self.assertTrue(count["matches_cpu_reference"])
        self.assertTrue(total["matches_cpu_reference"])
        self.assertEqual(count["rows"], app.run_result_mode("count")["rows"])
        self.assertEqual(total["rows"], app.run_result_mode("sum")["rows"])
        self.assertFalse(count["metadata"]["rt_core_accelerated"])
        self.assertFalse(count["metadata"]["native_abi_added"])

    def test_optix_cli_suite_runs_when_available(self) -> None:
        _require_optix()
        proc = subprocess.run(
            [
                sys.executable,
                "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
                "--backend",
                "optix",
                "--mode",
                "all",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn('"backend": "optix"', proc.stdout)
        self.assertIn('"all_match_cpu_reference": true', proc.stdout)
        self.assertIn('"native_abi_added": false', proc.stdout)


if __name__ == "__main__":
    unittest.main()

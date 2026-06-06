from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "raydb_style" / "rtdl_raydb_style_benchmark_app.py"


class Goal3575RaydbStatsModePartnerResidentTest(unittest.TestCase):
    def test_stats_mode_is_generic_columnar_and_partner_resident_scope(self) -> None:
        self.assertIn("stats", rt.SUPPORTED_AGGREGATES)
        self.assertIn("stats", app.CPU_RESULT_MODES)
        self.assertIn("stats", app.OPTIX_PARTNER_RESIDENT_RESULT_MODES)
        self.assertNotIn("stats", app.PAPER_RT_RESULT_MODES)

        plan = app.make_plan("stats")
        self.assertEqual(plan["aggregate"], "stats")
        self.assertEqual(plan["value_field"], "revenue")
        spec = rt.columnar_plan_to_grouped_reduction_spec(plan)
        self.assertEqual(spec.operation, "group_stats_i64")

    def test_cpu_oracle_stats_rows_match_fixture(self) -> None:
        result = app.run_result_mode("stats")
        self.assertEqual(
            result["rows"],
            [
                {"region_id": 0, "sum": 190, "count": 2, "min": 90, "max": 100},
                {"region_id": 1, "sum": 200, "count": 1, "min": 200, "max": 200},
                {"region_id": 2, "sum": 80, "count": 1, "min": 80, "max": 80},
            ],
        )
        self.assertEqual(result["metadata"]["aggregate"], "stats")
        self.assertFalse(result["metadata"]["rt_core_accelerated"])

    def test_partner_resident_lowering_declares_stats_without_releasing_claims(self) -> None:
        lowering = rt.plan_columnar_aggregate_lowering(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
        self.assertEqual(lowering.supported_aggregates, rt.SUPPORTED_AGGREGATES)
        self.assertEqual(lowering.unsupported_aggregates, ())
        self.assertIn("stats", lowering.claim_boundary)
        self.assertFalse(lowering.true_zero_copy_authorized)

    def test_cli_stats_mode_runs_without_native_backends(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(APP), "--mode", "stats"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn('"mode": "stats"', proc.stdout)
        self.assertIn('"sum": 190', proc.stdout)
        self.assertIn('"rt_core_accelerated": false', proc.stdout)


if __name__ == "__main__":
    unittest.main()

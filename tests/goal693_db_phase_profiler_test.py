from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal693DbPhaseProfilerTest(unittest.TestCase):
    def test_sales_risk_cpu_profiler_emits_phase_split(self) -> None:
        payload = run_json(
            "scripts/goal693_db_phase_profiler.py",
            "--scenario",
            "sales_risk",
            "--backend",
            "cpu",
            "--iterations",
            "1",
        )
        self.assertEqual(payload["app"], "database_analytics")
        self.assertEqual(payload["scenario"], "sales_risk")
        self.assertEqual(payload["optix_performance_class"], "python_interface_dominated")
        self.assertIn("sales_risk.query_conjunctive_scan_and_materialize", payload["phase_stats"])
        self.assertIn("sales_risk.query_grouped_count_and_materialize", payload["phase_stats"])
        self.assertIn("sales_risk.query_grouped_sum_and_materialize", payload["phase_stats"])
        self.assertIn("sales_risk.python_postprocess", payload["phase_stats"])
        self.assertEqual(payload["last_output"]["sales_risk"]["summary"]["highest_risk_region"], "west")

    def test_regional_cpu_reference_profiler_emits_phase_split(self) -> None:
        payload = run_json(
            "scripts/goal693_db_phase_profiler.py",
            "--scenario",
            "regional_dashboard",
            "--backend",
            "cpu_reference",
            "--iterations",
            "1",
        )
        self.assertEqual(payload["scenario"], "regional_dashboard")
        self.assertEqual(payload["copies"], 1)
        self.assertEqual(payload["scale_metadata"]["regional_dashboard"]["row_count"], 7)
        self.assertIn("regional_dashboard.python_input_construction", payload["phase_stats"])
        self.assertIn("regional_dashboard.backend_selection", payload["phase_stats"])
        self.assertIn("regional_dashboard.cpu_reference_execute_and_postprocess", payload["phase_stats"])
        output = payload["last_output"]["regional_dashboard"]
        self.assertEqual(output["backend"], "cpu_reference")
        self.assertIn("promo_order_ids", output["results"])

    def test_unified_db_app_cpu_backend_no_longer_crashes(self) -> None:
        payload = run_json("examples/rtdl_database_analytics_app.py", "--backend", "cpu")
        self.assertEqual(payload["app"], "database_analytics")
        self.assertEqual(payload["sections"]["regional_dashboard"]["backend"], "cpu_reference")
        self.assertEqual(payload["sections"]["sales_risk"]["backend"], "cpu")

    def test_scaled_copies_are_reported_for_all_scenarios(self) -> None:
        payload = run_json(
            "scripts/goal693_db_phase_profiler.py",
            "--scenario",
            "all",
            "--backend",
            "cpu",
            "--copies",
            "3",
            "--iterations",
            "1",
        )
        self.assertEqual(payload["copies"], 3)
        self.assertTrue(payload["scale_metadata"]["identical_inputs_across_backends"])
        self.assertEqual(payload["scale_metadata"]["regional_dashboard"]["row_count"], 21)
        self.assertEqual(payload["scale_metadata"]["regional_dashboard"]["expected_promo_order_ids"], 12)
        self.assertEqual(payload["scale_metadata"]["sales_risk"]["row_count"], 18)
        self.assertEqual(payload["scale_metadata"]["sales_risk"]["expected_scan_rows"], 12)
        self.assertEqual(payload["last_output"]["regional_dashboard"]["copies"], 3)
        self.assertEqual(payload["last_output"]["sales_risk"]["copies"], 3)
        self.assertEqual(payload["last_output"]["regional_dashboard"]["prepared_dataset"], None)
        self.assertGreaterEqual(payload["last_output"]["sales_risk"]["row_counts"]["scan"], 1)

    def test_summary_last_output_omits_large_rows(self) -> None:
        payload = run_json(
            "scripts/goal693_db_phase_profiler.py",
            "--scenario",
            "all",
            "--backend",
            "cpu",
            "--copies",
            "3",
            "--iterations",
            "1",
            "--last-output-mode",
            "summary",
        )
        self.assertEqual(payload["last_output_mode"], "summary")
        self.assertNotIn("results", payload["last_output"]["regional_dashboard"])
        self.assertNotIn("rows", payload["last_output"]["sales_risk"])
        self.assertNotIn("risky_order_ids", payload["last_output"]["sales_risk"]["summary"])
        self.assertIn("risky_order_count", payload["last_output"]["sales_risk"]["summary"])

    def test_rejects_non_positive_copies(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/goal693_db_phase_profiler.py",
                "--copies",
                "0",
                "--iterations",
                "1",
            ],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": "src:."},
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--copies must be positive", completed.stderr)


if __name__ == "__main__":
    unittest.main()

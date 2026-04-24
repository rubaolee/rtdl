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


class Goal756DbPreparedSessionPerfTest(unittest.TestCase):
    def test_cpu_backend_reports_one_shot_and_warm_session_timing(self) -> None:
        payload = run_json(
            "scripts/goal756_db_prepared_session_perf.py",
            "--backend",
            "cpu",
            "--scenario",
            "sales_risk",
            "--copies",
            "2",
            "--iterations",
            "2",
            "--strict",
        )
        self.assertEqual(payload["suite"], "goal756_db_prepared_session_perf")
        self.assertEqual(payload["schema_version"], "goal825_tier1_phase_contract_v1")
        self.assertIn("cloud_claim_contract", payload)
        result = payload["results"][0]
        self.assertEqual(result["backend"], "cpu")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["schema_version"], "goal825_tier1_phase_contract_v1")
        self.assertIn("prepared DB compact-summary sessions only", result["cloud_claim_contract"]["claim_scope"])
        self.assertIn("not SQL", result["cloud_claim_contract"]["non_claim"])
        self.assertIn("one_shot_total_sec", result)
        self.assertIn("prepared_session_warm_query_sec", result)
        self.assertIn("phase_contract", result)
        self.assertIn("reported_prepare_phases_sec", result)
        self.assertIn("reported_run_phases_sec", result)
        self.assertIn("reported_run_phase_modes", result)
        self.assertIn("reported_run_phases", result["phase_contract"])
        self.assertIn("reported_run_phase_modes", result["phase_contract"])
        self.assertEqual(result["prepared_session_output"]["execution_mode"], "prepared_session")
        self.assertIn("sales_risk", result["reported_run_phases_sec"])
        self.assertIn("sales_risk", result["reported_run_phase_modes"])
        self.assertIn(
            "query_conjunctive_scan_and_materialize_sec",
            result["reported_run_phases_sec"]["sales_risk"],
        )
        self.assertEqual(result["reported_run_phase_modes"]["sales_risk"]["scan"], "row_materializing")
        self.assertIn("GTX 1070", payload["boundary"])

    def test_phase_mode_helper_recognizes_summary_and_materializing_paths(self) -> None:
        module = __import__("scripts.goal756_db_prepared_session_perf", fromlist=["_reported_run_phase_modes"])
        modes = module._reported_run_phase_modes(
            {
                "sections": {
                    "regional_dashboard": {
                        "run_phases": {
                            "query_conjunctive_scan_count_sec": 0.1,
                            "query_grouped_count_summary_sec": 0.2,
                            "query_grouped_sum_summary_sec": 0.3,
                        }
                    },
                    "sales_risk": {
                        "run_phases": {
                            "query_conjunctive_scan_and_materialize_sec": 0.1,
                            "query_grouped_count_and_materialize_sec": 0.2,
                            "query_grouped_sum_and_materialize_sec": 0.3,
                        }
                    },
                }
            }
        )
        self.assertEqual(modes["regional_dashboard"]["scan"], "count_summary")
        self.assertEqual(modes["regional_dashboard"]["grouped_count"], "group_summary")
        self.assertEqual(modes["regional_dashboard"]["grouped_sum"], "group_summary")
        self.assertEqual(modes["sales_risk"]["scan"], "row_materializing")

    def test_optional_backend_failure_is_recorded_without_strict(self) -> None:
        payload = run_json(
            "scripts/goal756_db_prepared_session_perf.py",
            "--backend",
            "optix",
            "--scenario",
            "sales_risk",
            "--copies",
            "1",
            "--iterations",
            "1",
        )
        self.assertIn(payload["results"][0]["status"], {"ok", "skipped_or_failed"})


if __name__ == "__main__":
    unittest.main()

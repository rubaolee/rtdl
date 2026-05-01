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
        self.assertEqual(payload["schema_version"], "goal921_db_phase_review_contract_v2")
        self.assertIn("cloud_claim_contract", payload)
        result = payload["results"][0]
        self.assertEqual(result["backend"], "cpu")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["schema_version"], "goal921_db_phase_review_contract_v2")
        self.assertIn("prepared DB compact-summary sessions only", result["cloud_claim_contract"]["claim_scope"])
        self.assertIn("not SQL", result["cloud_claim_contract"]["non_claim"])
        self.assertIn("one_shot_total_sec", result)
        self.assertIn("prepared_session_warm_query_sec", result)
        self.assertIn("phase_contract", result)
        self.assertIn("reported_prepare_phases_sec", result)
        self.assertIn("reported_run_phases_sec", result)
        self.assertIn("reported_run_phase_modes", result)
        self.assertIn("reported_run_phase_totals_sec", result)
        self.assertIn("reported_native_db_phase_totals_sec", result)
        self.assertIn("db_review_observation", result)
        self.assertIn("reported_run_phases", result["phase_contract"])
        self.assertIn("reported_run_phase_modes", result["phase_contract"])
        self.assertIn("reported_run_phase_totals", result["phase_contract"])
        self.assertIn("reported_native_db_phase_totals", result["phase_contract"])
        self.assertIn("db_review_observation", result["phase_contract"])
        self.assertEqual(result["prepared_session_output"]["execution_mode"], "prepared_session")
        self.assertIn("sales_risk", result["reported_run_phases_sec"])
        self.assertIn("sales_risk", result["reported_run_phase_modes"])
        self.assertIn(
            "query_conjunctive_scan_and_materialize_sec",
            result["reported_run_phases_sec"]["sales_risk"],
        )
        self.assertEqual(result["reported_run_phase_modes"]["sales_risk"]["scan"], "row_materializing")
        self.assertEqual(
            result["reported_run_phase_totals_sec"]["row_materializing_operation_count"],
            3,
        )
        self.assertEqual(result["reported_native_db_phase_totals_sec"]["counter_status"], "empty")
        self.assertEqual(result["db_review_observation"]["status"], "not_claim_path")
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

    def test_native_phase_totals_and_observation_recognize_phase_clean_candidate(self) -> None:
        module = __import__(
            "scripts.goal756_db_prepared_session_perf",
            fromlist=[
                "_db_review_observation",
                "_reported_native_db_phase_totals",
                "_reported_run_phase_totals",
            ],
        )
        payload = {
            "sections": {
                "sales_risk": {
                    "run_phases": {
                        "query_conjunctive_scan_count_sec": 0.01,
                        "query_grouped_count_summary_sec": 0.02,
                        "query_grouped_sum_summary_sec": 0.03,
                        "python_summary_postprocess_sec": 0.004,
                    }
                }
            }
        }
        native = {
            "sales_risk": {
                "grouped_sum_summary": {
                    "traversal": 0.01,
                    "bitset_copyback": 0.002,
                    "exact_filter": 0.003,
                    "output_pack": 0.004,
                    "raw_candidate_count": 12,
                    "emitted_count": 3,
                }
            }
        }
        run_totals = module._reported_run_phase_totals(payload)
        native_totals = module._reported_native_db_phase_totals(native)
        observation = module._db_review_observation(
            output_mode="compact_summary",
            run_phase_totals=run_totals,
            native_phase_totals=native_totals,
        )

        self.assertAlmostEqual(run_totals["all_sections_query_sec"], 0.06)
        self.assertEqual(run_totals["compact_summary_operation_count"], 3)
        self.assertEqual(run_totals["row_materializing_operation_count"], 0)
        self.assertEqual(native_totals["counter_status"], "exported")
        self.assertEqual(native_totals["operation_count"], 1)
        self.assertAlmostEqual(native_totals["traversal_sec"], 0.01)
        self.assertEqual(native_totals["raw_candidate_count"], 12)
        self.assertEqual(observation["status"], "phase_clean_candidate_for_rtx_review")

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

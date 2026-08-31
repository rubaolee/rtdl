from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import rtdsl as rt
from scripts.goal3828_current_benchmark_scale_profile_runner import (
    _evaluate_hot_path_floor,
    _summarize_hot_path_floor,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3828_current_benchmark_scale_profile_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal4311_current_scale_timing_floor_guard_2026-06-11.md"


class Goal4311CurrentScaleTimingFloorGuardTest(unittest.TestCase):
    def test_runtime_floor_evaluation_accepts_numeric_metric_at_or_above_target(self) -> None:
        row = {
            "row_id": "synthetic_robot",
            "representative_hot_path_metric": "run_summary.phase_timing_seconds.traversal.total_sec",
            "hot_path_duration_target_sec": 1.0,
            "scale_calibration_status": "resident_high_repeat_summary_contract_goal3984",
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout = Path(tmp) / "row.json"
            stdout.write_text(
                json.dumps({"run_summary": {"phase_timing_seconds": {"traversal": {"total_sec": 1.25}}}}),
                encoding="utf-8",
            )
            evaluation = _evaluate_hot_path_floor(row, stdout)

        self.assertEqual(evaluation["status"], "floor_met_internal_evidence_only")
        self.assertTrue(evaluation["hot_path_duration_target_met"])
        self.assertEqual(evaluation["hot_path_duration_observed_sec"], 1.25)
        self.assertEqual(evaluation["metric_resolution_status"], "metric_numeric")
        self.assertFalse(evaluation["decision_grade_timing_authorized"])
        self.assertFalse(evaluation["public_speedup_claim_authorized"])

    def test_runtime_floor_evaluation_flags_subfloor_or_non_numeric_metrics(self) -> None:
        row = {
            "row_id": "synthetic_subfloor",
            "representative_hot_path_metric": "metadata.hot.total_sec",
            "hot_path_duration_target_sec": 1.0,
            "scale_calibration_status": "floor_required",
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout = Path(tmp) / "row.json"
            stdout.write_text(json.dumps({"metadata": {"hot": {"total_sec": 0.25}}}), encoding="utf-8")
            subfloor = _evaluate_hot_path_floor(row, stdout)
            stdout.write_text(json.dumps({"metadata": {"hot": {"total_sec": {"median": 0.25}}}}), encoding="utf-8")
            non_numeric = _evaluate_hot_path_floor(row, stdout)

        self.assertEqual(subfloor["status"], "subfloor_not_claim_grade")
        self.assertFalse(subfloor["hot_path_duration_target_met"])
        self.assertEqual(subfloor["metric_resolution_status"], "metric_numeric")
        self.assertEqual(non_numeric["status"], "metric_not_numeric")
        self.assertEqual(non_numeric["metric_resolution_status"], "metric_not_numeric")
        self.assertFalse(non_numeric["hot_path_duration_target_met"])

    def test_runtime_floor_evaluation_distinguishes_missing_metric_causes(self) -> None:
        row = {
            "row_id": "synthetic_missing",
            "representative_hot_path_metric": "metadata.hot.total_sec",
            "hot_path_duration_target_sec": 1.0,
            "scale_calibration_status": "floor_required",
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout = Path(tmp) / "row.json"
            missing_file = _evaluate_hot_path_floor(row, stdout)
            stdout.write_text(json.dumps({"metadata": {"cold": 1.0}}), encoding="utf-8")
            missing_path = _evaluate_hot_path_floor(row, stdout)

        self.assertEqual(missing_file["status"], "metric_not_numeric")
        self.assertEqual(missing_file["metric_resolution_status"], "stdout_json_missing_or_unparseable")
        self.assertEqual(missing_path["status"], "metric_not_numeric")
        self.assertEqual(missing_path["metric_resolution_status"], "metric_path_missing")

    def test_rows_without_floor_are_labeled_smoke_or_internal(self) -> None:
        row = {
            "row_id": "synthetic_smoke",
            "representative_hot_path_metric": "elapsed_sec",
            "hot_path_duration_target_sec": None,
            "scale_calibration_status": "internal_current_scale_not_claim_grade",
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout = Path(tmp) / "row.json"
            stdout.write_text(json.dumps({"elapsed_sec": 10.0}), encoding="utf-8")
            evaluation = _evaluate_hot_path_floor(row, stdout)

        self.assertEqual(evaluation["status"], "smoke_scale_or_internal_not_claim_grade")
        self.assertIsNone(evaluation["hot_path_duration_target_met"])
        self.assertFalse(evaluation["decision_grade_timing_authorized"])

    def test_runner_dry_run_exposes_floor_policy_for_all_ten_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry_run.json"
            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["summary"]["row_count"], 10)
        self.assertEqual(len(payload["rows"]), 10)
        self.assertIn("hot_path_floor_summary", payload)
        self.assertEqual(payload["hot_path_floor_summary"]["status"], "dry_run_policy_only_no_runtime_evaluation")
        self.assertFalse(payload["hot_path_floor_summary"]["decision_grade_timing_authorized"])
        self.assertEqual(
            set(payload["hot_path_floor_summary"]["targeted_floor_rows"]),
            {
                "robot_collision_optix_scale_default_1024_no_probe_reference",
                "raydb_style_optix_count_scale_default_262k",
            },
        )
        for row in payload["rows"]:
            evaluation = row["hot_path_floor_evaluation"]
            self.assertIn("representative_hot_path_metric", evaluation)
            self.assertFalse(evaluation["decision_grade_timing_authorized"])

    def test_summary_reports_subfloor_rows_without_authorizing_claims(self) -> None:
        rows = [
            {
                "row_id": "ok",
                "hot_path_floor_evaluation": {
                    "status": "floor_met_internal_evidence_only",
                    "hot_path_duration_target_sec": 1.0,
                },
            },
            {
                "row_id": "short",
                "hot_path_floor_evaluation": {
                    "status": "subfloor_not_claim_grade",
                    "hot_path_duration_target_sec": 1.0,
                },
            },
        ]
        summary = _summarize_hot_path_floor(rows)
        self.assertEqual(summary["status"], "needs_floor_attention")
        self.assertEqual(summary["subfloor_or_metric_missing_rows"], ("short",))
        self.assertFalse(summary["decision_grade_timing_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])

    def test_report_documents_goal4311_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4311",
            "hot_path_floor_evaluation",
            "smoke_scale_or_internal_not_claim_grade",
            "subfloor_not_claim_grade",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

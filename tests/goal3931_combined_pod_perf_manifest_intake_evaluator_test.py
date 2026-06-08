from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3931_evaluate_combined_pod_perf_manifest.py"
RUNNER = ROOT / "scripts" / "goal3927_combined_pod_perf_queue.py"
REPORT = ROOT / "docs" / "reports" / "goal3931_combined_pod_perf_manifest_intake_evaluator_2026-06-08.md"
SCRATCH = ROOT / "scratch" / "goal3931_manifest_test"


class Goal3931CombinedPodPerfManifestIntakeEvaluatorTest(unittest.TestCase):
    def setUp(self) -> None:
        SCRATCH.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_evaluator_accepts_synthetic_pass_manifest_with_bounded_recommendation(self) -> None:
        manifest = _manifest(unblocked=10.0, blocked=8.0)
        path = SCRATCH / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--output", str(SCRATCH / "intake.json")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        intake = json.loads(completed.stdout)

        self.assertEqual("accept_with_boundary", intake["status"])
        self.assertEqual(1.25, intake["rtdbscan"]["blocked_vs_unblocked_speedup"])
        self.assertEqual(
            "blocked_candidate_faster_review_before_promotion",
            intake["rtdbscan"]["recommendation"],
        )
        self.assertTrue(intake["rayjoin"]["all_cases_have_nested_subprobe_timing"])
        self.assertFalse(intake["claim_boundary"]["route_promotion_authorized"])

    def test_evaluator_rejects_claim_boundary_leak_and_missing_blocked_row(self) -> None:
        manifest = _manifest(unblocked=10.0, blocked=8.0)
        manifest["claim_boundary"]["release_authorized"] = True
        manifest["rtdbscan"] = [manifest["rtdbscan"][0]]
        path = SCRATCH / "bad_manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        intake = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("reject", intake["status"])
        self.assertTrue(any("release_authorized" in error for error in intake["errors"]))
        self.assertTrue(any("both blocked and unblocked" in error for error in intake["errors"]))

    def test_evaluator_accepts_goal3927_dry_run_manifest_shape(self) -> None:
        runner_dir = SCRATCH / "runner"
        subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--dry-run",
                "--output-dir",
                str(runner_dir),
                "--rtdl-optix-library",
                str(ROOT / "build" / "librtdl_optix.so"),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(runner_dir / "summary_manifest.json"),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        intake = json.loads(completed.stdout)

        self.assertEqual("accept_with_boundary", intake["status"])
        self.assertTrue(intake["planned_commands"]["required_commands_present"])
        self.assertTrue(intake["rayjoin"]["dry_run"])
        self.assertEqual("dry_run_planned_commands_only", intake["rtdbscan"]["recommendation"])

    def test_report_records_non_authorizing_intake_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("1.05x review threshold", text)
        self.assertIn("does not run performance tests", text)
        self.assertIn("route_promotion_authorized", source)
        self.assertIn("blocked_candidate_faster_review_before_promotion", source)


def _manifest(*, unblocked: float, blocked: float) -> dict[str, object]:
    return {
        "status": "pass",
        "source_commit": "abc1234",
        "source_commit_label": "abc1234",
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "rayjoin": {
            "gpu": "A5000",
            "wrapper_phase_timing_sec": {"total": 1.0},
            "cases": [
                {
                    "workload": "pip",
                    "loaded_case_reuse_enabled": True,
                    "rtdl_optix_execution_route": "loaded_case_reuse",
                    "subprobe_wrapper_phase_timing_sec": {"total": 0.5},
                }
            ],
        },
        "rtdbscan": [
            {
                "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
                "elapsed_sec": unblocked,
                "partner": "numba",
                "blocked": False,
                "claim_boundary": {
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "whole_app_speedup_claim_authorized": False,
                    "true_zero_copy_claim_authorized": False,
                },
            },
            {
                "mode": "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
                "elapsed_sec": blocked,
                "partner": "numba",
                "blocked": True,
                "claim_boundary": {
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "whole_app_speedup_claim_authorized": False,
                    "true_zero_copy_claim_authorized": False,
                },
            },
        ],
    }


if __name__ == "__main__":
    unittest.main()

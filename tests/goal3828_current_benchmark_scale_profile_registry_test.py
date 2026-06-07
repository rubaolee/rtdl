from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import rtdsl as rt
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3828_current_benchmark_scale_profile_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3828_current_benchmark_scale_profile_registry_2026-06-07.md"


class Goal3828CurrentBenchmarkScaleProfileRegistryTest(unittest.TestCase):
    def test_scale_profile_registry_covers_all_promoted_apps_without_claim_authorization(self) -> None:
        rows = rt.current_benchmark_scale_profiles()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["row_id"] for row in rows}), 10)

        validation = rt.validate_current_benchmark_scale_profiles()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

        for row in rows:
            self.assertEqual(row["profile_kind"], "default_scale", row["row_id"])
            self.assertEqual(row["stdout_policy"], "file_backed_stdout_required", row["row_id"])
            self.assertFalse(row["release_authorized"], row["row_id"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["row_id"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["row_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["row_id"])

    def test_calibrated_sizes_follow_goal3827_correction(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_scale_profiles()}

        self.assertIn("--point-count", rows["rt_dbscan"]["command"])
        self.assertIn("8192", rows["rt_dbscan"]["command"])
        self.assertNotIn("65536", rows["rt_dbscan"]["command"])

        self.assertIn("--pose-count", rows["robot_collision"]["command"])
        self.assertIn("1024", rows["robot_collision"]["command"])
        self.assertNotIn("4096", rows["robot_collision"]["command"])

        self.assertIn("--body-count", rows["barnes_hut"]["command"])
        self.assertIn("8192", rows["barnes_hut"]["command"])
        self.assertIn("--skip-validation", rows["barnes_hut"]["command"])

        self.assertTrue(rows["rt_dbscan"]["requires_numba"])
        self.assertTrue(rows["barnes_hut"]["requires_numba"])

    def test_summary_tracks_file_backed_stdout_rows(self) -> None:
        summary = rt.summarize_current_benchmark_scale_profiles()
        self.assertEqual(summary["version"], rt.CURRENT_BENCHMARK_SCALE_PROFILE_VERSION)
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["profile_kinds"], ("default_scale",))
        self.assertEqual(len(summary["file_backed_stdout_rows"]), 10)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_runner_dry_run_outputs_machine_readable_scale_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scale_profiles.json"
            completed = subprocess.run(
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
            self.assertIn("current_benchmark_scale_profiles.goal3828", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["file_backed_stdout_probe"])
        self.assertIsNone(payload["all_pass"])
        self.assertEqual(payload["summary"]["app_count"], 10)
        self.assertEqual(payload["summary"]["row_count"], 10)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertEqual(
            {row["stdout_policy"] for row in payload["rows"]},
            {"file_backed_stdout_required"},
        )

    def test_report_records_scale_profile_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3828",
            "calibrated scale-profile commands",
            "not use undrained stdout pipes",
            "file-backed runner",
            "rt_dbscan_optix_numba_scale_default_8192",
            "robot_collision_optix_scale_default_1024",
            "barnes_hut_numba_scale_default_8192",
            "Rows fail closed",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

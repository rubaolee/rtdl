from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3927_combined_pod_perf_queue.py"
REPORT = ROOT / "docs" / "reports" / "goal3927_repo_native_combined_pod_perf_queue_2026-06-08.md"
SCRATCH = ROOT / "scratch" / "goal3927_test_dry_run"


class Goal3927RepoNativeCombinedPodPerfQueueTest(unittest.TestCase):
    def tearDown(self) -> None:
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_runner_dry_run_writes_manifest_with_queued_diagnostics(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--dry-run",
                "--output-dir",
                str(SCRATCH),
                "--rtdl-optix-library",
                str(ROOT / "build" / "librtdl_optix.so"),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertIn("[goal3927] dry-run complete", completed.stdout)
        manifest = json.loads((SCRATCH / "summary_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("Goal3927", manifest["goal"])
        self.assertEqual("dry_run", manifest["status"])
        self.assertTrue(manifest["dry_run"])
        names = [row["name"] for row in manifest["planned_commands"]]
        self.assertEqual(
            [
                "rayjoin_subprobe",
                "rtdbscan_optix_rt_core_grouped_stream_numba_column_signature_3d",
                "rtdbscan_optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
            ],
            names,
        )
        self.assertFalse(manifest["claim_boundary"]["release_authorized"])
        self.assertFalse(manifest["claim_boundary"]["automatic_partner_selection_authorized"])

    def test_runner_source_has_fail_closed_prerequisites_progress_and_manifest_fields(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        for phrase in (
            "RTDL OptiX library not found",
            "RayJoin public CDB fixture missing",
            "[goal3927] RayJoin subprobe begin",
            "[goal3927] RTDBSCAN mode={mode} begin",
            "wrapper_phase_timing_sec",
            "subprobe_wrapper_phase_timing_sec",
            "loaded_case_reuse_enabled",
            "grouped_union_query_blocked_candidate",
            "automatic_partner_selection_authorized",
        ):
            self.assertIn(phrase, source)

    def test_report_declares_non_authorizing_orchestration_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("checked-in Python runner", text)
        self.assertIn("fails closed", text)
        self.assertIn("does not create performance evidence until", text)
        self.assertIn("does not auto-select partners", text)
        self.assertIn("summary_manifest.json", text)


if __name__ == "__main__":
    unittest.main()

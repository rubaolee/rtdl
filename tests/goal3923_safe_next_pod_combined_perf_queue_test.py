from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "handoff" / "GOAL3923_SAFE_NEXT_POD_COMBINED_PERF_QUEUE_2026-06-08.md"
REPORT = ROOT / "docs" / "reports" / "goal3923_safe_next_pod_combined_perf_queue_2026-06-08.md"


class Goal3923SafeNextPodCombinedPerfQueueTest(unittest.TestCase):
    def test_runbook_uses_stdin_safe_workspace_and_progress_logging(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("|", text)
        self.assertIn("ssh -o BatchMode=yes", text)
        self.assertIn("'bash -s'", text)
        self.assertIn('mktemp -d /root/goal3923_queue.XXXXXX', text)
        self.assertIn('test "$workdir" != "/root"', text)
        self.assertIn("PowerShell double-quoted SSH command", text)
        self.assertIn("[goal3923] RayJoin subprobe begin", text)
        self.assertIn("[goal3923] RayJoin subprobe done", text)
        self.assertIn("[goal3923] RTDBSCAN mode=$mode begin", text)
        self.assertIn("[goal3923] RTDBSCAN mode=$mode done", text)
        self.assertIn("[goal3923] complete", text)

    def test_runbook_queues_rayjoin_and_rtdbscan_without_unsafe_cleanup(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("scripts/goal3866_rayjoin_representative_scale_profile.py", text)
        self.assertIn("--data-dir /root/rtdl/data/rayjoin_public_cdb", text)
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", text)
        self.assertIn("optix_rt_core_grouped_stream_blocked_numba_column_signature_3d", text)
        self.assertIn("--grouped-union-query-block-size 4096", text)
        self.assertNotIn("rm -rf /root", text)
        self.assertNotIn("--output /root/goal3923", text)

    def test_runbook_declares_claim_boundary_and_manifest_shape(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("summary_manifest.json", text)
        self.assertIn("wrapper_phase_timing_sec", text)
        self.assertIn("subprobe_wrapper_phase_timing_sec", text)
        self.assertIn("loaded_case_reuse_enabled", text)
        self.assertIn('"release_authorized": False', text)
        self.assertIn('"automatic_partner_selection_authorized": False', text)
        self.assertIn("does not authorize public", text)

    def test_report_records_safe_queue_and_non_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal3913 RayJoin", text)
        self.assertIn("Goal3920 RT-DBSCAN", text)
        self.assertIn("stdin", text)
        self.assertIn("does not create performance evidence", text)


if __name__ == "__main__":
    unittest.main()

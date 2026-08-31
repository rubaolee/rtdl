from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3932_local_linux_combined_pod_queue_preflight_2026-06-08.md"


class Goal3932LocalLinuxCombinedPodQueuePreflightTest(unittest.TestCase):
    def test_report_records_successful_local_preflight_shape(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "192.168.1.20",
            "goal3927_combined_pod_perf_queue.py",
            "goal3931_evaluate_combined_pod_perf_manifest.py",
            "runner_status=dry_run",
            "planned_commands=3",
            "intake_status=accept_with_boundary",
            "required_commands_present=True",
        ):
            self.assertIn(phrase, text)

    def test_report_keeps_failed_pod_probe_and_non_authorization_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Permission denied (publickey,password)", text)
        self.assertIn("No A5000 evidence was collected", text)
        self.assertIn("preflight evidence only", text)
        self.assertIn("does not run performance workloads", text)
        self.assertIn("does not run performance workloads", text)
        self.assertIn("does not run performance workloads", text)
        self.assertIn("authorize route promotion", text)
        self.assertIn("authorize true-zero-copy claims", text)


if __name__ == "__main__":
    unittest.main()

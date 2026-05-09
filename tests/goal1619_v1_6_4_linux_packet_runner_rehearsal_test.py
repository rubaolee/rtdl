from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1619_v1_6_4_linux_packet_runner_rehearsal_2026-05-09.md"
JSON_ARTIFACT = ROOT / "docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.json"
MD_ARTIFACT = ROOT / "docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.md"


class Goal1619LinuxPacketRunnerRehearsalTest(unittest.TestCase):
    def test_linux_packet_runner_artifact_is_all_backend_accepted(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_packet_execution")
        self.assertEqual(tuple(payload["backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(tuple(payload["required_backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(payload["failed_subpackages"], [])
        self.assertTrue(payload["subpackages"]["goal1614_bounds_stress"]["accepted"])
        self.assertTrue(payload["subpackages"]["goal1615_reduced_copy_benchmark"]["accepted"])

    def test_report_records_gtx_rehearsal_not_rtx_performance(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("GTX 1070 behavior evidence only", text)
        self.assertIn("not representative RTX\nperformance evidence", text)
        self.assertIn("does not satisfy the\nrepresentative RTX packet requirement", text)

    def test_report_and_artifact_block_overclaiming(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        markdown = MD_ARTIFACT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("does not authorize public speedup wording", report)
        self.assertIn("true\nzero-copy wording", report)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", report)
        self.assertIn("release action", report)
        self.assertIn("packet-execution evidence", markdown)
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertFalse(payload["true_zero_copy_wording_authorized"])
        self.assertFalse(payload["stable_collect_k_promotion_authorized"])
        self.assertFalse(payload["release_action_authorized"])

    def test_external_reviews_and_consensus_accept_rehearsal_only(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1619_v1_6_4_linux_packet_runner_rehearsal_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1619_v1_6_4_linux_packet_runner_rehearsal_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1619_v1_6_4_linux_packet_runner_rehearsal_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("GTX 1070 all-backend packet-runner rehearsal", consensus)
        self.assertIn("does not accept representative RTX performance evidence", consensus)
        self.assertIn("next blocker is representative RTX pod evidence", consensus)


if __name__ == "__main__":
    unittest.main()

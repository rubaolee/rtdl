from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1804V2PartnerOptixPodPacketTest(unittest.TestCase):
    def test_runner_contains_required_pod_steps_and_claim_guards(self) -> None:
        runner = (ROOT / "scripts" / "goal1804_v2_partner_optix_pod_runner.sh").read_text(encoding="utf-8")
        self.assertIn("nvidia-smi", runner)
        self.assertIn("partner_probe.json", runner)
        self.assertIn("make build-optix", runner)
        self.assertIn("tests.goal1799_partner_anyhit_public_dispatch_test", runner)
        self.assertIn("tests.goal1787_optix_partner_anyhit_host_stage_test", runner)
        self.assertIn("for partner in numpy torch-cuda cupy-cuda", runner)
        self.assertIn('--partner "${partner}"', runner)
        self.assertIn('example_${partner}_optix.json', runner)
        self.assertIn("--backend optix", runner)
        self.assertIn("true_zero_copy_authorized", runner)
        self.assertIn("rt_core_speedup_claim_authorized", runner)
        self.assertIn("transfer_mode", runner)

    def test_report_preserves_no_pod_and_no_overclaim_boundary(self) -> None:
        report = (ROOT / "docs" / "reports" / "goal1804_v2_partner_optix_pod_packet_2026-05-12.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("No pod was started", report)
        self.assertIn("pre-pod-ready", report)
        self.assertIn("does not authorize", report)
        self.assertIn("true_zero_copy_authorized = false", report)
        self.assertIn("rt_core_speedup_claim_authorized = false", report)
        self.assertIn("GTX 1070", report)


if __name__ == "__main__":
    unittest.main()

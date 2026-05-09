from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_2026-05-09.md"
JSON_ARTIFACT = ROOT / "docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.json"
MD_ARTIFACT = ROOT / "docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.md"


class Goal1620RtxA4500CollectKPacketEvidenceTest(unittest.TestCase):
    def test_rtx_packet_artifact_is_required_backend_accepted(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_packet_execution")
        self.assertEqual(payload["environment_label"], "representative_rtx_a4500_required_backend_packet")
        self.assertEqual(tuple(payload["backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(tuple(payload["required_backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(payload["failed_subpackages"], [])
        self.assertTrue(payload["subpackages"]["goal1614_bounds_stress"]["accepted"])
        self.assertTrue(payload["subpackages"]["goal1615_reduced_copy_benchmark"]["accepted"])

    def test_report_records_representative_rtx_environment_and_build(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX A4500", text)
        self.assertIn("550.127.05", text)
        self.assertIn("OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`", text)
        self.assertIn("CUDA used for build: `/usr/local/cuda-12.4`", text)
        self.assertIn("make build-optix", text)
        self.assertIn("RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so", text)

    def test_report_accepts_packet_execution_but_blocks_overclaiming(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        markdown = MD_ARTIFACT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("ACCEPTED as representative RTX required-backend packet-execution evidence", report)
        self.assertIn("not public speedup evidence", report)
        self.assertIn("not true zero-copy evidence", report)
        self.assertIn("not stable\n`COLLECT_K_BOUNDED` promotion", report)
        self.assertIn("Stable promotion remains blocked", report)
        self.assertIn("Timing remains diagnostic only", markdown)
        self.assertFalse(payload["representative_rtx_performance_evidence_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertFalse(payload["true_zero_copy_wording_authorized"])
        self.assertFalse(payload["stable_collect_k_promotion_authorized"])
        self.assertFalse(payload["release_action_authorized"])

    def test_external_reviews_and_consensus_accept_rtx_packet_only(self) -> None:
        review_paths = (
            ROOT
            / "docs/reviews/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_claude_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_gemini_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("representative RTX\nrequired-backend packet-execution evidence", consensus)
        self.assertIn("timing remains\ndiagnostic", consensus)


if __name__ == "__main__":
    unittest.main()

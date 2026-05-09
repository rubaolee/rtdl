from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09_report.md"
JSON_ARTIFACT = ROOT / "docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.json"
MD_ARTIFACT = ROOT / "docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.md"


class Goal1622RtxA4500LatestMainReproPacketTest(unittest.TestCase):
    def test_latest_main_repro_packet_is_accepted_for_required_backends(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_packet_execution")
        self.assertEqual(payload["environment_label"], "representative_rtx_a4500_latest_main_repro_packet")
        self.assertEqual(payload["git_commit"], "6fde3868de2525414d9902afcbc9d24b64831113")
        self.assertEqual(tuple(payload["backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(tuple(payload["required_backends"]), ("fake_native", "embree", "optix"))
        self.assertEqual(payload["failed_subpackages"], [])
        self.assertTrue(payload["subpackages"]["goal1614_bounds_stress"]["accepted"])
        self.assertTrue(payload["subpackages"]["goal1615_reduced_copy_benchmark"]["accepted"])

    def test_report_records_pod_environment_and_latest_main_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("root@213.173.108.199 -p 18169", text)
        self.assertIn("6fde3868de2525414d9902afcbc9d24b64831113", text)
        self.assertIn("NVIDIA RTX A4500", text)
        self.assertIn("550.127.05", text)
        self.assertIn("git reset --hard origin/main", text)
        self.assertIn("representative_rtx_a4500_latest_main_repro_packet", text)

    def test_repro_packet_keeps_all_public_claim_flags_false(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        markdown = MD_ARTIFACT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("ACCEPTED as latest-main reproducibility evidence", report)
        self.assertIn("not public speedup evidence", report)
        self.assertIn("not true zero-copy evidence", report)
        self.assertIn("not stable\n`COLLECT_K_BOUNDED` promotion", report)
        self.assertIn("Stable promotion remains blocked", report)
        self.assertIn("Timing remains diagnostic only", markdown)
        self.assertFalse(payload["representative_rtx_performance_evidence_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertFalse(payload["true_zero_copy_wording_authorized"])
        self.assertFalse(payload["stable_collect_k_promotion_authorized"])
        self.assertFalse(payload["broad_rtx_wording_authorized"])
        self.assertFalse(payload["release_action_authorized"])

    def test_external_reviews_and_consensus_accept_repro_only(self) -> None:
        review_paths = (
            ROOT
            / "docs/reviews/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_claude_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_gemini_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPT", text.upper())
                self.assertIn("COLLECT_K_BOUNDED", text)

        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("latest-main reproducibility evidence", consensus)
        self.assertIn("not a stable-promotion consensus", consensus)
        self.assertIn("Stable promotion still requires a separate", consensus)


if __name__ == "__main__":
    unittest.main()

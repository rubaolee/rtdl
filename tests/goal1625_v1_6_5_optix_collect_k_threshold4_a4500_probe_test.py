from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe.py"
JSON_ARTIFACT = ROOT / "docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.json"
MD_ARTIFACT = ROOT / "docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.md"


class Goal1625OptixCollectKThreshold4A4500ProbeTest(unittest.TestCase):
    def test_probe_compares_optimized_baseline_to_gated_candidate(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE": "1"', text)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT": "1"', text)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS": "1"', text)
        self.assertIn("DEFAULT_COUNTS = (65536, 65537, 65538, 65552, 69632, 69633)", text)
        self.assertIn('"baseline": str(item["baseline"]), "gated": str(item["gated"])', text)

    def test_probe_records_internal_claim_boundary_only(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"public_speedup_wording_authorized": False', text)
        self.assertIn('"true_zero_copy_wording_authorized": False', text)
        self.assertIn('"stable_collect_k_promotion_authorized": False', text)
        self.assertIn('"broad_rtx_gpu_wording_authorized": False', text)
        self.assertIn('"release_action_authorized": False', text)
        self.assertIn("internal same-host OptiX collect-k threshold-4 diagnostic evidence only", text)

    def test_probe_summarizes_round_level_deltas_and_payload_copies(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"avg_delta_ms"', text)
        self.assertIn('"median_delta_ms"', text)
        self.assertIn('"faster_rounds"', text)
        self.assertIn('"baseline_payload_copies"', text)
        self.assertIn('"gated_payload_copies"', text)
        self.assertIn('"all_parity"', text)

    def test_a4500_artifact_records_strong_copy_reduction_regions(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        rows = {int(row["candidate_count"]): row for row in payload["rows"]}

        self.assertEqual(payload["status"], "internal_threshold4_a4500_probe_recorded")
        self.assertEqual(payload["git_commit"], "30c8cb9bb44c53544156163602509d57a13867b6")
        self.assertIn("NVIDIA RTX A4500", payload["gpu_summary"])
        for count in (65537, 65538, 65552, 69632):
            with self.subTest(count=count):
                row = rows[count]
                self.assertTrue(row["all_parity"])
                self.assertLess(row["gated_payload_copies"], row["baseline_payload_copies"])
                self.assertLess(row["median_delta_ms"], 0.0)
                self.assertGreaterEqual(row["faster_rounds"], 4)

    def test_a4500_artifact_keeps_no_copy_reduction_controls_non_claimed(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        rows = {int(row["candidate_count"]): row for row in payload["rows"]}

        self.assertEqual(rows[65536]["baseline_payload_copies"], 0)
        self.assertEqual(rows[65536]["gated_payload_copies"], 0)
        self.assertGreater(rows[65536]["median_delta_ms"], 0.0)
        self.assertLessEqual(rows[65536]["faster_rounds"], 1)

        self.assertEqual(rows[69633]["baseline_payload_copies"], 4)
        self.assertEqual(rows[69633]["gated_payload_copies"], 4)
        self.assertLess(abs(rows[69633]["median_delta_ms"]), 0.005)

    def test_a4500_artifact_blocks_public_claims(self) -> None:
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        markdown = MD_ARTIFACT.read_text(encoding="utf-8")

        for flag, value in payload["claim_flags"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)
        self.assertIn("internal same-host OptiX collect-k threshold-4 diagnostic evidence only", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)
        self.assertIn("does not authorize", payload["claim_boundary"])

    def test_external_reviews_and_consensus_accept_internal_scope_only(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPT", text.upper())
                self.assertIn("A4500", text)

        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("internal diagnostic evidence only", consensus)
        self.assertIn("Future public performance wording", consensus)


if __name__ == "__main__":
    unittest.main()

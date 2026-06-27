from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")
SCRIPT = ROOT / "scripts/v3_phoenix_rtnn_full_batch_float32_review_gate.py"


class V3PhoenixRtnnFullBatchFloat32ReviewGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_gate_blocks_m7_while_preserving_hot_signal(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "rtnn_full_batch_float32_review_blocked_not_m7")
        self.assertEqual(
            packet["evidence_status"],
            "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7",
        )
        self.assertEqual(packet["external_review_status"], "blocked_no_external_ai_verdict")
        self.assertEqual(packet["codex_review_status"], "approve_as_prepared_hot_query_intake_blocks_m7")
        self.assertFalse(packet["m7_candidate_reopen_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["whole_app_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        signal = packet["prepared_hot_query_internal_signal"]
        self.assertEqual(signal["point_count"], 1_048_576)
        self.assertEqual(signal["repeat"], 5)
        self.assertGreater(signal["hot_speedup_optix_over_cupy_grid"], 7.0)
        self.assertLess(signal["cold_plus_query_speedup_optix_over_cupy_grid"], 0.5)
        self.assertLess(signal["runner_wall_speedup_optix_over_cupy_grid"], 0.7)
        self.assertTrue(signal["same_contract_signature_match"])

    def test_required_blockers_cover_review_wall_scope_and_precision(self) -> None:
        blockers = set(self.packet["required_blockers_before_m7"])
        self.assertIn("external_ai_review_missing", blockers)
        self.assertIn("codex_consensus_response_missing_after_external_review", blockers)
        self.assertIn("cold_plus_query_wall_regresses", blockers)
        self.assertIn("runner_wall_regresses", blockers)
        self.assertIn("prepared_hot_query_scope_not_reviewed", blockers)
        self.assertIn("float32_exact_false_boundary_requires_wording", blockers)
        self.assertIn("pack_prepare_amortization_not_solved", blockers)
        self.assertIn("public_wording_review_missing", blockers)

    def test_review_records_are_present_and_external_attempt_failed(self) -> None:
        records = self.packet["review_records"]
        for key in ("call_for_review", "external_review_blocked", "gemini_stderr", "codex_blocking_review"):
            self.assertIn(key, records)
            self.assertTrue((ROOT / records[key]).exists(), key)
        blocked_text = (ROOT / records["external_review_blocked"]).read_text(encoding="utf-8")
        self.assertIn("No 2-AI closure exists", blocked_text)
        gemini_stderr = (ROOT / records["gemini_stderr"]).read_text(encoding="utf-8")
        self.assertIn("IneligibleTierError", gemini_stderr)

    def test_markdown_keeps_prepared_hot_only_boundary(self) -> None:
        markdown = self.markdown
        self.assertIn("This packet blocks M7 promotion", markdown)
        self.assertIn("Prepared hot-query OptiX/CuPy speedup: `7.790x`", markdown)
        self.assertIn("Cold-plus-query wall speedup: `0.393x`", markdown)
        self.assertIn("Runner-wall speedup: `0.627x`", markdown)
        self.assertIn("block end-to-end wording", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()

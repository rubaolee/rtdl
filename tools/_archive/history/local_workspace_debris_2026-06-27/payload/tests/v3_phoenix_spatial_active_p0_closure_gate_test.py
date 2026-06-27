from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.json"
PACKET_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.md"
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_active_p0_closure_gate.py"


class V3PhoenixSpatialActiveP0ClosureGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_claude_codex_consensus_closes_spatial_active_p0_only(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "spatial_active_p0_closed_current_v3_future_research")
        self.assertEqual(packet["external_review_verdict"], "close-active-p0")
        self.assertEqual(packet["external_review_source"], "claude")
        self.assertEqual(packet["external_review_status"], "external_verdict_present")
        self.assertTrue(packet["active_p0_closure_authorized"])
        self.assertFalse(packet["codex_consensus_required_after_external_review"])
        self.assertEqual(
            packet["codex_consensus_status"],
            "codex_consensus_complete_close_active_p0_future_research",
        )
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])

    def test_checks_preserve_active_queue_and_blocked_review_record(self) -> None:
        checks = self.packet["checks"]
        self.assertTrue(checks["spatial_queue_state_valid_for_gate_phase"])
        self.assertTrue(checks["review_gate_blocks_m7"])
        self.assertTrue(checks["author_basis_records_author_query_faster"])
        self.assertTrue(checks["claude_review_verdict_close_active_p0"])
        self.assertTrue(checks["codex_consensus_closes_active_p0_future_research"])
        self.assertTrue(checks["gemini_attempt_blocked"])
        self.assertTrue(checks["gemini_tool_failure_does_not_override_claude_verdict"])
        self.assertTrue(checks["external_blocked_record_says_not_verdict"])
        self.assertTrue(checks["real_external_verdict_present"])
        self.assertTrue(checks["closure_authorized_only_after_external_and_codex_consensus"])
        self.assertEqual(self.packet["failed_checks"], [])

    def test_evidence_points_to_current_spatial_author_gap(self) -> None:
        evidence = self.packet["evidence"]
        self.assertEqual(
            evidence["next_queue"],
            "docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json",
        )
        self.assertEqual(
            evidence["review_gate"],
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json",
        )
        self.assertEqual(
            evidence["call_for_review"],
            "docs/reviews/call_for_review_phoenix_v3_spatial_active_p0_closure_2026-06-21.md",
        )
        self.assertEqual(
            evidence["claude_review"],
            "docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md",
        )
        self.assertEqual(
            evidence["codex_consensus"],
            "docs/reviews/codex_phoenix_v3_spatial_active_p0_closure_2ai_consensus_2026-06-21.md",
        )
        self.assertAlmostEqual(evidence["same_dataset_author_query_ms"], 1.86566)
        self.assertGreater(evidence["rtdl_exact_f64_prepared_query_ms"], 6.0)
        self.assertGreater(evidence["rayjoin_author_query_speedup_vs_rtdl"], 3.0)

    def test_required_closure_conditions_include_real_external_review(self) -> None:
        required = set(self.packet["required_to_close_active_p0"])
        self.assertIn("real external AI verdict, not CLI stderr", required)
        self.assertIn("Codex consensus response after the external verdict", required)
        self.assertIn("machine update to next generic-engine queue", required)
        self.assertIn("release readiness gate rerun with generic queue changed", required)
        self.assertIn(
            "public wording that keeps RTDL-beats-RayJoin and broad V3-over-V2 false",
            required,
        )
        reopen = set(self.packet["reopen_conditions"])
        self.assertIn(
            "fresh same-dataset br_county.cdb POD packet with RTDL prepared-query median below 1.865660 ms with stable margin",
            reopen,
        )
        self.assertIn("stable exact count 47,262", reopen)

    def test_markdown_states_no_closure(self) -> None:
        markdown = self.markdown
        self.assertIn("Status: `spatial_active_p0_closed_current_v3_future_research`", markdown)
        self.assertIn("Active P0 closure authorized: `true`", markdown)
        self.assertIn("External review verdict: `close-active-p0`", markdown)
        self.assertIn("External review source: `claude`", markdown)
        self.assertIn("Codex consensus status: `codex_consensus_complete_close_active_p0_future_research`", markdown)
        self.assertIn("Gemini stderr", markdown)
        self.assertIn("RayJoin author Query speedup vs RTDL", markdown)
        self.assertIn("Reopen Conditions", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")
SCRIPT = ROOT / "scripts/v3_phoenix_aabb_native_query_handle_review_gate.py"


class V3PhoenixAabbNativeQueryHandleReviewGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PACKET_JSON.exists() or not PACKET_MD.exists():
            subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_gate_promotes_two_rows_while_preserving_release_boundary(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "aabb_native_query_handle_two_rows_m7_qualified_row_scoped")
        self.assertEqual(packet["evidence_status"], "aabb_native_query_handle_m7_candidate_pending_external_review")
        self.assertEqual(packet["external_review_status"], "claude_approve_with_conditions")
        self.assertEqual(
            packet["subagent_review_status"],
            "huygens_followup_local_blockers_closed_external_review_supersedes",
        )
        self.assertTrue(packet["m7_candidate_reopen_authorized"])
        self.assertTrue(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 2)
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertTrue(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(packet["whole_app_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["full_contact_solver_speedup_claim_authorized"])
        self.assertFalse(packet["broad_aabb_index_acceleration_claim_authorized"])
        signal = packet["material_signal_preserved"]
        self.assertGreaterEqual(signal["weakest_cold_plus_collect_wall_speedup"], signal["material_wall_speedup_floor"])
        self.assertGreater(signal["best_cold_plus_collect_wall_speedup"], 1.6)
        self.assertEqual(set(signal["grid_counts"]), {32_768, 65_536})

    def test_required_blockers_are_closed_after_claude_codex_consensus(self) -> None:
        blockers = set(self.packet["required_blockers_before_m7"])
        self.assertEqual(blockers, set())
        self.assertNotIn("stable_candidate_row_id_missing", blockers)
        self.assertNotIn("public_wording_review_missing", blockers)
        self.assertNotIn("fresh_run_stability_missing", blockers)
        self.assertNotIn("raw_aabb_oracle_missing", blockers)
        self.assertNotIn("remote_provenance_missing_or_weak", blockers)
        self.assertTrue(self.packet["raw_oracle_closes_correctness_blocker"])
        self.assertTrue(self.packet["source_manifest_provenance_closes_blocker"])
        self.assertTrue(self.packet["fresh_run_stability_closes_blocker"])
        self.assertTrue(self.packet["stable_candidate_row_id_gate_closed"])
        self.assertTrue(self.packet["candidate_wording_gate_present"])
        self.assertTrue(self.packet["public_wording_review_closed"])
        self.assertTrue(self.packet["codex_consensus_response_closed"])
        self.assertTrue(self.packet["claude_p1_conditions_applied"])
        self.assertTrue(self.packet["checks"]["claude_final_review_exists_and_approves_with_conditions"])
        self.assertTrue(self.packet["checks"]["codex_final_consensus_closes_p0"])
        self.assertTrue(self.packet["checks"]["all_promotion_blockers_closed"])
        self.assertEqual(
            self.packet["stable_candidate_row_ids"],
            [
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
            ],
        )

    def test_review_records_make_failed_review_and_huygens_block_visible(self) -> None:
        records = self.packet["review_records"]
        for key in (
            "candidate_evidence",
            "call_for_review",
            "final_call_for_review",
            "gemini_blocked",
            "gemini_stderr",
            "external_ai_blocked",
            "final_external_ai_blocked",
            "claude_final_review",
            "claude_final_review_stream",
            "codex_final_consensus",
            "huygens_review",
            "huygens_followup_review",
            "row_wording_gate",
        ):
            self.assertIn(key, records)
            self.assertTrue((ROOT / records[key]).exists(), key)
        self.assertIn("raw_oracle_expected", records)
        self.assertIn("stability_expected", records)
        self.assertTrue((ROOT / records["raw_oracle_expected"]).exists())
        gemini_text = (ROOT / records["gemini_blocked"]).read_text(encoding="utf-8")
        self.assertIn("not an external review verdict", gemini_text)
        final_call_text = (ROOT / records["final_call_for_review"]).read_text(encoding="utf-8")
        self.assertIn("Final M7 Review", final_call_text)
        self.assertIn(
            "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
            final_call_text,
        )
        final_blocked_text = (ROOT / records["final_external_ai_blocked"]).read_text(encoding="utf-8")
        self.assertIn("external_review_blocked_no_2ai_consensus", final_blocked_text)
        self.assertIn("claude.exe", final_blocked_text)
        self.assertIn("UNSUPPORTED_CLIENT", final_blocked_text)
        self.assertIn("Codex Chrome Extension", final_blocked_text)
        claude_text = (ROOT / records["claude_final_review"]).read_text(encoding="utf-8")
        self.assertIn("Verdict: `approve-with-conditions`", claude_text)
        self.assertIn("This review closes `external_ai_review_missing`", claude_text)
        consensus_text = (ROOT / records["codex_final_consensus"]).read_text(encoding="utf-8")
        self.assertIn("claude_codex_consensus_complete_approve_two_row_scoped_m7_rows", consensus_text)
        self.assertIn("OptiX prepare alone remains slower than Embree", consensus_text)
        huygens_text = (ROOT / records["huygens_review"]).read_text(encoding="utf-8")
        self.assertIn("Status: `blocked_as_is`", huygens_text)
        self.assertIn("Raw Embree/OptiX `range_intersection_rows`", huygens_text)
        followup_text = (ROOT / records["huygens_followup_review"]).read_text(encoding="utf-8")
        self.assertIn("Raw AABB oracle is adequately closed", followup_text)
        self.assertIn("No public speedup wording is allowed yet", followup_text)

    def test_remote_git_problem_is_countered_by_source_manifest(self) -> None:
        heads = self.packet["remote_git_heads_observed"]
        self.assertTrue(heads)
        self.assertTrue(any("fatal: not a git repository" in head for head in heads))
        self.assertEqual(len(self.packet["source_manifest_provenance_sha256"]), 64)
        self.assertTrue(self.packet["source_manifest_provenance_closes_blocker"])
        self.assertTrue(self.packet["checks"]["source_manifest_provenance_gate_closed_or_blocker_recorded"])

    def test_markdown_keeps_not_m7_boundary_and_decision_audit(self) -> None:
        markdown = self.markdown
        self.assertIn("promotes exactly two AABB native-query-handle rows", markdown)
        self.assertIn("Best cold-plus-collect wall speedup: `1.719x`", markdown)
        self.assertIn("Weakest cold-plus-collect wall speedup: `1.637x`", markdown)
        self.assertIn("Required Blockers Before M7", markdown)
        self.assertIn("- none", markdown)
        self.assertIn("M7 rows added: `2`", markdown)
        self.assertIn("OptiX prepare alone remains slower than Embree", markdown)
        self.assertIn("final_call_for_review", markdown)
        self.assertIn("claude_final_review", markdown)
        self.assertIn("codex_final_consensus", markdown)
        self.assertNotIn("stable_candidate_row_id_missing", markdown)
        self.assertIn("row_wording_gate", markdown)
        self.assertIn("not a Contact Manifold solver", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_approved_wording_is_post_review_not_candidate_draft(self) -> None:
        packet = self.packet
        self.assertEqual(len(packet["approved_row_scoped_public_wording"]), 2)
        for wording in packet["approved_row_scoped_public_wording"]:
            self.assertIn("OptiX prepare alone remains slower than Embree", wording)
            self.assertIn("row-scoped", wording)
            self.assertNotIn("candidate-only until external review", wording)
        for row in packet["candidate_rows"]:
            self.assertTrue(row["m7_promoted"])
            self.assertTrue(row["row_scoped_public_speedup_claim_authorized"])
            self.assertIn("approved_row_scoped_public_wording", row)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()

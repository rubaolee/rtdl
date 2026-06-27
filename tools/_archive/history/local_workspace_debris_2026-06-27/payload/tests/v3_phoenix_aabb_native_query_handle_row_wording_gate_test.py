from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")
SCRIPT = ROOT / "scripts/v3_phoenix_aabb_native_query_handle_row_wording_gate.py"


class V3PhoenixAabbNativeQueryHandleRowWordingGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PACKET_JSON.exists() or not PACKET_MD.exists():
            subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_stable_candidate_rows_are_defined_and_row_scoped_promoted(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review",
        )
        self.assertTrue(packet["stable_candidate_row_id_gate_closed"])
        self.assertTrue(packet["candidate_wording_gate_present"])
        self.assertTrue(packet["public_wording_review_closed"])
        self.assertEqual(packet["external_review_status"], "claude_approve_with_conditions")
        self.assertTrue(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 2)
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertTrue(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(packet["whole_app_speedup_claim_authorized"])
        self.assertFalse(packet["broad_aabb_index_acceleration_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(
            packet["candidate_row_ids"],
            [
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
            ],
        )

    def test_candidate_rows_preserve_material_signal_and_boundaries(self) -> None:
        rows = {row["aabb_count"]: row for row in self.packet["candidate_rows"]}
        self.assertEqual(set(rows), {32_768, 65_536})
        self.assertGreaterEqual(
            rows[32_768]["optix_over_embree_cold_plus_collect_wall_speedup"],
            self.packet["material_wall_speedup_floor"],
        )
        self.assertGreaterEqual(
            rows[65_536]["optix_over_embree_cold_plus_collect_wall_speedup"],
            self.packet["material_wall_speedup_floor"],
        )
        for row in rows.values():
            self.assertEqual(row["generic_capability"], "aabb_candidate_stream")
            self.assertEqual(row["operation"], "range_intersection_rows")
            self.assertTrue(row["app_is_evidence_harness_only"])
            self.assertTrue(row["same_contract"])
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertTrue(row["native_query_handle_cache_observed"])
            self.assertTrue(row["m7_promoted"])
            self.assertTrue(row["row_scoped_public_speedup_claim_authorized"])
            self.assertTrue(row["pre_review_draft_wording_superseded"])
            self.assertIsNone(row["draft_row_scoped_wording_not_publishable"])
            self.assertIn("OptiX prepare alone remains slower than Embree", row["approved_row_scoped_public_wording"])
            self.assertIn("OptiX prepare remains slower than Embree", row["prepare_phase_note"])

    def test_remaining_blockers_are_closed_after_external_review(self) -> None:
        blockers = set(self.packet["remaining_blockers_before_m7"])
        self.assertEqual(blockers, set())
        self.assertTrue(self.packet["checks"]["raw_oracle_closed"])
        self.assertTrue(self.packet["checks"]["stability_closed"])
        self.assertTrue(self.packet["checks"]["review_gate_or_final_reviews_close_public_wording"])
        self.assertTrue(self.packet["checks"]["gemini_final_attempt_recorded_as_blocked"])
        self.assertTrue(self.packet["checks"]["source_evidence_flags_remain_false"])
        self.assertEqual(self.packet["failed_checks"], [])

    def test_markdown_records_approved_wording_and_audit(self) -> None:
        markdown = self.markdown
        self.assertIn("approved row-scoped wording", markdown)
        self.assertIn("aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50", markdown)
        self.assertIn("aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50", markdown)
        self.assertIn("OptiX prepare alone remains slower than Embree", markdown)
        self.assertIn("OptiX prepare phase is faster than Embree", markdown)
        self.assertIn("- none", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()

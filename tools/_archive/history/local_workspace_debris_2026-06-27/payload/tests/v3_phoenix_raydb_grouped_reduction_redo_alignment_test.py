import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.json"
)
ALIGNMENT_MD = ALIGNMENT_JSON.with_suffix(".md")
SCALAR_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json"
)
DEVICE_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json"
)
SURFACE_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_release_surface_breadth_gate_2026-06-21.json"
)
CURRENT_STATUS = ROOT / "docs" / "rebuild" / "v3" / "v3_current_status_2026-06-20.md"


class V3PhoenixRaydbGroupedReductionRedoAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ALIGNMENT_JSON.read_text(encoding="utf-8"))
        cls.text = ALIGNMENT_MD.read_text(encoding="utf-8")
        cls.scalar = json.loads(SCALAR_PACKET.read_text(encoding="utf-8"))
        cls.device = json.loads(DEVICE_PACKET.read_text(encoding="utf-8"))
        cls.surface = json.loads(SURFACE_GATE.read_text(encoding="utf-8"))
        cls.current_status = CURRENT_STATUS.read_text(encoding="utf-8")

    def test_alignment_keeps_raydb_grouped_reduction_not_release(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "raydb_grouped_reduction_redo_aligned_reusable_capability_not_release",
        )
        self.assertEqual(payload["generic_capability"], "grouped_reduction")
        self.assertEqual(payload["app_probe"], "raydb_style")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertTrue(payload["row_scoped_public_speedup_claim_authorized_for_exact_rows_only"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["automatic_backend_or_partner_selection_authorized"])
        self.assertFalse(payload["app_specific_native_engine_logic_allowed"])

    def test_alignment_exactly_matches_current_grouped_reduction_surface_rows(self):
        rows = {row["row_id"]: row for row in self.payload["m7_rows_retained_as_internal_release_surface_evidence"]}
        expected = {
            "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
            "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
            "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
        }
        self.assertEqual(set(rows), expected)

        surface_rows = set(self.surface["evidence"]["m7_rows_by_capability"]["grouped_reduction"])
        self.assertEqual(surface_rows, expected)
        self.assertEqual(
            self.surface["evidence"]["m7_row_count_by_capability"]["grouped_reduction"],
            3,
        )
        self.assertFalse(self.surface["release_authorized"])
        self.assertFalse(self.surface["public_speedup_claim_authorized"])
        self.assertFalse(self.surface["broad_v3_faster_than_v2_claim_authorized"])

    def test_retained_rows_inherit_source_packet_boundaries(self):
        rows = {row["row_id"]: row for row in self.payload["m7_rows_retained_as_internal_release_surface_evidence"]}
        self.assertEqual(self.scalar["candidate_row_id"], "grouped_reduction_sum_scalar_broadcast_repeat100_262144")
        self.assertTrue(self.scalar["m7_promotion_authorized"])
        self.assertFalse(self.scalar["release_authorized"])
        self.assertFalse(self.scalar["broad_v3_faster_than_v2_claim_authorized"])

        device_rows = {row["row_id"]: row for row in self.device["candidate_rows"]}
        for row_id in (
            "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
            "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
        ):
            self.assertIn(row_id, device_rows)
            self.assertTrue(device_rows[row_id]["m7_promoted"])
            self.assertTrue(device_rows[row_id]["same_contract"])
            self.assertTrue(device_rows[row_id]["all_match_cpu_reference"])
            self.assertFalse(device_rows[row_id]["app_specific_native_engine_logic_allowed"])
            self.assertFalse(device_rows[row_id]["native_engine_customization"])
            self.assertFalse(device_rows[row_id]["true_zero_copy_authorized"])
            self.assertFalse(rows[row_id]["release_authorized"])
            self.assertFalse(rows[row_id]["broad_v3_faster_than_v2_claim_authorized"])
            self.assertEqual(
                rows[row_id]["m7_status"],
                "m7_row_evidence_scoped_not_release_after_claude_codex_consensus",
            )
            self.assertEqual(
                device_rows[row_id]["local_gate_reading"],
                "m7_row_evidence_scoped_not_release_after_claude_codex_consensus",
            )

        supersession = self.payload["device_column_review_supersession"]
        self.assertTrue(supersession["old_subagent_consensus_is_historical_only"])
        self.assertEqual(
            supersession["claude_external_review"],
            "docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md",
        )
        self.assertEqual(
            supersession["codex_supersession_consensus"],
            "docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md",
        )
        self.assertTrue(supersession["p1_status_fields_updated"])
        self.assertTrue(supersession["p1_source_manifest_orchestration_scope_acknowledged"])

    def test_redo_interpretation_blocks_gap1_and_broad_claim_overread(self):
        interpretation = self.payload["redo_interpretation"]
        self.assertTrue(interpretation["closed_as_reusable_engine_capability"])
        self.assertFalse(interpretation["counts_as_benchmark_app_development"])
        self.assertFalse(interpretation["counts_as_v4_or_embedding_work"])
        self.assertFalse(interpretation["counts_as_whole_raydb_or_database_product_claim"])
        self.assertFalse(interpretation["counts_as_broad_v3_over_v2_speedup"])
        self.assertFalse(interpretation["counts_as_productized_execution_path_gap1_completion"])
        self.assertIn("productized prepared execution/session runner", interpretation["why_not_gap1_completion"])

    def test_serious_v2x_context_remains_the_release_gate(self):
        context = self.payload["serious_v2x_context"]
        self.assertEqual(context["same_metric_comparison_count"], 52)
        self.assertAlmostEqual(context["overall_geomean_v3_speedup_vs_v2_14"], 1.0117790403434224)
        self.assertEqual(context["apps_with_geomean_gt_1_05"], 1)
        self.assertEqual(context["apps_with_geomean_lt_0_95"], 2)
        self.assertFalse(context["release_consideration_eligible"])
        self.assertIn("failed broad V2.14 vs Phoenix V3 performance gate", context["interpretation"])
        self.assertIn("status: redo_required", self.current_status)
        self.assertIn("serious_all_app_paired_evidence_failed_release_bar", self.current_status)

    def test_set_ab_note_prevents_rerun_bias(self):
        note = self.payload["set_a_set_b_measurement_note"]
        self.assertIn("Set-B", note["classification_for_future_all_app_scorecard"])
        self.assertIn("row-scoped controls", note["classification_for_future_all_app_scorecard"])
        self.assertTrue(note["freeze_before_run_required"])

    def test_markdown_is_handoff_readable_and_has_decision_audit(self):
        for phrase in (
            "raydb_grouped_reduction_redo_aligned_reusable_capability_not_release",
            "Exactly three grouped-reduction rows",
            "not V3 release authorization",
            "not broad V3-over-V2.x evidence",
            "do not complete Gap 1",
            "Set-B or row-scoped controls",
            "real Claude external review plus Codex supersession consensus",
            "subagent_codex_consensus_complete` record is historical only",
            "claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md",
            "Do not claim RTDL is a database engine",
            "## Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, self.text)

    def test_goal_level_decision_audit_has_required_four_answers(self):
        audit = self.payload["goal_level_decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("No.", audit["was_i_foolish"])
        self.assertIn("large row-scoped speedups", audit["foolish_actions"])
        self.assertIn("Retain the exact rows", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()

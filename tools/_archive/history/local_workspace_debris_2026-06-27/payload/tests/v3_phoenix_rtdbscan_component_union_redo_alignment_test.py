import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.json"
)
ALIGNMENT_MD = ALIGNMENT_JSON.with_suffix(".md")
OPTIMIZED_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.json"
)
NO_GO_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.json"
)
SURFACE_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_release_surface_breadth_gate_2026-06-21.json"
)
CURRENT_STATUS = ROOT / "docs" / "rebuild" / "v3" / "v3_current_status_2026-06-20.md"


class V3PhoenixRTDBSCANComponentUnionRedoAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ALIGNMENT_JSON.read_text(encoding="utf-8"))
        cls.text = ALIGNMENT_MD.read_text(encoding="utf-8")
        cls.optimized = json.loads(OPTIMIZED_PACKET.read_text(encoding="utf-8"))
        cls.no_go = json.loads(NO_GO_PACKET.read_text(encoding="utf-8"))
        cls.surface = json.loads(SURFACE_GATE.read_text(encoding="utf-8"))
        cls.current_status = CURRENT_STATUS.read_text(encoding="utf-8")

    def test_alignment_keeps_rtdbscan_component_union_not_release(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "rtdbscan_component_union_redo_aligned_reusable_capability_not_release",
        )
        self.assertEqual(payload["generic_capability"], "component_union")
        self.assertEqual(payload["app_probe"], "rt_dbscan")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertTrue(payload["row_scoped_public_speedup_claim_authorized_for_exact_rows_only"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["automatic_backend_or_partner_selection_authorized"])
        self.assertFalse(payload["app_specific_native_engine_logic_allowed"])

    def test_alignment_matches_current_component_union_surface_row(self):
        rows = {row["row_id"]: row for row in self.payload["m7_rows_retained_as_internal_release_surface_evidence"]}
        expected = {"component_union_clustered3d_65536_524288_repeat5_row_scoped"}
        self.assertEqual(set(rows), expected)

        surface_rows = set(self.surface["evidence"]["m7_rows_by_capability"]["component_union"])
        self.assertEqual(surface_rows, expected)
        self.assertEqual(
            self.surface["evidence"]["m7_row_count_by_capability"]["component_union"],
            1,
        )
        self.assertFalse(self.surface["release_authorized"])
        self.assertFalse(self.surface["public_speedup_claim_authorized"])
        self.assertFalse(self.surface["broad_v3_faster_than_v2_claim_authorized"])

    def test_retained_row_inherits_optimized_packet_boundaries(self):
        row = self.payload["m7_rows_retained_as_internal_release_surface_evidence"][0]
        claim = self.optimized["claim_boundary"]
        self.assertEqual(
            self.optimized["status"],
            "rtdbscan_component_signature_optimized_rtx_evidence_m7_approved_row_scoped",
        )
        self.assertEqual(self.optimized["generic_capability"], "component_union")
        self.assertTrue(claim["m7_promotion_authorized"])
        self.assertTrue(claim["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(claim["release_authorized"])
        self.assertFalse(claim["public_speedup_claim_authorized"])
        self.assertFalse(claim["whole_app_speedup_claim_authorized"])
        self.assertFalse(claim["paper_reproduction_claim_authorized"])
        self.assertFalse(claim["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["whole_app_speedup_claim_authorized"])
        self.assertFalse(row["paper_reproduction_claim_authorized"])
        self.assertFalse(row["broad_v3_faster_than_v2_claim_authorized"])

    def test_route_contract_blocks_native_dbscan_and_host_signature_materialization(self):
        route = self.payload["route_contract"]
        self.assertEqual(route["column_signature_strategy"], "numba_label_count_and_flag_count_label_columns")
        self.assertFalse(route["column_signature_materializes_point_ids"])
        self.assertFalse(route["column_signature_materializes_core_flags"])
        self.assertFalse(route["native_dbscan_abi_added"])
        self.assertFalse(route["full_dbscan_labels_claim_authorized"])
        self.assertEqual(route["embree_mode"], self.optimized["route_contract"]["embree_mode"])
        self.assertEqual(route["optix_mode"], self.optimized["route_contract"]["optix_mode"])

    def test_old_no_go_remains_context_not_public_claim(self):
        self.assertEqual(self.no_go["status"], "rtdbscan_continuation_bottleneck_no_go_not_promoted")
        self.assertFalse(self.no_go["m7_promotion_authorized"])
        self.assertIn("do_not_promote_rtdbscan_to_m7", self.no_go["verdict"])
        forbidden = "\n".join(self.payload["forbidden_readings"])
        self.assertIn("old 1483.603x", forbidden)
        self.assertIn("RT threshold phase alone", forbidden)
        self.assertTrue(
            self.payload["retained_evidence_summary"]["large_rows_continuation_still_dominates_at_262144_and_524288"]
        )

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

    def test_set_ab_note_keeps_rtdbscan_as_set_a_only_when_shared_path_is_measured(self):
        note = self.payload["set_a_set_b_measurement_note"]
        self.assertIn("Set-A candidate", note["classification_for_future_all_app_scorecard"])
        self.assertIn("shared component_union", note["classification_for_future_all_app_scorecard"])
        self.assertIn("Set-B controls", note["classification_for_future_all_app_scorecard"])
        self.assertTrue(note["freeze_before_run_required"])

    def test_markdown_is_handoff_readable_and_has_decision_audit(self):
        for phrase in (
            "rtdbscan_component_union_redo_aligned_reusable_capability_not_release",
            "Exactly one RTDBSCAN-linked row",
            "not full DBSCAN label publication",
            "not broad V3-over-V2.x performance evidence",
            "does not complete Gap 1",
            "Do not revive the old `1483.603x`",
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
        self.assertIn("1483.603x", audit["foolish_actions"])
        self.assertIn("Retain exactly one component_union row", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()

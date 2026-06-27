import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.json"
)
ALIGNMENT_MD = ALIGNMENT_JSON.with_suffix(".md")
DEFAULT_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json"
)
HOTPATH_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json"
)
SURFACE_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_release_surface_breadth_gate_2026-06-21.json"
)
CURRENT_STATUS = ROOT / "docs" / "rebuild" / "v3" / "v3_current_status_2026-06-20.md"


class V3PhoenixSpatialTopologyStreamRedoAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ALIGNMENT_JSON.read_text(encoding="utf-8"))
        cls.text = ALIGNMENT_MD.read_text(encoding="utf-8")
        cls.default_packet = json.loads(DEFAULT_PACKET.read_text(encoding="utf-8"))
        cls.no_go = json.loads(HOTPATH_NO_GO.read_text(encoding="utf-8"))
        cls.surface = json.loads(SURFACE_GATE.read_text(encoding="utf-8"))
        cls.current_status = CURRENT_STATUS.read_text(encoding="utf-8")

    def test_alignment_keeps_spatial_topology_stream_not_public_speedup(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "spatial_topology_stream_redo_aligned_internal_row_not_public_speedup",
        )
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["app_probe"], "spatial_rayjoin")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["v4_embedding_claim_authorized"])
        self.assertFalse(payload["app_specific_native_engine_logic_allowed"])

    def test_alignment_matches_current_point_location_surface_row(self):
        rows = {
            row["row_id"]
            for row in self.payload["m7_rows_retained_as_internal_release_surface_evidence"]
        }
        expected = {
            "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7"
        }
        self.assertEqual(rows, expected)

        surface_rows = set(self.surface["evidence"]["m7_rows_by_capability"]["point_location_topology_stream"])
        self.assertEqual(surface_rows, expected)
        self.assertEqual(
            self.surface["evidence"]["m7_row_count_by_capability"]["point_location_topology_stream"],
            1,
        )
        self.assertFalse(self.surface["release_authorized"])
        self.assertFalse(self.surface["public_speedup_claim_authorized"])
        self.assertFalse(self.surface["broad_v3_faster_than_v2_claim_authorized"])

    def test_retained_row_inherits_default_path_packet_boundaries(self):
        row = self.payload["m7_rows_retained_as_internal_release_surface_evidence"][0]
        packet = self.default_packet
        self.assertEqual(
            packet["status"],
            "spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary",
        )
        self.assertEqual(packet["candidate_row_id"], row["row_id"])
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertTrue(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 1)
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["paper_reproduction_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(row["paper_reproduction_claim_authorized"])

    def test_default_path_metrics_are_recorded_without_author_count_overread(self):
        evidence = self.payload["default_path_evidence"]
        candidate = self.default_packet["default_path_candidate"]
        summary = self.default_packet["summary"]
        self.assertEqual(evidence["exact_emitted_count"], 47262)
        self.assertEqual(candidate["emitted_counts"], [47262])
        self.assertEqual(candidate["raw_counts"], [47570])
        self.assertEqual(candidate["dropped_counts"], [308])
        self.assertTrue(candidate["row_count_consistent"])
        self.assertEqual(candidate["query_repeat"], 50)
        self.assertEqual(candidate["warmup"], 5)
        self.assertEqual(candidate["sample_repeat"], 7)
        self.assertAlmostEqual(evidence["default_path_median_ms"], 1.0805986821651459)
        self.assertAlmostEqual(evidence["default_path_worst_ms"], 1.083526760339737)
        self.assertAlmostEqual(evidence["author_query_ms"], 1.86566)
        self.assertAlmostEqual(evidence["default_path_speedup_vs_author_query_timer"], 1.7265058997313072)
        self.assertAlmostEqual(evidence["default_path_speedup_vs_disable_control"], 5.371926183589535)
        self.assertAlmostEqual(summary["default_path_speedup_vs_author_query_timer"], 1.7265058997313072)
        self.assertFalse(evidence["author_result_count_parity_verified"])
        self.assertFalse(evidence["author_result_count_printed"])
        self.assertFalse(self.default_packet["author_bar"]["author_result_count_parity_verified"])
        self.assertFalse(self.default_packet["author_bar"]["author_result_count_printed"])

    def test_historical_no_go_remains_warning_and_rejects_overcount_route(self):
        self.assertEqual(
            self.no_go["status"],
            "spatial_rayjoin_hotpath_probe_no_go_author_gap_not_closed",
        )
        self.assertFalse(self.no_go["m7_promotion_authorized"])
        self.assertFalse(self.no_go["release_authorized"])
        self.assertFalse(self.no_go["public_speedup_claim_authorized"])
        self.assertAlmostEqual(self.no_go["best_legal_route"]["prepared_query_ms"], 5.406518)
        self.assertAlmostEqual(self.no_go["same_dataset_author_gap"]["author_query_ms"], 1.86566)
        rejected = self.no_go["device_filtered_rejected_route"]
        self.assertTrue(rejected["excluded_from_m7"])
        self.assertEqual(rejected["observed_count"], 47570)
        self.assertEqual(rejected["exact_count"], 47262)
        self.assertEqual(rejected["candidate_minus_exact"], 308)

        context = self.payload["historical_no_go_context"]
        self.assertEqual(context["status"], "superseded_for_one_default_path_internal_row_but_retained_as_warning")
        self.assertTrue(context["device_filtered_route_rejected"])
        self.assertEqual(context["device_filtered_observed_count"], 47570)
        self.assertEqual(context["expected_exact_count"], 47262)

    def test_redo_interpretation_blocks_gap1_public_claims_and_app_tuning(self):
        interpretation = self.payload["redo_interpretation"]
        self.assertTrue(interpretation["closed_as_reusable_engine_capability"])
        self.assertFalse(interpretation["counts_as_benchmark_app_development"])
        self.assertFalse(interpretation["counts_as_rayjoin_paper_reproduction"])
        self.assertFalse(interpretation["counts_as_rtdl_beats_rayjoin_public_claim"])
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

    def test_set_ab_note_keeps_spatial_set_a_only_when_productized_path_is_measured(self):
        note = self.payload["set_a_set_b_measurement_note"]
        self.assertIn("Set-A probe", note["classification_for_future_all_app_scorecard"])
        self.assertIn("productized topology/point-location execution path", note["classification_for_future_all_app_scorecard"])
        self.assertTrue(note["freeze_before_run_required"])

    def test_markdown_is_handoff_readable_and_has_decision_audit(self):
        for phrase in (
            "spatial_topology_stream_redo_aligned_internal_row_not_public_speedup",
            "Exactly one Spatial-linked row",
            "not \"RTDL beats RayJoin\"",
            "author Query timer is a performance bar",
            "does not complete Gap 1",
            "Do not revive the device-filtered 47,570-count route",
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
        self.assertIn("RTDL-beats-RayJoin", audit["foolish_actions"])
        self.assertIn("Retain exactly one internal topology-stream row", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()

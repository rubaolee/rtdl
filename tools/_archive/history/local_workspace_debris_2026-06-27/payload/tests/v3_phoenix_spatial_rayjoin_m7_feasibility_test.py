import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md"


class V3PhoenixSpatialRayJoinM7FeasibilityTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_keeps_spatial_rayjoin_unpromoted(self):
        payload = self.load()
        self.assertEqual(payload["status"], "spatial_rayjoin_m7_feasibility_not_promoted")
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["current_packet_external_review_status"], "claude_approved_with_required_fixes")
        self.assertEqual(
            payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_no_m7_promotion",
        )
        self.assertIn("claude_phoenix_v3_spatial_rayjoin_m7_feasibility_review", payload["current_packet_external_review"])
        self.assertIn("codex_phoenix_v3_spatial_rayjoin_m7_feasibility_2ai_consensus", payload["current_packet_codex_consensus"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)

    def test_tiny_negative_row_and_hot_rows_are_separated(self):
        payload = self.load()
        tiny = payload["tiny_negative_row"]
        self.assertEqual(tiny["row"], "rayjoin_all_backend_query_summary")
        self.assertLess(tiny["optix_speedup_vs_embree"], 1.0)
        self.assertFalse(tiny["public_speedup_claim_authorized"])
        self.assertFalse(tiny["paper_result_comparison_allowed"])

        hot_rows = {row["row"]: row for row in payload["authored_hot_route_rows"]}
        self.assertGreater(hot_rows["rayjoin_overlay_seed_authored_tiled_x2048"]["optix_speedup_vs_embree"], 1000.0)
        self.assertGreater(hot_rows["rayjoin_lsi_authored_tiled_x2048"]["optix_speedup_vs_embree"], 100.0)
        self.assertGreater(hot_rows["rayjoin_pip_authored_tiled_x2048"]["optix_speedup_vs_embree"], 1.0)
        for row in hot_rows.values():
            self.assertEqual(row["classification"], "internal_hot_route_not_m7")
            self.assertEqual(
                row["evidence_basis"],
                "docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json",
            )

    def test_m5_pip_preserves_author_direction_and_same_contract_value(self):
        pip = self.load()["m5_pip_point_location"]
        self.assertEqual(pip["point_count"], 100000)
        self.assertEqual(pip["query_generation"], "backend_parity_filtered_random_bbox")
        self.assertEqual(pip["parity_filter_rejected_count"], 1)
        self.assertEqual(pip["exact_mismatch_count"], 0)
        self.assertFalse(pip["row_materialization_in_timed_path"])
        self.assertGreater(pip["rtdl_optix_speedup_vs_rtdl_embree"], 1.0)
        self.assertGreater(pip["rtdl_optix_native_traversal_speedup_vs_embree"], 1.0)
        self.assertGreater(pip["rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"], 3.0)
        self.assertFalse(pip["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(pip["public_speedup_claim_authorized"])

    def test_overlay_is_active_count_not_full_overlay(self):
        overlay = self.load()["m5_overlay_active_count"]
        self.assertEqual(overlay["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(overlay["active_count"], 174)
        self.assertEqual(overlay["optix_repeats"], 25)
        self.assertEqual(overlay["embree_repeats"], 25)
        self.assertTrue(overlay["active_counts_match"])
        self.assertTrue(overlay["row_materialization_avoided_in_timed_path"])
        self.assertGreater(overlay["optix_speedup_vs_rtdl_embree_timed_median"], 100.0)
        self.assertFalse(overlay["full_polygon_overlay_claim_authorized"])
        self.assertFalse(overlay["rayjoin_section57_full_reproduction_claim_authorized"])
        self.assertFalse(overlay["public_speedup_claim_authorized"])

    def test_blockers_and_report_text_prevent_public_overclaim(self):
        payload = self.load()
        for blocker in [
            "rayjoin_author_rt_faster_than_rtdl_optix",
            "not_full_rayjoin_paper_reproduction",
            "mixed_timing_basis_requires_public_methodology_review",
            "no_public_row_level_release_review",
            "no_future_public_row_2ai_consensus_for_spatial_rayjoin_m7_promotion",
        ]:
            self.assertIn(blocker, payload["m7_blockers"])
        self.assertIn("Do not claim RTDL beats RayJoin", payload["forbidden_public_reading"])

        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not M7 promotion",
            "rtdl_beats_rayjoin_claim_authorized: false",
            "RayJoin author RT is still faster than RTDL OptiX",
            "2ai_consensus_status: claude_codex_consensus_complete_no_m7_promotion",
            "tiny 0.034x row",
            "Phoenix M7-qualified release rows: 0",
            "OptiX and Embree repeats | 25 / 25",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

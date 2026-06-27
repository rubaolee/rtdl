import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
CALL_FOR_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md"
)


class V3PhoenixAABBCandidateStream32768M7FinalReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.review = CALL_FOR_REVIEW.read_text(encoding="utf-8")

    def test_packet_is_m7_qualified_row_scoped_not_release(self):
        self.assertEqual(
            self.payload["status"],
            "aabb_candidate_stream_32768_m7_qualified_row_scoped",
        )
        self.assertEqual(self.payload["generic_capability"], "aabb_candidate_stream")
        self.assertEqual(self.payload["candidate_row_id"], "aabb_candidate_stream_all_count_only_float32_32768")
        self.assertEqual(
            self.payload["current_packet_external_review_status"],
            "claude_approved_after_p0_wording_fix",
        )
        self.assertEqual(self.payload["current_packet_2ai_consensus_status"], "claude_codex_consensus_complete")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertTrue(self.payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["paper_reproduction_claim_authorized"])
        self.assertFalse(self.payload["librts_authors_code_claim_authorized"])
        self.assertFalse(self.payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertTrue(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 1)
        self.assertIn("claude_phoenix_v3_aabb_candidate_stream_32768", self.payload["external_review"])
        self.assertIn("codex_phoenix_v3_aabb_candidate_stream_32768", self.payload["codex_consensus"])

    def test_candidate_row_preserves_exact_scope_and_ratios(self):
        row = self.payload["candidate_row"]
        self.assertEqual(row["primitive_contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(row["generic_primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(row["numeric_contract"], "native_float32_inclusive_boundary")
        self.assertEqual(row["box_count"], 32768)
        self.assertEqual(row["point_query_count"], 32768)
        self.assertEqual(row["box_query_count"], 32768)
        self.assertEqual(row["operation"], "all_count_only")
        self.assertTrue(row["counts_match_between_backends"])
        self.assertTrue(row["matches_float32_cpu_reference"])
        self.assertFalse(row["matches_float64_cpu_reference"])
        self.assertAlmostEqual(row["query_optix_over_embree"], 814.3388221324167)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 132.75317674847796)
        self.assertAlmostEqual(row["elapsed_optix_over_embree"], 73.82647454204714)
        self.assertFalse(row["paper_equivalent_dataset"])
        self.assertFalse(row["authors_code_comparison"])
        self.assertFalse(row["native_engine_customization"])
        self.assertFalse(row["app_specific_native_engine_logic_allowed"])
        self.assertEqual(row["local_gate_reading"], "m7_qualified_row_scoped_after_claude_codex_consensus")
        self.assertTrue(row["m7_promoted"])

    def test_cpu_reference_evidence_discloses_precision_boundary(self):
        evidence = self.payload["cpu_reference_evidence"]
        self.assertEqual(evidence["float32_status"], "pass")
        self.assertEqual(evidence["float64_status"], "complete_with_expected_mismatch")
        self.assertIn("float32-inclusive", evidence["precision_contract_note"])
        deltas = self.payload["candidate_row"]["float64_mismatch_counts"]
        self.assertEqual(deltas["point_contains_delta_backend_minus_float64"], 10)
        self.assertEqual(deltas["range_contains_delta_backend_minus_float64"], 8)
        self.assertEqual(deltas["range_intersects_delta_backend_minus_float64"], 19)

    def test_v2_context_blocks_broad_speedup(self):
        context = self.payload["v2_14_context"]
        self.assertFalse(context["broad_v3_faster_than_v2_claim_authorized"])
        self.assertTrue(context["large_v2_14_optix_row_available"])
        self.assertFalse(context["large_v2_14_embree_row_available"])
        self.assertIn("not a V3-over-V2 performance improvement", context["interpretation"])

    def test_markdown_and_review_prompt_are_strict(self):
        for text in (self.text, self.review):
            self.assertIn("native_float32_inclusive_boundary", text)
            self.assertIn("814.339x", text)
            self.assertIn("132.753x", text)
            self.assertIn("float64", text)
            self.assertIn("not LibRTS", text)
        self.assertIn("V3-over-V2", text)
        self.assertIn("Do not claim the AABB row matches a float64 exact-geometry oracle", self.text)
        self.assertIn("Only `aabb_candidate_stream_all_count_only_float32_32768` is promoted", self.text)
        self.assertIn("Please be strict", self.review)
        self.assertIn("measured float32-inclusive query median", self.text)

    def test_closed_conditions_record_external_review_and_consensus(self):
        conditions = set(self.payload["closed_promotion_conditions"])
        self.assertIn("fresh_external_public_row_review_closed_by_claude", conditions)
        self.assertIn("reviewer_accepted_float32_numeric_contract_wording_after_p0_fix", conditions)
        self.assertIn("2_ai_consensus_closed_by_claude_codex", conditions)
        boundaries = set(self.payload["remaining_non_release_boundaries"])
        self.assertIn("float64 exact-geometry wording remains false", boundaries)
        closed = set(self.payload["closed_local_blockers"])
        self.assertIn("cpu_reference_skipped_and_matches_reference_null_closed_by_float32_oracle", closed)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
CALL_FOR_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md"
)
BLOCKED_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "external_review_blocked_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md"
)
CLAUDE_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_review_2026-06-21.md"
)
CODEX_CONSENSUS = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2ai_consensus_2026-06-21.md"
)


class V3PhoenixGroupedReductionSum262144M7FinalReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.review = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        cls.blocked_review = BLOCKED_REVIEW.read_text(encoding="utf-8")
        cls.claude_review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        cls.codex_consensus = CODEX_CONSENSUS.read_text(encoding="utf-8")

    def test_packet_promotes_one_row_without_releasing_v3(self):
        self.assertEqual(
            self.payload["status"],
            "grouped_reduction_sum_262144_m7_qualified_row_scoped",
        )
        self.assertEqual(self.payload["generic_capability"], "grouped_reduction")
        self.assertEqual(
            self.payload["candidate_row_id"],
            "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        )
        self.assertTrue(self.payload["local_evidence_sufficient_for_external_public_row_review"])
        self.assertTrue(self.payload["external_review_required_before_m7"])
        self.assertEqual(self.payload["current_packet_external_review_status"], "claude_approved")
        self.assertEqual(self.payload["current_packet_2ai_consensus_status"], "claude_codex_consensus_complete")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertTrue(self.payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertTrue(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 1)

    def test_candidate_row_is_exact_reusable_and_promoted(self):
        row = self.payload["candidate_row"]
        self.assertEqual(row["operation"], "group_sum_i64")
        self.assertEqual(row["generated_rows"], 262144)
        self.assertEqual(row["generated_groups"], 1024)
        self.assertEqual(row["warmup"], 3)
        self.assertEqual(row["repeat"], 100)
        self.assertFalse(row["partner_continuation_required"])
        self.assertTrue(row["same_contract"])
        self.assertTrue(row["all_match_cpu_reference"])
        self.assertFalse(row["app_specific_native_engine_logic_allowed"])
        self.assertFalse(row["native_engine_customization"])
        self.assertTrue(row["actual_repeat100_measured_not_modeled"])
        self.assertTrue(row["source_provenance_disclosed"])
        self.assertTrue(row["m7_promoted"])
        self.assertEqual(row["local_gate_reading"], "m7_qualified_row_scoped_after_claude_codex_consensus")
        self.assertAlmostEqual(row["hot_query_speedup_embree_over_optix"], 203.021747489659)
        self.assertAlmostEqual(row["actual_repeat100_loop_speedup"], 200.352573808868)
        self.assertAlmostEqual(row["actual_repeat100_cold_plus_loop_speedup"], 27.9170612400067)
        self.assertAlmostEqual(row["embree_cold_plus_loop_sec"], 102.218583457172)
        self.assertAlmostEqual(row["optix_cold_plus_loop_sec"], 3.66150944679975)
        self.assertEqual(row["embree_hit_event_count_before_dedup"], 1853)
        self.assertEqual(row["optix_hit_event_count_before_dedup"], 3693)
        self.assertIn("both rows match the CPU reference", row["hit_event_count_note"])

    def test_weaker_rows_are_excluded(self):
        excluded = {row["row_id"]: row for row in self.payload["excluded_rows"]}
        self.assertIn("grouped_reduction_sum_scalar_broadcast_repeat100_524288", excluded)
        self.assertIn("grouped_reduction_count_repeat100_262144", excluded)
        self.assertIn("grouped_reduction_count_repeat100_524288", excluded)
        self.assertEqual(
            excluded["grouped_reduction_sum_scalar_broadcast_repeat100_524288"]["reason"],
            "large_cold_prepare_cost_limits_public_claim",
        )
        self.assertAlmostEqual(
            excluded["grouped_reduction_sum_scalar_broadcast_repeat100_524288"][
                "actual_repeat100_cold_plus_loop_speedup"
            ],
            2.9834934390118,
        )
        for row_id in (
            "grouped_reduction_count_repeat100_262144",
            "grouped_reduction_count_repeat100_524288",
        ):
            self.assertEqual(excluded[row_id]["break_even_repeat_count_ceiling"], 14)
            self.assertFalse(excluded[row_id]["m7_promoted"])

    def test_closed_conditions_and_remaining_boundaries_are_explicit(self):
        closed = set(self.payload["closed_promotion_conditions"])
        self.assertIn("fresh_external_public_row_review_closed_by_claude", closed)
        self.assertIn("2_ai_consensus_closed_by_claude_codex", closed)
        self.assertIn("source_provenance_gap_documented", closed)
        remaining = "\n".join(self.payload["remaining_non_release_boundaries"])
        self.assertIn("release_authorized remains false", remaining)
        self.assertIn("broad_v3_faster_than_v2_claim_authorized remains false", remaining)
        self.assertIn("whole_app_speedup_claim_authorized remains false", remaining)

    def test_public_wording_is_approved_and_scoped(self):
        wording = self.payload["approved_row_scoped_public_wording"]
        self.assertIn("fixed-schema prepared grouped-sum workload", wording)
        self.assertIn("actual repeat=100", wording)
        self.assertIn("200.353x", wording)
        self.assertIn("27.917x", wording)
        self.assertIn("not a whole-app", wording)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("V3 is 200x faster", forbidden)
        self.assertIn("524,288 grouped_sum is the public row", forbidden)

    def test_markdown_and_review_prompt_preserve_decision_boundary(self):
        for text in (self.text, self.review):
            self.assertIn("grouped_reduction_sum_scalar_broadcast_repeat100_262144", text)
            self.assertIn("200.353x", text)
            self.assertIn("27.917x", text)
            self.assertIn("262,144", text)
            self.assertIn("524,288", text)
        self.assertIn("not V3 release authorization", self.text)
        self.assertIn("current_packet_external_review_status: claude_approved", self.text)
        self.assertIn("current_packet_2ai_consensus_status: claude_codex_consensus_complete", self.text)
        self.assertIn("source_manifest.sha256", self.text)
        self.assertIn("fatal: not a git repository", self.text)
        self.assertIn("Was I foolish?", self.text)
        self.assertIn("Approve this exact 262,144 grouped_sum row as M7-qualified?", self.review)

    def test_external_review_history_and_consensus_are_recorded(self):
        self.assertIn("claude_phoenix_v3_grouped_reduction_sum_262144", self.payload["external_review"])
        self.assertIn("codex_phoenix_v3_grouped_reduction_sum_262144", self.payload["codex_consensus"])
        self.assertIn(
            "external_review_blocked_phoenix_v3_grouped_reduction_sum_262144",
            self.payload["previous_external_review_blockage"],
        )
        self.assertIn("external review blocked, no M7 promotion", self.blocked_review)
        self.assertIn("Phoenix M7-qualified release rows: 0", self.blocked_review)
        self.assertIn("Option 1", self.claude_review)
        self.assertIn("Approve as M7-qualified", self.claude_review)
        self.assertIn("Claude/Codex consensus complete", self.codex_consensus)
        self.assertIn("row_scoped_public_speedup_claim_authorized: true", self.codex_consensus)

    def test_source_provenance_is_recorded(self):
        provenance = self.payload["source_provenance"]
        self.assertFalse(provenance["git_head_available"])
        self.assertEqual(provenance["traceability_basis"], "source_manifest.sha256")
        self.assertIn("src/rtdsl/optix_runtime.py", provenance["manifest_files"])
        self.assertEqual(provenance["source_version_value"], "v3-rebuild-2026-06-20")
        self.assertIn("pod artifact has no git HEAD", provenance["promotion_note"])


if __name__ == "__main__":
    unittest.main()

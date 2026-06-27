import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
CALL_FOR_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md"
)
CLAUDE_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md"
)


class V3PhoenixTrianglePreparedGraph80000M7FinalReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        cls.claude = CLAUDE_REVIEW.read_text(encoding="utf-8")

    def test_packet_is_final_review_candidate_not_promoted(self):
        self.assertEqual(
            self.payload["status"],
            "triangle_prepared_graph_chunk_80000_m7_qualified_row_scoped",
        )
        self.assertEqual(self.payload["generic_capability"], "prepared_graph_chunk")
        self.assertEqual(
            self.payload["candidate_row_id"],
            "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
        )
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertTrue(self.payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(self.payload["m113_graph_capture_claim_authorized"])
        self.assertTrue(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 1)
        self.assertTrue(self.payload["local_evidence_sufficient_for_external_public_row_review"])
        self.assertTrue(self.payload["external_review_required_before_m7"])
        self.assertEqual(
            self.payload["current_packet_external_review_status"],
            "claude_reviewed_approved_with_amendments_2026-06-21",
        )
        self.assertEqual(
            self.payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete",
        )
        self.assertEqual(
            self.payload["claude_review"],
            "docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md",
        )

    def test_exact_row_keeps_hot_wall_and_oracle_together(self):
        row = self.payload["row"]
        self.assertEqual(row["workload"], "Generated K4 clique ladder, 80,000 cliques")
        self.assertEqual(row["oracle_triangle_count"], 320000)
        self.assertTrue(row["oracle_match"])
        self.assertTrue(row["phase_timing_accept"])
        self.assertAlmostEqual(row["hot_optix_over_embree"], 347.23219125688223)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 6.342008514587283)
        self.assertGreater(row["hot_optix_over_embree"], row["wall_optix_over_embree"])

    def test_executor_linkage_is_narrow_non_graph_stream_only(self):
        resolutions = "\n".join(
            item["current_resolution"]
            for item in self.payload["closed_or_reframed_prior_blockers"]
        )
        self.assertIn("non-graph device-output stream", resolutions)
        self.assertIn("M113 graph capture remains blocked", resolutions)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("M113 graph capture is ready for Triangle", forbidden)
        self.assertIn("prepared_graph_chunk executor linkage is fully closed", forbidden)
        self.assertIn("Triangle V3 is 347x faster end to end", forbidden)
        self.assertIn("Triangle automatically selects the best partner", forbidden)
        self.assertIn(
            "exact 80,000-clique non-graph stream row is M7-qualified",
            forbidden,
        )
        wording = self.payload["draft_row_scoped_public_wording"]
        self.assertIn("measured benchmark wall-time median for this exact row", wording)
        self.assertIn("automatic partner selection", wording)
        self.assertIn("synthetic RT-Graph 2A1", wording)

    def test_markdown_and_review_request_are_strict(self):
        for text in (self.text, self.call):
            self.assertIn("347.232x", text)
            self.assertIn("6.342x", text)
            self.assertIn("non-graph", text)
            self.assertIn("M113 graph capture remains blocked", text)
            self.assertIn("not RT-Graph paper reproduction", text)
            self.assertIn("not graph database", text)
            self.assertIn("automatic partner selection", text)
        self.assertIn("claude_reviewed_approved_with_amendments_2026-06-21", self.text)
        self.assertIn("claude_codex_consensus_complete", self.text)
        self.assertIn(
            "claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md",
            self.text,
        )
        self.assertIn("Approve with amendments", self.claude)
        self.assertIn("No P0 blockers found", self.claude)
        self.assertIn("Was I foolish?", self.text)
        self.assertIn("Please be strict", self.call)


if __name__ == "__main__":
    unittest.main()

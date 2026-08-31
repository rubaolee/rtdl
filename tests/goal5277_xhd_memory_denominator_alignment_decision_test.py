import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5277_memory_denominator_alignment_decision_2026-07-09.json"
)
MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json"
)


class Goal5277XhdMemoryDenominatorAlignmentDecisionTest(unittest.TestCase):
    def test_decision_blocks_figure11_same_denominator_claim(self):
        payload = json.loads(DECISION.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["status"],
            "figure11_denominator_alignment_not_met__heavy_worklist_api_required",
        )
        self.assertFalse(payload["decision"]["same_denominator_author_figure11"])
        self.assertFalse(payload["decision"]["figure11_reproduced"])
        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_author_wl_and_wl_heavy_peak_semantics_are_distinct_from_rtdl(self):
        payload = json.loads(DECISION.read_text(encoding="utf-8"))
        author = payload["author_source_evidence"]["fields"]
        self.assertIn("in_queue + miss_queue", author["WL"]["semantics"])
        self.assertIn("2 * n_points_a * sizeof(uint32_t)", author["WL"]["semantics"])
        self.assertIn("heavy-cell offload queue", author["WL Heavy Peak"]["semantics"])
        rtdl = payload["rtdl_current"]
        self.assertEqual(
            rtdl["WL"]["status"],
            "estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
        )
        self.assertFalse(rtdl["WL"]["same_denominator_author_figure11"])
        self.assertFalse(rtdl["WL Heavy Peak"]["available"])
        self.assertFalse(rtdl["WL Heavy Peak"]["same_denominator_author_figure11"])

    def test_regenerated_bounded_matrix_uses_non_author_wl_status(self):
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertFalse(matrix["coverage"]["all_rows_same_denominator_author_figure11"])
        for row in matrix["rows"]:
            wl = row["author_mapped_fields"]["WL"]
            self.assertEqual(
                wl["status"],
                "estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
            )
            self.assertIn("not the author's Figure 11 WL denominator", wl["method"])
            self.assertFalse(row["same_denominator_author_figure11"])


if __name__ == "__main__":
    unittest.main()

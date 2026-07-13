from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5517ExactRangeContainsBatchTest(unittest.TestCase):
    def test_four_exact_count_matches_are_checkpointed(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5517_exact_range_contains_batch_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["case_count"], 4)
        self.assertEqual(result["matched_case_count"], 4)
        self.assertEqual(result["archive_extraction"]["selected_pair_count"], 4)
        expected = {104426, 117314, 120457, 112637}
        self.assertEqual({case["author"]["result_count"] for case in result["cases"]}, expected)
        self.assertTrue(all(case["matched"] for case in result["cases"]))
        self.assertTrue(result["evidence_integrity"]["same_files_passed_to_author_and_rtdl"])

    def test_claims_remain_bounded(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5517_exact_range_contains_batch_gate.json").read_text(
                encoding="utf-8"
            )
        )
        boundary = result["claim_boundary"]
        self.assertTrue(boundary["same_input_count_level_evidence_only"])
        self.assertFalse(boundary["complete_range_contains_matrix_claimed"])
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()

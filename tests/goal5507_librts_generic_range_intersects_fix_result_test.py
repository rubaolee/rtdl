from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps/librts-paper/results/goal5507_generic_range_intersects_fix_gate.json"


class Goal5507LibrtsGenericRangeIntersectsFixResultTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_bounded_runtime_gate_matches_author_and_source(self) -> None:
        self.assertEqual(self.payload["status"], "generic_float32_range_intersects_fix_completed")
        self.assertTrue(self.payload["checks"]["source_model_matches_author_on_all_cases"])
        self.assertTrue(self.payload["checks"]["rtdl_matches_author_on_all_cases"])
        self.assertTrue(self.payload["checks"]["rtdl_rows_match_counts_on_all_cases"])
        self.assertEqual(
            [(case["source_model_count"], case["author_runtime_count"], case["rtdl_runtime_count"])
             for case in self.payload["cases"]],
            [(5, 5, 5), (21, 21, 21)],
        )

    def test_full_paper_and_performance_claims_remain_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["generic_rtdl_core_fix_supported_by_source_and_runtime"])
        self.assertFalse(boundary["author_specific_behavior_copied_into_core"])
        self.assertFalse(boundary["full_official_archive_matrix_reproduced"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["paper_reproduction_claimed"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()

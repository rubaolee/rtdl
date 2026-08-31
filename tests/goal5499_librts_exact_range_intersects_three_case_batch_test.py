from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"


class Goal5499LibrtsExactRangeIntersectsThreeCaseBatchTest(unittest.TestCase):
    def test_three_exact_cases_match_and_use_distinct_queries(self):
        names = (
            "librts_goal5496_range_intersects_dtl_cnty_gate.json",
            "librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json",
            "librts_goal5499_range_intersects_dtl_cnty_select0001_gate.json",
        )
        payloads = [json.loads((RESULTS / name).read_text(encoding="utf-8")) for name in names]
        self.assertEqual(
            [payload["author"]["result_count"] for payload in payloads],
            [1570285, 242920, 239884],
        )
        for payload in payloads:
            self.assertTrue(payload["matched"])
            self.assertEqual(payload["author"]["load_factor"], "1")
            self.assertFalse(payload["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
            self.assertFalse(payload["claim_boundary"]["performance_ratio_authorized"])
        geometry_hashes = {payload["input_identity"]["geometry_sha256"] for payload in payloads}
        query_hashes = {payload["input_identity"]["query_sha256"] for payload in payloads}
        self.assertEqual(geometry_hashes, {"9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f"})
        self.assertEqual(len(query_hashes), 3)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"


class Goal5497LibrtsExactRangeIntersectsBatchEvidenceTest(unittest.TestCase):
    def test_two_exact_rows_match_and_preserve_count_only_boundary(self):
        paths = (
            RESULTS / "librts_goal5496_range_intersects_dtl_cnty_gate.json",
            RESULTS / "librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json",
        )
        payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        self.assertEqual([payload["status"] for payload in payloads], [
            "exact_input_range_intersects_count_matched",
            "exact_input_range_intersects_count_matched",
        ])
        self.assertEqual(
            [payload["author"]["result_count"] for payload in payloads],
            [1570285, 242920],
        )
        for payload in payloads:
            self.assertTrue(payload["matched"])
            self.assertTrue(payload["input_identity"]["same_files_passed_to_author_and_rtdl"])
            self.assertEqual(
                payload["input_identity"]["geometry_sha256"],
                "9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f",
            )
            self.assertEqual(payload["author"]["load_factor"], "1")
            self.assertFalse(payload["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
            self.assertFalse(payload["claim_boundary"]["performance_ratio_authorized"])

        self.assertNotEqual(
            payloads[0]["input_identity"]["query_sha256"],
            payloads[1]["input_identity"]["query_sha256"],
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5509RangeIntersectsNextBatchTest(unittest.TestCase):
    def test_case_manifest_is_exact_and_six_member_batch(self) -> None:
        cases = json.loads(
            (APP / "data" / "goal5509_range_intersects_next_exact_batch.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(cases), 6)
        self.assertEqual(
            {case["query_member"] for case in cases},
            {
                "PPoPPAE/datasets/queries/range-intersects_select_0.0001_queries_10000/"
                + suffix
                for suffix in (
                    "parks_Europe.wkt",
                    "parks.bz2.wkt",
                    "dtl_cnty.wkt",
                    "lakes.bz2.wkt",
                    "USACensusBlockGroupBoundaries.wkt",
                    "USADetailedWaterBodies.wkt",
                )
            },
        )
        self.assertEqual(
            len({case["geometry_member"] for case in cases}),
            6,
        )

    def test_gate_keeps_count_only_and_capacity_boundaries(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5509_exact_range_intersects_next_batch_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["query_family"], "range-intersects_select_0.0001_queries_10000")
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(result["matched_case_count"], 4)
        self.assertEqual(result["unresolved_case_count"], 2)
        self.assertEqual(result["coverage"]["cumulative_attempted_case_count"], 10)
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])
        self.assertFalse(result["claim_boundary"]["complete_paper_reproduction_claimed"])
        self.assertFalse(result["claim_boundary"]["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()

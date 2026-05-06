from __future__ import annotations

import unittest

import rtdsl as rt


def _score_rows(_left, _right, candidate_pairs):
    pairs = tuple(candidate_pairs)
    return (
        {
            "intersection_area": len(pairs),
            "left_area": 10,
            "right_area": 10,
            "union_area": 20 - len(pairs),
            "jaccard_similarity": len(pairs) / (20 - len(pairs)),
        },
    )


class Goal1414V151LegacyCandidatePairsContractBridgeTest(unittest.TestCase):
    def test_legacy_candidate_pairs_are_canonicalized_before_score_reduction(self) -> None:
        collection = {
            "primitive": "COLLECT_K_BOUNDED",
            "backend": "embree",
            "complete_candidate_coverage": True,
            "overflowed": False,
            "capacity": 2,
            "candidate_pairs": ((2, 20), (1, 10), (2, 20)),
        }

        result = rt.run_generic_polygon_set_jaccard_score_reduction(
            left=(),
            right=(),
            collection=collection,
            backend="embree",
            exact_score_fn=_score_rows,
        )

        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertEqual(result["summary"]["intersection_area"], 2)

    def test_legacy_candidate_pairs_fail_closed_on_capacity_overflow(self) -> None:
        collection = {
            "primitive": "COLLECT_K_BOUNDED",
            "backend": "embree",
            "complete_candidate_coverage": True,
            "overflowed": False,
            "capacity": 1,
            "candidate_pairs": ((1, 10), (2, 20)),
        }

        with self.assertRaisesRegex(RuntimeError, "overflow"):
            rt.run_generic_polygon_set_jaccard_score_reduction(
                left=(),
                right=(),
                collection=collection,
                backend="embree",
                exact_score_fn=_score_rows,
            )

    def test_legacy_candidate_pairs_reject_wrong_row_width(self) -> None:
        collection = {
            "primitive": "COLLECT_K_BOUNDED",
            "backend": "embree",
            "complete_candidate_coverage": True,
            "overflowed": False,
            "capacity": 1,
            "candidate_pairs": ((1, 10, 100),),
        }

        with self.assertRaisesRegex(ValueError, "candidate row width mismatch"):
            rt.run_generic_polygon_set_jaccard_score_reduction(
                left=(),
                right=(),
                collection=collection,
                backend="embree",
                exact_score_fn=_score_rows,
            )


if __name__ == "__main__":
    unittest.main()

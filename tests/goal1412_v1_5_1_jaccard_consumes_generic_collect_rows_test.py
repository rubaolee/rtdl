from __future__ import annotations

import unittest

import rtdsl as rt


def _score_rows(_left, _right, candidate_pairs):
    pairs = tuple(sorted(candidate_pairs))
    return (
        {
            "intersection_area": len(pairs),
            "left_area": 10,
            "right_area": 10,
            "union_area": 20 - len(pairs),
            "jaccard_similarity": len(pairs) / (20 - len(pairs)),
        },
    )


class Goal1412V151JaccardConsumesGenericCollectRowsTest(unittest.TestCase):
    def test_jaccard_score_reduction_accepts_candidate_id_rows_without_candidate_pairs(self) -> None:
        collection = rt.collect_k_bounded_rows(((2, 20), (1, 10)), k=2, row_width=2) | {
            "backend": "embree",
            "native_collection": False,
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

    def test_jaccard_summary_accepts_generic_collection_without_transition_field(self) -> None:
        collection = rt.collect_k_bounded_rows(((2, 20), (1, 10)), k=2, row_width=2) | {
            "backend": "optix",
            "native_collection": False,
        }

        result = rt.run_generic_polygon_set_jaccard_summary(
            left=(),
            right=(),
            collection=collection,
            backend="optix",
            exact_score_fn=_score_rows,
        )

        self.assertEqual(result["collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertEqual(result["summary"]["intersection_area"], 2)
        self.assertNotIn("candidate_pairs", result["collection"])

    def test_jaccard_rejects_wrong_width_generic_rows(self) -> None:
        collection = rt.collect_k_bounded_rows((1, 2), k=2, row_width=1) | {
            "backend": "embree",
            "native_collection": False,
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

from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_polygon_set_jaccard as jaccard_app
import rtdsl as rt


def _collection(backend: str):
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "backend": backend,
        "candidate_pairs": ((1, 10), (2, 11)),
        "capacity": 4,
        "emitted_count": 2,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "failure_mode": "fail_closed_overflow",
        "overflow_policy": "no_silent_truncation",
        "result_layout": "bounded_candidate_pair_ids",
        "native_collection": True,
    }


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


class Goal1320V15JaccardGenericScoreReductionTest(unittest.TestCase):
    def test_generic_score_reduction_metadata_requires_complete_collection(self) -> None:
        result = rt.run_generic_polygon_set_jaccard_score_reduction(
            left=(),
            right=(),
            collection=_collection("optix"),
            backend="optix",
            exact_score_fn=_score_rows,
        )

        self.assertEqual(result["primitive"], "POLYGON_SET_JACCARD_SCORE_REDUCTION")
        self.assertEqual(result["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["result_layout"], "summary_float64_sums_plus_ratio")
        self.assertEqual(result["summary_contract"]["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["summary_contract"]["result_layout"], "summary_float64_sums_plus_ratio")
        self.assertEqual(
            result["summary_contract"]["value_fields"],
            ("intersection_area", "left_area", "right_area", "union_area"),
        )
        self.assertTrue(result["summary_contract"]["integer_parity_required"])
        self.assertFalse(result["summary_contract"]["scalar_helper_direct_use"])
        self.assertIn(result["summary_contract"]["result_layout"], rt.V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS)
        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertEqual(result["summary"]["intersection_area"], 2)
        self.assertEqual(result["integer_parity_values"]["union_area"], 18)
        self.assertIn("query_polygon_jaccard_reduce_float_sum_sec", result["run_phases"])

    def test_generic_score_reduction_rejects_incomplete_collection(self) -> None:
        collection = _collection("embree") | {"complete_candidate_coverage": False}
        score_fn = mock.Mock(side_effect=_score_rows)

        with self.assertRaisesRegex(RuntimeError, "complete candidate coverage"):
            rt.run_generic_polygon_set_jaccard_score_reduction(
                left=(),
                right=(),
                collection=collection,
                backend="embree",
                exact_score_fn=score_fn,
            )

        score_fn.assert_not_called()

    def test_generic_jaccard_summary_embeds_score_reduction_metadata(self) -> None:
        result = rt.run_generic_polygon_set_jaccard_summary(
            left=(),
            right=(),
            collection=_collection("optix"),
            backend="optix",
            exact_score_fn=_score_rows,
        )

        self.assertEqual(result["score_reduction_primitive"], "POLYGON_SET_JACCARD_SCORE_REDUCTION")
        self.assertEqual(result["score_reduction"]["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["score_reduction"]["candidate_pair_count"], 2)
        self.assertEqual(result["summary"]["jaccard_similarity"], 2 / 18)

    def test_app_summary_exposes_generic_score_reduction_metadata(self) -> None:
        with (
            mock.patch.object(rt, "collect_polygon_pair_candidates_bounded_optix", return_value=_collection("optix")),
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=_score_rows),
        ):
            payload = jaccard_app.run_case("optix", copies=1, output_mode="summary", collection_capacity=4)

        generic = payload["generic_jaccard_summary"]
        self.assertEqual(generic["score_reduction_primitive"], "POLYGON_SET_JACCARD_SCORE_REDUCTION")
        self.assertEqual(generic["score_reduction"]["result_layout"], "summary_float64_sums_plus_ratio")
        self.assertEqual(payload["summary"]["intersection_area"], 2)


if __name__ == "__main__":
    unittest.main()

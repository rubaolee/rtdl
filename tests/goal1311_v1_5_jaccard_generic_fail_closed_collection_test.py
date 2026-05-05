from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_polygon_set_jaccard as jaccard_app
import rtdsl as rt


def _candidate_pairs(*_args, **_kwargs):
    return {(2, 11), (1, 10)}


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


class Goal1311V15JaccardGenericFailClosedCollectionTest(unittest.TestCase):
    def test_collect_k_bounded_succeeds_when_capacity_covers_all_pairs(self) -> None:
        result = rt.collect_k_bounded_candidate_pairs({(2, 11), (1, 10)}, k=2)

        self.assertEqual(result["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(result["candidate_pairs"], ((1, 10), (2, 11)))
        self.assertEqual(result["capacity"], 2)
        self.assertEqual(result["emitted_count"], 2)
        self.assertFalse(result["overflowed"])
        self.assertTrue(result["complete_candidate_coverage"])

    def test_collect_k_bounded_fails_closed_before_truncation(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "COLLECT_K_BOUNDED overflowed capacity 1"):
            rt.collect_k_bounded_candidate_pairs({(2, 11), (1, 10)}, k=1)

    def test_generic_jaccard_summary_runs_score_only_after_complete_collection(self) -> None:
        result = rt.run_generic_polygon_set_jaccard_summary(
            left=(),
            right=(),
            candidate_pairs={(2, 11), (1, 10)},
            backend="optix",
            exact_score_fn=_score_rows,
            collection_capacity=2,
        )

        self.assertEqual(result["collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(result["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertFalse(result["collection"]["overflowed"])
        self.assertEqual(result["summary"]["intersection_area"], 2)
        self.assertIn("query_polygon_collect_k_bounded_sec", result["run_phases"])

    def test_generic_jaccard_summary_does_not_call_score_after_overflow(self) -> None:
        score_fn = mock.Mock(side_effect=_score_rows)
        with self.assertRaisesRegex(RuntimeError, "fail_closed_overflow"):
            rt.run_generic_polygon_set_jaccard_summary(
                left=(),
                right=(),
                candidate_pairs={(2, 11), (1, 10)},
                backend="optix",
                exact_score_fn=score_fn,
                collection_capacity=1,
            )

        score_fn.assert_not_called()

    def test_generic_jaccard_summary_rejects_empty_score_rows_for_non_empty_candidates(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "exact_score_fn returned no rows"):
            rt.run_generic_polygon_set_jaccard_summary(
                left=(),
                right=(),
                candidate_pairs={(1, 10)},
                backend="embree",
                exact_score_fn=lambda *_args: (),
                collection_capacity=1,
            )

    def test_app_embree_summary_uses_generic_collection_metadata(self) -> None:
        with (
            mock.patch.object(jaccard_app, "_positive_candidate_pairs_embree", side_effect=_candidate_pairs),
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=_score_rows),
        ):
            payload = jaccard_app.run_case("embree", copies=1, output_mode="summary", collection_capacity=2)

        generic_summary = payload["generic_jaccard_summary"]
        self.assertEqual(payload["summary"]["intersection_area"], 2)
        self.assertEqual(generic_summary["collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertFalse(generic_summary["collection"]["overflowed"])
        self.assertEqual(payload["primitive_contract"]["bounded_collection_policy"]["failure_mode"], "fail_closed_overflow")

    def test_app_embree_summary_fails_closed_before_score_on_overflow(self) -> None:
        score_fn = mock.Mock(side_effect=_score_rows)
        with (
            mock.patch.object(jaccard_app, "_positive_candidate_pairs_embree", side_effect=_candidate_pairs),
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=score_fn),
        ):
            with self.assertRaisesRegex(RuntimeError, "COLLECT_K_BOUNDED overflowed capacity 1"):
                jaccard_app.run_case("embree", copies=1, output_mode="summary", collection_capacity=1)

        score_fn.assert_not_called()


if __name__ == "__main__":
    unittest.main()

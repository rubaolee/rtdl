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


class Goal1318V15JaccardNativeCollectionRoutingTest(unittest.TestCase):
    def test_generic_jaccard_accepts_native_collection_metadata(self) -> None:
        result = rt.run_generic_polygon_set_jaccard_summary(
            left=(),
            right=(),
            collection=_collection("optix"),
            backend="optix",
            exact_score_fn=_score_rows,
        )

        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertTrue(result["collection"]["native_collection"])
        self.assertEqual(result["collection"]["backend"], "optix")
        self.assertEqual(result["summary"]["intersection_area"], 2)

    def test_app_routes_optix_summary_through_native_bounded_collector(self) -> None:
        with (
            mock.patch.object(
                rt,
                "collect_polygon_pair_candidates_bounded_optix",
                return_value=_collection("optix"),
            ) as collect_fn,
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=_score_rows),
        ):
            payload = jaccard_app.run_case("optix", copies=1, output_mode="summary", collection_capacity=4)

        collect_fn.assert_called_once()
        self.assertEqual(payload["candidate_row_count"], 2)
        self.assertTrue(payload["generic_jaccard_summary"]["collection"]["native_collection"])
        self.assertEqual(payload["summary"]["intersection_area"], 2)

    def test_app_falls_back_when_native_collector_symbol_is_missing(self) -> None:
        with (
            mock.patch.object(
                rt,
                "collect_polygon_pair_candidates_bounded_embree",
                side_effect=ValueError("rtdl_embree_collect_shape_pair_candidates_bounded missing"),
            ),
            mock.patch.object(jaccard_app, "_positive_candidate_pairs_embree", return_value={(1, 10)}),
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=_score_rows),
        ):
            payload = jaccard_app.run_case("embree", copies=1, output_mode="summary", collection_capacity=4)

        collection = payload["generic_jaccard_summary"]["collection"]
        self.assertFalse(collection["native_collection"])
        self.assertEqual(collection["native_collection_backend"], "python_lsi_pip_fallback")
        self.assertEqual(payload["candidate_row_count"], 1)

    def test_app_native_collection_overflow_stops_before_score(self) -> None:
        score_fn = mock.Mock(side_effect=_score_rows)
        with (
            mock.patch.object(
                rt,
                "collect_polygon_pair_candidates_bounded_optix",
                side_effect=RuntimeError("native bounded OptiX polygon-pair candidate collection overflowed"),
            ),
            mock.patch.object(jaccard_app, "_native_jaccard_rows_for_candidates", side_effect=score_fn),
        ):
            with self.assertRaisesRegex(RuntimeError, "native bounded OptiX"):
                jaccard_app.run_case("optix", copies=1, output_mode="summary", collection_capacity=1)

        score_fn.assert_not_called()


if __name__ == "__main__":
    unittest.main()

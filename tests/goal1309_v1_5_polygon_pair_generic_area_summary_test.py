from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app


class Goal1309V15PolygonPairGenericAreaSummaryTest(unittest.TestCase):
    def test_generic_polygon_area_summary_metadata(self) -> None:
        result = rt.run_generic_polygon_pair_exact_area_summary(
            left=("left",),
            right=("right",),
            candidate_pairs={(1, 10), (2, 11)},
            backend="optix",
            exact_summary_fn=lambda _left, _right, _pairs: {
                "overlap_pair_count": 2,
                "total_intersection_area": 5,
                "total_union_area": 17,
            },
        )

        self.assertEqual(result["primitive"], "POLYGON_PAIR_EXACT_AREA_SUMMARY")
        self.assertEqual(result["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["result_layout"], "summary_float64_sums")
        self.assertEqual(result["dtype"], "float64")
        self.assertEqual(result["total_intersection_area"], 5.0)
        self.assertEqual(result["integer_parity_values"]["total_union_area"], 17)

    def test_polygon_pair_summary_uses_generic_area_summary(self) -> None:
        with mock.patch.object(
            pair_app,
            "_positive_candidate_pairs_optix",
            return_value={(1, 10), (2, 11)},
        ):
            payload = pair_app.run_case("optix", copies=1, output_mode="summary")

        generic = payload["generic_area_summary"]
        self.assertEqual(generic["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(generic["result_layout"], "summary_float64_sums")
        self.assertEqual(payload["summary"], generic["integer_parity_values"])
        self.assertIn("query_polygon_exact_area_reduce_float_sum_sec", payload["run_phases"])

    def test_polygon_generic_area_rejects_frozen_backends(self) -> None:
        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.run_generic_polygon_pair_exact_area_summary(
                        left=(),
                        right=(),
                        candidate_pairs=(),
                        backend=backend,
                        exact_summary_fn=lambda *_args: {
                            "overlap_pair_count": 0,
                            "total_intersection_area": 0,
                            "total_union_area": 0,
                        },
                    )


if __name__ == "__main__":
    unittest.main()

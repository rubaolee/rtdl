from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1350V15GenericScalarReductionTest(unittest.TestCase):
    def test_declares_only_stable_scalar_summary_primitives(self) -> None:
        self.assertEqual(
            rt.V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES,
            (
                "COUNT_HITS",
                "REDUCE_FLOAT(MIN)",
                "REDUCE_FLOAT(MAX)",
                "REDUCE_FLOAT(SUM)",
                "REDUCE_INT(COUNT)",
                "REDUCE_INT(SUM)",
            ),
        )

    def test_count_hits_counts_truthy_any_hit_rows(self) -> None:
        summary = rt.run_generic_scalar_reduction(
            (
                {"ray_id": 1, "any_hit": 1},
                {"ray_id": 2, "any_hit": 0},
                {"ray_id": 3, "any_hit": True},
            ),
            summary_primitive="COUNT_HITS",
        )

        self.assertEqual(summary["summary_primitive"], "COUNT_HITS")
        self.assertEqual(summary["result_layout"], "scalar_int64_hit_count")
        self.assertEqual(summary["dtype"], "int64")
        self.assertEqual(summary["row_count"], 3)
        self.assertEqual(summary["input_field"], "any_hit")
        self.assertEqual(summary["result"], 2)
        self.assertIn("not native backend acceleration", summary["claim_boundary"])

    def test_reduce_int_count_and_sum_are_app_name_free(self) -> None:
        rows = (
            {"bucket": "a", "payload": 3},
            {"bucket": "b", "payload": -1},
            {"bucket": "c", "payload": 5},
        )

        count_summary = rt.run_generic_scalar_reduction(rows, summary_primitive="REDUCE_INT(COUNT)")
        sum_summary = rt.run_generic_scalar_reduction(
            rows,
            summary_primitive="REDUCE_INT(SUM)",
            value_field="payload",
        )

        self.assertEqual(count_summary["result"], 3)
        self.assertEqual(count_summary["result_layout"], "scalar_int64_count")
        self.assertIsNone(count_summary["input_field"])
        self.assertEqual(sum_summary["result"], 7)
        self.assertEqual(sum_summary["result_layout"], "scalar_int64_sum")
        self.assertEqual(sum_summary["input_field"], "payload")

    def test_reduce_float_min_max_sum_use_float64_layouts(self) -> None:
        rows = (
            {"distance": 4},
            {"distance": 2.5},
            {"distance": 8.25},
        )

        self.assertEqual(
            rt.run_generic_scalar_reduction(
                rows,
                summary_primitive="REDUCE_FLOAT(MIN)",
                value_field="distance",
            )["result"],
            2.5,
        )
        self.assertEqual(
            rt.run_generic_scalar_reduction(
                rows,
                summary_primitive="REDUCE_FLOAT(MAX)",
                value_field="distance",
            )["result"],
            8.25,
        )
        sum_summary = rt.run_generic_scalar_reduction(
            rows,
            summary_primitive="REDUCE_FLOAT(SUM)",
            value_field="distance",
        )
        self.assertEqual(sum_summary["result"], 14.75)
        self.assertEqual(sum_summary["dtype"], "float64")
        self.assertEqual(sum_summary["result_layout"], "scalar_float64_sum")

    def test_empty_input_identities_are_bounded(self) -> None:
        self.assertEqual(
            rt.run_generic_scalar_reduction((), summary_primitive="COUNT_HITS")["result"],
            0,
        )
        self.assertEqual(
            rt.run_generic_scalar_reduction((), summary_primitive="REDUCE_INT(COUNT)")["result"],
            0,
        )
        self.assertEqual(
            rt.run_generic_scalar_reduction((), summary_primitive="REDUCE_INT(SUM)", value_field="payload")["result"],
            0,
        )
        self.assertEqual(
            rt.run_generic_scalar_reduction((), summary_primitive="REDUCE_FLOAT(SUM)", value_field="score")["result"],
            0.0,
        )
        with self.assertRaisesRegex(ValueError, "has no identity"):
            rt.run_generic_scalar_reduction((), summary_primitive="REDUCE_FLOAT(MIN)", value_field="score")

    def test_rejects_unknown_or_mismatched_primitive_shapes(self) -> None:
        rows = ({"any_hit": 1, "payload": 3, "score": 1.5},)

        with self.assertRaisesRegex(ValueError, "summary_primitive must be one of"):
            rt.run_generic_scalar_reduction(rows, summary_primitive="GROUPED_BOOL_FLAGS")
        with self.assertRaisesRegex(ValueError, "COUNT_HITS does not accept value_field"):
            rt.run_generic_scalar_reduction(rows, summary_primitive="COUNT_HITS", value_field="payload")
        with self.assertRaisesRegex(ValueError, "requires value_field"):
            rt.run_generic_scalar_reduction(rows, summary_primitive="REDUCE_FLOAT(SUM)")
        with self.assertRaisesRegex(ValueError, "does not accept value_field"):
            rt.run_generic_scalar_reduction(rows, summary_primitive="REDUCE_INT(COUNT)", value_field="payload")
        with self.assertRaisesRegex(TypeError, "integer values"):
            rt.run_generic_scalar_reduction(rows, summary_primitive="REDUCE_INT(SUM)", value_field="score")
        with self.assertRaisesRegex(TypeError, "mapping objects"):
            rt.run_generic_scalar_reduction((("not", "a", "row"),), summary_primitive="REDUCE_INT(COUNT)")


if __name__ == "__main__":
    unittest.main()

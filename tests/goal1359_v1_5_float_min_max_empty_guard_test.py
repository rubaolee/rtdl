from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1359V15FloatMinMaxEmptyGuardTest(unittest.TestCase):
    def test_current_v1_5_inventory_has_no_float_min_max_summary_rows(self) -> None:
        disallowed_until_integrated = {"REDUCE_FLOAT(MIN)", "REDUCE_FLOAT(MAX)"}

        for row in rt.validate_v1_5_generic_migration_inventory():
            with self.subTest(app=row["app"], subpath=row["subpath"]):
                summary_primitives = {
                    primitive.strip()
                    for primitive in row["summary_primitive"].split(",")
                    if primitive.strip()
                }
                self.assertFalse(summary_primitives & disallowed_until_integrated)

    def test_float_min_max_empty_input_errors_are_explicit(self) -> None:
        for primitive in ("REDUCE_FLOAT(MIN)", "REDUCE_FLOAT(MAX)"):
            with self.subTest(summary_primitive=primitive):
                with self.assertRaisesRegex(ValueError, "has no identity for an empty input"):
                    rt.run_generic_scalar_reduction(
                        (),
                        summary_primitive=primitive,
                        value_field="score",
                    )

    def test_float_sum_empty_input_remains_the_only_float_identity(self) -> None:
        summary = rt.run_generic_scalar_reduction(
            (),
            summary_primitive="REDUCE_FLOAT(SUM)",
            value_field="score",
        )

        self.assertEqual(summary["result"], 0.0)
        self.assertEqual(summary["result_layout"], "scalar_float64_sum")
        self.assertEqual(summary["row_count"], 0)


if __name__ == "__main__":
    unittest.main()

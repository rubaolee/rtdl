from __future__ import annotations

import platform
import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_conjunctive_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal617AppleRtDbConjunctiveScanTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "ship_date": 10, "discount": 5, "quantity": 12, "tax": 0.10},
            {"row_id": 2, "ship_date": 11, "discount": 8, "quantity": 30, "tax": 0.20},
            {"row_id": 3, "ship_date": 12, "discount": 6, "quantity": 18, "tax": 0.20},
            {"row_id": 4, "ship_date": 13, "discount": 6, "quantity": 10, "tax": 0.10},
            {"row_id": 5, "ship_date": 14, "discount": 6, "quantity": 19, "tax": 0.20},
        )

    def _predicates(self):
        return (
            ("ship_date", "between", 11, 13),
            ("discount", "eq", 6),
            ("quantity", "lt", 20),
        )

    def test_direct_numeric_conjunctive_scan_matches_cpu(self) -> None:
        expected = rt.conjunctive_scan_cpu(
            rt.normalize_denorm_table(self._table()),
            rt.normalize_predicate_bundle(self._predicates()),
        )
        self.assertEqual(rt.conjunctive_scan_apple_rt(self._table(), self._predicates()), expected)

    def test_run_apple_rt_native_only_matches_cpu_reference(self) -> None:
        inputs = {"table": self._table(), "predicates": self._predicates()}
        self.assertEqual(
            rt.run_apple_rt(sales_conjunctive_scan_kernel, native_only=True, **inputs),
            rt.run_cpu_python_reference(sales_conjunctive_scan_kernel, **inputs),
        )

    def test_float_predicate_is_supported_for_bounded_values(self) -> None:
        predicates = (("tax", "eq", 0.20), ("quantity", "ge", 18))
        self.assertEqual(
            rt.conjunctive_scan_apple_rt(self._table(), predicates),
            ({"row_id": 2}, {"row_id": 3}, {"row_id": 5}),
        )

    def test_no_predicates_matches_all_rows(self) -> None:
        self.assertEqual(
            rt.conjunctive_scan_apple_rt(self._table(), ()),
            tuple({"row_id": row["row_id"]} for row in self._table()),
        )

    def test_bounded_stress_matches_cpu_reference(self) -> None:
        table = tuple(
            {
                "row_id": index,
                "ship_date": index % 31,
                "discount": index % 9,
                "quantity": (index * 7) % 53,
            }
            for index in range(1, 4097)
        )
        predicates = (("ship_date", "between", 8, 18), ("discount", "eq", 6), ("quantity", "lt", 20))
        expected = rt.conjunctive_scan_cpu(
            rt.normalize_denorm_table(table),
            rt.normalize_predicate_bundle(predicates),
        )
        self.assertEqual(rt.conjunctive_scan_apple_rt(table, predicates), expected)

    def test_support_matrix_marks_conjunctive_scan_as_metal_compute(self) -> None:
        by_predicate = {row["predicate"]: row for row in rt.apple_rt_support_matrix()}
        row = by_predicate["conjunctive_scan"]
        self.assertEqual(row["mode"], "native_metal_compute")
        self.assertEqual(row["native_only"], "supported_for_numeric_predicates")

    def test_text_predicate_remains_out_of_scope(self) -> None:
        table = ({"row_id": 1, "region": "ASIA"},)
        with self.assertRaises(ValueError):
            rt.conjunctive_scan_apple_rt(table, (("region", "eq", "ASIA"),))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import platform
import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"))
    return rt.emit(groups, fields=["region", "sum"])


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal618AppleRtDbGroupedAggregationTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "quantity": 8, "revenue": 2},
        )

    def test_direct_grouped_count_matches_cpu(self) -> None:
        query = {"predicates": (("ship_date", "ge", 11), ("quantity", "lt", 20)), "group_keys": ("region",)}
        self.assertEqual(
            rt.grouped_count_apple_rt(self._table(), query),
            rt.grouped_count_cpu(rt.normalize_denorm_table(self._table()), rt.normalize_grouped_query(query)),
        )

    def test_direct_grouped_sum_matches_cpu(self) -> None:
        query = {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        }
        self.assertEqual(
            rt.grouped_sum_apple_rt(self._table(), query),
            rt.grouped_sum_cpu(rt.normalize_denorm_table(self._table()), rt.normalize_grouped_query(query)),
        )

    def test_run_apple_rt_native_only_grouped_count_matches_cpu_reference(self) -> None:
        query = {"predicates": (("ship_date", "ge", 11), ("quantity", "lt", 20)), "group_keys": ("region",)}
        inputs = {"query": query, "table": self._table()}
        self.assertEqual(
            rt.run_apple_rt(sales_grouped_count_kernel, native_only=True, **inputs),
            rt.run_cpu_python_reference(sales_grouped_count_kernel, **inputs),
        )

    def test_run_apple_rt_native_only_grouped_sum_matches_cpu_reference(self) -> None:
        query = {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        }
        inputs = {"query": query, "table": self._table()}
        self.assertEqual(
            rt.run_apple_rt(sales_grouped_sum_kernel, native_only=True, **inputs),
            rt.run_cpu_python_reference(sales_grouped_sum_kernel, **inputs),
        )

    def test_bounded_stress_grouped_count_and_sum_match_cpu(self) -> None:
        table = tuple(
            {
                "row_id": index,
                "region": ("east", "west", "north", "south")[index % 4],
                "ship_date": index % 31,
                "quantity": (index * 7) % 53,
                "revenue": index % 17,
            }
            for index in range(1, 4097)
        )
        count_query = {"predicates": (("ship_date", "between", 8, 18), ("quantity", "lt", 20)), "group_keys": ("region",)}
        sum_query = {
            "predicates": (("ship_date", "between", 8, 18), ("quantity", "lt", 20)),
            "group_keys": ("region",),
            "value_field": "revenue",
        }
        self.assertEqual(
            rt.grouped_count_apple_rt(table, count_query),
            rt.grouped_count_cpu(rt.normalize_denorm_table(table), rt.normalize_grouped_query(count_query)),
        )
        self.assertEqual(
            rt.grouped_sum_apple_rt(table, sum_query),
            rt.grouped_sum_cpu(rt.normalize_denorm_table(table), rt.normalize_grouped_query(sum_query)),
        )

    def test_support_matrix_marks_grouped_rows_as_native_assisted(self) -> None:
        by_predicate = {row["predicate"]: row for row in rt.apple_rt_support_matrix()}
        for predicate in ("grouped_count", "grouped_sum"):
            self.assertEqual(by_predicate[predicate]["mode"], "native_metal_filter_cpu_aggregate")
            self.assertEqual(by_predicate[predicate]["native_only"], "supported_for_numeric_predicates_cpu_aggregation")

    def test_text_predicate_remains_out_of_scope(self) -> None:
        query = {"predicates": (("region", "eq", "east"),), "group_keys": ("region",)}
        with self.assertRaises(ValueError):
            rt.grouped_count_apple_rt(self._table(), query)


if __name__ == "__main__":
    unittest.main()

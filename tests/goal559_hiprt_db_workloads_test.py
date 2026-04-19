from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import conjunctive_scan_hiprt
from rtdsl.hiprt_runtime import grouped_count_hiprt
from rtdsl.hiprt_runtime import grouped_sum_hiprt
from rtdsl.hiprt_runtime import hiprt_context_probe


@rt.kernel(backend="rtdl", precision="float_approx")
def conjunctive_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"))
    return rt.emit(groups, fields=["region", "sum"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def table_fixture():
    return (
        {"row_id": 1, "region": "east", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 100},
        {"row_id": 2, "region": "east", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 150},
        {"row_id": 3, "region": "west", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 200},
        {"row_id": 4, "region": "west", "ship_date": 14, "discount": 7, "quantity": 30, "revenue": 300},
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal559HiprtDbWorkloadsTest(unittest.TestCase):
    def test_conjunctive_scan_direct_helper_matches_cpu_reference(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        predicates = rt.normalize_predicate_bundle((("ship_date", "between", 12, 14), ("discount", "eq", 6)))
        self.assertEqual(conjunctive_scan_hiprt(table, predicates), rt.conjunctive_scan_cpu(table, predicates))

    def test_conjunctive_scan_run_hiprt_matches_cpu_reference(self) -> None:
        inputs = {"table": table_fixture(), "predicates": (("discount", "eq", 6),)}
        self.assertEqual(
            rt.run_hiprt(conjunctive_scan_kernel, **inputs),
            rt.run_cpu_python_reference(conjunctive_scan_kernel, **inputs),
        )

    def test_grouped_count_direct_helper_matches_cpu_reference(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        query = rt.normalize_grouped_query({"group_keys": ("region",), "predicates": (("discount", "ge", 6),)})
        self.assertEqual(grouped_count_hiprt(table, query), rt.grouped_count_cpu(table, query))

    def test_grouped_count_run_hiprt_matches_cpu_reference(self) -> None:
        inputs = {"table": table_fixture(), "query": {"group_keys": ("region",), "predicates": (("discount", "ge", 6),)}}
        self.assertEqual(
            rt.run_hiprt(grouped_count_kernel, **inputs),
            rt.run_cpu_python_reference(grouped_count_kernel, **inputs),
        )

    def test_grouped_sum_direct_helper_matches_cpu_reference(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        query = rt.normalize_grouped_query(
            {"group_keys": ("region",), "value_field": "revenue", "predicates": (("discount", "ge", 6),)}
        )
        self.assertEqual(grouped_sum_hiprt(table, query), rt.grouped_sum_cpu(table, query))

    def test_grouped_sum_run_hiprt_matches_cpu_reference(self) -> None:
        inputs = {
            "table": table_fixture(),
            "query": {"group_keys": ("region",), "value_field": "revenue", "predicates": (("discount", "ge", 6),)},
        }
        self.assertEqual(
            rt.run_hiprt(grouped_sum_kernel, **inputs),
            rt.run_cpu_python_reference(grouped_sum_kernel, **inputs),
        )

    def test_empty_tables_return_empty_rows(self) -> None:
        self.assertEqual(rt.run_hiprt(conjunctive_scan_kernel, table=(), predicates=()), ())
        self.assertEqual(rt.run_hiprt(grouped_count_kernel, table=(), query={"group_keys": ("region",)}), ())
        self.assertEqual(
            rt.run_hiprt(
                grouped_sum_kernel,
                table=(),
                query={"group_keys": ("region",), "value_field": "revenue"},
            ),
            (),
        )


if __name__ == "__main__":
    unittest.main()

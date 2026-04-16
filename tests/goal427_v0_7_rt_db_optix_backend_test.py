import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests._optix_support import optix_available


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_conjunctive_scan_reference():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_count_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_sum_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


@unittest.skipUnless(optix_available(), "OptiX runtime is not available")
class Goal427V07RtDbOptixBackendTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "discount": 8, "quantity": 30, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "discount": 5, "quantity": 8, "revenue": 2},
        )

    def test_run_optix_matches_python_for_conjunctive_scan(self) -> None:
        inputs = {
            "predicates": (("ship_date", "between", 11, 13), ("discount", "eq", 6), ("quantity", "lt", 20)),
            "table": self._table(),
        }
        self.assertEqual(
            rt.run_optix(sales_conjunctive_scan_reference, **inputs),
            rt.run_cpu_python_reference(sales_conjunctive_scan_reference, **inputs),
        )

    def test_run_optix_matches_oracle_for_conjunctive_scan(self) -> None:
        inputs = {
            "predicates": (("ship_date", "between", 11, 13), ("discount", "eq", 6), ("quantity", "lt", 20)),
            "table": self._table(),
        }
        self.assertEqual(
            rt.run_optix(sales_conjunctive_scan_reference, **inputs),
            rt.run_cpu(sales_conjunctive_scan_reference, **inputs),
        )

    def test_run_optix_matches_oracle_for_grouped_count(self) -> None:
        inputs = {
            "query": {
                "predicates": (("ship_date", "ge", 11), ("quantity", "lt", 20)),
                "group_keys": ("region",),
            },
            "table": self._table(),
        }
        self.assertEqual(
            rt.run_optix(sales_grouped_count_reference, **inputs),
            rt.run_cpu(sales_grouped_count_reference, **inputs),
        )

    def test_run_optix_matches_oracle_for_grouped_sum(self) -> None:
        inputs = {
            "query": {
                "predicates": (("ship_date", "ge", 11),),
                "group_keys": ("region",),
                "value_field": "revenue",
            },
            "table": self._table(),
        }
        self.assertEqual(
            rt.run_optix(sales_grouped_sum_reference, **inputs),
            rt.run_cpu(sales_grouped_sum_reference, **inputs),
        )


if __name__ == "__main__":
    unittest.main()

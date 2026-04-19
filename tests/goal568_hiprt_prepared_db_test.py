from __future__ import annotations

import unittest

import rtdsl as rt
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
        {"row_id": 5, "region": "north", "ship_date": 15, "discount": 6, "quantity": 4, "revenue": 50},
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal568HiprtPreparedDbTest(unittest.TestCase):
    def test_direct_prepared_scan_reuses_table_for_multiple_predicates(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        prepared = rt.prepare_hiprt_db_table(table)
        try:
            for predicates_payload in (
                (("ship_date", "between", 12, 14), ("discount", "eq", 6)),
                (("region", "eq", "east"),),
                (("region", "eq", "missing"),),
            ):
                predicates = rt.normalize_predicate_bundle(predicates_payload)
                self.assertEqual(prepared.conjunctive_scan(predicates), rt.conjunctive_scan_cpu(table, predicates))
        finally:
            prepared.close()

    def test_direct_prepared_grouped_count_decodes_text_group_keys(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        query = rt.normalize_grouped_query({"group_keys": ("region",), "predicates": (("discount", "ge", 6),)})
        prepared = rt.prepare_hiprt_db_table(table)
        try:
            self.assertEqual(prepared.grouped_count(query), rt.grouped_count_cpu(table, query))
        finally:
            prepared.close()

    def test_direct_prepared_grouped_sum_decodes_text_group_keys(self) -> None:
        table = rt.normalize_denorm_table(table_fixture())
        query = rt.normalize_grouped_query(
            {"group_keys": ("region",), "value_field": "revenue", "predicates": (("quantity", "lt", 25),)}
        )
        prepared = rt.prepare_hiprt_db_table(table)
        try:
            self.assertEqual(prepared.grouped_sum(query), rt.grouped_sum_cpu(table, query))
        finally:
            prepared.close()

    def test_prepare_hiprt_conjunctive_scan_matches_cpu_reference(self) -> None:
        table = table_fixture()
        prepared = rt.prepare_hiprt(conjunctive_scan_kernel, table=table)
        try:
            predicates = (("discount", "eq", 6),)
            self.assertEqual(
                prepared.run(predicates=predicates),
                rt.run_cpu_python_reference(conjunctive_scan_kernel, table=table, predicates=predicates),
            )
        finally:
            prepared.close()

    def test_prepare_hiprt_grouped_count_matches_cpu_reference(self) -> None:
        table = table_fixture()
        prepared = rt.prepare_hiprt(grouped_count_kernel, table=table)
        try:
            query = {"group_keys": ("region",), "predicates": (("discount", "ge", 6),)}
            self.assertEqual(
                prepared.run(query=query),
                rt.run_cpu_python_reference(grouped_count_kernel, table=table, query=query),
            )
        finally:
            prepared.close()

    def test_prepare_hiprt_grouped_sum_matches_cpu_reference(self) -> None:
        table = table_fixture()
        prepared = rt.prepare_hiprt(grouped_sum_kernel, table=table)
        try:
            query = {"group_keys": ("region",), "value_field": "revenue", "predicates": (("discount", "ge", 6),)}
            self.assertEqual(
                prepared.run(query=query),
                rt.run_cpu_python_reference(grouped_sum_kernel, table=table, query=query),
            )
        finally:
            prepared.close()

    def test_empty_prepared_table_returns_empty_rows(self) -> None:
        prepared = rt.prepare_hiprt_db_table(())
        try:
            self.assertEqual(prepared.conjunctive_scan(()), ())
            self.assertEqual(prepared.grouped_count({"group_keys": ("region",)}), ())
            self.assertEqual(prepared.grouped_sum({"group_keys": ("region",), "value_field": "revenue"}), ())
        finally:
            prepared.close()


if __name__ == "__main__":
    unittest.main()

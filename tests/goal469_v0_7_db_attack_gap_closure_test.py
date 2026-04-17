import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.api as rt_api


@rt.kernel(backend="rtdl", precision="float_approx")
def goal469_scan_reference():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def goal469_count_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def goal469_quantity_sum_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="quantity"),
    )
    return rt.emit(groups, fields=["region", "sum"])


@rt.kernel(backend="rtdl", precision="float_approx")
def goal469_bad_kernel():
    rt.input("predicates", rt.PredicateSet, role="probe")
    return None


def _sales_table():
    return (
        {"row_id": 1, "region": "east", "ship_date": 10, "discount": 5, "quantity": 12, "score": 0.5},
        {"row_id": 2, "region": "west", "ship_date": 11, "discount": 8, "quantity": 30, "score": 1.25},
        {"row_id": 3, "region": "east", "ship_date": 12, "discount": 6, "quantity": 18, "score": 1.75},
        {"row_id": 4, "region": "west", "ship_date": 13, "discount": 6, "quantity": 10, "score": 2.75},
        {"row_id": 5, "region": "west", "ship_date": 14, "discount": 7, "quantity": 8, "score": 3.5},
    )


def _large_table(row_count):
    return tuple(
        {
            "row_id": row_id,
            "region": row_id % 8,
            "ship_date": row_id % 512,
            "discount": row_id % 11,
            "quantity": (row_id % 31) + 1,
        }
        for row_id in range(1, row_count + 1)
    )


class Goal469V07DbAttackGapClosureTest(unittest.TestCase):
    def _assert_cpu_matches_python(self, kernel_fn, **inputs):
        expected = rt.run_cpu_python_reference(kernel_fn, **inputs)
        self.assertEqual(rt.run_cpu(kernel_fn, **inputs), expected)
        return expected

    def test_float_between_scan_matches_native_cpu_oracle(self):
        rows = self._assert_cpu_matches_python(
            goal469_scan_reference,
            predicates=(("score", "between", 1.25, 2.75),),
            table=_sales_table(),
        )
        self.assertEqual(rows, ({"row_id": 2}, {"row_id": 3}, {"row_id": 4}))

    def test_alternate_integer_value_field_grouped_sum_matches_native_cpu_oracle(self):
        rows = self._assert_cpu_matches_python(
            goal469_quantity_sum_reference,
            query={
                "predicates": (("ship_date", "between", 11, 14),),
                "group_keys": ("region",),
                "value_field": "quantity",
            },
            table=_sales_table(),
        )
        self.assertEqual(rows, ({"region": "east", "sum": 18}, {"region": "west", "sum": 48}))

    def test_empty_denorm_table_returns_empty_for_all_db_workloads(self):
        self.assertEqual(
            self._assert_cpu_matches_python(
                goal469_scan_reference,
                predicates=(("ship_date", "between", 1, 10),),
                table=(),
            ),
            (),
        )
        self.assertEqual(
            self._assert_cpu_matches_python(
                goal469_count_reference,
                query={"predicates": (("ship_date", "between", 1, 10),), "group_keys": ("region",)},
                table=(),
            ),
            (),
        )
        self.assertEqual(
            self._assert_cpu_matches_python(
                goal469_quantity_sum_reference,
                query={
                    "predicates": (("ship_date", "between", 1, 10),),
                    "group_keys": ("region",),
                    "value_field": "quantity",
                },
                table=(),
            ),
            (),
        )

    def test_large_power_of_two_scan_boundary_matches_native_cpu_oracle(self):
        table = _large_table(65536)
        rows = self._assert_cpu_matches_python(
            goal469_scan_reference,
            predicates=(("ship_date", "between", 128, 255), ("discount", "eq", 6)),
            table=table,
        )
        self.assertGreater(len(rows), 0)
        self.assertTrue(all(128 <= table[row["row_id"] - 1]["ship_date"] <= 255 for row in rows))

    def test_grouped_boundaries_match_native_cpu_oracle(self):
        for row_count in (1, 1024):
            table = _large_table(row_count)
            count_rows = self._assert_cpu_matches_python(
                goal469_count_reference,
                query={"predicates": (("ship_date", "between", 0, 511),), "group_keys": ("region",)},
                table=table,
            )
            sum_rows = self._assert_cpu_matches_python(
                goal469_quantity_sum_reference,
                query={
                    "predicates": (("ship_date", "between", 0, 511),),
                    "group_keys": ("region",),
                    "value_field": "quantity",
                },
                table=table,
            )
            self.assertEqual(sum(row["count"] for row in count_rows), row_count)
            self.assertEqual(sum(row["sum"] for row in sum_rows), sum(row["quantity"] for row in table))

    def test_repeated_compile_and_failed_compile_do_not_leak_context(self):
        for _ in range(25):
            rt.compile_kernel(goal469_scan_reference)
            rt.compile_kernel(goal469_count_reference)
            rt.compile_kernel(goal469_quantity_sum_reference)
        with self.assertRaisesRegex(TypeError, "kernel function must return rt.emit"):
            rt.compile_kernel(goal469_bad_kernel)
        self.assertEqual(len(rt_api._context_stack), 0)
        self.assertEqual(rt.compile_kernel(goal469_scan_reference).emit_op.fields, ("row_id",))


if __name__ == "__main__":
    unittest.main()

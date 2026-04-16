import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


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


class Goal419V07RtDbGroupedSumTruthPathTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "revenue": 2},
        )

    def test_compile_kernel_preserves_grouped_sum_surface(self) -> None:
        compiled = rt.compile_kernel(sales_grouped_sum_reference)
        self.assertEqual(
            tuple(item.geometry.name for item in compiled.inputs),
            ("grouped_query", "denorm_table"),
        )
        self.assertEqual(compiled.candidates.mode, "db_group")
        self.assertEqual(compiled.refine_op.predicate.name, "grouped_sum")
        self.assertEqual(compiled.emit_op.fields, ("region", "sum"))

    def test_python_reference_runs_grouped_sum(self) -> None:
        rows = rt.run_cpu_python_reference(
            sales_grouped_sum_reference,
            query={
                "predicates": (("ship_date", "ge", 11),),
                "group_keys": ("region",),
                "value_field": "revenue",
            },
            table=self._table(),
        )
        self.assertEqual(
            rows,
            (
                {"region": "east", "sum": 6},
                {"region": "west", "sum": 20},
            ),
        )

    def test_grouped_sum_requires_value_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a value_field"):
            rt.grouped_sum(group_keys=("region",), value_field="")


if __name__ == "__main__":
    unittest.main()

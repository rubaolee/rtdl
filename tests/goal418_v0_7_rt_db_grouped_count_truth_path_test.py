import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_count_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


class Goal418V07RtDbGroupedCountTruthPathTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "quantity": 8},
        )

    def test_compile_kernel_preserves_db_group_mode_and_predicate(self) -> None:
        compiled = rt.compile_kernel(sales_grouped_count_reference)
        self.assertEqual(
            tuple(item.geometry.name for item in compiled.inputs),
            ("grouped_query", "denorm_table"),
        )
        self.assertEqual(compiled.candidates.mode, "db_group")
        self.assertEqual(compiled.refine_op.predicate.name, "grouped_count")
        self.assertEqual(compiled.emit_op.fields, ("region", "count"))

    def test_python_reference_runs_grouped_count(self) -> None:
        rows = rt.run_cpu_python_reference(
            sales_grouped_count_reference,
            query={
                "predicates": (
                    ("ship_date", "ge", 11),
                    ("quantity", "lt", 20),
                ),
                "group_keys": ("region",),
            },
            table=self._table(),
        )
        self.assertEqual(
            rows,
            (
                {"region": "east", "count": 1},
                {"region": "west", "count": 2},
            ),
        )

    def test_grouped_count_requires_group_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires at least one group key"):
            rt.grouped_count(group_keys=())


if __name__ == "__main__":
    unittest.main()

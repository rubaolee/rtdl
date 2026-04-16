import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_conjunctive_scan_reference():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


class Goal417V07RtDbConjunctiveScanTruthPathTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "ship_date": 10, "discount": 5, "quantity": 12},
            {"row_id": 2, "ship_date": 11, "discount": 8, "quantity": 30},
            {"row_id": 3, "ship_date": 12, "discount": 6, "quantity": 18},
            {"row_id": 4, "ship_date": 13, "discount": 6, "quantity": 10},
        )

    def test_db_surface_exports_exist(self) -> None:
        self.assertEqual(rt.DenormTable.name, "denorm_table")
        self.assertEqual(rt.PredicateSet.name, "predicate_set")
        predicate = rt.conjunctive_scan(exact=True)
        self.assertEqual(predicate.name, "conjunctive_scan")
        self.assertTrue(predicate.options["exact"])

    def test_compile_kernel_preserves_db_mode_and_predicate(self) -> None:
        compiled = rt.compile_kernel(sales_conjunctive_scan_reference)
        self.assertEqual(
            tuple(item.geometry.name for item in compiled.inputs),
            ("predicate_set", "denorm_table"),
        )
        self.assertEqual(compiled.candidates.mode, "db_scan")
        self.assertEqual(compiled.refine_op.predicate.name, "conjunctive_scan")
        self.assertEqual(compiled.emit_op.fields, ("row_id",))

    def test_python_reference_runs_bounded_conjunctive_scan(self) -> None:
        rows = rt.run_cpu_python_reference(
            sales_conjunctive_scan_reference,
            predicates=(
                ("ship_date", "between", 11, 13),
                ("discount", "eq", 6),
                ("quantity", "lt", 20),
            ),
            table=self._table(),
        )
        self.assertEqual(rows, ({"row_id": 3}, {"row_id": 4}))

    def test_python_reference_accepts_mapping_bundle_inputs(self) -> None:
        rows = rt.run_cpu_python_reference(
            sales_conjunctive_scan_reference,
            predicates={
                "clauses": (
                    {"field": "ship_date", "op": "ge", "value": 12},
                    {"field": "quantity", "op": "le", "value": 18},
                )
            },
            table={"rows": self._table()},
        )
        self.assertEqual(rows, ({"row_id": 3}, {"row_id": 4}))

    def test_python_reference_rejects_invalid_operator(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported predicate operator"):
            rt.run_cpu_python_reference(
                sales_conjunctive_scan_reference,
                predicates=(("ship_date", "neq", 12),),
                table=self._table(),
            )


if __name__ == "__main__":
    unittest.main()

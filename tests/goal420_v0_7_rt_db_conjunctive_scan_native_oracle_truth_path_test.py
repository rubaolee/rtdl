import os
import sys
import unittest
from unittest import mock

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


class Goal420V07RtDbConjunctiveScanNativeOracleTruthPathTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "ship_date": 10, "discount": 5, "quantity": 12},
            {"row_id": 2, "ship_date": 11, "discount": 8, "quantity": 30},
            {"row_id": 3, "ship_date": 12, "discount": 6, "quantity": 18},
            {"row_id": 4, "ship_date": 13, "discount": 6, "quantity": 10},
        )

    def _predicates(self):
        return (
            ("ship_date", "between", 11, 13),
            ("discount", "eq", 6),
            ("quantity", "lt", 20),
        )

    def test_run_cpu_matches_python_truth_path(self) -> None:
        inputs = {
            "predicates": self._predicates(),
            "table": self._table(),
        }
        self.assertEqual(
            rt.run_cpu(sales_conjunctive_scan_reference, **inputs),
            rt.run_cpu_python_reference(sales_conjunctive_scan_reference, **inputs),
        )

    def test_run_cpu_no_longer_depends_on_python_truth_helper(self) -> None:
        with mock.patch("rtdsl.runtime.conjunctive_scan_cpu", side_effect=AssertionError("python helper should not be used")):
            rows = rt.run_cpu(
                sales_conjunctive_scan_reference,
                predicates=self._predicates(),
                table=self._table(),
            )
        self.assertEqual(rows, ({"row_id": 3}, {"row_id": 4}))

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_run_cpu_matches_live_postgresql_on_linux(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        with rt.connect_postgresql(dsn) as connection:
            pg_rows = rt.run_postgresql_conjunctive_scan(
                connection,
                self._table(),
                self._predicates(),
            )
        self.assertEqual(
            rt.run_cpu(
                sales_conjunctive_scan_reference,
                predicates=self._predicates(),
                table=self._table(),
            ),
            pg_rows,
        )

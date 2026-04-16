import os
import sys
import unittest
from unittest import mock

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


class Goal422V07RtDbGroupedSumNativeOracleTruthPathTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "quantity": 8, "revenue": 2},
        )

    def _query(self):
        return {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        }

    def test_run_cpu_matches_python_truth_path(self) -> None:
        inputs = {"query": self._query(), "table": self._table()}
        self.assertEqual(
            rt.run_cpu(sales_grouped_sum_reference, **inputs),
            rt.run_cpu_python_reference(sales_grouped_sum_reference, **inputs),
        )

    def test_run_cpu_no_longer_depends_on_grouped_sum_python_helper(self) -> None:
        with mock.patch("rtdsl.oracle_runtime.grouped_sum_cpu", side_effect=AssertionError("python grouped_sum helper should not be used")):
            rows = rt.run_cpu(
                sales_grouped_sum_reference,
                query=self._query(),
                table=self._table(),
            )
        self.assertEqual(rows, ({"region": "east", "sum": 6}, {"region": "west", "sum": 20}))

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_run_cpu_matches_live_postgresql_on_linux(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        with rt.connect_postgresql(dsn) as connection:
            pg_rows = rt.run_postgresql_grouped_sum(connection, self._table(), self._query())
        self.assertEqual(
            rt.run_cpu(
                sales_grouped_sum_reference,
                query=self._query(),
                table=self._table(),
            ),
            pg_rows,
        )

import os
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


class Goal423V07PostgresqlDbCorrectnessTest(unittest.TestCase):
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

    def test_sql_shape_contains_bounded_where_clause(self) -> None:
        sql = rt.build_postgresql_conjunctive_scan_sql(self._predicates())
        self.assertIn("SELECT row_id", sql)
        self.assertIn("ship_date BETWEEN %s AND %s", sql)
        self.assertIn("discount = %s", sql)
        self.assertIn("quantity < %s", sql)
        self.assertIn("ORDER BY row_id", sql)

    def test_fake_postgresql_runner_matches_python_reference(self) -> None:
        connection = rt.FakePostgresqlConnection()
        rows = rt.run_postgresql_conjunctive_scan(
            connection,
            self._table(),
            self._predicates(),
        )
        self.assertEqual(
            rows,
            rt.run_cpu_python_reference(
                sales_conjunctive_scan_reference,
                predicates=self._predicates(),
                table=self._table(),
            ),
        )
        self.assertTrue(any("CREATE INDEX rtdl_denorm_table_tmp_discount_idx" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_denorm_table_tmp_quantity_idx" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_denorm_table_tmp_ship_date_idx" in sql for sql in connection.executed_sql))

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_live_postgresql_matches_python_truth_and_cpu(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        with rt.connect_postgresql(dsn) as connection:
            pg_rows = rt.run_postgresql_conjunctive_scan(
                connection,
                self._table(),
                self._predicates(),
            )
        inputs = {
            "predicates": self._predicates(),
            "table": self._table(),
        }
        self.assertEqual(pg_rows, rt.run_cpu_python_reference(sales_conjunctive_scan_reference, **inputs))
        self.assertEqual(pg_rows, rt.run_cpu(sales_conjunctive_scan_reference, **inputs))

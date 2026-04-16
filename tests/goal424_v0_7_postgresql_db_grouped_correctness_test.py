import os
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


class Goal424V07PostgresqlDbGroupedCorrectnessTest(unittest.TestCase):
    def _table(self):
        return (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "quantity": 8, "revenue": 2},
        )

    def test_grouped_count_sql_shape(self) -> None:
        sql = rt.build_postgresql_grouped_count_sql(
            {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",)}
        )
        self.assertIn("COUNT(*) AS count", sql)
        self.assertIn("GROUP BY region", sql)
        self.assertIn("ORDER BY region", sql)

    def test_grouped_sum_sql_shape(self) -> None:
        sql = rt.build_postgresql_grouped_sum_sql(
            {
                "predicates": (("ship_date", "ge", 11),),
                "group_keys": ("region",),
                "value_field": "revenue",
            }
        )
        self.assertIn("SUM(revenue) AS sum", sql)
        self.assertIn("GROUP BY region", sql)
        self.assertIn("ORDER BY region", sql)

    def test_fake_grouped_count_runner_matches_python_reference(self) -> None:
        connection = rt.FakePostgresqlConnection()
        query = {"predicates": (("ship_date", "ge", 11), ("quantity", "lt", 20)), "group_keys": ("region",)}
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(query)
        rows = rt.run_postgresql_grouped_count(connection, self._table(), query)
        self.assertEqual(
            rows,
            rt.run_cpu_python_reference(
                sales_grouped_count_reference,
                query=query,
                table=self._table(),
            ),
        )

    def test_fake_grouped_sum_runner_matches_python_reference(self) -> None:
        connection = rt.FakePostgresqlConnection()
        query = {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        }
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(query)
        rows = rt.run_postgresql_grouped_sum(connection, self._table(), query)
        self.assertEqual(
            rows,
            rt.run_cpu_python_reference(
                sales_grouped_sum_reference,
                query=query,
                table=self._table(),
            ),
        )

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_live_grouped_count_and_sum_match_python_truth(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        grouped_count_query = {
            "predicates": (("ship_date", "ge", 11), ("quantity", "lt", 20)),
            "group_keys": ("region",),
        }
        grouped_sum_query = {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        }
        with rt.connect_postgresql(dsn) as connection:
            pg_count_rows = rt.run_postgresql_grouped_count(connection, self._table(), grouped_count_query)
        with rt.connect_postgresql(dsn) as connection:
            pg_sum_rows = rt.run_postgresql_grouped_sum(connection, self._table(), grouped_sum_query)
        self.assertEqual(
            pg_count_rows,
            rt.run_cpu_python_reference(
                sales_grouped_count_reference,
                query=grouped_count_query,
                table=self._table(),
            ),
        )
        self.assertEqual(
            pg_count_rows,
            rt.run_cpu(
                sales_grouped_count_reference,
                query=grouped_count_query,
                table=self._table(),
            ),
        )
        self.assertEqual(
            pg_sum_rows,
            rt.run_cpu_python_reference(
                sales_grouped_sum_reference,
                query=grouped_sum_query,
                table=self._table(),
            ),
        )
        self.assertEqual(
            pg_sum_rows,
            rt.run_cpu(
                sales_grouped_sum_reference,
                query=grouped_sum_query,
                table=self._table(),
            ),
        )

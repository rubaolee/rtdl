from __future__ import annotations

from typing import Any

from .db_reference import conjunctive_scan_cpu
from .db_reference import normalize_grouped_query
from .db_reference import normalize_denorm_table
from .db_reference import normalize_predicate_bundle
from .graph_postgresql import connect_postgresql
from .graph_postgresql import postgresql_available


def build_postgresql_conjunctive_scan_sql(
    predicates,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> str:
    bundle = normalize_predicate_bundle(predicates)
    where_sql = " AND ".join(_sql_clause_text(clause) for clause in bundle.clauses)
    if not where_sql:
        where_sql = "TRUE"
    return f"""
SELECT row_id
FROM {table_name}
WHERE {where_sql}
ORDER BY row_id
""".strip()


def prepare_postgresql_denorm_table(
    connection,
    table_rows,
    predicates,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> None:
    rows = normalize_denorm_table(table_rows)
    bundle = normalize_predicate_bundle(predicates)
    cursor = connection.cursor()
    try:
        columns = _infer_columns(rows)
        column_sql = ",\n    ".join(
            f"{name} {_postgres_type(dtype)} NOT NULL" for name, dtype in columns
        )
        cursor.execute(
            f"""
CREATE TEMP TABLE {table_name} (
    {column_sql}
) ON COMMIT DROP
""".strip()
        )
        column_names = [name for name, _ in columns]
        placeholders = ", ".join(["%s"] * len(column_names))
        cursor.executemany(
            f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})",
            [tuple(row[name] for name in column_names) for row in rows],
        )
        cursor.execute(f"CREATE INDEX {table_name}_row_id_idx ON {table_name} (row_id)")
        indexed_fields = {clause.field for clause in bundle.clauses}
        for field in sorted(indexed_fields):
            cursor.execute(f"CREATE INDEX {table_name}_{field}_idx ON {table_name} ({field})")
        cursor.execute(f"ANALYZE {table_name}")
        if hasattr(connection, "_rtdl_fake_db"):
            connection._rtdl_fake_rows = rows
            connection._rtdl_fake_predicates = bundle
    finally:
        cursor.close()


def query_postgresql_conjunctive_scan(
    connection,
    predicates,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, int], ...]:
    bundle = normalize_predicate_bundle(predicates)
    sql = build_postgresql_conjunctive_scan_sql(bundle, table_name=table_name)
    params = _sql_params(bundle)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return tuple({"row_id": int(row_id)} for (row_id,) in cursor.fetchall())
    finally:
        cursor.close()


def run_postgresql_conjunctive_scan(
    connection,
    table_rows,
    predicates,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, int], ...]:
    prepare_postgresql_denorm_table(
        connection,
        table_rows,
        predicates,
        table_name=table_name,
    )
    return query_postgresql_conjunctive_scan(
        connection,
        predicates,
        table_name=table_name,
    )


def build_postgresql_grouped_count_sql(
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> str:
    grouped_query = normalize_grouped_query(query)
    if not grouped_query.group_keys:
        raise ValueError("grouped_count query requires at least one group key")
    select_keys = ", ".join(grouped_query.group_keys)
    group_keys = ", ".join(grouped_query.group_keys)
    order_keys = ", ".join(grouped_query.group_keys)
    where_sql = " AND ".join(_sql_clause_text(clause) for clause in grouped_query.predicates) or "TRUE"
    return f"""
SELECT {select_keys}, COUNT(*) AS count
FROM {table_name}
WHERE {where_sql}
GROUP BY {group_keys}
ORDER BY {order_keys}
""".strip()


def query_postgresql_grouped_count(
    connection,
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, Any], ...]:
    grouped_query = normalize_grouped_query(query)
    sql = build_postgresql_grouped_count_sql(grouped_query, table_name=table_name)
    params = _sql_params_from_clauses(grouped_query.predicates)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        rows = []
        for row in cursor.fetchall():
            result = {
                grouped_query.group_keys[index]: row[index]
                for index in range(len(grouped_query.group_keys))
            }
            result["count"] = int(row[-1])
            rows.append(result)
        return tuple(rows)
    finally:
        cursor.close()


def run_postgresql_grouped_count(
    connection,
    table_rows,
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, Any], ...]:
    grouped_query = normalize_grouped_query(query)
    prepare_postgresql_denorm_table(
        connection,
        table_rows,
        grouped_query.predicates,
        table_name=table_name,
    )
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = grouped_query
    return query_postgresql_grouped_count(
        connection,
        grouped_query,
        table_name=table_name,
    )


def build_postgresql_grouped_sum_sql(
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> str:
    grouped_query = normalize_grouped_query(query)
    if not grouped_query.group_keys:
        raise ValueError("grouped_sum query requires at least one group key")
    if not grouped_query.value_field:
        raise ValueError("grouped_sum query requires a value field")
    select_keys = ", ".join(grouped_query.group_keys)
    group_keys = ", ".join(grouped_query.group_keys)
    order_keys = ", ".join(grouped_query.group_keys)
    where_sql = " AND ".join(_sql_clause_text(clause) for clause in grouped_query.predicates) or "TRUE"
    return f"""
SELECT {select_keys}, SUM({grouped_query.value_field}) AS sum
FROM {table_name}
WHERE {where_sql}
GROUP BY {group_keys}
ORDER BY {order_keys}
""".strip()


def query_postgresql_grouped_sum(
    connection,
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, Any], ...]:
    grouped_query = normalize_grouped_query(query)
    sql = build_postgresql_grouped_sum_sql(grouped_query, table_name=table_name)
    params = _sql_params_from_clauses(grouped_query.predicates)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        rows = []
        for row in cursor.fetchall():
            result = {
                grouped_query.group_keys[index]: row[index]
                for index in range(len(grouped_query.group_keys))
            }
            value = row[-1]
            result["sum"] = int(value) if float(value).is_integer() else float(value)
            rows.append(result)
        return tuple(rows)
    finally:
        cursor.close()


def run_postgresql_grouped_sum(
    connection,
    table_rows,
    query,
    *,
    table_name: str = "rtdl_denorm_table_tmp",
) -> tuple[dict[str, Any], ...]:
    grouped_query = normalize_grouped_query(query)
    prepare_postgresql_denorm_table(
        connection,
        table_rows,
        grouped_query.predicates,
        table_name=table_name,
    )
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = grouped_query
    return query_postgresql_grouped_sum(
        connection,
        grouped_query,
        table_name=table_name,
    )


def _infer_columns(rows: tuple[dict[str, Any], ...]) -> tuple[tuple[str, str], ...]:
    if not rows:
        return (("row_id", "int"),)
    return tuple((name, _infer_scalar_type(value)) for name, value in rows[0].items())


def _infer_scalar_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    return "text"


def _postgres_type(dtype: str) -> str:
    if dtype == "bool":
        return "BOOLEAN"
    if dtype == "int":
        return "BIGINT"
    if dtype == "float":
        return "DOUBLE PRECISION"
    return "TEXT"


def _sql_clause_text(clause) -> str:
    field = clause.field
    if clause.op == "eq":
        return f"{field} = %s"
    if clause.op == "lt":
        return f"{field} < %s"
    if clause.op == "le":
        return f"{field} <= %s"
    if clause.op == "gt":
        return f"{field} > %s"
    if clause.op == "ge":
        return f"{field} >= %s"
    if clause.op == "between":
        return f"{field} BETWEEN %s AND %s"
    raise ValueError(f"unsupported predicate operator: {clause.op}")


def _sql_params(bundle) -> tuple[Any, ...]:
    params: list[Any] = []
    for clause in bundle.clauses:
        params.append(clause.value)
        if clause.op == "between":
            params.append(clause.value_hi)
    return tuple(params)


def _sql_params_from_clauses(clauses) -> tuple[Any, ...]:
    params: list[Any] = []
    for clause in clauses:
        params.append(clause.value)
        if clause.op == "between":
            params.append(clause.value_hi)
    return tuple(params)


class _FakeDbCursor:
    def __init__(self, connection):
        self._connection = connection
        self._rows = []

    def execute(self, sql, params=None):
        text = sql.strip()
        self._connection.executed_sql.append(text)
        if "CREATE TEMP TABLE" in text or "CREATE INDEX" in text or text.startswith("ANALYZE"):
            return
        if text.startswith("SELECT row_id"):
            rows = conjunctive_scan_cpu(
                self._connection._rtdl_fake_rows,
                self._connection._rtdl_fake_predicates,
            )
            self._rows = [(row["row_id"],) for row in rows]
            return
        if "COUNT(*) AS count" in text:
            from .db_reference import grouped_count_cpu

            rows = grouped_count_cpu(
                self._connection._rtdl_fake_rows,
                self._connection._rtdl_fake_grouped_query,
            )
            self._rows = [
                tuple(row[key] for key in self._connection._rtdl_fake_grouped_query.group_keys)
                + (row["count"],)
                for row in rows
            ]
            return
        if "SUM(" in text and " AS sum" in text:
            from .db_reference import grouped_sum_cpu

            rows = grouped_sum_cpu(
                self._connection._rtdl_fake_rows,
                self._connection._rtdl_fake_grouped_query,
            )
            self._rows = [
                tuple(row[key] for key in self._connection._rtdl_fake_grouped_query.group_keys)
                + (row["sum"],)
                for row in rows
            ]
            return
        raise AssertionError(f"unexpected SQL: {text}")

    def executemany(self, sql, payload):
        rows = list(payload)
        self._connection.executed_sql.append(sql.strip())
        if "INSERT INTO rtdl_denorm_table_tmp" in sql:
            self._connection.inserted_rows = tuple(rows)
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return


class FakePostgresqlConnection:
    _rtdl_fake_db = True

    def __init__(self):
        self.executed_sql: list[str] = []
        self.inserted_rows = ()
        self._rtdl_fake_rows = ()
        self._rtdl_fake_predicates = normalize_predicate_bundle(())
        self._rtdl_fake_grouped_query = None

    def cursor(self):
        return _FakeDbCursor(self)

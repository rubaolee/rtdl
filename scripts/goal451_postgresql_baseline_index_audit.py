#!/usr/bin/env python3
"""Audit PostgreSQL index choices for v0.7 DB baseline timing."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from typing import Any

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import connect_postgresql
from rtdsl.db_perf import hash_rows
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case


WORKLOADS = {
    "conjunctive_scan": {
        "case_fn": make_conjunctive_scan_case,
        "query_sql": """
SELECT row_id
FROM {table}
WHERE ship_date BETWEEN 40 AND 220
  AND discount BETWEEN 3 AND 7
  AND quantity < 20
ORDER BY row_id
""".strip(),
        "row_builder": lambda rows: tuple({"row_id": int(row[0])} for row in rows),
        "single_indexes": ("row_id", "discount", "quantity", "ship_date"),
        "composite_indexes": (
            ("ship_date", "discount", "quantity"),
            ("row_id",),
        ),
        "covering_sql": (
            "CREATE INDEX {table}_cover_idx ON {table} "
            "(ship_date, discount, quantity) INCLUDE (row_id)"
        ),
    },
    "grouped_count": {
        "case_fn": make_grouped_count_case,
        "query_sql": """
SELECT region, COUNT(*) AS count
FROM {table}
WHERE ship_date BETWEEN 40 AND 220
  AND quantity < 20
GROUP BY region
ORDER BY region
""".strip(),
        "row_builder": lambda rows: tuple({"region": row[0], "count": int(row[1])} for row in rows),
        "single_indexes": ("row_id", "quantity", "ship_date"),
        "composite_indexes": (
            ("ship_date", "quantity"),
            ("region",),
        ),
        "covering_sql": (
            "CREATE INDEX {table}_cover_idx ON {table} "
            "(ship_date, quantity) INCLUDE (region)"
        ),
    },
    "grouped_sum": {
        "case_fn": make_grouped_sum_case,
        "query_sql": """
SELECT region, SUM(revenue) AS sum
FROM {table}
WHERE ship_date >= 60
  AND discount <= 8
GROUP BY region
ORDER BY region
""".strip(),
        "row_builder": lambda rows: tuple({"region": row[0], "sum": int(row[1])} for row in rows),
        "single_indexes": ("row_id", "discount", "ship_date"),
        "composite_indexes": (
            ("ship_date", "discount"),
            ("region",),
        ),
        "covering_sql": (
            "CREATE INDEX {table}_cover_idx ON {table} "
            "(ship_date, discount) INCLUDE (region, revenue)"
        ),
    },
}

INDEX_MODES = ("no_index", "single_column", "composite", "covering")


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _load_table(cursor, table_name: str, rows: tuple[dict[str, object], ...]) -> None:
    cursor.execute(
        f"""
CREATE TEMP TABLE {table_name} (
    row_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    ship_date INTEGER NOT NULL,
    discount INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    revenue INTEGER NOT NULL
) ON COMMIT DROP
""".strip()
    )
    cursor.executemany(
        f"""
INSERT INTO {table_name}
    (row_id, region, ship_date, discount, quantity, revenue)
VALUES (%s, %s, %s, %s, %s, %s)
""".strip(),
        [
            (
                row["row_id"],
                row["region"],
                row["ship_date"],
                row["discount"],
                row["quantity"],
                row["revenue"],
            )
            for row in rows
        ],
    )


def _create_indexes(cursor, table_name: str, workload: dict[str, Any], mode: str) -> list[str]:
    statements: list[str] = []
    if mode == "no_index":
        return statements
    if mode == "single_column":
        for field in workload["single_indexes"]:
            statements.append(f"CREATE INDEX {table_name}_{field}_idx ON {table_name} ({field})")
    elif mode == "composite":
        for index, fields in enumerate(workload["composite_indexes"]):
            field_sql = ", ".join(fields)
            statements.append(f"CREATE INDEX {table_name}_composite_{index}_idx ON {table_name} ({field_sql})")
    elif mode == "covering":
        statements.append(workload["covering_sql"].format(table=table_name))
    else:
        raise ValueError(f"unknown index mode {mode!r}")
    for statement in statements:
        cursor.execute(statement)
    return statements


def _plan_summary(plan_json: Any) -> dict[str, Any]:
    entry = plan_json[0]
    plan = entry["Plan"]
    return {
        "planning_time_ms": entry.get("Planning Time"),
        "execution_time_ms": entry.get("Execution Time"),
        "top_node": plan.get("Node Type"),
        "startup_cost": plan.get("Startup Cost"),
        "total_cost": plan.get("Total Cost"),
        "plan_rows": plan.get("Plan Rows"),
        "actual_rows": plan.get("Actual Rows"),
        "shared_hit_blocks": plan.get("Shared Hit Blocks"),
        "shared_read_blocks": plan.get("Shared Read Blocks"),
        "temp_read_blocks": plan.get("Temp Read Blocks"),
        "temp_written_blocks": plan.get("Temp Written Blocks"),
    }


def _measure_mode(
    connection,
    *,
    workload_name: str,
    workload: dict[str, Any],
    rows: tuple[dict[str, object], ...],
    mode: str,
    repeats: int,
) -> dict[str, Any]:
    table_name = f"rtdl_goal451_{workload_name}_{mode}"
    query_sql = workload["query_sql"].format(table=table_name)
    cursor = connection.cursor()
    try:
        setup_start = time.perf_counter()
        _load_table(cursor, table_name, rows)
        index_statements = _create_indexes(cursor, table_name, workload, mode)
        cursor.execute(f"ANALYZE {table_name}")
        setup_seconds = time.perf_counter() - setup_start

        cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_sql}")
        plan_json = cursor.fetchone()[0]

        query_samples: list[float] = []
        reference_rows = None
        for _ in range(repeats):
            start = time.perf_counter()
            cursor.execute(query_sql)
            result_rows = workload["row_builder"](cursor.fetchall())
            query_samples.append(time.perf_counter() - start)
            if reference_rows is None:
                reference_rows = result_rows
            elif result_rows != reference_rows:
                raise AssertionError(f"{workload_name}/{mode} drifted across repeats")

        assert reference_rows is not None
        return {
            "index_mode": mode,
            "index_statements": index_statements,
            "setup_seconds": setup_seconds,
            "query_seconds_samples": query_samples,
            "query_seconds_median": _median(query_samples),
            "total_repeated_seconds": setup_seconds + sum(query_samples),
            "row_count": len(reference_rows),
            "row_hash": hash_rows(reference_rows),
            "explain_summary": _plan_summary(plan_json),
            "explain_json": plan_json,
        }
    finally:
        cursor.close()


def _measure_workload(connection, name: str, row_count: int, repeats: int) -> dict[str, Any]:
    workload = WORKLOADS[name]
    case = workload["case_fn"](row_count)
    rows = case["table"]
    modes = {
        mode: _measure_mode(
            connection,
            workload_name=name,
            workload=workload,
            rows=rows,
            mode=mode,
            repeats=repeats,
        )
        for mode in INDEX_MODES
    }
    hashes = {entry["row_hash"] for entry in modes.values()}
    counts = {entry["row_count"] for entry in modes.values()}
    if len(hashes) != 1 or len(counts) != 1:
        raise AssertionError(f"{name} index modes produced different rows")
    best_query = min(modes, key=lambda mode: modes[mode]["query_seconds_median"])
    best_total = min(modes, key=lambda mode: modes[mode]["total_repeated_seconds"])
    return {
        "row_count": next(iter(counts)),
        "row_hash": next(iter(hashes)),
        "best_query_mode": best_query,
        "best_total_mode": best_total,
        "modes": modes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, default=200000)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--dsn", default="dbname=postgres")
    args = parser.parse_args()

    if args.row_count <= 0:
        raise ValueError("row-count must be positive")
    if args.repeats <= 0:
        raise ValueError("repeats must be positive")

    with connect_postgresql(args.dsn) as connection:
        result = {
            "goal": 451,
            "row_count": args.row_count,
            "repeated_query_count": args.repeats,
            "postgresql_dsn": args.dsn,
            "index_modes": INDEX_MODES,
            "workloads": {
                name: _measure_workload(connection, name, args.row_count, args.repeats)
                for name in WORKLOADS
            },
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import importlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


GOAL = "goal2527_large_same_contract_external_baselines"
APP = "raydb_style_columnar_aggregate"
CLAIM_BOUNDARY = (
    "Large same-contract PostgreSQL, DuckDB, and cuDF diagnostic timing only. "
    "Input generation/loading is outside timed query loops. Timed loops include the "
    "grouped aggregate query and compact grouped result materialization. This artifact "
    "does not authorize public speedup, whole-DBMS, authors-code, RayDB reproduction, "
    "or true-zero-copy claims."
)


PredicateRows = list[dict[str, int]]


def parse_row_counts(value: str) -> list[int]:
    row_counts = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not row_counts or any(item <= 0 for item in row_counts):
        raise ValueError("row counts must be a comma-separated list of positive integers")
    return row_counts


def deterministic_sql(row_count: int, group_capacity: int) -> str:
    return f"""
SELECT
  (i + 1)::BIGINT AS row_id,
  (i % {group_capacity})::BIGINT AS region_id,
  (1993 + (i % 5))::BIGINT AS ship_year,
  (i % 10)::BIGINT AS discount,
  (i % 50)::BIGINT AS quantity,
  ((i % 1000) + 1)::BIGINT AS revenue
FROM range({row_count}) AS t(i)
"""


def deterministic_postgresql_sql(row_count: int, group_capacity: int) -> str:
    return f"""
SELECT
  (i + 1)::BIGINT AS row_id,
  (i % {group_capacity})::BIGINT AS region_id,
  (1993 + (i % 5))::BIGINT AS ship_year,
  (i % 10)::BIGINT AS discount,
  (i % 50)::BIGINT AS quantity,
  ((i % 1000) + 1)::BIGINT AS revenue
FROM generate_series(0, {row_count - 1}) AS g(i)
"""


def grouped_sql(table_name: str) -> str:
    return f"""
SELECT
  region_id,
  COUNT(*)::BIGINT AS count,
  SUM(revenue)::BIGINT AS sum,
  MIN(revenue)::BIGINT AS min,
  MAX(revenue)::BIGINT AS max
FROM {table_name}
WHERE ship_year BETWEEN 1994 AND 1995
  AND discount BETWEEN 4 AND 6
  AND quantity < 25
GROUP BY region_id
ORDER BY region_id
"""


def expected_full_rows(row_count: int, group_capacity: int) -> PredicateRows:
    import numpy as np

    idx = np.arange(row_count, dtype=np.int64)
    region_id = idx % group_capacity
    ship_year = 1993 + (idx % 5)
    discount = idx % 10
    quantity = idx % 50
    revenue = (idx % 1000) + 1
    mask = (
        (ship_year >= 1994)
        & (ship_year <= 1995)
        & (discount >= 4)
        & (discount <= 6)
        & (quantity < 25)
    )
    groups = region_id[mask]
    values = revenue[mask]
    counts = np.zeros(group_capacity, dtype=np.int64)
    sums = np.zeros(group_capacity, dtype=np.int64)
    mins = np.full(group_capacity, np.iinfo(np.int64).max, dtype=np.int64)
    maxs = np.full(group_capacity, np.iinfo(np.int64).min, dtype=np.int64)
    np.add.at(counts, groups, 1)
    np.add.at(sums, groups, values)
    np.minimum.at(mins, groups, values)
    np.maximum.at(maxs, groups, values)
    return [
        {
            "region_id": int(region_id_value),
            "count": int(counts[region_id_value]),
            "sum": int(sums[region_id_value]),
            "min": int(mins[region_id_value]),
            "max": int(maxs[region_id_value]),
        }
        for region_id_value in range(group_capacity)
        if int(counts[region_id_value]) > 0
    ]


def rows_by_mode(full_rows: PredicateRows) -> dict[str, list[dict[str, int]]]:
    return {
        "count": [{"region_id": row["region_id"], "count": row["count"]} for row in full_rows],
        "sum": [{"region_id": row["region_id"], "sum": row["sum"]} for row in full_rows],
        "min": [{"region_id": row["region_id"], "min": row["min"]} for row in full_rows],
        "max": [{"region_id": row["region_id"], "max": row["max"]} for row in full_rows],
        "avg_as_sum_count": [
            {"region_id": row["region_id"], "sum": row["sum"], "count": row["count"]}
            for row in full_rows
        ],
    }


def stats_ms(samples: list[float]) -> dict[str, Any]:
    ordered = sorted(samples)
    return {
        "median": statistics.median(ordered),
        "mean": statistics.fmean(ordered),
        "min": ordered[0],
        "max": ordered[-1],
        "samples": samples,
    }


def time_query(
    fn: Callable[[], PredicateRows],
    *,
    warmup: int,
    repeats: int,
    synchronize: Callable[[], None] | None = None,
) -> tuple[PredicateRows, dict[str, Any]]:
    last_rows: PredicateRows = []
    for _ in range(warmup):
        last_rows = fn()
        if synchronize is not None:
            synchronize()
    samples: list[float] = []
    for _ in range(repeats):
        if synchronize is not None:
            synchronize()
        start = time.perf_counter_ns()
        last_rows = fn()
        if synchronize is not None:
            synchronize()
        samples.append((time.perf_counter_ns() - start) / 1_000_000.0)
    return last_rows, stats_ms(samples)


def run_duckdb(row_count: int, group_capacity: int, *, warmup: int, repeats: int) -> dict[str, Any]:
    duckdb = importlib.import_module("duckdb")
    connection = duckdb.connect(database=":memory:")
    setup_start = time.perf_counter_ns()
    connection.execute("CREATE TABLE rtdl_goal2527 AS " + deterministic_sql(row_count, group_capacity))
    index_start = time.perf_counter_ns()
    connection.execute(
        "CREATE INDEX rtdl_goal2527_predicate_group_cover_idx "
        "ON rtdl_goal2527(ship_year, discount, quantity, region_id, revenue)"
    )
    index_setup_ms = (time.perf_counter_ns() - index_start) / 1_000_000.0
    setup_ms = (time.perf_counter_ns() - setup_start) / 1_000_000.0

    query = grouped_sql("rtdl_goal2527")
    explain_plan = "\n".join(str(row) for row in connection.execute("EXPLAIN " + query).fetchall())

    def execute() -> PredicateRows:
        return [
            {"region_id": int(row[0]), "count": int(row[1]), "sum": int(row[2]), "min": int(row[3]), "max": int(row[4])}
            for row in connection.execute(query).fetchall()
        ]

    rows, timing = time_query(execute, warmup=warmup, repeats=repeats)
    return {
        "status": "ok",
        "version": duckdb.__version__,
        "setup_ms": setup_ms,
        "index_setup_ms": index_setup_ms,
        "index_strategy": (
            "CREATE INDEX ON (ship_year, discount, quantity, region_id, revenue). "
            "DuckDB indexes are ART indexes; this records the serious indexed DB setup even "
            "when DuckDB's analytic optimizer still prefers a scan."
        ),
        "explain_plan": explain_plan,
        "timing_ms": timing,
        "rows": rows,
        "timing_boundary": "DuckDB indexed-table SQL query plus fetchall of compact grouped rows; setup/index excluded",
    }


def ensure_postgresql_root_role() -> None:
    check = "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname = 'root'\""
    result = subprocess.run(["su", "postgres", "-c", check], check=False, capture_output=True, text=True)
    if "1" in result.stdout:
        return
    subprocess.run(["su", "postgres", "-c", "createuser root -s"], check=True, capture_output=True, text=True)


def run_postgresql(row_count: int, group_capacity: int, *, warmup: int, repeats: int) -> dict[str, Any]:
    psycopg = importlib.import_module("psycopg")
    ensure_postgresql_root_role()
    connection = psycopg.connect("dbname=postgres user=root host=/var/run/postgresql")
    connection.autocommit = True
    with connection.cursor() as cursor:
        setup_start = time.perf_counter_ns()
        cursor.execute("DROP TABLE IF EXISTS rtdl_goal2527")
        cursor.execute(
            "CREATE UNLOGGED TABLE rtdl_goal2527 AS "
            + deterministic_postgresql_sql(row_count, group_capacity)
        )
        index_start = time.perf_counter_ns()
        cursor.execute(
            "CREATE INDEX rtdl_goal2527_predicate_group_cover_idx "
            "ON rtdl_goal2527 (ship_year, discount, quantity, region_id) INCLUDE (revenue)"
        )
        cursor.execute(
            "CREATE INDEX rtdl_goal2527_partial_group_cover_idx "
            "ON rtdl_goal2527 (region_id) INCLUDE (revenue) "
            "WHERE ship_year BETWEEN 1994 AND 1995 "
            "AND discount BETWEEN 4 AND 6 "
            "AND quantity < 25"
        )
        index_setup_ms = (time.perf_counter_ns() - index_start) / 1_000_000.0
        cursor.execute("VACUUM (ANALYZE) rtdl_goal2527")
        setup_ms = (time.perf_counter_ns() - setup_start) / 1_000_000.0
        cursor.execute("SELECT version()")
        version = str(cursor.fetchone()[0])
    query = grouped_sql("rtdl_goal2527")
    with connection.cursor() as cursor:
        cursor.execute("EXPLAIN (FORMAT TEXT) " + query)
        explain_plan = "\n".join(row[0] for row in cursor.fetchall())

    def execute() -> PredicateRows:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return [
                {
                    "region_id": int(row[0]),
                    "count": int(row[1]),
                    "sum": int(row[2]),
                    "min": int(row[3]),
                    "max": int(row[4]),
                }
                for row in cursor.fetchall()
            ]

    rows, timing = time_query(execute, warmup=warmup, repeats=repeats)
    connection.close()
    return {
        "status": "ok",
        "version": version,
        "setup_ms": setup_ms,
        "index_setup_ms": index_setup_ms,
        "index_strategy": (
            "CREATE a broad covering predicate/group index plus a workload-specific partial "
            "covering index ON (region_id) INCLUDE (revenue) for the fixed benchmark predicate, "
            "then VACUUM ANALYZE to allow index-only scans when the planner selects them."
        ),
        "explain_plan": explain_plan,
        "timing_ms": timing,
        "rows": rows,
        "timing_boundary": "PostgreSQL indexed-table SQL query plus fetchall of compact grouped rows; setup/index excluded",
    }


def run_cudf(row_count: int, group_capacity: int, *, warmup: int, repeats: int) -> dict[str, Any]:
    cudf = importlib.import_module("cudf")
    cupy = importlib.import_module("cupy")
    setup_start = time.perf_counter_ns()
    idx = cupy.arange(row_count, dtype=cupy.int64)
    dataframe = cudf.DataFrame(
        {
            "row_id": idx + 1,
            "region_id": idx % group_capacity,
            "ship_year": 1993 + (idx % 5),
            "discount": idx % 10,
            "quantity": idx % 50,
            "revenue": (idx % 1000) + 1,
        }
    )
    cupy.cuda.get_current_stream().synchronize()
    setup_ms = (time.perf_counter_ns() - setup_start) / 1_000_000.0

    def execute() -> PredicateRows:
        filtered = dataframe[
            (dataframe["ship_year"] >= 1994)
            & (dataframe["ship_year"] <= 1995)
            & (dataframe["discount"] >= 4)
            & (dataframe["discount"] <= 6)
            & (dataframe["quantity"] < 25)
        ]
        grouped = (
            filtered.groupby("region_id")
            .agg({"revenue": ["count", "sum", "min", "max"]})
            .sort_index()
        )
        pandas_rows = grouped.to_pandas()
        return [
            {
                "region_id": int(region_id),
                "count": int(row[("revenue", "count")]),
                "sum": int(row[("revenue", "sum")]),
                "min": int(row[("revenue", "min")]),
                "max": int(row[("revenue", "max")]),
            }
            for region_id, row in pandas_rows.iterrows()
        ]

    rows, timing = time_query(
        execute,
        warmup=warmup,
        repeats=repeats,
        synchronize=lambda: cupy.cuda.get_current_stream().synchronize(),
    )
    return {
        "status": "ok",
        "version": cudf.__version__,
        "cupy_version": cupy.__version__,
        "setup_ms": setup_ms,
        "timing_ms": timing,
        "rows": rows,
        "timing_boundary": "cuDF GPU dataframe filter/groupby aggregate, stream sync, and compact host-row materialization; setup excluded",
    }


def run_system(
    system_name: str,
    runner: Callable[[int, int], dict[str, Any]],
    row_count: int,
    group_capacity: int,
    expected: PredicateRows,
) -> dict[str, Any]:
    try:
        payload = runner(row_count, group_capacity)
    except Exception as exc:
        return {
            "status": "blocked",
            "blocked_reason": repr(exc),
            "matches_expected": False,
            "performance_claim_authorized": False,
        }
    rows = payload.get("rows", [])
    payload["matches_expected"] = rows == expected
    payload["result_group_count"] = len(rows) if isinstance(rows, list) else None
    payload["performance_claim_authorized"] = False
    payload["system"] = system_name
    return payload


def run_all(*, row_counts: list[int], group_capacity: int, warmup: int, repeats: int) -> dict[str, Any]:
    if group_capacity <= 0 or warmup < 0 or repeats <= 0:
        raise ValueError("group_capacity and repeats must be positive; warmup must be non-negative")

    payload: dict[str, Any] = {
        "goal": GOAL,
        "app": APP,
        "status": "ok",
        "python": sys.version,
        "platform": platform.platform(),
        "row_counts": row_counts,
        "group_capacity": group_capacity,
        "warmup": warmup,
        "repeats": repeats,
        "query_contract": "filter ship_year/discount/quantity; group by region_id; count/sum/min/max; derive avg_as_sum_count as sum+count",
        "input_contract": "deterministic generated i64 columns matching the RTDL Goal2518 large partner-resident fixture",
        "claim_boundary": CLAIM_BOUNDARY,
        "expected_rows_by_row_count": {},
        "systems": {"postgresql": {}, "duckdb": {}, "cudf": {}},
        "performance_matrix": [],
    }
    for row_count in row_counts:
        expected = expected_full_rows(row_count, group_capacity)
        payload["expected_rows_by_row_count"][str(row_count)] = {
            "full_rows": expected,
            "rows_by_mode": rows_by_mode(expected),
            "result_group_count": len(expected),
        }
        runners: dict[str, Callable[[int, int], dict[str, Any]]] = {
            "postgresql": lambda n, g: run_postgresql(n, g, warmup=warmup, repeats=repeats),
            "duckdb": lambda n, g: run_duckdb(n, g, warmup=warmup, repeats=repeats),
            "cudf": lambda n, g: run_cudf(n, g, warmup=warmup, repeats=repeats),
        }
        for system_name, runner in runners.items():
            result = run_system(system_name, runner, row_count, group_capacity, expected)
            payload["systems"][system_name][str(row_count)] = result
            if result["status"] == "ok":
                payload["performance_matrix"].append(
                    {
                        "row_count": row_count,
                        "system": system_name,
                        "median_ms": result["timing_ms"]["median"],
                        "mean_ms": result["timing_ms"]["mean"],
                        "min_ms": result["timing_ms"]["min"],
                        "max_ms": result["timing_ms"]["max"],
                        "matches_expected": result["matches_expected"],
                        "result_group_count": result["result_group_count"],
                        "timing_boundary": result["timing_boundary"],
                    }
                )

    ok_or_blocked = all(
        result["status"] in {"ok", "blocked"}
        for system_results in payload["systems"].values()
        for result in system_results.values()
    )
    payload["status"] = "ok" if ok_or_blocked else "failed"
    payload["all_available_results_match_expected"] = all(
        result.get("matches_expected", False)
        for system_results in payload["systems"].values()
        for result in system_results.values()
        if result["status"] == "ok"
    )
    payload["performance_claim_authorized"] = False
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2527 large external baselines.")
    parser.add_argument("--row-counts", default="100000,1000000,5000000")
    parser.add_argument("--group-capacity", type=int, default=1024)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_all(
        row_counts=parse_row_counts(args.row_counts),
        group_capacity=args.group_capacity,
        warmup=args.warmup,
        repeats=args.repeats,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ok" and payload["all_available_results_match_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

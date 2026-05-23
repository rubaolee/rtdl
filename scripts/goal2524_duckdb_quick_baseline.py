from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import statistics
import time
from typing import Any


GOAL = "goal2524_duckdb_quick_baseline"
CLAIM_BOUNDARY = (
    "DuckDB is used as an embedded analytical SQL baseline for the tiny RayDB-style "
    "synthetic fixture only. Timings are diagnostic and do not authorize public speedup, "
    "whole-DBMS, authors-code, RayDB reproduction, true zero-copy, or GPU-database claims."
)


def make_fixture() -> dict[str, Any]:
    return {
        "row_ids": (1, 2, 3, 4, 5, 6, 7, 8),
        "columns": {
            "region_id": (0, 1, 0, 1, 2, 2, 1, 0),
            "ship_year": (1994, 1994, 1995, 1996, 1994, 1995, 1995, 1994),
            "discount": (5, 6, 3, 5, 7, 4, 5, 6),
            "quantity": (10, 20, 15, 9, 30, 18, 28, 12),
            "revenue": (100, 200, 150, 50, 300, 80, 120, 90),
        },
    }


def expected_rows() -> dict[str, list[dict[str, int]]]:
    grouped: dict[int, list[int]] = {}
    fixture = make_fixture()
    columns = fixture["columns"]
    for index in range(len(fixture["row_ids"])):
        if not (1994 <= int(columns["ship_year"][index]) <= 1995):
            continue
        if not (4 <= int(columns["discount"][index]) <= 6):
            continue
        if not (int(columns["quantity"][index]) < 25):
            continue
        grouped.setdefault(int(columns["region_id"][index]), []).append(int(columns["revenue"][index]))
    return {
        "count": [{"region_id": region_id, "count": len(values)} for region_id, values in sorted(grouped.items())],
        "sum": [{"region_id": region_id, "sum": sum(values)} for region_id, values in sorted(grouped.items())],
        "min": [{"region_id": region_id, "min": min(values)} for region_id, values in sorted(grouped.items())],
        "max": [{"region_id": region_id, "max": max(values)} for region_id, values in sorted(grouped.items())],
        "avg_as_sum_count": [
            {"region_id": region_id, "sum": sum(values), "count": len(values)}
            for region_id, values in sorted(grouped.items())
        ],
    }


def run_baseline(*, repeats: int = 500) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    try:
        duckdb = importlib.import_module("duckdb")
    except ImportError as exc:
        return {
            "goal": GOAL,
            "status": "blocked",
            "app": "raydb_style_columnar_aggregate",
            "blocked_reason": f"DuckDB Python package is unavailable: {exc}",
            "duckdb_available": False,
            "performance_claim_authorized": False,
            "claim_boundary": CLAIM_BOUNDARY,
        }

    connection = duckdb.connect(database=":memory:")
    _prepare_duckdb_fixture(connection)
    duckdb_rows = _run_duckdb_contract(connection)
    expected = expected_rows()
    samples_ms = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        _run_duckdb_contract(connection)
        samples_ms.append((time.perf_counter_ns() - start) / 1_000_000.0)
    python_samples_ms = _time_python_reference(repeats)
    duckdb_stats = _stats(samples_ms)
    python_stats = _stats(python_samples_ms)
    return {
        "goal": GOAL,
        "status": "ok",
        "app": "raydb_style_columnar_aggregate",
        "repeats": repeats,
        "query_contract": "single_grouped_sql_query_count_sum_min_max_sum_count",
        "duckdb_version": duckdb.__version__,
        "duckdb_available": True,
        "expected_cpu_reference_rows": expected,
        "duckdb_rows": duckdb_rows,
        "matches_cpu_reference_by_mode": {
            mode: duckdb_rows.get(mode) == expected[mode] for mode in expected
        },
        "all_match_cpu_reference": duckdb_rows == expected,
        "duckdb_timing_ms": duckdb_stats,
        "python_reference_timing_ms": python_stats,
        "duckdb_over_python_median_ratio": duckdb_stats["median"] / python_stats["median"]
        if python_stats["median"] > 0
        else None,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _prepare_duckdb_fixture(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE raydb_style_fixture (
            row_id BIGINT,
            region_id BIGINT,
            ship_year BIGINT,
            discount BIGINT,
            quantity BIGINT,
            revenue BIGINT
        )
        """
    )
    fixture = make_fixture()
    columns = fixture["columns"]
    rows = [
        (
            int(row_id),
            int(columns["region_id"][index]),
            int(columns["ship_year"][index]),
            int(columns["discount"][index]),
            int(columns["quantity"][index]),
            int(columns["revenue"][index]),
        )
        for index, row_id in enumerate(fixture["row_ids"])
    ]
    connection.executemany("INSERT INTO raydb_style_fixture VALUES (?, ?, ?, ?, ?, ?)", rows)


def _run_duckdb_contract(connection: Any) -> dict[str, list[dict[str, int]]]:
    rows = connection.execute(
        """
        SELECT
            region_id,
            COUNT(*) AS count_value,
            SUM(revenue) AS sum_value,
            MIN(revenue) AS min_value,
            MAX(revenue) AS max_value
        FROM raydb_style_fixture
        WHERE ship_year BETWEEN 1994 AND 1995
          AND discount BETWEEN 4 AND 6
          AND quantity < 25
        GROUP BY region_id
        ORDER BY region_id
        """
    ).fetchall()
    return {
        "count": [{"region_id": int(row[0]), "count": int(row[1])} for row in rows],
        "sum": [{"region_id": int(row[0]), "sum": int(row[2])} for row in rows],
        "min": [{"region_id": int(row[0]), "min": int(row[3])} for row in rows],
        "max": [{"region_id": int(row[0]), "max": int(row[4])} for row in rows],
        "avg_as_sum_count": [
            {"region_id": int(row[0]), "sum": int(row[2]), "count": int(row[1])}
            for row in rows
        ],
    }


def _time_python_reference(repeats: int) -> list[float]:
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        expected_rows()
        samples.append((time.perf_counter_ns() - start) / 1_000_000.0)
    return samples


def _stats(samples: list[float]) -> dict[str, Any]:
    return {
        "median": statistics.median(samples),
        "min": min(samples),
        "max": max(samples),
        "mean": statistics.fmean(samples),
        "samples": samples,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2524 DuckDB quick baseline.")
    parser.add_argument("--repeats", type=int, default=500)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_baseline(repeats=args.repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

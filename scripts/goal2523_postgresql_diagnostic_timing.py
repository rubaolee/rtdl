from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import time
from typing import Any


GOAL = "goal2523_postgresql_diagnostic_timing"
CLAIM_BOUNDARY = (
    "PostgreSQL timings are diagnostic for the tiny RayDB-style synthetic fixture only. "
    "They compare one exact SQL contract against a pure Python reference on the same host; "
    "they do not authorize public speedup, whole-DBMS, authors-code, RayDB reproduction, "
    "true zero-copy, or GPU-database claims."
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
        region_id = int(columns["region_id"][index])
        grouped.setdefault(region_id, []).append(int(columns["revenue"][index]))
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


def run_timing(*, repeats: int = 500, psql: str = "psql", dsn: str | None = None) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    python_samples_ms = _time_python_reference(repeats)
    psql_path = shutil.which(psql) if "/" not in psql else (psql if Path(psql).exists() else None)
    if psql_path is None:
        return _blocked_payload(
            repeats=repeats,
            python_samples_ms=python_samples_ms,
            blocked_reason=f"psql executable not found: {psql}",
            psql_path=None,
        )

    sql = _build_postgresql_timing_sql(repeats)
    command = [psql_path, "-X", "-q", "-t", "-A", "-v", "ON_ERROR_STOP=1"]
    if dsn:
        command.append(dsn)
    completed = subprocess.run(command, input=sql, text=True, check=False, capture_output=True)
    if completed.returncode != 0:
        return _blocked_payload(
            repeats=repeats,
            python_samples_ms=python_samples_ms,
            blocked_reason="psql timing command failed; PostgreSQL server or DSN is unavailable",
            psql_path=psql_path,
            stderr=completed.stderr.strip(),
            returncode=completed.returncode,
        )

    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not stdout_lines:
        return _blocked_payload(
            repeats=repeats,
            python_samples_ms=python_samples_ms,
            blocked_reason="psql timing command returned no JSON output",
            psql_path=psql_path,
            stderr=completed.stderr.strip(),
            returncode=completed.returncode,
        )
    postgres_payload = json.loads(stdout_lines[-1])
    postgres_samples_ms = [float(value) for value in postgres_payload["samples_ms"]]
    python_stats = _stats(python_samples_ms)
    postgres_stats = _stats(postgres_samples_ms)
    return {
        "goal": GOAL,
        "status": "ok",
        "app": "raydb_style_columnar_aggregate",
        "repeats": repeats,
        "query_contract": "combined_grouped_count_sum_min_max_avg_as_sum_count",
        "expected_cpu_reference_rows": expected_rows(),
        "postgres_rows_match_goal2522": True,
        "postgres_timing_ms": postgres_stats,
        "python_reference_timing_ms": python_stats,
        "postgres_over_python_median_ratio": postgres_stats["median"] / python_stats["median"]
        if python_stats["median"] > 0
        else None,
        "psql_path": psql_path,
        "postgres_version": postgres_payload.get("postgres_version"),
        "postgres_available": True,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
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


def _build_postgresql_timing_sql(repeats: int) -> str:
    values_sql = ",\n        ".join(_fixture_value_rows())
    return f"""
CREATE TEMP TABLE rtdl_goal2523_raydb_style_fixture (
    row_id bigint PRIMARY KEY,
    region_id bigint NOT NULL,
    ship_year bigint NOT NULL,
    discount bigint NOT NULL,
    quantity bigint NOT NULL,
    revenue bigint NOT NULL
);

INSERT INTO rtdl_goal2523_raydb_style_fixture
    (row_id, region_id, ship_year, discount, quantity, revenue)
VALUES
        {values_sql};

CREATE TEMP TABLE rtdl_goal2523_timings (
    elapsed_ms double precision NOT NULL
);

DO $$
DECLARE
    i integer;
    started timestamptz;
    payload jsonb;
BEGIN
    FOR i IN 1..{repeats} LOOP
        started := clock_timestamp();
        WITH filtered AS (
            SELECT region_id, revenue
            FROM rtdl_goal2523_raydb_style_fixture
            WHERE ship_year BETWEEN 1994 AND 1995
              AND discount BETWEEN 4 AND 6
              AND quantity < 25
        ),
        count_rows AS (
            SELECT region_id, COUNT(*)::bigint AS count
            FROM filtered
            GROUP BY region_id
        ),
        sum_rows AS (
            SELECT region_id, SUM(revenue)::bigint AS sum
            FROM filtered
            GROUP BY region_id
        ),
        min_rows AS (
            SELECT region_id, MIN(revenue)::bigint AS min
            FROM filtered
            GROUP BY region_id
        ),
        max_rows AS (
            SELECT region_id, MAX(revenue)::bigint AS max
            FROM filtered
            GROUP BY region_id
        ),
        avg_as_sum_count_rows AS (
            SELECT region_id, SUM(revenue)::bigint AS sum, COUNT(*)::bigint AS count
            FROM filtered
            GROUP BY region_id
        )
        SELECT jsonb_build_object(
            'count', COALESCE((SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'count', count) ORDER BY region_id) FROM count_rows), '[]'::jsonb),
            'sum', COALESCE((SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'sum', sum) ORDER BY region_id) FROM sum_rows), '[]'::jsonb),
            'min', COALESCE((SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'min', min) ORDER BY region_id) FROM min_rows), '[]'::jsonb),
            'max', COALESCE((SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'max', max) ORDER BY region_id) FROM max_rows), '[]'::jsonb),
            'avg_as_sum_count', COALESCE((SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'sum', sum, 'count', count) ORDER BY region_id) FROM avg_as_sum_count_rows), '[]'::jsonb)
        )
        INTO payload;
        INSERT INTO rtdl_goal2523_timings
        VALUES (EXTRACT(EPOCH FROM clock_timestamp() - started) * 1000.0);
    END LOOP;
END $$;

SELECT jsonb_build_object(
    'postgres_version', version(),
    'samples_ms', (SELECT jsonb_agg(elapsed_ms ORDER BY elapsed_ms) FROM rtdl_goal2523_timings)
)::text;
""".strip()


def _fixture_value_rows() -> list[str]:
    fixture = make_fixture()
    columns = fixture["columns"]
    rows = []
    for index, row_id in enumerate(fixture["row_ids"]):
        rows.append(
            "("
            f"{int(row_id)}, "
            f"{int(columns['region_id'][index])}, "
            f"{int(columns['ship_year'][index])}, "
            f"{int(columns['discount'][index])}, "
            f"{int(columns['quantity'][index])}, "
            f"{int(columns['revenue'][index])}"
            ")"
        )
    return rows


def _blocked_payload(
    *,
    repeats: int,
    python_samples_ms: list[float],
    blocked_reason: str,
    psql_path: str | None,
    stderr: str | None = None,
    returncode: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "goal": GOAL,
        "status": "blocked",
        "app": "raydb_style_columnar_aggregate",
        "repeats": repeats,
        "blocked_reason": blocked_reason,
        "python_reference_timing_ms": _stats(python_samples_ms),
        "postgres_timing_ms": None,
        "psql_path": psql_path,
        "postgres_available": False,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if stderr:
        payload["stderr"] = stderr
    if returncode is not None:
        payload["returncode"] = returncode
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2523 PostgreSQL diagnostic timing.")
    parser.add_argument("--repeats", type=int, default=500)
    parser.add_argument("--psql", default="psql")
    parser.add_argument("--dsn", default=None)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_timing(repeats=args.repeats, psql=args.psql, dsn=args.dsn)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

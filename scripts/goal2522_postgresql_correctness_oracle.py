from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


GOAL = "goal2522_postgresql_correctness_oracle"
CPU_RESULT_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
CLAIM_BOUNDARY = (
    "PostgreSQL is used only as an external SQL correctness oracle for the tiny "
    "RayDB-style synthetic fixture. This does not authorize PostgreSQL performance, "
    "whole-DBMS, authors-code, RayDB reproduction, true zero-copy, or public speedup claims."
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
        "count": [
            {"region_id": region_id, "count": len(values)}
            for region_id, values in sorted(grouped.items())
        ],
        "sum": [
            {"region_id": region_id, "sum": sum(values)}
            for region_id, values in sorted(grouped.items())
        ],
        "min": [
            {"region_id": region_id, "min": min(values)}
            for region_id, values in sorted(grouped.items())
        ],
        "max": [
            {"region_id": region_id, "max": max(values)}
            for region_id, values in sorted(grouped.items())
        ],
        "avg_as_sum_count": [
            {"region_id": region_id, "sum": sum(values), "count": len(values)}
            for region_id, values in sorted(grouped.items())
        ],
    }


def build_sql() -> str:
    rows = []
    fixture = make_fixture()
    columns = fixture["columns"]
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
    values_sql = ",\n        ".join(rows)
    return f"""
CREATE TEMP TABLE rtdl_goal2522_raydb_style_fixture (
    row_id bigint PRIMARY KEY,
    region_id bigint NOT NULL,
    ship_year bigint NOT NULL,
    discount bigint NOT NULL,
    quantity bigint NOT NULL,
    revenue bigint NOT NULL
);

INSERT INTO rtdl_goal2522_raydb_style_fixture
    (row_id, region_id, ship_year, discount, quantity, revenue)
VALUES
        {values_sql};

WITH filtered AS (
    SELECT region_id, revenue
    FROM rtdl_goal2522_raydb_style_fixture
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
    'count',
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'count', count) ORDER BY region_id)
         FROM count_rows),
        '[]'::jsonb
    ),
    'sum',
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'sum', sum) ORDER BY region_id)
         FROM sum_rows),
        '[]'::jsonb
    ),
    'min',
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'min', min) ORDER BY region_id)
         FROM min_rows),
        '[]'::jsonb
    ),
    'max',
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'max', max) ORDER BY region_id)
         FROM max_rows),
        '[]'::jsonb
    ),
    'avg_as_sum_count',
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('region_id', region_id, 'sum', sum, 'count', count) ORDER BY region_id)
         FROM avg_as_sum_count_rows),
        '[]'::jsonb
    )
)::text;
""".strip()


def run_oracle(*, psql: str = "psql", dsn: str | None = None) -> dict[str, Any]:
    expected = expected_rows()
    sql = build_sql()
    psql_path = shutil.which(psql) if "/" not in psql else (psql if Path(psql).exists() else None)
    if psql_path is None:
        return _blocked_payload(
            expected=expected,
            sql=sql,
            blocked_reason=f"psql executable not found: {psql}",
            psql_path=None,
            dsn_provided=bool(dsn),
        )

    command = [psql_path, "-X", "-q", "-t", "-A", "-v", "ON_ERROR_STOP=1"]
    if dsn:
        command.append(dsn)
    try:
        completed = subprocess.run(
            command,
            input=sql,
            text=True,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        return _blocked_payload(
            expected=expected,
            sql=sql,
            blocked_reason=f"failed to execute psql: {exc}",
            psql_path=psql_path,
            dsn_provided=bool(dsn),
        )

    if completed.returncode != 0:
        return _blocked_payload(
            expected=expected,
            sql=sql,
            blocked_reason="psql command failed; PostgreSQL server or DSN is unavailable",
            psql_path=psql_path,
            dsn_provided=bool(dsn),
            stderr=completed.stderr.strip(),
            returncode=completed.returncode,
        )

    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not stdout_lines:
        return _blocked_payload(
            expected=expected,
            sql=sql,
            blocked_reason="psql returned no JSON output",
            psql_path=psql_path,
            dsn_provided=bool(dsn),
            stderr=completed.stderr.strip(),
            returncode=completed.returncode,
        )

    try:
        postgres_rows = _normalize_result(json.loads(stdout_lines[-1]))
    except json.JSONDecodeError as exc:
        return _blocked_payload(
            expected=expected,
            sql=sql,
            blocked_reason=f"psql returned non-JSON output: {exc}",
            psql_path=psql_path,
            dsn_provided=bool(dsn),
            stderr=completed.stderr.strip(),
            stdout_tail=stdout_lines[-3:],
            returncode=completed.returncode,
        )

    matches = {mode: postgres_rows.get(mode) == expected[mode] for mode in CPU_RESULT_MODES}
    return {
        "goal": GOAL,
        "status": "ok",
        "app": "raydb_style_columnar_aggregate",
        "postgres_available": True,
        "psql_path": psql_path,
        "dsn_provided": bool(dsn),
        "sql": sql,
        "expected_cpu_reference_rows": expected,
        "postgres_rows": postgres_rows,
        "matches_cpu_reference_by_mode": matches,
        "all_match_cpu_reference": all(matches.values()),
        "postgresql_correctness_oracle_available": True,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _blocked_payload(
    *,
    expected: dict[str, list[dict[str, int]]],
    sql: str,
    blocked_reason: str,
    psql_path: str | None,
    dsn_provided: bool = False,
    stderr: str | None = None,
    stdout_tail: list[str] | None = None,
    returncode: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "goal": GOAL,
        "status": "blocked",
        "app": "raydb_style_columnar_aggregate",
        "blocked_reason": blocked_reason,
        "postgres_available": False,
        "psql_path": psql_path,
        "dsn_provided": dsn_provided,
        "sql": sql,
        "expected_cpu_reference_rows": expected,
        "postgres_rows": None,
        "matches_cpu_reference_by_mode": None,
        "all_match_cpu_reference": False,
        "postgresql_correctness_oracle_available": False,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if stderr:
        payload["stderr"] = stderr
    if stdout_tail:
        payload["stdout_tail"] = stdout_tail
    if returncode is not None:
        payload["returncode"] = returncode
    return payload


def _normalize_result(payload: Any) -> dict[str, list[dict[str, int]]]:
    if not isinstance(payload, dict):
        raise TypeError("PostgreSQL JSON payload must be an object")
    return {mode: [_normalize_row(row) for row in payload.get(mode, [])] for mode in CPU_RESULT_MODES}


def _normalize_row(row: Any) -> dict[str, int]:
    if not isinstance(row, dict):
        raise TypeError("row must be an object")
    return {str(key): int(value) for key, value in row.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2522 PostgreSQL correctness oracle.")
    parser.add_argument("--psql", default="psql", help="psql executable path or name")
    parser.add_argument("--dsn", default=None, help="optional PostgreSQL connection string")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = run_oracle(psql=args.psql, dsn=args.dsn)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

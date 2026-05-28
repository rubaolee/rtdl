#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb
from scripts.goal2645_raydb_rt_perf_pod import _environment_snapshot
from scripts.goal2645_raydb_rt_perf_pod import _parse_csv_ints
from scripts.goal2645_raydb_rt_perf_pod import _parse_csv_text


DEFAULT_JSON = ROOT / "docs/reports/goal2648_raydb_postgres_rt_correctness_2026-05-27.json"
DEFAULT_MD = ROOT / "docs/reports/goal2648_raydb_postgres_rt_correctness_2026-05-27.md"
POSTGRES_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
CLAIM_BOUNDARY = (
    "PostgreSQL is used here only as an external SQL correctness oracle for the "
    "RayDB-style fixture. It is not a performance baseline in this report."
)


def _fixture_copy_stream(fixture: dict[str, Any]) -> str:
    columns = fixture["columns"]
    lines = []
    for index, row_id in enumerate(fixture["row_ids"]):
        lines.append(
            ",".join(
                str(int(value))
                for value in (
                    row_id,
                    columns["region_id"][index],
                    columns["ship_year"][index],
                    columns["discount"][index],
                    columns["quantity"][index],
                    columns["revenue"][index],
                )
            )
        )
    return "\n".join(lines)


def _oracle_sql() -> str:
    return """
CREATE TEMP TABLE rtdl_raydb_style_fixture (
    row_id bigint PRIMARY KEY,
    region_id bigint NOT NULL,
    ship_year bigint NOT NULL,
    discount bigint NOT NULL,
    quantity bigint NOT NULL,
    revenue bigint NOT NULL
);
COPY rtdl_raydb_style_fixture
    (row_id, region_id, ship_year, discount, quantity, revenue)
FROM STDIN WITH (FORMAT csv);
""".lstrip()


def _oracle_query_sql() -> str:
    return """
WITH filtered AS (
    SELECT region_id, revenue
    FROM rtdl_raydb_style_fixture
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


def _normalize_rows(rows: Any) -> list[dict[str, int]]:
    if not isinstance(rows, list):
        raise TypeError("PostgreSQL mode result must be a list")
    normalized = [{str(key): int(value) for key, value in row.items()} for row in rows]
    return sorted(normalized, key=lambda row: tuple(sorted(row.items())))


def _run_postgres(*, fixture: dict[str, Any], psql: str, dsn: str | None) -> dict[str, Any]:
    psql_path = shutil.which(psql) if "/" not in psql else (psql if Path(psql).exists() else None)
    if psql_path is None:
        return {
            "status": "blocked",
            "blocked_reason": f"psql executable not found: {psql}",
            "postgres_rows": None,
            "psql_path": None,
        }
    command = [psql_path, "-X", "-q", "-t", "-A", "-v", "ON_ERROR_STOP=1"]
    if dsn:
        command.append(dsn)
    sql = _oracle_sql() + _fixture_copy_stream(fixture) + "\n\\.\n" + _oracle_query_sql() + "\n"
    completed = subprocess.run(command, input=sql, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return {
            "status": "blocked",
            "blocked_reason": "psql command failed; PostgreSQL server or DSN is unavailable",
            "postgres_rows": None,
            "psql_path": psql_path,
            "returncode": completed.returncode,
            "stderr": completed.stderr[-4000:],
        }
    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not stdout_lines:
        return {
            "status": "blocked",
            "blocked_reason": "psql returned no JSON output",
            "postgres_rows": None,
            "psql_path": psql_path,
            "stderr": completed.stderr[-4000:],
        }
    postgres_payload = json.loads(stdout_lines[-1])
    return {
        "status": "ok",
        "postgres_rows": {
            mode: _normalize_rows(postgres_payload.get(mode, []))
            for mode in POSTGRES_MODES
        },
        "psql_path": psql_path,
    }


def _run_backend_rows(backend: str, mode: str, args: argparse.Namespace) -> dict[str, Any]:
    payload = raydb.run_result_mode(
        mode,
        backend=backend,
        copies=args.copies,
        fixture_kind=args.fixture_kind,
        generated_rows=args.generated_rows,
        generated_groups=args.generated_groups,
        generated_revenue_mod=args.generated_revenue_mod,
    )
    return {
        "backend": backend,
        "mode": mode,
        "rows": _normalize_rows(payload["rows"]),
        "metadata": payload.get("metadata", {}),
        "matches_cpu_reference": bool(payload.get("matches_cpu_reference", False)),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    fixture = raydb.make_benchmark_fixture(
        fixture_kind=args.fixture_kind,
        copies=args.copies,
        generated_rows=args.generated_rows,
        generated_groups=args.generated_groups,
        generated_revenue_mod=args.generated_revenue_mod,
    )
    postgres = _run_postgres(fixture=fixture, psql=args.psql, dsn=args.dsn)
    comparisons: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    postgres_rows = postgres.get("postgres_rows")
    if postgres["status"] == "ok":
        for backend in args.backends:
            for mode in args.modes:
                try:
                    backend_result = _run_backend_rows(backend, mode, args)
                    expected = postgres_rows[mode]
                    comparisons.append(
                        {
                            "backend": backend,
                            "mode": mode,
                            "copies": args.copies,
                            "row_count": len(fixture["row_ids"]),
                            "rows": backend_result["rows"],
                            "postgres_rows": expected,
                            "matches_postgresql": backend_result["rows"] == expected,
                            "matches_cpu_reference": backend_result["matches_cpu_reference"],
                            "native_symbol": backend_result["metadata"].get("native_symbol"),
                            "rt_core_accelerated": backend_result["metadata"].get("rt_core_accelerated"),
                            "contract": backend_result["metadata"].get("contract"),
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(
                        {
                            "backend": backend,
                            "mode": mode,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        }
                    )
    return {
        "goal": "Goal2648 RayDB PostgreSQL correctness for paper RT backends",
        "script": str(Path(__file__).resolve()),
        "environment": _environment_snapshot(),
        "arguments": {
            "copies": args.copies,
            "fixture_kind": args.fixture_kind,
            "generated_rows": args.generated_rows,
            "generated_groups": args.generated_groups,
            "generated_revenue_mod": args.generated_revenue_mod,
            "modes": list(args.modes),
            "backends": list(args.backends),
            "dsn_provided": bool(args.dsn),
        },
        "postgres": postgres,
        "comparisons": comparisons,
        "errors": errors,
        "all_compared_rows_match_postgresql": bool(comparisons) and all(
            row["matches_postgresql"] for row in comparisons
        ),
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_json": str(args.output_json),
        "output_markdown": str(args.output_markdown),
    }


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal2648 RayDB PostgreSQL Correctness for Paper RT Backends",
        "",
        f"Status: `{payload['postgres']['status']}`.",
        "",
        "## Provenance",
        "",
        f"- timestamp UTC: `{payload['environment'].get('timestamp_utc')}`",
        f"- host: `{payload['environment'].get('hostname')}`",
        f"- git commit: `{payload['environment'].get('git_commit')}`",
        f"- script: `{payload['script']}`",
        f"- output JSON: `{payload['output_json']}`",
        f"- fixture kind: `{payload['arguments']['fixture_kind']}`",
        "",
        "## Matrix",
        "",
        "| backend | mode | rows | PostgreSQL match | RT core | native symbol |",
        "|---|---|---:|---|---|---|",
    ]
    for row in payload["comparisons"]:
        lines.append(
            "| {backend} | {mode} | {row_count} | {matches_postgresql} | {rt_core_accelerated} | `{native_symbol}` |".format(
                **row
            )
        )
    if payload["postgres"]["status"] != "ok":
        lines.extend(["", f"Blocked reason: {payload['postgres'].get('blocked_reason')}"])
    if payload["errors"]:
        lines.extend(["", "## Backend Errors", ""])
        for error in payload["errors"]:
            lines.append(f"- {error['backend']} {error['mode']}: {error['error_type']}: {error['error']}")
    lines.extend(["", "## Boundary", "", f"- {payload['claim_boundary']}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", type=int, default=1000)
    parser.add_argument("--fixture-kind", choices=("repeated", "generated"), default="repeated")
    parser.add_argument("--generated-rows", type=int, default=raydb.DEFAULT_GENERATED_ROW_COUNT)
    parser.add_argument("--generated-groups", type=int, default=raydb.DEFAULT_GENERATED_GROUP_COUNT)
    parser.add_argument("--generated-revenue-mod", type=int, default=raydb.DEFAULT_GENERATED_REVENUE_MOD)
    parser.add_argument("--modes", type=_parse_csv_text, default=("count", "sum"))
    parser.add_argument("--backends", type=_parse_csv_text, default=("paper_rt_embree", "paper_rt_optix"))
    parser.add_argument("--psql", default="psql")
    parser.add_argument("--dsn", default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    if args.copies <= 0:
        parser.error("--copies must be positive")
    if args.generated_rows <= 0:
        parser.error("--generated-rows must be positive")
    if args.generated_groups <= 0:
        parser.error("--generated-groups must be positive")
    if args.generated_revenue_mod <= 0:
        parser.error("--generated-revenue-mod must be positive")
    for mode in args.modes:
        if mode not in POSTGRES_MODES:
            parser.error(f"unsupported mode: {mode}")
    for backend in args.backends:
        if backend not in raydb.BACKENDS:
            parser.error(f"unsupported backend: {backend}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, args.output_markdown)
    print(
        json.dumps(
            {
                "postgres_status": payload["postgres"]["status"],
                "all_compared_rows_match_postgresql": payload["all_compared_rows_match_postgresql"],
                "errors": payload["errors"],
                "output_json": str(args.output_json),
            },
            sort_keys=True,
        )
    )
    return 0 if payload["postgres"]["status"] in {"ok", "blocked"} and not payload["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

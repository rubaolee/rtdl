#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime
from rtdsl import vulkan_runtime
from scripts.goal50_postgis_ground_truth import (
    build_postgis_pip_select_sql,
    connect,
    explain_json,
    hash_tuples,
    load_case_geometry,
    run_postgis_pip,
    summarize_plan,
    time_call,
)
from scripts.goal69_pip_positive_hit_performance import point_in_counties_positive_hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure repeated raw-input runtime-cache impact for positive-hit county_zipcode pip."
    )
    parser.add_argument("--county-dir", default=None)
    parser.add_argument("--zipcode-dir", default=None)
    parser.add_argument("--county-cdb", default=None)
    parser.add_argument("--zipcode-cdb", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--backend", choices=("embree", "optix", "vulkan"), required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--reruns", type=int, default=3)
    return parser.parse_args()


def select_run_fn(backend: str):
    if backend == "embree":
        return rt.run_embree
    if backend == "optix":
        return rt.run_optix
    if backend == "vulkan":
        return rt.run_vulkan
    raise ValueError(f"unsupported backend: {backend}")


def select_clear_cache_fn(backend: str):
    if backend == "embree":
        return embree_runtime.clear_embree_prepared_cache
    if backend == "optix":
        return optix_runtime.clear_optix_prepared_cache
    if backend == "vulkan":
        return vulkan_runtime.clear_vulkan_prepared_cache
    raise ValueError(f"unsupported backend: {backend}")


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        f"# Goal 77 Runtime Cache Measurement: {summary['backend'].capitalize()}",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "Case: `county_zipcode`",
        f"Backend: `{summary['backend']}`",
        "",
        "- boundary: raw-input repeated-call timing in one process",
        "- timing includes runtime-owned normalization, cache lookup, bind reuse when available, and backend run",
        "- parity is checked against PostGIS positive-hit output on every run",
        "",
        "## PostGIS",
        "",
        f"- indexed plan: `{summary['postgis']['plan']['uses_index']}`",
        f"- plan nodes: `{', '.join(summary['postgis']['plan']['node_types'])}`",
        f"- row count: `{summary['postgis']['row_count']}`",
        f"- sha256: `{summary['postgis']['sha256']}`",
        "",
        "## Runs",
        "",
    ]
    for index, run in enumerate(summary["runs"], start=1):
        lines.extend(
            [
                f"### Run {index}",
                "",
                f"- backend sec: `{run['backend_sec']:.9f}`",
                f"- PostGIS sec: `{run['postgis_sec']:.9f}`",
                f"- parity vs PostGIS: `{run['parity_vs_postgis']}`",
                f"- row count: `{run['row_count']}`",
                f"- sha256: `{run['sha256']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Outcome",
            "",
            f"- first run sec: `{summary['result']['first_run_sec']:.9f}`",
            f"- best repeated run sec: `{summary['result']['best_repeated_run_sec']:.9f}`",
            f"- repeated run improved vs first: `{summary['result']['repeated_run_improved']}`",
            f"- parity preserved on all runs: `{summary['result']['parity_preserved_all_reruns']}`",
            "",
        ]
    )
    return "\n".join(lines)


def persist_summary(output_dir: Path, summary: dict[str, object]) -> None:
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "summary.md").write_text(render_markdown(summary), encoding="utf-8")


def _load_case_dataset(*, directory: str | None, cdb_path: str | None, name: str):
    if directory:
        return rt.arcgis_pages_to_cdb(directory, name=name, ignore_invalid_tail=True)
    if cdb_path:
        return rt.load_cdb(cdb_path)
    raise ValueError(f"{name} requires either a staged directory or a CDB path")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = _load_case_dataset(
        directory=args.county_dir,
        cdb_path=args.county_cdb,
        name="county_top4",
    )
    zipcode = _load_case_dataset(
        directory=args.zipcode_dir,
        cdb_path=args.zipcode_cdb,
        name="zipcode_top4",
    )
    points = rt.chains_to_probe_points(zipcode)
    polygons = rt.chains_to_polygons(county)

    run_fn = select_run_fn(args.backend)
    clear_cache_fn = select_clear_cache_fn(args.backend)
    clear_cache_fn()

    conn = connect(args.db_name, args.db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal50 CASCADE")
            cur.execute("CREATE SCHEMA goal50")
        load_case_geometry(conn, prefix="county_zipcode", points=points, polygons=polygons)
        pip_postgis_hits, _ = run_postgis_pip(conn, "county_zipcode")
        with conn.cursor() as cur:
            pip_plan = summarize_plan(explain_json(cur, build_postgis_pip_select_sql("county_zipcode")))
        postgis_hash = hash_tuples(pip_postgis_hits["positive_hits"], presorted=True)

        runs: list[dict[str, object]] = []
        for _ in range(args.reruns):
            backend_rows, backend_sec = time_call(
                run_fn,
                point_in_counties_positive_hits,
                points=points,
                polygons=polygons,
            )
            _, postgis_sec = run_postgis_pip(conn, "county_zipcode")
            hashed = hash_tuples(
                tuple((row["point_id"], row["polygon_id"], row["contains"]) for row in backend_rows),
                presorted=False,
            )
            runs.append(
                {
                    "backend_sec": backend_sec,
                    "postgis_sec": postgis_sec,
                    "parity_vs_postgis": (
                        hashed["sha256"] == postgis_hash["sha256"]
                        and hashed["row_count"] == postgis_hash["row_count"]
                    ),
                    "row_count": hashed["row_count"],
                    "sha256": hashed["sha256"],
                }
            )
    finally:
        conn.close()

    first_run_sec = runs[0]["backend_sec"]
    repeated_secs = [run["backend_sec"] for run in runs[1:]] or [first_run_sec]
    summary = {
        "date": "2026-04-04",
        "host_label": args.host_label,
        "db_name": args.db_name,
        "backend": args.backend,
        "scope": "county_zipcode; positive-hit pip; repeated raw-input calls; runtime-owned cache measurement",
        "postgis": {
            "plan": pip_plan,
            "row_count": postgis_hash["row_count"],
            "sha256": postgis_hash["sha256"],
        },
        "runs": runs,
        "result": {
            "first_run_sec": first_run_sec,
            "best_repeated_run_sec": min(repeated_secs),
            "repeated_run_improved": min(repeated_secs) < first_run_sec,
            "parity_preserved_all_reruns": all(run["parity_vs_postgis"] for run in runs),
        },
    }
    persist_summary(output_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

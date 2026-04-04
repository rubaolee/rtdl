#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rtdsl as rt
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
        description="Measure prepared-execution positive-hit county_zipcode PIP against PostGIS."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--backend", choices=("embree", "vulkan", "optix"), required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--reruns", type=int, default=2)
    return parser.parse_args()


def select_prepare_fn(backend: str):
    if backend == "embree":
        return rt.prepare_embree
    if backend == "vulkan":
        return rt.prepare_vulkan
    if backend == "optix":
        return rt.prepare_optix
    raise ValueError(f"unsupported backend: {backend}")


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        f"# Goal Prepared County Positive-Hit Report: {summary['backend'].capitalize()}",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "Case: `county_zipcode`",
        f"Backend: `{summary['backend']}`",
        "",
        "- boundary: execution-ready / prepacked",
        "- timed section includes only prepared `.run()` and the PostGIS indexed query",
        "- parity is checked against PostGIS positive-hit output",
        "",
        "## Preparation",
        "",
        f"- prepare kernel sec: `{summary['prepare_kernel_sec']:.9f}`",
        f"- pack points sec: `{summary['pack_points_sec']:.9f}`",
        f"- pack polygons sec: `{summary['pack_polygons_sec']:.9f}`",
        f"- bind sec: `{summary['bind_sec']:.9f}`",
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
    result = summary["result"]
    lines.extend(
        [
            "## Outcome",
            "",
            f"- beats PostGIS on all reruns: `{result['beats_postgis_all_reruns']}`",
            f"- parity preserved on all reruns: `{result['parity_preserved_all_reruns']}`",
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


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = rt.arcgis_pages_to_cdb(args.county_dir, name="county_top4", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(args.zipcode_dir, name="zipcode_top4", ignore_invalid_tail=True)
    points = rt.chains_to_probe_points(zipcode)
    polygons = rt.chains_to_polygons(county)

    prepare_fn = select_prepare_fn(args.backend)
    prepared_kernel, prepare_kernel_sec = time_call(prepare_fn, point_in_counties_positive_hits)
    packed_points, pack_points_sec = time_call(rt.pack_points, records=points)
    packed_polygons, pack_polygons_sec = time_call(rt.pack_polygons, records=polygons)
    bound, bind_sec = time_call(prepared_kernel.bind, points=packed_points, polygons=packed_polygons)

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
            backend_rows, backend_sec = time_call(bound.run)
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

    summary = {
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "host_label": args.host_label,
        "db_name": args.db_name,
        "backend": args.backend,
        "scope": (
            "county_zipcode; positive-hit pip; execution-ready/prepacked timing; "
            f"backend={args.backend}"
        ),
        "prepare_kernel_sec": prepare_kernel_sec,
        "pack_points_sec": pack_points_sec,
        "pack_polygons_sec": pack_polygons_sec,
        "bind_sec": bind_sec,
        "postgis": {
            "plan": pip_plan,
            "row_count": postgis_hash["row_count"],
            "sha256": postgis_hash["sha256"],
        },
        "runs": runs,
        "result": {
            "beats_postgis_all_reruns": all(run["backend_sec"] < run["postgis_sec"] for run in runs),
            "parity_preserved_all_reruns": all(run["parity_vs_postgis"] for run in runs),
        },
    }
    persist_summary(output_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

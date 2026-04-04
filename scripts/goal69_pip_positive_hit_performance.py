#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import rtdsl as rt
from scripts.goal50_postgis_ground_truth import (
    backend_payload,
    build_postgis_pip_select_sql,
    connect,
    dataset_summary,
    explain_json,
    hash_tuples,
    load_case_geometry,
    run_postgis_pip,
    summarize_plan,
    time_call,
)


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_counties_positive_hits():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(
            exact=False,
            boundary_mode="inclusive",
            result_mode="positive_hits",
        ),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare indexed PostGIS positive-hit PIP performance against RTDL positive-hit PIP mode."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--blockgroup-dir", required=True)
    parser.add_argument("--waterbodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument(
        "--cases",
        default="county_zipcode,blockgroup_waterbodies",
        help="Comma-separated subset of cases: county_zipcode,blockgroup_waterbodies",
    )
    parser.add_argument(
        "--backends",
        default="optix,embree",
        help="Comma-separated subset of RTDL backends: optix,embree,cpu",
    )
    return parser.parse_args()


def render_markdown(summary: dict[str, object]) -> str:
    def section(label: str, payload: dict[str, object]) -> list[str]:
        lines = [
            f"## {label}",
            "",
            f"- load sec: `{payload['load_sec']:.9f}`",
            f"- compared backends: `{', '.join(payload['compared_backends'])}`",
            f"- PostGIS query mode: `{payload['postgis_mode']}`",
            f"- PostGIS indexed plan: `{payload['pip']['plan']['uses_index']}`",
            f"- positive-hit parity: `"
            + ", ".join(f"{name}={payload['pip'][name]['parity_vs_postgis']}" for name in payload["compared_backends"])
            + "`",
            "",
            "### PIP Positive Hits",
            "",
            f"- PostGIS: `{payload['pip']['postgis_sec']:.9f} s`",
            f"- plan nodes: `{', '.join(payload['pip']['plan']['node_types'])}`",
            f"- hit rows: `{payload['pip']['postgis']['row_count']}`",
            "",
        ]
        for backend_name in payload["compared_backends"]:
            lines.extend(
                [
                    f"#### {backend_name.upper()}",
                    "",
                    f"- time: `{payload['pip'][backend_name]['sec']:.9f} s`",
                    f"- parity: `{payload['pip'][backend_name]['parity_vs_postgis']}`",
                    f"- hit rows: `{payload['pip'][backend_name]['row_count']}`",
                    "",
                ]
            )
        return lines

    lines = [
        "# Goal 69 PIP Positive-Hit Performance",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- compares indexed PostGIS positive-hit `pip` against RTDL's explicit positive-hit PIP mode",
        "- this goal does not replace the accepted full-matrix parity contract from Goal 50",
        "- it measures the narrower query shape that most closely matches the PostGIS execution contract",
        "",
    ]
    if "county_zipcode" in summary:
        lines.extend(section("County/Zipcode `top4_tx_ca_ny_pa`", summary["county_zipcode"]))
    if "blockgroup_waterbodies" in summary:
        lines.extend(section("BlockGroup/WaterBodies `county2300_s10`", summary["blockgroup_waterbodies"]))
    return "\n".join(lines)


def persist_summary(output_dir: Path, summary: dict[str, object]) -> None:
    (output_dir / "goal69_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal69_summary.md").write_text(render_markdown(summary), encoding="utf-8")


def run_backend_positive_hits(fn, *, postgis_digest: str, postgis_count: int, **kwargs) -> dict[str, object]:
    rows, sec = time_call(fn, point_in_counties_positive_hits, **kwargs)
    payload = backend_payload(
        rows,
        sec,
        postgis_digest,
        postgis_count,
        "pip",
        presorted=True,
        positive_only=True,
    )
    del rows
    gc.collect()
    return payload


def run_case(conn, *, prefix: str, compared_backends: tuple[str, ...], points, polygons) -> tuple[dict[str, object], dict[str, int]]:
    load_stats = load_case_geometry(conn, prefix=prefix, points=points, polygons=polygons)
    pip_postgis_hits, pip_postgis_sec = run_postgis_pip(conn, prefix)
    with conn.cursor() as cur:
        pip_plan = summarize_plan(explain_json(cur, build_postgis_pip_select_sql(prefix)))
    postgis_hash = hash_tuples(pip_postgis_hits["positive_hits"], presorted=True)

    payload = {
        "load_sec": load_stats["load_sec"],
        "compared_backends": list(compared_backends),
        "postgis_mode": "indexed GiST-assisted positive-hit join with separate load/query timing",
        "pip": {
            "postgis": postgis_hash,
            "postgis_sec": pip_postgis_sec,
            "plan": pip_plan,
        },
    }

    if "cpu" in compared_backends:
        payload["pip"]["cpu"] = run_backend_positive_hits(
            rt.run_cpu,
            postgis_digest=postgis_hash["sha256"],
            postgis_count=postgis_hash["row_count"],
            points=points,
            polygons=polygons,
        )
    if "embree" in compared_backends:
        payload["pip"]["embree"] = run_backend_positive_hits(
            rt.run_embree,
            postgis_digest=postgis_hash["sha256"],
            postgis_count=postgis_hash["row_count"],
            points=points,
            polygons=polygons,
        )
    if "optix" in compared_backends:
        payload["pip"]["optix"] = run_backend_positive_hits(
            rt.run_optix,
            postgis_digest=postgis_hash["sha256"],
            postgis_count=postgis_hash["row_count"],
            points=points,
            polygons=polygons,
        )

    return payload, {"points": len(points), "polygons": len(polygons)}


def main() -> int:
    args = parse_args()
    selected_cases = tuple(part.strip() for part in args.cases.split(",") if part.strip())
    compared_backends = tuple(part.strip() for part in args.backends.split(",") if part.strip())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = connect(args.db_name, args.db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal50 CASCADE")
            cur.execute("CREATE SCHEMA goal50")

        summary = {
            "host_label": args.host_label,
            "db_name": args.db_name,
            "compared_backends": list(compared_backends),
            "selected_cases": list(selected_cases),
        }

        if "county_zipcode" in selected_cases:
            county = rt.arcgis_pages_to_cdb(args.county_dir, name="county_top4", ignore_invalid_tail=True)
            zipcode = rt.arcgis_pages_to_cdb(args.zipcode_dir, name="zipcode_top4", ignore_invalid_tail=True)
            county_points = rt.chains_to_probe_points(zipcode)
            county_polygons = rt.chains_to_polygons(county)
            county_case, county_sizes = run_case(
                conn,
                prefix="county_zipcode",
                compared_backends=compared_backends,
                points=county_points,
                polygons=county_polygons,
            )
            summary["county_zipcode"] = {
                "county": dataset_summary(county),
                "zipcode": dataset_summary(zipcode),
                "derived_sizes": county_sizes,
                **county_case,
            }
            persist_summary(output_dir, summary)

        if "blockgroup_waterbodies" in selected_cases:
            blockgroup = rt.arcgis_pages_to_cdb(args.blockgroup_dir, name="blockgroup_county2300_s10", ignore_invalid_tail=True)
            waterbodies = rt.arcgis_pages_to_cdb(args.waterbodies_dir, name="waterbodies_county2300_s10", ignore_invalid_tail=True)
            block_points = rt.chains_to_probe_points(waterbodies)
            block_polygons = rt.chains_to_polygons(blockgroup)
            block_case, block_sizes = run_case(
                conn,
                prefix="blockgroup_waterbodies",
                compared_backends=compared_backends,
                points=block_points,
                polygons=block_polygons,
            )
            summary["blockgroup_waterbodies"] = {
                "blockgroup": dataset_summary(blockgroup),
                "waterbodies": dataset_summary(waterbodies),
                "derived_sizes": block_sizes,
                **block_case,
            }
            persist_summary(output_dir, summary)
    finally:
        conn.close()

    persist_summary(output_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

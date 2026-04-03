#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


SRID = 4326


class HashingSink:
    def __init__(self) -> None:
        self._hasher = hashlib.sha256()
        self.row_count = 0

    def write(self, data: str) -> int:
        self._hasher.update(data.encode("utf-8"))
        self.row_count += data.count("\n")
        return len(data)

    @property
    def hexdigest(self) -> str:
        return self._hasher.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load bounded RTDL real-data packages into PostGIS and compare query results/performance against RTDL backends."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--blockgroup-dir", required=True)
    parser.add_argument("--waterbodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    return parser.parse_args()


def ensure_closed_ring(vertices: tuple[tuple[float, float], ...]) -> tuple[tuple[float, float], ...]:
    if not vertices:
        return vertices
    if vertices[0] == vertices[-1]:
        return vertices
    return vertices + (vertices[0],)


def linestring_wkt(x0: float, y0: float, x1: float, y1: float) -> str:
    return f"LINESTRING({x0} {y0},{x1} {y1})"


def point_wkt(x: float, y: float) -> str:
    return f"POINT({x} {y})"


def polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = ensure_closed_ring(vertices)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def hash_tuples(rows: list[tuple[int, ...]]) -> dict[str, object]:
    rows = sorted(rows)
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(("\t".join(str(value) for value in row) + "\n").encode("utf-8"))
    return {"row_count": len(rows), "sha256": hasher.hexdigest()}


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def lsi_pairs(rows) -> list[tuple[int, int]]:
    return [(int(row["left_id"]), int(row["right_id"])) for row in rows]


def pip_triplets(rows) -> list[tuple[int, int, int]]:
    return [(int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in rows]


def dataset_summary(dataset: rt.CdbDataset) -> dict[str, int]:
    return {
        "feature_count": len(dataset.face_ids()),
        "chain_count": len(dataset.chains),
    }


def connect(db_name: str, db_user: str | None):
    import psycopg2

    kwargs = {"dbname": db_name}
    if db_user:
        kwargs["user"] = db_user
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn


def recreate_schema(cur) -> None:
    cur.execute("DROP SCHEMA IF EXISTS goal50 CASCADE")
    cur.execute("CREATE SCHEMA goal50")


def copy_geom_rows(cur, table: str, geom_type: str, rows: list[tuple[int, str]]) -> None:
    cur.execute(f"CREATE TABLE goal50.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row_id, wkt in rows:
        writer.writerow([row_id, wkt])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal50.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal50.{table} AS
        SELECT id, ST_GeomFromText(wkt, %s)::geometry({geom_type}, {SRID}) AS geom
        FROM goal50.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal50.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal50.{table}")


def load_case_geometry(
    conn,
    *,
    prefix: str,
    left_segments: tuple[dict[str, float | int], ...] | None = None,
    right_segments: tuple[dict[str, float | int], ...] | None = None,
    points: tuple[dict[str, float | int], ...] | None = None,
    polygons: tuple[dict[str, object], ...] | None = None,
) -> dict[str, float]:
    timings: dict[str, float] = {}
    with conn.cursor() as cur:
        start = time.perf_counter()
        if left_segments is not None:
            copy_geom_rows(
                cur,
                f"{prefix}_left_segments",
                "LINESTRING",
                [(int(row["id"]), linestring_wkt(row["x0"], row["y0"], row["x1"], row["y1"])) for row in left_segments],
            )
        if right_segments is not None:
            copy_geom_rows(
                cur,
                f"{prefix}_right_segments",
                "LINESTRING",
                [(int(row["id"]), linestring_wkt(row["x0"], row["y0"], row["x1"], row["y1"])) for row in right_segments],
            )
        if points is not None:
            copy_geom_rows(
                cur,
                f"{prefix}_points",
                "POINT",
                [(int(row["id"]), point_wkt(row["x"], row["y"])) for row in points],
            )
        if polygons is not None:
            copy_geom_rows(
                cur,
                f"{prefix}_polygons",
                "POLYGON",
                [(int(row["id"]), polygon_wkt(tuple(row["vertices"]))) for row in polygons],
            )
        end = time.perf_counter()
        timings["load_sec"] = end - start
    return timings


def copy_query_hash(cur, sql: str) -> tuple[str, int]:
    sink = HashingSink()
    cur.copy_expert(sql, sink)
    return sink.hexdigest, sink.row_count


def run_postgis_lsi(conn, prefix: str) -> tuple[dict[str, object], float]:
    sql = f"""
COPY (
    SELECT l.id, r.id
    FROM goal50.{prefix}_left_segments AS l
    JOIN goal50.{prefix}_right_segments AS r
      ON l.geom && r.geom
     AND ST_Intersects(l.geom, r.geom)
    ORDER BY 1, 2
) TO STDOUT WITH (FORMAT csv, DELIMITER E'\\t')
"""
    with conn.cursor() as cur:
        start = time.perf_counter()
        digest, row_count = copy_query_hash(cur, sql)
        end = time.perf_counter()
    return {"row_count": row_count, "sha256": digest}, end - start


def run_postgis_pip(conn, prefix: str) -> tuple[dict[str, object], float]:
    sql = f"""
COPY (
    SELECT p.id, g.id, 1
    FROM goal50.{prefix}_points AS p
    JOIN goal50.{prefix}_polygons AS g
      ON g.geom && p.geom
     AND ST_Covers(g.geom, p.geom)
    ORDER BY 1, 2, 3
) TO STDOUT WITH (FORMAT csv, DELIMITER E'\\t')
"""
    with conn.cursor() as cur:
        start = time.perf_counter()
        digest, row_count = copy_query_hash(cur, sql)
        end = time.perf_counter()
    return {"row_count": row_count, "sha256": digest}, end - start


def render_markdown(summary: dict[str, object]) -> str:
    def section(label: str, payload: dict[str, object]) -> list[str]:
        lines = [
            f"## {label}",
            "",
            f"- load sec: `{payload['load_sec']:.9f}`",
            f"- lsi parity vs postgis: `{payload['lsi']['cpu']['parity_vs_postgis']}` / `{payload['lsi']['embree']['parity_vs_postgis']}` / `{payload['lsi']['optix']['parity_vs_postgis']}`",
            f"- pip parity vs postgis: `{payload['pip']['cpu']['parity_vs_postgis']}` / `{payload['pip']['embree']['parity_vs_postgis']}` / `{payload['pip']['optix']['parity_vs_postgis']}`",
            "",
            "### LSI",
            "",
            f"- PostGIS: `{payload['lsi']['postgis_sec']:.9f} s`",
            f"- C oracle: `{payload['lsi']['cpu']['sec']:.9f} s`",
            f"- Embree: `{payload['lsi']['embree']['sec']:.9f} s`",
            f"- OptiX: `{payload['lsi']['optix']['sec']:.9f} s`",
            f"- row count: `{payload['lsi']['postgis']['row_count']}`",
            "",
            "### PIP",
            "",
            f"- PostGIS: `{payload['pip']['postgis_sec']:.9f} s`",
            f"- C oracle: `{payload['pip']['cpu']['sec']:.9f} s`",
            f"- Embree: `{payload['pip']['embree']['sec']:.9f} s`",
            f"- OptiX: `{payload['pip']['optix']['sec']:.9f} s`",
            f"- row count: `{payload['pip']['postgis']['row_count']}`",
            "",
        ]
        return lines

    lines = [
        "# Goal 50 PostGIS Ground-Truth Comparison",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- compares PostGIS against RTDL C oracle, Embree, and OptiX on the same bounded real-data packages already accepted in the Linux validation track",
        "- PostGIS is measured as a loaded-and-indexed query engine; load time is reported separately from query time",
        "- `lsi` uses segment tables and `ST_Intersects`; `pip` uses probe points, polygon rings, and boundary-inclusive `ST_Covers`",
        "",
    ]
    lines.extend(section("County/Zipcode `top4_tx_ca_ny_pa`", summary["county_zipcode"]))
    lines.extend(section("BlockGroup/WaterBodies `county2300_s10`", summary["blockgroup_waterbodies"]))
    return "\n".join(lines)


def backend_payload(rows, sec: float, postgis_digest: str, postgis_count: int, kind: str) -> dict[str, object]:
    tuples = lsi_pairs(rows) if kind == "lsi" else pip_triplets(rows)
    hashed = hash_tuples(tuples)
    return {
        "sec": sec,
        "row_count": hashed["row_count"],
        "sha256": hashed["sha256"],
        "parity_vs_postgis": hashed["sha256"] == postgis_digest and hashed["row_count"] == postgis_count,
    }


def run_case(
    conn,
    *,
    prefix: str,
    left_segments,
    right_segments,
    points,
    polygons,
) -> tuple[dict[str, object], dict[str, object]]:
    load_stats = load_case_geometry(
        conn,
        prefix=prefix,
        left_segments=left_segments,
        right_segments=right_segments,
        points=points,
        polygons=polygons,
    )

    lsi_postgis, lsi_postgis_sec = run_postgis_lsi(conn, prefix)
    pip_postgis, pip_postgis_sec = run_postgis_pip(conn, prefix)

    cpu_lsi_rows, cpu_lsi_sec = time_call(rt.run_cpu, county_zip_join_reference, left=left_segments, right=right_segments)
    embree_lsi_rows, embree_lsi_sec = time_call(rt.run_embree, county_zip_join_reference, left=left_segments, right=right_segments)
    optix_lsi_rows, optix_lsi_sec = time_call(rt.run_optix, county_zip_join_reference, left=left_segments, right=right_segments)

    cpu_pip_rows, cpu_pip_sec = time_call(rt.run_cpu, point_in_counties_reference, points=points, polygons=polygons)
    embree_pip_rows, embree_pip_sec = time_call(rt.run_embree, point_in_counties_reference, points=points, polygons=polygons)
    optix_pip_rows, optix_pip_sec = time_call(rt.run_optix, point_in_counties_reference, points=points, polygons=polygons)

    summary = {
        "load_sec": load_stats["load_sec"],
        "lsi": {
            "postgis": lsi_postgis,
            "postgis_sec": lsi_postgis_sec,
            "cpu": backend_payload(cpu_lsi_rows, cpu_lsi_sec, lsi_postgis["sha256"], lsi_postgis["row_count"], "lsi"),
            "embree": backend_payload(embree_lsi_rows, embree_lsi_sec, lsi_postgis["sha256"], lsi_postgis["row_count"], "lsi"),
            "optix": backend_payload(optix_lsi_rows, optix_lsi_sec, lsi_postgis["sha256"], lsi_postgis["row_count"], "lsi"),
        },
        "pip": {
            "postgis": pip_postgis,
            "postgis_sec": pip_postgis_sec,
            "cpu": backend_payload(cpu_pip_rows, cpu_pip_sec, pip_postgis["sha256"], pip_postgis["row_count"], "pip"),
            "embree": backend_payload(embree_pip_rows, embree_pip_sec, pip_postgis["sha256"], pip_postgis["row_count"], "pip"),
            "optix": backend_payload(optix_pip_rows, optix_pip_sec, pip_postgis["sha256"], pip_postgis["row_count"], "pip"),
        },
    }
    return summary, {
        "left_segments": len(left_segments),
        "right_segments": len(right_segments),
        "points": len(points),
        "polygons": len(polygons),
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = rt.arcgis_pages_to_cdb(args.county_dir, name="county_top4", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(args.zipcode_dir, name="zipcode_top4", ignore_invalid_tail=True)
    blockgroup = rt.arcgis_pages_to_cdb(args.blockgroup_dir, name="blockgroup_county2300_s10", ignore_invalid_tail=True)
    waterbodies = rt.arcgis_pages_to_cdb(args.waterbodies_dir, name="waterbodies_county2300_s10", ignore_invalid_tail=True)

    county_summary = dataset_summary(county)
    zipcode_summary = dataset_summary(zipcode)
    block_summary = dataset_summary(blockgroup)
    water_summary = dataset_summary(waterbodies)

    county_left = rt.chains_to_segments(zipcode)
    county_right = rt.chains_to_segments(county)
    county_points = rt.chains_to_probe_points(zipcode)
    county_polygons = rt.chains_to_polygons(county)

    block_left = rt.chains_to_segments(waterbodies)
    block_right = rt.chains_to_segments(blockgroup)
    block_points = rt.chains_to_probe_points(waterbodies)
    block_polygons = rt.chains_to_polygons(blockgroup)

    conn = connect(args.db_name, args.db_user)
    try:
        with conn.cursor() as cur:
            recreate_schema(cur)

        county_case, county_sizes = run_case(
            conn,
            prefix="county_zipcode",
            left_segments=county_left,
            right_segments=county_right,
            points=county_points,
            polygons=county_polygons,
        )
        block_case, block_sizes = run_case(
            conn,
            prefix="blockgroup_waterbodies",
            left_segments=block_left,
            right_segments=block_right,
            points=block_points,
            polygons=block_polygons,
        )
    finally:
        conn.close()

    summary = {
        "host_label": args.host_label,
        "db_name": args.db_name,
        "county_zipcode": {
            "county": county_summary,
            "zipcode": zipcode_summary,
            "derived_sizes": county_sizes,
            **county_case,
        },
        "blockgroup_waterbodies": {
            "blockgroup": block_summary,
            "waterbodies": water_summary,
            "derived_sizes": block_sizes,
            **block_case,
        },
    }

    (output_dir / "goal50_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal50_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

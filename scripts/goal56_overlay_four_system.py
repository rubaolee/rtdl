#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import io
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_soil_overlay_reference


SRID = 4326


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal 56 four-system LKAU/PKAU overlay-seed comparison.")
    parser.add_argument("--lakes-json", required=True)
    parser.add_argument("--parks-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bbox", required=True)
    parser.add_argument("--bbox-label", default="custom")
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--backends", default="cpu,embree,optix")
    return parser.parse_args()


def ensure_closed_ring(vertices: tuple[tuple[float, float], ...]) -> tuple[tuple[float, float], ...]:
    if not vertices:
        return vertices
    if vertices[0] == vertices[-1]:
        return vertices
    return vertices + (vertices[0],)


def polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = ensure_closed_ring(vertices)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def overlay_quadruples(rows) -> list[tuple[int, int, int, int]]:
    return [
        (
            int(row["left_polygon_id"]),
            int(row["right_polygon_id"]),
            int(row["requires_lsi"]),
            int(row["requires_pip"]),
        )
        for row in rows
    ]


def hash_tuples(rows: list[tuple[int, ...]], *, presorted: bool = False) -> dict[str, object]:
    if not presorted:
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


def connect(db_name: str, db_user: str | None):
    import psycopg2

    kwargs = {"dbname": db_name}
    if db_user:
        kwargs["user"] = db_user
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn


def recreate_schema(cur) -> None:
    cur.execute("DROP SCHEMA IF EXISTS goal56 CASCADE")
    cur.execute("CREATE SCHEMA goal56")


def copy_polygon_rows(cur, table: str, rows: tuple[dict[str, object], ...]) -> None:
    cur.execute(f"CREATE TABLE goal56.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), polygon_wkt(tuple(row["vertices"]))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal56.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal56.{table} AS
        SELECT id, ST_GeomFromText(wkt, %s)::geometry(POLYGON, {SRID}) AS geom
        FROM goal56.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal56.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal56.{table}")


def copy_segment_rows(cur, table: str, polygons: tuple[dict[str, object], ...]) -> None:
    cur.execute(f"CREATE TABLE goal56.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for polygon in polygons:
        polygon_id = int(polygon["id"])
        ring = ensure_closed_ring(tuple(polygon["vertices"]))
        for start, end in zip(ring, ring[1:]):
            writer.writerow([polygon_id, start[0], start[1], end[0], end[1]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal56.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal56.{table} AS
        SELECT
            id,
            x0,
            y0,
            x1,
            y1,
            ST_GeomFromText(
                'LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')',
                %s
            )::geometry(LINESTRING, {SRID}) AS geom
        FROM goal56.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal56.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal56.{table}")


def copy_first_vertex_points(cur, table: str, polygons: tuple[dict[str, object], ...]) -> None:
    cur.execute(f"CREATE TABLE goal56.{table}_raw (id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for polygon in polygons:
        vertex = tuple(polygon["vertices"])[0]
        writer.writerow([int(polygon["id"]), vertex[0], vertex[1]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal56.{table}_raw (id, x, y) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal56.{table} AS
        SELECT
            id,
            x,
            y,
            ST_GeomFromText('POINT(' || x || ' ' || y || ')', %s)::geometry(POINT, {SRID}) AS geom
        FROM goal56.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal56.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal56.{table}")


def load_case_geometry(conn, *, left_polygons, right_polygons) -> float:
    with conn.cursor() as cur:
        recreate_schema(cur)
        start = time.perf_counter()
        copy_polygon_rows(cur, "left_polygons", left_polygons)
        copy_polygon_rows(cur, "right_polygons", right_polygons)
        copy_segment_rows(cur, "left_segments", left_polygons)
        copy_segment_rows(cur, "right_segments", right_polygons)
        copy_first_vertex_points(cur, "left_points", left_polygons)
        copy_first_vertex_points(cur, "right_points", right_polygons)
        end = time.perf_counter()
    return end - start


def fetch_query_tuples(cur, sql: str) -> tuple[tuple[int, ...], ...]:
    cur.execute(sql)
    return tuple(tuple(int(value) for value in row) for row in cur.fetchall())


def build_overlay_lsi_positive_sql(*, ordered: bool = True) -> str:
    sql = f"""
SELECT DISTINCT l.id AS left_id, r.id AS right_id
FROM goal56.left_segments AS l
JOIN goal56.right_segments AS r
  ON l.geom && r.geom
 AND ABS(((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) >= 1.0e-7
 AND (((r.x0 - l.x0) * (r.y1 - r.y0)) - ((r.y0 - l.y0) * (r.x1 - r.x0)))
       / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
 AND (((r.x0 - l.x0) * (l.y1 - l.y0)) - ((r.y0 - l.y0) * (l.x1 - l.x0)))
       / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
"""
    if ordered:
        sql += "\nORDER BY 1, 2\n"
    return sql


def build_overlay_pip_positive_sql(*, ordered: bool = True) -> str:
    sql = f"""
SELECT left_id, right_id
FROM (
    SELECT p.id AS left_id, g.id AS right_id
    FROM goal56.left_points AS p
    JOIN goal56.right_polygons AS g
      ON g.geom && p.geom
     AND ST_Covers(g.geom, p.geom)
    UNION
    SELECT g.id AS left_id, p.id AS right_id
    FROM goal56.right_points AS p
    JOIN goal56.left_polygons AS g
      ON g.geom && p.geom
     AND ST_Covers(g.geom, p.geom)
) AS seed_hits
"""
    if ordered:
        sql += "\nORDER BY 1, 2\n"
    return sql


def build_overlay_seed_select_sql() -> str:
    return f"""
WITH lsi_hits AS (
{build_overlay_lsi_positive_sql(ordered=False).strip()}
),
pip_hits AS (
{build_overlay_pip_positive_sql(ordered=False).strip()}
)
SELECT
    l.id,
    r.id,
    CASE WHEN lsi_hits.left_id IS NULL THEN 0 ELSE 1 END AS requires_lsi,
    CASE WHEN pip_hits.left_id IS NULL THEN 0 ELSE 1 END AS requires_pip
FROM goal56.left_polygons AS l
CROSS JOIN goal56.right_polygons AS r
LEFT JOIN lsi_hits
  ON l.id = lsi_hits.left_id
 AND r.id = lsi_hits.right_id
LEFT JOIN pip_hits
  ON l.id = pip_hits.left_id
 AND r.id = pip_hits.right_id
ORDER BY 1, 2, 3, 4
"""


def explain_json(cur, select_sql: str) -> dict[str, object]:
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {select_sql}")
    payload = cur.fetchone()[0]
    if isinstance(payload, list):
        return payload[0]
    return payload


def summarize_plan(plan_json: dict[str, object]) -> dict[str, object]:
    plan_root = plan_json["Plan"]
    node_types: set[str] = set()
    index_names: set[str] = set()

    def walk(node: dict[str, object]) -> None:
        node_types.add(str(node.get("Node Type", "")))
        if "Index Name" in node:
            index_names.add(str(node["Index Name"]))
        for child in node.get("Plans", []) or []:
            walk(child)

    walk(plan_root)
    node_types_list = sorted(node for node in node_types if node)
    index_names_list = sorted(index_names)
    uses_index = any("Index" in node for node in node_types_list) or bool(index_names_list)
    return {
        "execution_time_ms": plan_json.get("Execution Time"),
        "planning_time_ms": plan_json.get("Planning Time"),
        "node_types": node_types_list,
        "index_names": index_names_list,
        "uses_index": uses_index,
    }


def run_postgis_overlay(conn) -> tuple[dict[str, object], float]:
    sql = build_overlay_seed_select_sql()
    with conn.cursor() as cur:
        start = time.perf_counter()
        rows = fetch_query_tuples(cur, sql)
        end = time.perf_counter()
    return hash_tuples(list(rows), presorted=True), end - start


def backend_payload(rows, sec: float, postgis_digest: str, postgis_count: int) -> dict[str, object]:
    hashed = hash_tuples(overlay_quadruples(rows), presorted=False)
    return {
        "sec": sec,
        "row_count": hashed["row_count"],
        "sha256": hashed["sha256"],
        "parity_vs_postgis": hashed["sha256"] == postgis_digest and hashed["row_count"] == postgis_count,
    }


def run_backend(fn, *, postgis_digest: str, postgis_count: int, **kwargs) -> dict[str, object]:
    rows, sec = time_call(fn, county_soil_overlay_reference, **kwargs)
    payload = backend_payload(rows, sec, postgis_digest, postgis_count)
    del rows
    gc.collect()
    return payload


def render_markdown(summary: dict[str, object]) -> str:
    overlay = summary["overlay"]
    lines = [
        "# Goal 56 LKAU PKAU Overlay Four-System Closure",
        "",
        f"Host label: `{summary['host_label']}`",
        f"BBox label: `{summary['bbox_label']}`",
        f"BBox: `{summary['bbox']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- bounded derived-input Australia slice from live OSM Overpass data",
        "- overlay is evaluated here as an `overlay-seed analogue`, not full polygon materialization",
        "- PostGIS truth is derived from indexed segment-intersection and first-vertex coverage predicates",
        "- not continent-scale `LKAU ⊲⊳ PKAU`",
        "",
        "## Inputs",
        "",
        f"- lakes source elements: `{summary['lakes']['element_count']}`",
        f"- lakes closed ways: `{summary['lakes']['closed_way_count']}`",
        f"- lakes features: `{summary['lakes']['feature_count']}`",
        f"- parks source elements: `{summary['parks']['element_count']}`",
        f"- parks closed ways: `{summary['parks']['closed_way_count']}`",
        f"- parks features: `{summary['parks']['feature_count']}`",
        f"- load sec: `{summary['load_sec']:.9f}`",
        "",
        "## PostGIS",
        "",
        f"- LSI seed plan uses index: `{overlay['lsi_plan']['uses_index']}`",
        f"- PIP seed plan uses index: `{overlay['pip_plan']['uses_index']}`",
        f"- full overlay-seed query uses index: `{overlay['overlay_plan']['uses_index']}`",
        "",
        "## Overlay Seed Rows",
        "",
        f"- PostGIS: `{overlay['postgis_sec']:.9f} s` rows `{overlay['postgis']['row_count']}`",
    ]
    for backend in summary["compared_backends"]:
        lines.append(
            f"- {backend}: `{overlay[backend]['sec']:.9f} s` parity `{overlay[backend]['parity_vs_postgis']}`"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    compared_backends = tuple(part.strip() for part in args.backends.split(",") if part.strip())

    lakes_elements = rt.load_overpass_elements(args.lakes_json)
    parks_elements = rt.load_overpass_elements(args.parks_json)
    lakes_stats = rt.overpass_elements_stats(lakes_elements)
    parks_stats = rt.overpass_elements_stats(parks_elements)
    lakes = rt.overpass_elements_to_cdb(lakes_elements, name="lkau_slice")
    parks = rt.overpass_elements_to_cdb(parks_elements, name="pkau_slice")

    left_polygons = tuple(rt.chains_to_polygons(lakes))
    right_polygons = tuple(rt.chains_to_polygons(parks))

    conn = connect(args.db_name, args.db_user)
    try:
        load_sec = load_case_geometry(conn, left_polygons=left_polygons, right_polygons=right_polygons)
        postgis_overlay, postgis_sec = run_postgis_overlay(conn)
        with conn.cursor() as cur:
            lsi_plan = summarize_plan(explain_json(cur, build_overlay_lsi_positive_sql()))
            pip_plan = summarize_plan(explain_json(cur, build_overlay_pip_positive_sql()))
            overlay_plan = summarize_plan(explain_json(cur, build_overlay_seed_select_sql()))
    finally:
        conn.close()

    summary = {
        "host_label": args.host_label,
        "bbox_label": args.bbox_label,
        "bbox": args.bbox,
        "db_name": args.db_name,
        "compared_backends": list(compared_backends),
        "load_sec": load_sec,
        "lakes": {
            "element_count": lakes_stats.element_count,
            "closed_way_count": lakes_stats.closed_way_count,
            "feature_count": len(lakes.face_ids()),
        },
        "parks": {
            "element_count": parks_stats.element_count,
            "closed_way_count": parks_stats.closed_way_count,
            "feature_count": len(parks.face_ids()),
        },
        "overlay": {
            "postgis": postgis_overlay,
            "postgis_sec": postgis_sec,
            "lsi_plan": lsi_plan,
            "pip_plan": pip_plan,
            "overlay_plan": overlay_plan,
        },
    }

    backend_map = {
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
    }
    for backend in compared_backends:
        summary["overlay"][backend] = run_backend(
            backend_map[backend],
            postgis_digest=postgis_overlay["sha256"],
            postgis_count=postgis_overlay["row_count"],
            left=left_polygons,
            right=right_polygons,
        )

    (output_dir / "goal56_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "goal56_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference


SRID = 4326


class HashingSink:
    def __init__(self) -> None:
        self._hasher = hashlib.sha256()
        self.row_count = 0

    def write(self, data: str | bytes) -> int:
        if isinstance(data, bytes):
            payload = data
            newline_count = data.count(b"\n")
        else:
            payload = data.encode("utf-8")
            newline_count = data.count("\n")
        self._hasher.update(payload)
        self.row_count += newline_count
        return len(data)

    @property
    def hexdigest(self) -> str:
        return self._hasher.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal 54 four-system LKAU/PKAU comparison.")
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


def hash_tuples(rows: list[tuple[int, ...]], *, presorted: bool = False) -> dict[str, object]:
    if not presorted:
        rows = sorted(rows)
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(("\t".join(str(value) for value in row) + "\n").encode("utf-8"))
    return {"row_count": len(rows), "sha256": hasher.hexdigest()}


def hash_full_pip_truth(
    point_ids: tuple[int, ...],
    polygon_ids: tuple[int, ...],
    positive_hits: tuple[tuple[int, int], ...],
) -> dict[str, object]:
    hasher = hashlib.sha256()
    positive_set = set(positive_hits)
    row_count = 0
    for point_id in point_ids:
        for polygon_id in polygon_ids:
            contains = 1 if (point_id, polygon_id) in positive_set else 0
            hasher.update(f"{point_id}\t{polygon_id}\t{contains}\n".encode("utf-8"))
            row_count += 1
    return {"row_count": row_count, "sha256": hasher.hexdigest(), "positive_row_count": len(positive_hits)}


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def lsi_pairs(rows) -> list[tuple[int, int]]:
    return [(int(row["left_id"]), int(row["right_id"])) for row in rows]


def pip_triplets(rows) -> list[tuple[int, int, int]]:
    return [(int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in rows]


def connect(db_name: str, db_user: str | None):
    import psycopg2

    kwargs = {"dbname": db_name}
    if db_user:
        kwargs["user"] = db_user
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn


def recreate_schema(cur) -> None:
    cur.execute("DROP SCHEMA IF EXISTS goal54 CASCADE")
    cur.execute("CREATE SCHEMA goal54")


def copy_segment_rows(cur, table: str, rows: tuple[dict[str, float | int], ...]) -> None:
    cur.execute(f"CREATE TABLE goal54.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), row["x0"], row["y0"], row["x1"], row["y1"]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal54.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal54.{table} AS
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
        FROM goal54.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal54.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal54.{table}")


def copy_point_rows(cur, table: str, rows: tuple[dict[str, float | int], ...]) -> None:
    cur.execute(f"CREATE TABLE goal54.{table}_raw (id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), row["x"], row["y"]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal54.{table}_raw (id, x, y) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal54.{table} AS
        SELECT
            id,
            x,
            y,
            ST_GeomFromText('POINT(' || x || ' ' || y || ')', %s)::geometry(POINT, {SRID}) AS geom
        FROM goal54.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal54.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal54.{table}")


def copy_polygon_rows(cur, table: str, rows: tuple[dict[str, object], ...]) -> None:
    cur.execute(f"CREATE TABLE goal54.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), polygon_wkt(tuple(row["vertices"]))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal54.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal54.{table} AS
        SELECT id, ST_GeomFromText(wkt, %s)::geometry(POLYGON, {SRID}) AS geom
        FROM goal54.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal54.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal54.{table}")


def load_case_geometry(conn, *, left_segments, right_segments, points, polygons) -> float:
    with conn.cursor() as cur:
        recreate_schema(cur)
        start = time.perf_counter()
        copy_segment_rows(cur, "left_segments", left_segments)
        copy_segment_rows(cur, "right_segments", right_segments)
        copy_point_rows(cur, "points", points)
        copy_polygon_rows(cur, "polygons", polygons)
        end = time.perf_counter()
    return end - start


def fetch_query_tuples(cur, sql: str) -> tuple[tuple[int, ...], ...]:
    cur.execute(sql)
    return tuple(tuple(int(value) for value in row) for row in cur.fetchall())


def build_postgis_lsi_select_sql() -> str:
    return f"""
SELECT l.id, r.id
FROM goal54.left_segments AS l
JOIN goal54.right_segments AS r
  ON l.geom && r.geom
 AND ABS(((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) >= 1.0e-7
 AND (((r.x0 - l.x0) * (r.y1 - r.y0)) - ((r.y0 - l.y0) * (r.x1 - r.x0)))
       / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
 AND (((r.x0 - l.x0) * (l.y1 - l.y0)) - ((r.y0 - l.y0) * (l.x1 - l.x0)))
       / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
ORDER BY 1, 2
"""


def build_postgis_pip_select_sql() -> str:
    return f"""
SELECT p.id, g.id, 1
FROM goal54.points AS p
JOIN goal54.polygons AS g
  ON g.geom && p.geom
 AND ST_Covers(g.geom, p.geom)
ORDER BY 1, 2, 3
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


def run_postgis_lsi(conn) -> tuple[dict[str, object], float]:
    sql = build_postgis_lsi_select_sql()
    with conn.cursor() as cur:
        start = time.perf_counter()
        rows = fetch_query_tuples(cur, sql)
        end = time.perf_counter()
    return hash_tuples(list(rows), presorted=True), end - start


def run_postgis_pip(conn, point_ids: tuple[int, ...], polygon_ids: tuple[int, ...]) -> tuple[dict[str, object], float]:
    sql = build_postgis_pip_select_sql()
    with conn.cursor() as cur:
        start = time.perf_counter()
        rows = fetch_query_tuples(cur, sql)
        end = time.perf_counter()
    positives = tuple((point_id, polygon_id) for point_id, polygon_id, _ in rows)
    return hash_full_pip_truth(point_ids, polygon_ids, positives), end - start


def backend_payload(rows, sec: float, postgis_digest: str, postgis_count: int, *, kind: str) -> dict[str, object]:
    tuples = lsi_pairs(rows) if kind == "lsi" else pip_triplets(rows)
    hashed = hash_tuples(tuples, presorted=False)
    return {
        "sec": sec,
        "row_count": hashed["row_count"],
        "sha256": hashed["sha256"],
        "parity_vs_postgis": hashed["sha256"] == postgis_digest and hashed["row_count"] == postgis_count,
    }


def run_backend(fn, kernel, *, kind: str, postgis_digest: str, postgis_count: int, **kwargs) -> dict[str, object]:
    rows, sec = time_call(fn, kernel, **kwargs)
    payload = backend_payload(rows, sec, postgis_digest, postgis_count, kind=kind)
    del rows
    gc.collect()
    return payload


def render_markdown(summary: dict[str, object]) -> str:
    lsi = summary["lsi"]
    pip = summary["pip"]
    lines = [
        "# Goal 54 LKAU PKAU Four-System Comparison",
        "",
        f"Host label: `{summary['host_label']}`",
        f"BBox label: `{summary['bbox_label']}`",
        f"BBox: `{summary['bbox']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- bounded derived-input Australia slice from live OSM Overpass data",
        "- not continent-scale `LKAU ⊲⊳ PKAU`",
        "- not multipolygon relation reconstruction",
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
        f"- LSI indexed plan: `{lsi['plan']['uses_index']}`",
        f"- PIP indexed plan: `{pip['plan']['uses_index']}`",
        "",
        "## LSI",
        "",
        f"- PostGIS: `{lsi['postgis_sec']:.9f} s` rows `{lsi['postgis']['row_count']}`",
    ]
    for backend in summary["compared_backends"]:
        lines.append(
            f"- {backend}: `{lsi[backend]['sec']:.9f} s` parity `{lsi[backend]['parity_vs_postgis']}`"
        )
    lines.extend(
        [
            "",
            "## PIP",
            "",
            f"- PostGIS: `{pip['postgis_sec']:.9f} s` rows `{pip['postgis']['row_count']}` positive hits `{pip['postgis']['positive_row_count']}`",
        ]
    )
    for backend in summary["compared_backends"]:
        lines.append(
            f"- {backend}: `{pip[backend]['sec']:.9f} s` parity `{pip[backend]['parity_vs_postgis']}`"
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

    lake_segments = rt.chains_to_segments(lakes)
    park_segments = rt.chains_to_segments(parks)
    lake_points = rt.chains_to_probe_points(lakes)
    park_polygons = rt.chains_to_polygons(parks)
    point_ids = tuple(int(row["id"]) for row in lake_points)
    polygon_ids = tuple(int(row["id"]) for row in park_polygons)

    conn = connect(args.db_name, args.db_user)
    try:
        load_sec = load_case_geometry(
            conn,
            left_segments=tuple(lake_segments),
            right_segments=tuple(park_segments),
            points=tuple(lake_points),
            polygons=tuple(park_polygons),
        )
        lsi_postgis, lsi_postgis_sec = run_postgis_lsi(conn)
        pip_postgis, pip_postgis_sec = run_postgis_pip(conn, point_ids, polygon_ids)
        with conn.cursor() as cur:
            lsi_plan = summarize_plan(explain_json(cur, build_postgis_lsi_select_sql()))
            pip_plan = summarize_plan(explain_json(cur, build_postgis_pip_select_sql()))
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
        "lsi": {
            "postgis": lsi_postgis,
            "postgis_sec": lsi_postgis_sec,
            "plan": lsi_plan,
        },
        "pip": {
            "postgis": pip_postgis,
            "postgis_sec": pip_postgis_sec,
            "plan": pip_plan,
        },
    }

    if "cpu" in compared_backends:
        summary["lsi"]["cpu"] = run_backend(
            rt.run_cpu,
            county_zip_join_reference,
            kind="lsi",
            postgis_digest=lsi_postgis["sha256"],
            postgis_count=lsi_postgis["row_count"],
            left=lake_segments,
            right=park_segments,
        )
        summary["pip"]["cpu"] = run_backend(
            rt.run_cpu,
            point_in_counties_reference,
            kind="pip",
            postgis_digest=pip_postgis["sha256"],
            postgis_count=pip_postgis["row_count"],
            points=lake_points,
            polygons=park_polygons,
        )
    if "embree" in compared_backends:
        summary["lsi"]["embree"] = run_backend(
            rt.run_embree,
            county_zip_join_reference,
            kind="lsi",
            postgis_digest=lsi_postgis["sha256"],
            postgis_count=lsi_postgis["row_count"],
            left=lake_segments,
            right=park_segments,
        )
        summary["pip"]["embree"] = run_backend(
            rt.run_embree,
            point_in_counties_reference,
            kind="pip",
            postgis_digest=pip_postgis["sha256"],
            postgis_count=pip_postgis["row_count"],
            points=lake_points,
            polygons=park_polygons,
        )
    if "optix" in compared_backends:
        summary["lsi"]["optix"] = run_backend(
            rt.run_optix,
            county_zip_join_reference,
            kind="lsi",
            postgis_digest=lsi_postgis["sha256"],
            postgis_count=lsi_postgis["row_count"],
            left=lake_segments,
            right=park_segments,
        )
        summary["pip"]["optix"] = run_backend(
            rt.run_optix,
            point_in_counties_reference,
            kind="pip",
            postgis_digest=pip_postgis["sha256"],
            postgis_count=pip_postgis["row_count"],
            points=lake_points,
            polygons=park_polygons,
        )

    (output_dir / "goal54_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal54_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

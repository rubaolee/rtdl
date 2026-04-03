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
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


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
    parser.add_argument(
        "--cases",
        default="county_zipcode,blockgroup_waterbodies",
        help="Comma-separated subset of cases: county_zipcode,blockgroup_waterbodies",
    )
    parser.add_argument(
        "--backends",
        default="cpu,embree,optix",
        help="Comma-separated subset of RTDL backends to compare against PostGIS: cpu,embree,optix",
    )
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


def lsi_pairs(rows) -> list[tuple[int, int]]:
    return [(int(row["left_id"]), int(row["right_id"])) for row in rows]


def pip_triplets(rows) -> list[tuple[int, int, int]]:
    return [(int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in rows]


def pip_positive_triplets(rows) -> list[tuple[int, int, int]]:
    return [(int(row["point_id"]), int(row["polygon_id"]), 1) for row in rows if int(row["contains"]) == 1]


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


def copy_segment_rows(cur, table: str, rows: tuple[dict[str, float | int], ...]) -> None:
    cur.execute(f"CREATE TABLE goal50.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), row["x0"], row["y0"], row["x1"], row["y1"]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal50.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal50.{table} AS
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
        FROM goal50.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal50.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal50.{table}")


def copy_point_rows(cur, table: str, rows: tuple[dict[str, float | int], ...]) -> None:
    cur.execute(f"CREATE TABLE goal50.{table}_raw (id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), row["x"], row["y"]])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal50.{table}_raw (id, x, y) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal50.{table} AS
        SELECT
            id,
            x,
            y,
            ST_GeomFromText('POINT(' || x || ' ' || y || ')', %s)::geometry(POINT, {SRID}) AS geom
        FROM goal50.{table}_raw
        """,
        (SRID,),
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal50.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal50.{table}")


def copy_polygon_rows(cur, table: str, rows: tuple[dict[str, object], ...]) -> None:
    cur.execute(f"CREATE TABLE goal50.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row["id"]), polygon_wkt(tuple(row["vertices"]))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal50.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal50.{table} AS
        SELECT id, ST_GeomFromText(wkt, %s)::geometry(POLYGON, {SRID}) AS geom
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
            copy_segment_rows(cur, f"{prefix}_left_segments", left_segments)
        if right_segments is not None:
            copy_segment_rows(cur, f"{prefix}_right_segments", right_segments)
        if points is not None:
            copy_point_rows(cur, f"{prefix}_points", points)
        if polygons is not None:
            copy_polygon_rows(cur, f"{prefix}_polygons", polygons)
        end = time.perf_counter()
        timings["load_sec"] = end - start
    return timings


def copy_query_hash(cur, sql: str) -> tuple[str, int]:
    sink = HashingSink()
    cur.copy_expert(sql, sink)
    return sink.hexdigest, sink.row_count


def build_postgis_lsi_sql(prefix: str) -> str:
    return f"""
COPY (
    SELECT l.id, r.id
    FROM goal50.{prefix}_left_segments AS l
    JOIN goal50.{prefix}_right_segments AS r
      ON l.geom && r.geom
     AND ABS(((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) >= 1.0e-7
     AND (((r.x0 - l.x0) * (r.y1 - r.y0)) - ((r.y0 - l.y0) * (r.x1 - r.x0)))
           / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
     AND (((r.x0 - l.x0) * (l.y1 - l.y0)) - ((r.y0 - l.y0) * (l.x1 - l.x0)))
           / (((l.x1 - l.x0) * (r.y1 - r.y0)) - ((l.y1 - l.y0) * (r.x1 - r.x0))) BETWEEN 0.0 AND 1.0
    ORDER BY 1, 2
) TO STDOUT WITH (FORMAT csv, DELIMITER E'\\t')
"""


def run_postgis_lsi(conn, prefix: str) -> tuple[dict[str, object], float]:
    sql = build_postgis_lsi_sql(prefix)
    with conn.cursor() as cur:
        start = time.perf_counter()
        digest, row_count = copy_query_hash(cur, sql)
        end = time.perf_counter()
    return {"row_count": row_count, "sha256": digest}, end - start


def build_postgis_pip_sql(prefix: str) -> str:
    return f"""
COPY (
    SELECT p.id, g.id, 1
    FROM goal50.{prefix}_points AS p
    JOIN goal50.{prefix}_polygons AS g
      ON g.geom && p.geom
     AND ST_Covers(g.geom, p.geom)
    ORDER BY 1, 2, 3
) TO STDOUT WITH (FORMAT csv, DELIMITER E'\\t')
"""


def run_postgis_pip(conn, prefix: str) -> tuple[dict[str, object], float]:
    sql = build_postgis_pip_sql(prefix)
    with conn.cursor() as cur:
        start = time.perf_counter()
        digest, row_count = copy_query_hash(cur, sql)
        end = time.perf_counter()
    return {"row_count": row_count, "sha256": digest}, end - start


def render_markdown(summary: dict[str, object]) -> str:
    def section(label: str, payload: dict[str, object]) -> list[str]:
        lsi_parity = ", ".join(f"{name}={payload['lsi'][name]['parity_vs_postgis']}" for name in payload["compared_backends"])
        pip_parity = ", ".join(f"{name}={payload['pip'][name]['parity_vs_postgis']}" for name in payload["compared_backends"])
        lines = [
            f"## {label}",
            "",
            f"- load sec: `{payload['load_sec']:.9f}`",
            f"- compared backends: `{', '.join(payload['compared_backends'])}`",
            f"- PostGIS query mode: `{payload['postgis_mode']}`",
            f"- lsi parity vs postgis: `{lsi_parity}`",
            f"- pip parity vs postgis: `{pip_parity}`",
            "",
            "### LSI",
            "",
            f"- PostGIS: `{payload['lsi']['postgis_sec']:.9f} s`",
            f"- row count: `{payload['lsi']['postgis']['row_count']}`",
            "",
            "### PIP",
            "",
            f"- PostGIS: `{payload['pip']['postgis_sec']:.9f} s`",
            f"- row count: `{payload['pip']['postgis']['row_count']}`",
            "",
        ]
        for backend_name in payload["compared_backends"]:
            lines.extend(
                [
                    f"#### {backend_name.upper()}",
                    "",
                    f"- lsi: `{payload['lsi'][backend_name]['sec']:.9f} s` parity `{payload['lsi'][backend_name]['parity_vs_postgis']}`",
                    f"- pip: `{payload['pip'][backend_name]['sec']:.9f} s` parity `{payload['pip'][backend_name]['parity_vs_postgis']}`",
                    "",
                ]
            )
        return lines

    lines = [
        "# Goal 50 PostGIS Ground-Truth Comparison",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- compares PostGIS against RTDL C oracle, Embree, and OptiX on the same bounded real-data packages already accepted in the Linux validation track",
        "- PostGIS is measured as a loaded-and-indexed query engine; load time is reported separately from query time",
        "- `lsi` uses index-assisted segment candidate pruning plus RTDL-matching exact segment math",
        "- `pip` uses an index-assisted positive-hit join via `&&` + `ST_Covers`; RTDL rows are reduced to `contains=1` for the database comparison",
        "",
    ]
    if "county_zipcode" in summary:
        lines.extend(section("County/Zipcode `top4_tx_ca_ny_pa`", summary["county_zipcode"]))
    if "blockgroup_waterbodies" in summary:
        lines.extend(section("BlockGroup/WaterBodies `county2300_s10`", summary["blockgroup_waterbodies"]))
    return "\n".join(lines)


def backend_payload(
    rows,
    sec: float,
    postgis_digest: str,
    postgis_count: int,
    kind: str,
    *,
    presorted: bool = False,
    positive_only: bool = False,
) -> dict[str, object]:
    if kind == "lsi":
        tuples = lsi_pairs(rows)
    elif positive_only:
        tuples = pip_positive_triplets(rows)
    else:
        tuples = pip_triplets(rows)
    hashed = hash_tuples(tuples, presorted=presorted)
    return {
        "sec": sec,
        "row_count": hashed["row_count"],
        "sha256": hashed["sha256"],
        "parity_vs_postgis": hashed["sha256"] == postgis_digest and hashed["row_count"] == postgis_count,
    }


def run_backend_payload(
    fn,
    kernel,
    *,
    kind: str,
    postgis_digest: str,
    postgis_count: int,
    presorted: bool = False,
    positive_only: bool = False,
    **kwargs,
) -> dict[str, object]:
    rows, sec = time_call(fn, kernel, **kwargs)
    payload = backend_payload(
        rows,
        sec,
        postgis_digest,
        postgis_count,
        kind,
        presorted=presorted,
        positive_only=positive_only,
    )
    del rows
    gc.collect()
    return payload


def run_case(
    conn,
    *,
    prefix: str,
    compared_backends: tuple[str, ...],
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

    lsi_summary = {
        "load_sec": load_stats["load_sec"],
        "compared_backends": list(compared_backends),
        "postgis_mode": "index-assisted positive-hit joins",
        "lsi": {
            "postgis": lsi_postgis,
            "postgis_sec": lsi_postgis_sec,
        },
        "pip": {
            "postgis": pip_postgis,
            "postgis_sec": pip_postgis_sec,
        },
    }

    if "cpu" in compared_backends:
        lsi_summary["lsi"]["cpu"] = run_backend_payload(
                rt.run_cpu,
                county_zip_join_reference,
                kind="lsi",
                postgis_digest=lsi_postgis["sha256"],
                postgis_count=lsi_postgis["row_count"],
                presorted=True,
                left=left_segments,
                right=right_segments,
            )
        lsi_summary["pip"]["cpu"] = run_backend_payload(
                rt.run_cpu,
                point_in_counties_reference,
                kind="pip",
                postgis_digest=pip_postgis["sha256"],
                postgis_count=pip_postgis["row_count"],
                presorted=True,
                positive_only=True,
                points=points,
                polygons=polygons,
            )
    if "embree" in compared_backends:
        lsi_summary["lsi"]["embree"] = run_backend_payload(
                rt.run_embree,
                county_zip_join_reference,
                kind="lsi",
                postgis_digest=lsi_postgis["sha256"],
                postgis_count=lsi_postgis["row_count"],
                left=left_segments,
                right=right_segments,
            )
        lsi_summary["pip"]["embree"] = run_backend_payload(
                rt.run_embree,
                point_in_counties_reference,
                kind="pip",
                postgis_digest=pip_postgis["sha256"],
                postgis_count=pip_postgis["row_count"],
                positive_only=True,
                points=points,
                polygons=polygons,
            )
    if "optix" in compared_backends:
        lsi_summary["lsi"]["optix"] = run_backend_payload(
                rt.run_optix,
                county_zip_join_reference,
                kind="lsi",
                postgis_digest=lsi_postgis["sha256"],
                postgis_count=lsi_postgis["row_count"],
                left=left_segments,
                right=right_segments,
            )
        lsi_summary["pip"]["optix"] = run_backend_payload(
                rt.run_optix,
                point_in_counties_reference,
                kind="pip",
                postgis_digest=pip_postgis["sha256"],
                postgis_count=pip_postgis["row_count"],
                positive_only=True,
                points=points,
                polygons=polygons,
            )
    return lsi_summary, {
        "left_segments": len(left_segments),
        "right_segments": len(right_segments),
        "points": len(points),
        "polygons": len(polygons),
    }


def main() -> int:
    args = parse_args()
    selected_cases = tuple(part.strip() for part in args.cases.split(",") if part.strip())
    compared_backends = tuple(part.strip() for part in args.backends.split(",") if part.strip())
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

        if "county_zipcode" in selected_cases:
            county_case, county_sizes = run_case(
                conn,
                prefix="county_zipcode",
                compared_backends=compared_backends,
                left_segments=county_left,
                right_segments=county_right,
                points=county_points,
                polygons=county_polygons,
            )
        else:
            county_case, county_sizes = None, None
        if "blockgroup_waterbodies" in selected_cases:
            block_case, block_sizes = run_case(
                conn,
                prefix="blockgroup_waterbodies",
                compared_backends=compared_backends,
                left_segments=block_left,
                right_segments=block_right,
                points=block_points,
                polygons=block_polygons,
            )
        else:
            block_case, block_sizes = None, None
    finally:
        conn.close()

    summary = {
        "host_label": args.host_label,
        "db_name": args.db_name,
        "compared_backends": list(compared_backends),
        "selected_cases": list(selected_cases),
    }
    if county_case is not None:
        summary["county_zipcode"] = {
            "county": county_summary,
            "zipcode": zipcode_summary,
            "derived_sizes": county_sizes,
            **county_case,
        }
    if block_case is not None:
        summary["blockgroup_waterbodies"] = {
            "blockgroup": block_summary,
            "waterbodies": water_summary,
            "derived_sizes": block_sizes,
            **block_case,
        }

    (output_dir / "goal50_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal50_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

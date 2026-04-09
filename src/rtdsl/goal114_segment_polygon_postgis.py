from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import socket
import time
from datetime import datetime
from pathlib import Path

from .baseline_contracts import compare_baseline_rows
from .baseline_runner import load_representative_case


def segment_polygon_large_dataset_name(*, copies: int) -> str:
    if copies <= 0:
        raise ValueError("copies must be positive")
    return f"derived/br_county_subset_segment_polygon_tiled_x{copies}"


def connect_postgis(db_name: str, db_user: str | None):
    import psycopg2

    kwargs = {"dbname": db_name}
    if db_user:
        kwargs["user"] = db_user
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn


def _polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = vertices if vertices and vertices[0] == vertices[-1] else vertices + (vertices[0],)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def _copy_segments(cur, table: str, rows) -> None:
    cur.execute(
        f"CREATE TABLE goal114.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)"
    )
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row.id), row.x0, row.y0, row.x1, row.y1])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal114.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal114.{table} AS
        SELECT
            id,
            ST_GeomFromText(
                'LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')',
                4326
            )::geometry(LINESTRING, 4326) AS geom
        FROM goal114.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal114.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal114.{table}")


def _copy_polygons(cur, table: str, rows) -> None:
    cur.execute(f"CREATE TABLE goal114.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row.id), _polygon_wkt(tuple(row.vertices))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY goal114.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE goal114.{table} AS
        SELECT id, ST_GeomFromText(wkt, 4326)::geometry(POLYGON, 4326) AS geom
        FROM goal114.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON goal114.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE goal114.{table}")


def _hash_rows(rows: tuple[dict[str, int], ...]) -> dict[str, object]:
    normalized = tuple(sorted((int(row["segment_id"]), int(row["hit_count"])) for row in rows))
    hasher = hashlib.sha256()
    for segment_id, hit_count in normalized:
        hasher.update(f"{segment_id}\t{hit_count}\n".encode("utf-8"))
    return {"row_count": len(normalized), "sha256": hasher.hexdigest()}


def run_postgis_segment_polygon_hitcount(
    *,
    db_name: str,
    db_user: str | None,
    dataset: str,
) -> tuple[tuple[dict[str, int], ...], float]:
    case = load_representative_case("segment_polygon_hitcount", dataset)
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal114 CASCADE")
            cur.execute("CREATE SCHEMA goal114")
            _copy_segments(cur, "segments", tuple(case.inputs["segments"]))
            _copy_polygons(cur, "polygons", tuple(case.inputs["polygons"]))
            start = time.perf_counter()
            cur.execute(
                """
                SELECT
                    s.id::BIGINT AS segment_id,
                    COUNT(p.id)::BIGINT AS hit_count
                FROM goal114.segments AS s
                LEFT JOIN goal114.polygons AS p
                    ON ST_Intersects(s.geom, p.geom)
                GROUP BY s.id
                ORDER BY s.id
                """
            )
            rows = tuple(
                {"segment_id": int(segment_id), "hit_count": int(hit_count)}
                for segment_id, hit_count in cur.fetchall()
            )
            sec = time.perf_counter() - start
        return rows, sec
    finally:
        conn.close()


def run_goal114_segment_polygon_postgis_validation(
    *,
    dataset: str,
    backends: tuple[str, ...] = ("cpu", "embree", "optix"),
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt
    from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference

    case = load_representative_case("segment_polygon_hitcount", dataset)
    postgis_rows, postgis_sec = run_postgis_segment_polygon_hitcount(
        db_name=db_name,
        db_user=db_user,
        dataset=dataset,
    )
    postgis_hash = _hash_rows(postgis_rows)
    records = []
    for backend in backends:
        start = time.perf_counter()
        if backend == "cpu":
            rows = rt.run_cpu(segment_polygon_hitcount_reference, **case.inputs)
        elif backend == "embree":
            rows = rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
        elif backend == "optix":
            rows = rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
        elif backend == "vulkan":
            rows = rt.run_vulkan(segment_polygon_hitcount_reference, **case.inputs)
        else:
            raise ValueError(f"unsupported Goal 114 backend `{backend}`")
        sec = time.perf_counter() - start
        records.append(
            {
                "backend": backend,
                "row_count": len(rows),
                "sec": sec,
                "parity_vs_postgis": compare_baseline_rows(
                    "segment_polygon_hitcount",
                    postgis_rows,
                    rows,
                ),
                "hash": _hash_rows(rows),
            }
        )

    return {
        "suite": "goal114_segment_polygon_postgis_validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "dataset": dataset,
        "segment_count": len(case.inputs["segments"]),
        "polygon_count": len(case.inputs["polygons"]),
        "postgis": {
            "sec": postgis_sec,
            "row_count": postgis_hash["row_count"],
            "sha256": postgis_hash["sha256"],
        },
        "records": records,
    }


def render_goal114_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 114 Segment/Polygon PostGIS Validation Summary",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- Segments: `{payload['segment_count']}`",
        f"- Polygons: `{payload['polygon_count']}`",
        f"- Host: `{payload['host']['platform']}`",
        f"- PostGIS: `{payload['postgis']['sec']:.6f} s`, rows `{payload['postgis']['row_count']}`",
        "",
        "| Backend | Time (s) | Row Count | Parity vs PostGIS | SHA256 |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for record in payload["records"]:
        lines.append(
            f"| `{record['backend']}` | {record['sec']:.6f} | {record['row_count']} | "
            f"`{record['parity_vs_postgis']}` | `{record['hash']['sha256']}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_goal114_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal114_segment_polygon_postgis_validation.json"
    md_path = output_root / "goal114_segment_polygon_postgis_validation.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal114_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

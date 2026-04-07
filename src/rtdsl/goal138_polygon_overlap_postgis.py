from __future__ import annotations

import csv
import io
import json
import platform
import socket
import time
from datetime import datetime
from pathlib import Path

from .goal114_segment_polygon_postgis import connect_postgis


def _kernel():
    from examples.rtdl_polygon_pair_overlap_area_rows import polygon_pair_overlap_area_rows_reference

    return polygon_pair_overlap_area_rows_reference


def _case():
    from examples.rtdl_polygon_pair_overlap_area_rows import make_authored_polygon_pair_overlap_case

    return make_authored_polygon_pair_overlap_case()


def _polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = vertices if vertices and vertices[0] == vertices[-1] else vertices + (vertices[0],)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def _copy_polygons(cur, schema: str, table: str, rows) -> None:
    cur.execute(f"CREATE TABLE {schema}.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row.id), _polygon_wkt(tuple(row.vertices))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY {schema}.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE {schema}.{table} AS
        SELECT id, ST_GeomFromText(wkt, 0)::geometry(POLYGON) AS geom
        FROM {schema}.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON {schema}.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE {schema}.{table}")


def run_postgis_polygon_pair_overlap_area_rows(
    *,
    db_name: str,
    db_user: str | None = None,
) -> tuple[tuple[dict[str, int], ...], float]:
    case = _case()
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal138 CASCADE")
            cur.execute("CREATE SCHEMA goal138")
            _copy_polygons(cur, "goal138", "left_polygons", tuple(case["left"]))
            _copy_polygons(cur, "goal138", "right_polygons", tuple(case["right"]))
            start = time.perf_counter()
            cur.execute(
                """
                SELECT
                    l.id::BIGINT AS left_polygon_id,
                    r.id::BIGINT AS right_polygon_id,
                    ROUND(ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS intersection_area,
                    ROUND(ST_Area(l.geom))::BIGINT AS left_area,
                    ROUND(ST_Area(r.geom))::BIGINT AS right_area,
                    ROUND(ST_Area(l.geom) + ST_Area(r.geom) - ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS union_area
                FROM goal138.left_polygons AS l
                JOIN goal138.right_polygons AS r
                    ON ST_Intersects(l.geom, r.geom)
                WHERE ST_Area(ST_Intersection(l.geom, r.geom)) > 0.0
                ORDER BY l.id, r.id
                """
            )
            rows = tuple(
                {
                    "left_polygon_id": int(left_polygon_id),
                    "right_polygon_id": int(right_polygon_id),
                    "intersection_area": int(intersection_area),
                    "left_area": int(left_area),
                    "right_area": int(right_area),
                    "union_area": int(union_area),
                }
                for (
                    left_polygon_id,
                    right_polygon_id,
                    intersection_area,
                    left_area,
                    right_area,
                    union_area,
                ) in cur.fetchall()
            )
            sec = time.perf_counter() - start
        return rows, sec
    finally:
        conn.close()


def _rows_equal(left: tuple[dict[str, int], ...], right: tuple[dict[str, int], ...]) -> bool:
    return tuple(sorted(tuple(row.items()) for row in left)) == tuple(sorted(tuple(row.items()) for row in right))


def run_goal138_polygon_overlap_postgis_validation(
    *,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    case = _case()
    postgis_rows, postgis_sec = run_postgis_polygon_pair_overlap_area_rows(
        db_name=db_name,
        db_user=db_user,
    )
    python_rows = rt.run_cpu_python_reference(_kernel(), **case)
    cpu_rows = rt.run_cpu(_kernel(), **case)
    return {
        "suite": "goal138_polygon_overlap_postgis_validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "postgis_sec": postgis_sec,
        "postgis_rows": postgis_rows,
        "python_rows": python_rows,
        "cpu_rows": cpu_rows,
        "python_parity_vs_postgis": _rows_equal(postgis_rows, python_rows),
        "cpu_parity_vs_postgis": _rows_equal(postgis_rows, cpu_rows),
    }


def render_goal138_markdown(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Goal 138 Polygon Pair Overlap Area Rows Summary",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- host: `{payload['host']['platform']}`",
            f"- postgis_sec: `{payload['postgis_sec']:.6f}`",
            f"- python parity vs postgis: `{payload['python_parity_vs_postgis']}`",
            f"- cpu parity vs postgis: `{payload['cpu_parity_vs_postgis']}`",
            "",
            "## Rows",
            "",
            "| left_polygon_id | right_polygon_id | intersection_area | left_area | right_area | union_area |",
            "| --- | --- | --- | --- | --- | --- |",
            *[
                f"| `{row['left_polygon_id']}` | `{row['right_polygon_id']}` | `{row['intersection_area']}` | `{row['left_area']}` | `{row['right_area']}` | `{row['union_area']}` |"
                for row in payload["postgis_rows"]
            ],
            "",
        ]
    )


def write_goal138_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "summary.json"
    markdown_path = output_path / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_goal138_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

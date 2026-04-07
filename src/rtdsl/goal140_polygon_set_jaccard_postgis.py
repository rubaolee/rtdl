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
    from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference

    return polygon_set_jaccard_reference


def _case():
    from examples.rtdl_polygon_set_jaccard import make_authored_polygon_set_jaccard_case

    return make_authored_polygon_set_jaccard_case()


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


def run_postgis_polygon_set_jaccard(*, db_name: str, db_user: str | None = None) -> tuple[tuple[dict[str, float | int], ...], float]:
    case = _case()
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal140 CASCADE")
            cur.execute("CREATE SCHEMA goal140")
            _copy_polygons(cur, "goal140", "left_polygons", tuple(case["left"]))
            _copy_polygons(cur, "goal140", "right_polygons", tuple(case["right"]))
            start = time.perf_counter()
            cur.execute(
                """
                WITH cell_bounds AS (
                    SELECT
                        FLOOR(LEAST(
                            (SELECT MIN(ST_XMin(geom)) FROM goal140.left_polygons),
                            (SELECT MIN(ST_XMin(geom)) FROM goal140.right_polygons)
                        ))::INT AS min_x,
                        CEIL(GREATEST(
                            (SELECT MAX(ST_XMax(geom)) FROM goal140.left_polygons),
                            (SELECT MAX(ST_XMax(geom)) FROM goal140.right_polygons)
                        ))::INT AS max_x,
                        FLOOR(LEAST(
                            (SELECT MIN(ST_YMin(geom)) FROM goal140.left_polygons),
                            (SELECT MIN(ST_YMin(geom)) FROM goal140.right_polygons)
                        ))::INT AS min_y,
                        CEIL(GREATEST(
                            (SELECT MAX(ST_YMax(geom)) FROM goal140.left_polygons),
                            (SELECT MAX(ST_YMax(geom)) FROM goal140.right_polygons)
                        ))::INT AS max_y
                ),
                cells AS (
                    SELECT x, y
                    FROM cell_bounds,
                    generate_series(min_x, max_x - 1) AS x,
                    generate_series(min_y, max_y - 1) AS y
                ),
                left_cells AS (
                    SELECT DISTINCT c.x, c.y
                    FROM cells AS c
                    JOIN goal140.left_polygons AS p
                      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
                ),
                right_cells AS (
                    SELECT DISTINCT c.x, c.y
                    FROM cells AS c
                    JOIN goal140.right_polygons AS p
                      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
                ),
                stats AS (
                    SELECT
                        (SELECT COUNT(*) FROM left_cells) AS left_area,
                        (SELECT COUNT(*) FROM right_cells) AS right_area,
                        (
                            SELECT COUNT(*)
                            FROM left_cells AS l
                            JOIN right_cells AS r
                              ON l.x = r.x AND l.y = r.y
                        ) AS intersection_area,
                        (
                            SELECT COUNT(*)
                            FROM (
                                SELECT x, y FROM left_cells
                                UNION
                                SELECT x, y FROM right_cells
                            ) AS u
                        ) AS union_area
                )
                SELECT
                    intersection_area::BIGINT,
                    left_area::BIGINT,
                    right_area::BIGINT,
                    union_area::BIGINT,
                    CASE
                        WHEN union_area = 0 THEN 0.0
                        ELSE intersection_area::DOUBLE PRECISION / union_area::DOUBLE PRECISION
                    END AS jaccard_similarity
                FROM stats
                """
            )
            rows = tuple(
                {
                    "intersection_area": int(intersection_area),
                    "left_area": int(left_area),
                    "right_area": int(right_area),
                    "union_area": int(union_area),
                    "jaccard_similarity": float(jaccard_similarity),
                }
                for (
                    intersection_area,
                    left_area,
                    right_area,
                    union_area,
                    jaccard_similarity,
                ) in cur.fetchall()
            )
            sec = time.perf_counter() - start
        return rows, sec
    finally:
        conn.close()


def _rows_equal(left: tuple[dict[str, float | int], ...], right: tuple[dict[str, float | int], ...]) -> bool:
    if len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if any(int(left_row[key]) != int(right_row[key]) for key in ("intersection_area", "left_area", "right_area", "union_area")):
            return False
        if abs(float(left_row["jaccard_similarity"]) - float(right_row["jaccard_similarity"])) > 1.0e-9:
            return False
    return True


def run_goal140_polygon_set_jaccard_postgis_validation(
    *,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    case = _case()
    postgis_rows, postgis_sec = run_postgis_polygon_set_jaccard(db_name=db_name, db_user=db_user)
    python_rows = rt.run_cpu_python_reference(_kernel(), **case)
    cpu_rows = rt.run_cpu(_kernel(), **case)
    return {
        "suite": "goal140_polygon_set_jaccard_postgis_validation",
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


def render_goal140_markdown(payload: dict[str, object]) -> str:
    row = payload["postgis_rows"][0]
    return "\n".join(
        [
            "# Goal 140 Polygon Set Jaccard Summary",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- host: `{payload['host']['platform']}`",
            f"- postgis_sec: `{payload['postgis_sec']:.6f}`",
            f"- python parity vs postgis: `{payload['python_parity_vs_postgis']}`",
            f"- cpu parity vs postgis: `{payload['cpu_parity_vs_postgis']}`",
            "",
            "| intersection_area | left_area | right_area | union_area | jaccard_similarity |",
            "| --- | --- | --- | --- | --- |",
            f"| `{row['intersection_area']}` | `{row['left_area']}` | `{row['right_area']}` | `{row['union_area']}` | `{row['jaccard_similarity']:.6f}` |",
            "",
        ]
    )


def write_goal140_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "summary.json"
    markdown_path = output_path / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_goal140_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

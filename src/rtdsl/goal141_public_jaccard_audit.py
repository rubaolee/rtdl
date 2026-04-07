from __future__ import annotations

import csv
import io
import json
import platform
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .goal114_segment_polygon_postgis import connect_postgis
from .goal139_pathology_data import monuseg_drive_file_id
from .goal139_pathology_data import parse_monuseg_xml_annotations
from .reference import _point_in_polygon
from .reference import Polygon


MONUSEG_DEFAULT_XML = "MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml"


@dataclass(frozen=True)
class Goal141PublicCase:
    xml_name: str
    raw_polygon_count: int
    selected_polygon_count: int
    left_polygons: tuple[Polygon, ...]
    right_polygons: tuple[Polygon, ...]


def download_monuseg_training_zip(destination: str | Path) -> Path:
    import urllib.request

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_id = monuseg_drive_file_id()
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    urllib.request.urlretrieve(url, path)
    return path


def list_monuseg_training_xml_names(zip_path: str | Path) -> tuple[str, ...]:
    with zipfile.ZipFile(zip_path) as archive:
        return tuple(sorted(name for name in archive.namelist() if name.lower().endswith(".xml")))


def load_monuseg_training_xml_annotations(
    zip_path: str | Path,
    *,
    xml_name: str = MONUSEG_DEFAULT_XML,
) -> tuple[Polygon, ...]:
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(xml_name) as handle:
            xml_text = handle.read().decode("utf-8")
    return parse_monuseg_xml_annotations(xml_text)


def monuseg_polygons_to_unit_square_polygons(
    polygons: tuple[Polygon, ...],
    *,
    polygon_limit: int = 64,
) -> tuple[Polygon, ...]:
    cells: set[tuple[int, int]] = set()
    for polygon in polygons[:polygon_limit]:
        min_x = int(min(vertex[0] for vertex in polygon.vertices))
        max_x = int(max(vertex[0] for vertex in polygon.vertices))
        min_y = int(min(vertex[1] for vertex in polygon.vertices))
        max_y = int(max(vertex[1] for vertex in polygon.vertices))
        for x_value in range(min_x, max_x):
            for y_value in range(min_y, max_y):
                if _point_in_polygon(x_value + 0.5, y_value + 0.5, polygon.vertices):
                    cells.add((x_value, y_value))
    square_polygons = []
    for next_id, (x_value, y_value) in enumerate(sorted(cells), start=1):
        square_polygons.append(
            Polygon(
                id=next_id,
                vertices=(
                    (float(x_value), float(y_value)),
                    (float(x_value + 1), float(y_value)),
                    (float(x_value + 1), float(y_value + 1)),
                    (float(x_value), float(y_value + 1)),
                ),
            )
        )
    return tuple(square_polygons)


def build_goal141_public_case(
    zip_path: str | Path,
    *,
    xml_name: str = MONUSEG_DEFAULT_XML,
    polygon_limit: int = 64,
    shift_x: int = 1,
    shift_y: int = 0,
) -> Goal141PublicCase:
    raw_polygons = load_monuseg_training_xml_annotations(zip_path, xml_name=xml_name)
    left_polygons = monuseg_polygons_to_unit_square_polygons(raw_polygons, polygon_limit=polygon_limit)
    right_polygons = tuple(
        Polygon(
            id=polygon.id,
            vertices=tuple((x_value + shift_x, y_value + shift_y) for x_value, y_value in polygon.vertices),
        )
        for polygon in left_polygons
    )
    return Goal141PublicCase(
        xml_name=xml_name,
        raw_polygon_count=len(raw_polygons),
        selected_polygon_count=min(len(raw_polygons), polygon_limit),
        left_polygons=left_polygons,
        right_polygons=right_polygons,
    )


def tile_polygon_set(
    polygons: tuple[Polygon, ...],
    *,
    copies: int,
    stride_x: int,
) -> tuple[Polygon, ...]:
    tiled = []
    next_id = 1
    for copy_index in range(copies):
        x_offset = copy_index * stride_x
        for polygon in polygons:
            tiled.append(
                Polygon(
                    id=next_id,
                    vertices=tuple((x_value + x_offset, y_value) for x_value, y_value in polygon.vertices),
                )
            )
            next_id += 1
    return tuple(tiled)


def _copy_polygons(cur, schema: str, table: str, rows: tuple[Polygon, ...]) -> None:
    cur.execute(f"CREATE TABLE {schema}.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        ring = row.vertices if row.vertices[0] == row.vertices[-1] else row.vertices + (row.vertices[0],)
        writer.writerow([int(row.id), "POLYGON((" + ",".join(f"{x} {y}" for x, y in ring) + "))"])
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


def run_postgis_polygon_set_jaccard_for_case(
    left_polygons: tuple[Polygon, ...],
    right_polygons: tuple[Polygon, ...],
    *,
    db_name: str,
    db_user: str | None = None,
) -> tuple[tuple[dict[str, float | int], ...], float]:
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal141 CASCADE")
            cur.execute("CREATE SCHEMA goal141")
            _copy_polygons(cur, "goal141", "left_polygons", left_polygons)
            _copy_polygons(cur, "goal141", "right_polygons", right_polygons)
            start = time.perf_counter()
            cur.execute(
                """
                WITH cell_bounds AS (
                    SELECT
                        FLOOR(LEAST(
                            (SELECT MIN(ST_XMin(geom)) FROM goal141.left_polygons),
                            (SELECT MIN(ST_XMin(geom)) FROM goal141.right_polygons)
                        ))::INT AS min_x,
                        CEIL(GREATEST(
                            (SELECT MAX(ST_XMax(geom)) FROM goal141.left_polygons),
                            (SELECT MAX(ST_XMax(geom)) FROM goal141.right_polygons)
                        ))::INT AS max_x,
                        FLOOR(LEAST(
                            (SELECT MIN(ST_YMin(geom)) FROM goal141.left_polygons),
                            (SELECT MIN(ST_YMin(geom)) FROM goal141.right_polygons)
                        ))::INT AS min_y,
                        CEIL(GREATEST(
                            (SELECT MAX(ST_YMax(geom)) FROM goal141.left_polygons),
                            (SELECT MAX(ST_YMax(geom)) FROM goal141.right_polygons)
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
                    JOIN goal141.left_polygons AS p
                      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
                ),
                right_cells AS (
                    SELECT DISTINCT c.x, c.y
                    FROM cells AS c
                    JOIN goal141.right_polygons AS p
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


def run_goal141_public_jaccard_audit(
    *,
    zip_path: str | Path,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
    xml_name: str = MONUSEG_DEFAULT_XML,
    polygon_limit: int = 64,
    copies: tuple[int, ...] = (1, 4),
) -> dict[str, object]:
    import rtdsl as rt
    from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference

    case = build_goal141_public_case(
        zip_path,
        xml_name=xml_name,
        polygon_limit=polygon_limit,
    )
    max_x = max(int(vertex[0]) for polygon in case.left_polygons for vertex in polygon.vertices)
    min_x = min(int(vertex[0]) for polygon in case.left_polygons for vertex in polygon.vertices)
    stride_x = (max_x - min_x) + 8
    rows = []
    for copy_count in copies:
        left_polygons = tile_polygon_set(case.left_polygons, copies=copy_count, stride_x=stride_x)
        right_polygons = tile_polygon_set(case.right_polygons, copies=copy_count, stride_x=stride_x)
        python_start = time.perf_counter()
        python_rows = rt.run_cpu_python_reference(
            polygon_set_jaccard_reference,
            left=left_polygons,
            right=right_polygons,
        )
        python_sec = time.perf_counter() - python_start
        cpu_start = time.perf_counter()
        cpu_rows = rt.run_cpu(
            polygon_set_jaccard_reference,
            left=left_polygons,
            right=right_polygons,
        )
        cpu_sec = time.perf_counter() - cpu_start
        postgis_rows, postgis_sec = run_postgis_polygon_set_jaccard_for_case(
            left_polygons,
            right_polygons,
            db_name=db_name,
            db_user=db_user,
        )
        rows.append(
            {
                "copies": copy_count,
                "left_polygon_count": len(left_polygons),
                "right_polygon_count": len(right_polygons),
                "python_sec": python_sec,
                "cpu_sec": cpu_sec,
                "postgis_sec": postgis_sec,
                "python_parity_vs_postgis": _rows_equal(postgis_rows, python_rows),
                "cpu_parity_vs_postgis": _rows_equal(postgis_rows, cpu_rows),
                "postgis_rows": postgis_rows,
            }
        )
    return {
        "suite": "goal141_public_jaccard_audit",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "dataset": {
            "kind": "public_real_data_derived_pair",
            "source": "MoNuSeg 2018 Training Data",
            "xml_name": case.xml_name,
            "raw_polygon_count": case.raw_polygon_count,
            "selected_polygon_count": case.selected_polygon_count,
            "base_left_polygon_count": len(case.left_polygons),
            "base_right_polygon_count": len(case.right_polygons),
            "pair_derivation": "right set is the same real-data-derived unit-cell polygon set shifted by +1 cell in x",
        },
        "rows": rows,
    }


def render_goal141_markdown(payload: dict[str, object]) -> str:
    dataset = payload["dataset"]
    lines = [
        "# Goal 141 Public Jaccard Audit",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- host: `{payload['host']['platform']}`",
        f"- source: `{dataset['source']}`",
        f"- xml_name: `{dataset['xml_name']}`",
        f"- raw_polygon_count: `{dataset['raw_polygon_count']}`",
        f"- selected_polygon_count: `{dataset['selected_polygon_count']}`",
        f"- base_left_polygon_count: `{dataset['base_left_polygon_count']}`",
        f"- base_right_polygon_count: `{dataset['base_right_polygon_count']}`",
        f"- pair_derivation: `{dataset['pair_derivation']}`",
        "",
        "| copies | left_polygon_count | right_polygon_count | python_sec | cpu_sec | postgis_sec | python_parity_vs_postgis | cpu_parity_vs_postgis | jaccard_similarity |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        result = row["postgis_rows"][0]
        lines.append(
            f"| `{row['copies']}` | `{row['left_polygon_count']}` | `{row['right_polygon_count']}` | "
            f"`{row['python_sec']:.6f}` | `{row['cpu_sec']:.6f}` | `{row['postgis_sec']:.6f}` | "
            f"`{row['python_parity_vs_postgis']}` | `{row['cpu_parity_vs_postgis']}` | "
            f"`{result['jaccard_similarity']:.6f}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_goal141_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "summary.json"
    markdown_path = output_path / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_goal141_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

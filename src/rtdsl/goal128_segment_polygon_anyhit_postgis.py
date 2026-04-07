from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import socket
import statistics
import time
from datetime import datetime
from pathlib import Path

from .baseline_contracts import compare_baseline_rows
from .baseline_runner import load_representative_case
from .goal114_segment_polygon_postgis import connect_postgis
from .goal114_segment_polygon_postgis import segment_polygon_large_dataset_name


LARGE_COPIES = (64, 256, 512, 1024)
PREPARED_COPIES = (64, 256)


def _kernel():
    from examples.rtdl_goal10_reference import segment_polygon_anyhit_rows_reference

    return segment_polygon_anyhit_rows_reference


def _format_optional_mean(value: object | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6f}"


def _hash_rows(rows: tuple[dict[str, int], ...]) -> dict[str, object]:
    normalized = tuple(sorted((int(row["segment_id"]), int(row["polygon_id"])) for row in rows))
    hasher = hashlib.sha256()
    for segment_id, polygon_id in normalized:
        hasher.update(f"{segment_id}\t{polygon_id}\n".encode("utf-8"))
    return {"row_count": len(normalized), "sha256": hasher.hexdigest()}


def _polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = vertices if vertices and vertices[0] == vertices[-1] else vertices + (vertices[0],)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def _copy_segments(cur, schema: str, table: str, rows) -> None:
    cur.execute(
        f"CREATE TABLE {schema}.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)"
    )
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter='\t', lineterminator='\n')
    for row in rows:
        writer.writerow([int(row.id), row.x0, row.y0, row.x1, row.y1])
    payload.seek(0)
    cur.copy_expert(
        f"COPY {schema}.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE {schema}.{table} AS
        SELECT
            id,
            ST_GeomFromText(
                'LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')',
                4326
            )::geometry(LINESTRING, 4326) AS geom
        FROM {schema}.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON {schema}.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE {schema}.{table}")


def _copy_polygons(cur, schema: str, table: str, rows) -> None:
    cur.execute(f"CREATE TABLE {schema}.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter='\t', lineterminator='\n')
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
        SELECT id, ST_GeomFromText(wkt, 4326)::geometry(POLYGON, 4326) AS geom
        FROM {schema}.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON {schema}.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE {schema}.{table}")


def run_postgis_segment_polygon_anyhit_rows(
    *,
    db_name: str,
    db_user: str | None,
    dataset: str,
) -> tuple[tuple[dict[str, int], ...], float]:
    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal128 CASCADE")
            cur.execute("CREATE SCHEMA goal128")
            _copy_segments(cur, "goal128", "segments", tuple(case.inputs["segments"]))
            _copy_polygons(cur, "goal128", "polygons", tuple(case.inputs["polygons"]))
            start = time.perf_counter()
            cur.execute(
                """
                SELECT
                    s.id::BIGINT AS segment_id,
                    p.id::BIGINT AS polygon_id
                FROM goal128.segments AS s
                JOIN goal128.polygons AS p
                    ON ST_Intersects(s.geom, p.geom)
                ORDER BY s.id, p.id
                """
            )
            rows = tuple(
                {"segment_id": int(segment_id), "polygon_id": int(polygon_id)}
                for segment_id, polygon_id in cur.fetchall()
            )
            sec = time.perf_counter() - start
        return rows, sec
    finally:
        conn.close()


def run_goal128_segment_polygon_anyhit_postgis_validation(
    *,
    dataset: str,
    backends: tuple[str, ...] = ("cpu", "embree", "optix", "vulkan"),
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    postgis_rows, postgis_sec = run_postgis_segment_polygon_anyhit_rows(
        db_name=db_name,
        db_user=db_user,
        dataset=dataset,
    )
    postgis_hash = _hash_rows(postgis_rows)
    records = []
    for backend in backends:
        start = time.perf_counter()
        if backend == "cpu":
            rows = rt.run_cpu(_kernel(), **case.inputs)
        elif backend == "embree":
            rows = rt.run_embree(_kernel(), **case.inputs)
        elif backend == "optix":
            rows = rt.run_optix(_kernel(), **case.inputs)
        elif backend == "vulkan":
            rows = rt.run_vulkan(_kernel(), **case.inputs)
        else:
            raise ValueError(f"unsupported Goal 128 backend `{backend}`")
        sec = time.perf_counter() - start
        records.append(
            {
                "backend": backend,
                "row_count": len(rows),
                "sec": sec,
                "parity_vs_postgis": compare_baseline_rows(
                    "segment_polygon_anyhit_rows",
                    postgis_rows,
                    rows,
                ),
                "hash": _hash_rows(rows),
            }
        )

    return {
        "suite": "goal128_segment_polygon_anyhit_postgis_validation",
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


def _measure_current(backend: str, dataset: str, *, iterations: int) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    runner = {
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
    }[backend]
    timings: list[float] = []
    row_count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        rows = runner(_kernel(), **case.inputs)
        timings.append(time.perf_counter() - start)
        row_count = len(rows)
    return {
        "backend": backend,
        "dataset": dataset,
        "boundary": "current_run",
        "row_count": row_count,
        "timings_sec": timings,
        "mean_sec": statistics.mean(timings) if timings else 0.0,
        "median_sec": statistics.median(timings) if timings else 0.0,
        "min_sec": min(timings) if timings else 0.0,
        "max_sec": max(timings) if timings else 0.0,
    }


def _measure_prepared(backend: str, dataset: str, *, iterations: int) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    packed = {
        "segments": rt.pack_segments(records=case.inputs["segments"]),
        "polygons": rt.pack_polygons(records=case.inputs["polygons"]),
    }
    prepare = {
        "embree": rt.prepare_embree,
        "optix": rt.prepare_optix,
    }[backend]
    prepared = prepare(_kernel())

    bind_and_run_timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        prepared.bind(**packed).run()
        bind_and_run_timings.append(time.perf_counter() - start)

    bound = prepared.bind(**packed)
    reuse_timings: list[float] = []
    row_count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        rows = bound.run()
        reuse_timings.append(time.perf_counter() - start)
        row_count = len(rows)

    return {
        "backend": backend,
        "dataset": dataset,
        "row_count": row_count,
        "prepared_bind_and_run": {
            "timings_sec": bind_and_run_timings,
            "mean_sec": statistics.mean(bind_and_run_timings) if bind_and_run_timings else 0.0,
            "median_sec": statistics.median(bind_and_run_timings) if bind_and_run_timings else 0.0,
            "min_sec": min(bind_and_run_timings) if bind_and_run_timings else 0.0,
            "max_sec": max(bind_and_run_timings) if bind_and_run_timings else 0.0,
        },
        "prepared_reuse": {
            "timings_sec": reuse_timings,
            "mean_sec": statistics.mean(reuse_timings) if reuse_timings else 0.0,
            "median_sec": statistics.median(reuse_timings) if reuse_timings else 0.0,
            "min_sec": min(reuse_timings) if reuse_timings else 0.0,
            "max_sec": max(reuse_timings) if reuse_timings else 0.0,
        },
    }


def run_goal128_segment_polygon_anyhit_linux_large_perf(
    *,
    copies: tuple[int, ...] = LARGE_COPIES,
    prepared_copies: tuple[int, ...] = PREPARED_COPIES,
    perf_iterations: int = 3,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    postgis_rows = []
    for copy_count in copies:
        dataset = segment_polygon_large_dataset_name(copies=copy_count)
        payload = run_goal128_segment_polygon_anyhit_postgis_validation(
            dataset=dataset,
            backends=("cpu", "embree", "optix", "vulkan"),
            db_name=db_name,
            db_user=db_user,
        )
        postgis_rows.append(payload)

    performance_rows = []
    for copy_count in prepared_copies:
        dataset = segment_polygon_large_dataset_name(copies=copy_count)
        performance_rows.append(_measure_current("cpu", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("embree", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("optix", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("vulkan", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_prepared("embree", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_prepared("optix", dataset, iterations=perf_iterations))

    versions = {
        "oracle": rt.oracle_version(),
        "embree": rt.embree_version(),
        "optix": rt.optix_version(),
        "vulkan": rt.vulkan_version(),
    }
    return {
        "suite": "goal128_segment_polygon_anyhit_linux_large_perf",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "versions": versions,
        "copies": copies,
        "prepared_copies": prepared_copies,
        "perf_iterations": perf_iterations,
        "postgis_rows": postgis_rows,
        "performance_rows": performance_rows,
    }


def render_goal128_postgis_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 128 Segment/Polygon Any-Hit Rows PostGIS Validation Summary",
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


def render_goal128_linux_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 128 Segment/Polygon Any-Hit Rows Linux Large-Scale Performance",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Host: `{payload['host']['platform']}`",
        f"- Versions: oracle `{payload['versions']['oracle']}`, embree `{payload['versions']['embree']}`, "
        f"optix `{payload['versions']['optix']}`, vulkan `{payload['versions']['vulkan']}`",
        "",
        "## PostGIS-Backed Large-Scale Results",
        "",
        "| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["postgis_rows"]:
        rec = {item["backend"]: item for item in row["records"]}
        all_parity = all(item["parity_vs_postgis"] for item in row["records"])
        lines.append(
            f"| `{row['dataset']}` | {row['segment_count']} | {row['polygon_count']} | "
            f"{row['postgis']['sec']:.6f} | {rec['cpu']['sec']:.6f} | {rec['embree']['sec']:.6f} | "
            f"{rec['optix']['sec']:.6f} | {rec['vulkan']['sec']:.6f} | `{all_parity}` |"
        )

    lines.extend(
        [
            "",
            "## Current And Prepared Timings",
            "",
            "| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in payload["performance_rows"]:
        grouped[(row["dataset"], row["backend"])] = {**grouped.get((row["dataset"], row["backend"]), {}), **row}
    for dataset in [segment_polygon_large_dataset_name(copies=n) for n in payload["prepared_copies"]]:
        for backend in ("cpu", "embree", "optix", "vulkan"):
            row = grouped.get((dataset, backend), {"mean_sec": 0.0})
            bind_mean = row.get("prepared_bind_and_run", {}).get("mean_sec")
            reuse_mean = row.get("prepared_reuse", {}).get("mean_sec")
            lines.append(
                f"| `{dataset}` | `{backend}` | {row['mean_sec']:.6f} | "
                f"{_format_optional_mean(bind_mean)} | {_format_optional_mean(reuse_mean)} |"
            )

    return "\n".join(lines).rstrip() + "\n"


def write_goal128_postgis_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal128_segment_polygon_anyhit_postgis_validation.json"
    md_path = output_root / "goal128_segment_polygon_anyhit_postgis_validation.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal128_postgis_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def write_goal128_linux_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal128_segment_polygon_anyhit_linux_large_perf.json"
    md_path = output_root / "goal128_segment_polygon_anyhit_linux_large_perf.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal128_linux_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

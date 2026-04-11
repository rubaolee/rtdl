from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path
from urllib.request import urlopen

from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference

from .baseline_contracts import compare_baseline_rows
from .datasets import load_natural_earth_populated_places_geojson
from .external_baselines import connect_postgis
from .external_baselines import prepare_postgis_point_tables
from .external_baselines import query_postgis_fixed_radius_neighbors
from .external_baselines import query_postgis_knn_rows
from .reference import Point
from .runtime import run_cpu
from .embree_runtime import run_embree
from .optix_runtime import run_optix
from .vulkan_runtime import run_vulkan


NATURAL_EARTH_POPULATED_PLACES_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
    "ne_10m_populated_places_simple.geojson"
)


def ensure_natural_earth_populated_places(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with urlopen(NATURAL_EARTH_POPULATED_PLACES_URL) as response:
            payload = response.read()
        target.write_bytes(payload)
    return target


def tile_points(
    points: tuple[Point, ...],
    *,
    copies: int,
    step_x: float,
    step_y: float,
) -> tuple[Point, ...]:
    tiled: list[Point] = []
    next_id = 1
    for copy_index in range(copies):
        dx = step_x * copy_index
        dy = step_y * copy_index
        for point in points:
            tiled.append(
                Point(
                    id=next_id,
                    x=point.x + dx,
                    y=point.y + dy,
                )
            )
            next_id += 1
    return tuple(tiled)


def build_real_world_case(
    base_points: tuple[Point, ...],
    *,
    copies: int,
    query_stride: int,
) -> dict[str, tuple[Point, ...]]:
    search_points = tile_points(
        base_points,
        copies=copies,
        step_x=720.0,
        step_y=360.0,
    )
    query_points = tuple(
        Point(id=point.id, x=point.x, y=point.y)
        for index, point in enumerate(search_points)
        if index % query_stride == 0
    )
    return {
        "query_points": query_points,
        "search_points": search_points,
    }


def run_backend(workload: str, backend: str, case: dict[str, tuple[Point, ...]]):
    if workload == "fixed_radius_neighbors":
        kernel = fixed_radius_neighbors_reference
    elif workload == "knn_rows":
        kernel = knn_rows_reference
    else:
        raise ValueError(f"unsupported workload `{workload}`")

    if backend == "cpu":
        return tuple(run_cpu(kernel, **case))
    if backend == "embree":
        return tuple(run_embree(kernel, **case))
    if backend == "optix":
        return tuple(run_optix(kernel, **case))
    if backend == "vulkan":
        return tuple(run_vulkan(kernel, **case))
    raise ValueError(f"unsupported runtime backend `{backend}`")


def ensure_postgis_extension(connection) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    finally:
        cursor.close()


def run_prepared_postgis(workload: str, connection):
    if workload == "fixed_radius_neighbors":
        return query_postgis_fixed_radius_neighbors(connection, radius=0.5, k_max=3)
    if workload == "knn_rows":
        return query_postgis_knn_rows(connection, k=3)
    raise ValueError(f"unsupported workload `{workload}`")


def time_runner(runner, *, min_seconds: float) -> tuple[tuple[dict[str, object], ...], list[float]]:
    durations_ms: list[float] = []
    rows = ()
    elapsed = 0.0
    while elapsed < min_seconds or not durations_ms:
        start = time.perf_counter()
        rows = tuple(runner())
        sample = (time.perf_counter() - start) * 1000.0
        durations_ms.append(sample)
        elapsed += sample / 1000.0
    return rows, durations_ms


def summarize_samples(samples_ms: list[float]) -> dict[str, float | int]:
    return {
        "iterations": len(samples_ms),
        "median_ms": round(statistics.median(samples_ms), 3),
        "min_ms": round(min(samples_ms), 3),
        "max_ms": round(max(samples_ms), 3),
        "total_ms": round(sum(samples_ms), 3),
    }


def compare_rows_against_postgis(
    workload: str,
    postgis_rows: tuple[dict[str, object], ...],
    candidate_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    if workload == "fixed_radius_neighbors":
        key_fields = ("query_id", "neighbor_id")
    elif workload == "knn_rows":
        key_fields = ("query_id", "neighbor_id", "neighbor_rank")
    else:
        raise ValueError(f"unsupported workload `{workload}`")

    same_length = len(postgis_rows) == len(candidate_rows)
    key_match = same_length
    distance_errors: list[float] = []
    if same_length:
        for expected, actual in zip(postgis_rows, candidate_rows):
            if tuple(expected[field] for field in key_fields) != tuple(actual[field] for field in key_fields):
                key_match = False
                break
            distance_errors.append(abs(float(expected["distance"]) - float(actual["distance"])))
    max_error = max(distance_errors) if distance_errors else None
    median_error = statistics.median(distance_errors) if distance_errors else None
    return {
        "same_length": same_length,
        "key_match": key_match,
        "distance_max_abs_error": None if max_error is None else round(max_error, 9),
        "distance_median_abs_error": None if median_error is None else round(median_error, 9),
        "distance_within_1e_4": False if max_error is None else max_error <= 1e-4,
        "strict_baseline_parity_ok": False if not same_length else compare_baseline_rows(workload, postgis_rows, candidate_rows),
    }


def run_case_benchmark(
    *,
    workload: str,
    case_name: str,
    case: dict[str, tuple[Point, ...]],
    min_seconds: float,
    postgis_dsn: str,
) -> dict[str, object]:
    connection = connect_postgis(postgis_dsn)
    try:
        ensure_postgis_extension(connection)
        prepare_postgis_point_tables(
            connection,
            case["query_points"],
            case["search_points"],
        )
        postgis_rows, postgis_samples = time_runner(
            lambda: run_prepared_postgis(workload, connection),
            min_seconds=min_seconds,
        )
        results = [
            {
                "backend": "postgis",
                "row_count": len(postgis_rows),
                "parity_ok": True,
                **summarize_samples(postgis_samples),
            }
        ]
        for backend in ("cpu", "embree", "optix", "vulkan"):
            rows, samples = time_runner(
                lambda backend_name=backend: run_backend(workload, backend_name, case),
                min_seconds=min_seconds,
            )
            parity = compare_rows_against_postgis(workload, postgis_rows, rows)
            results.append(
                {
                    "backend": backend,
                    "row_count": len(rows),
                    "parity_ok": bool(parity["same_length"] and parity["key_match"] and parity["distance_within_1e_4"]),
                    **parity,
                    **summarize_samples(samples),
                }
            )
        return {
            "workload": workload,
            "case": case_name,
            "query_count": len(case["query_points"]),
            "search_count": len(case["search_points"]),
            "postgis_ground_truth_rows": len(postgis_rows),
            "results": results,
        }
    finally:
        connection.close()


def run_heavy_benchmark(
    *,
    dataset_path: str | Path,
    min_seconds: float,
    postgis_dsn: str,
    fixed_radius_copies: int = 16,
    fixed_radius_query_stride: int = 4,
    knn_copies: int = 1,
    knn_query_stride: int = 16,
) -> dict[str, object]:
    dataset_file = ensure_natural_earth_populated_places(dataset_path)
    base_points = load_natural_earth_populated_places_geojson(dataset_file)
    fixed_case = build_real_world_case(
        base_points,
        copies=fixed_radius_copies,
        query_stride=fixed_radius_query_stride,
    )
    knn_case = build_real_world_case(
        base_points,
        copies=knn_copies,
        query_stride=knn_query_stride,
    )
    return {
        "note": "Heavy Linux v0.4 nearest-neighbor benchmark using Natural Earth populated places as a real-world-derived point corpus.",
        "dataset_url": NATURAL_EARTH_POPULATED_PLACES_URL,
        "dataset_path": str(dataset_file),
        "base_point_count": len(base_points),
        "min_seconds_per_backend": min_seconds,
        "workload_configs": {
            "fixed_radius_neighbors": {
                "copies": fixed_radius_copies,
                "query_stride": fixed_radius_query_stride,
            },
            "knn_rows": {
                "copies": knn_copies,
                "query_stride": knn_query_stride,
            },
        },
        "cases": [
            run_case_benchmark(
                workload="fixed_radius_neighbors",
                case_name="natural_earth_tiled",
                case=fixed_case,
                min_seconds=min_seconds,
                postgis_dsn=postgis_dsn,
            ),
            run_case_benchmark(
                workload="knn_rows",
                case_name="natural_earth_tiled",
                case=knn_case,
                min_seconds=min_seconds,
                postgis_dsn=postgis_dsn,
            ),
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 228 Heavy Linux v0.4 Nearest-Neighbor Benchmark",
        "",
        f"- Dataset URL: `{payload['dataset_url']}`",
        f"- Base points: `{payload['base_point_count']}`",
        f"- Min timed window per backend: `{payload['min_seconds_per_backend']}` seconds",
        f"- Fixed-radius workload size: `copies={payload['workload_configs']['fixed_radius_neighbors']['copies']}`, `query_stride={payload['workload_configs']['fixed_radius_neighbors']['query_stride']}`",
        f"- kNN workload size: `copies={payload['workload_configs']['knn_rows']['copies']}`, `query_stride={payload['workload_configs']['knn_rows']['query_stride']}`",
        "",
    ]
    for case in payload["cases"]:
        lines.extend(
            [
                f"## {case['workload']} / {case['case']}",
                "",
                f"- Query points: `{case['query_count']}`",
                f"- Search points: `{case['search_count']}`",
                f"- PostGIS ground-truth rows: `{case['postgis_ground_truth_rows']}`",
                "",
                "| Backend | Parity | Key Match | Max Abs Err | Rows | Iterations | Median ms | Min ms | Max ms | Total ms |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for result in case["results"]:
            lines.append(
                f"| {result['backend']} | {result['parity_ok']} | {result.get('key_match', True)} | {result.get('distance_max_abs_error', 'n/a')} | {result['row_count']} | {result['iterations']} | {result['median_ms']} | {result['min_ms']} | {result['max_ms']} | {result['total_ms']} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict[str, object], output_dir: str | Path) -> tuple[Path, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / "summary.json"
    md_path = target_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def default_postgis_dsn() -> str:
    return os.environ.get("RTDL_POSTGIS_DSN", "dbname=postgres")

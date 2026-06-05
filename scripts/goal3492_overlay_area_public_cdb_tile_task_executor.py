from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from goal3474_shape_pair_exact_overlay_area_shapely_oracle import (  # noqa: E402
    _build_oracle_polygon,
    _build_oracle_polygons,
    _claim_boundary,
    _import_shapely,
)
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
import rtdsl as rt  # noqa: E402
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _exterior_vertices(polygon: Any) -> tuple[tuple[float, float], ...]:
    coords = tuple((float(x), float(y)) for x, y in polygon.exterior.coords)
    if len(coords) >= 2 and coords[0] == coords[-1]:
        return coords[:-1]
    return coords


def _component_vertices_for_prepared_geometry(geometry: Any) -> tuple[str, tuple[tuple[tuple[float, float], ...], ...]]:
    geom_type = str(getattr(geometry, "geom_type", "unknown"))
    if getattr(geometry, "is_empty", False):
        return "unsupported_empty", ()
    if geom_type == "Polygon":
        parts = (geometry,)
    elif geom_type == "MultiPolygon":
        parts = tuple(geometry.geoms)
    else:
        return f"unsupported_geometry_type_{geom_type}", ()

    component_vertices: list[tuple[tuple[float, float], ...]] = []
    for part in parts:
        if len(part.interiors) != 0:
            return "unsupported_holes", tuple(component_vertices)
        vertices = _exterior_vertices(part)
        try:
            triangulate_simple_polygon_ear_clip(vertices)
        except Exception:
            return "unsupported_triangulation_failed", tuple(component_vertices)
        component_vertices.append(vertices)
    return "prepared_simple_components", tuple(component_vertices)


def _add_count(counts: dict[str, int], key: str, value: int = 1) -> None:
    counts[key] = counts.get(key, 0) + int(value)


def _prepare_payload_from_geometries(
    geometries: tuple[Any, ...],
) -> tuple[rt.PreparedSimplePolygonComponentPayload, dict[int, tuple[int, ...]], dict[str, int]]:
    return _prepare_payload_from_geometry_map(dict(enumerate(geometries)))


def _prepare_payload_from_geometry_map(
    geometries: dict[int, Any],
) -> tuple[rt.PreparedSimplePolygonComponentPayload, dict[int, tuple[int, ...]], dict[str, int]]:
    components: list[tuple[tuple[float, float], ...]] = []
    source_shape_ids: list[int] = []
    shape_to_components: dict[int, tuple[int, ...]] = {}
    status_counts: dict[str, int] = {}
    for shape_ordinal, geometry in sorted(geometries.items()):
        status, component_vertices = _component_vertices_for_prepared_geometry(geometry)
        _add_count(status_counts, status)
        component_ordinals: list[int] = []
        if status == "prepared_simple_components":
            for vertices in component_vertices:
                component_ordinals.append(len(components))
                components.append(vertices)
                source_shape_ids.append(shape_ordinal)
        shape_to_components[shape_ordinal] = tuple(component_ordinals)
    payload = rt.prepare_simple_polygon_component_payload(components, source_shape_ids=source_shape_ids)
    return payload, shape_to_components, status_counts


def _build_oracle_geometry_map(
    records: tuple[Any, ...],
    shape_ordinals: set[int],
    ShapelyPolygon: Any,
    make_valid: Any,
) -> tuple[dict[int, Any], dict[str, int]]:
    geometries: dict[int, Any] = {}
    status_counts: dict[str, int] = {}
    for shape_ordinal in sorted(shape_ordinals):
        geometry, status = _build_oracle_polygon(records[shape_ordinal], ShapelyPolygon, make_valid)
        geometries[shape_ordinal] = geometry
        _add_count(status_counts, status)
    return geometries, status_counts


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return float(ordered[index])


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    print("[goal3492] load CDB", flush=True)
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))

    print("[goal3492] discover active relation ordinals with RTDL/OptiX", flush=True)
    discovery_start = time.perf_counter()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3492 public-CDB prepared tile-task executor over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
            cp.cuda.Stream.null.synchronize()
            ordinals = columns.as_cupy_ordinal_columns()
            left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
            right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)
    relation_discovery_sec = time.perf_counter() - discovery_start

    if args.active_shapes_only:
        left_shapes_to_build = set(map(int, left_ordinals))
        right_shapes_to_build = set(map(int, right_ordinals))
    else:
        left_shapes_to_build = set(range(len(left_shapes)))
        right_shapes_to_build = set(range(len(right_shapes)))

    print(
        "[goal3492] build Shapely oracle geometries "
        f"(left={len(left_shapes_to_build)}/{len(left_shapes)}, right={len(right_shapes_to_build)}/{len(right_shapes)})",
        flush=True,
    )
    build_start = time.perf_counter()
    if args.active_shapes_only:
        left_geometry_map, left_geometry_status = _build_oracle_geometry_map(
            left_shapes, left_shapes_to_build, ShapelyPolygon, make_valid
        )
        right_geometry_map, right_geometry_status = _build_oracle_geometry_map(
            right_shapes, right_shapes_to_build, ShapelyPolygon, make_valid
        )
    else:
        left_geometries, left_geometry_status = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
        right_geometries, right_geometry_status = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
        left_geometry_map = dict(enumerate(left_geometries))
        right_geometry_map = dict(enumerate(right_geometries))
    geometry_build_sec = time.perf_counter() - build_start

    print("[goal3492] prepare simple-polygon component payloads", flush=True)
    payload_start = time.perf_counter()
    left_payload, left_shape_components, left_prepared_status = _prepare_payload_from_geometry_map(left_geometry_map)
    right_payload, right_shape_components, right_prepared_status = _prepare_payload_from_geometry_map(right_geometry_map)
    payload_build_sec = time.perf_counter() - payload_start

    print(f"[goal3492] build exact oracle areas for {len(left_ordinals)} rows", flush=True)
    exact_start = time.perf_counter()
    exact_areas: list[float] = []
    for index, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        if int(args.progress_every) > 0 and index > 0 and index % int(args.progress_every) == 0:
            print(f"[goal3492] exact rows={index}/{len(left_ordinals)}", flush=True)
        exact_areas.append(
            float(left_geometry_map[int(left_ordinal)].intersection(right_geometry_map[int(right_ordinal)]).area)
        )
    exact_oracle_sec = time.perf_counter() - exact_start

    print("[goal3492] expand component pairs and tile tasks", flush=True)
    plan_start = time.perf_counter()
    component_pairs: list[tuple[int, int]] = []
    relation_row_ordinals: list[int] = []
    unsupported_rows = 0
    unsupported_positive_rows = 0
    for relation_row, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        left_components = left_shape_components.get(int(left_ordinal), ())
        right_components = right_shape_components.get(int(right_ordinal), ())
        if not left_components or not right_components:
            unsupported_rows += 1
            if exact_areas[relation_row] > rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE:
                unsupported_positive_rows += 1
            continue
        for left_component in left_components:
            for right_component in right_components:
                component_pairs.append((left_component, right_component))
                relation_row_ordinals.append(relation_row)
    pair_rows = rt.prepare_overlay_area_pair_rows(left_payload, right_payload, component_pairs)
    tasks = rt.plan_prepared_overlay_area_tile_tasks(
        pair_rows,
        max_triangle_pairs_per_task=int(args.max_triangle_pairs_per_task),
        relation_row_ordinals=relation_row_ordinals,
    )
    task_summary = rt.summarize_prepared_overlay_area_tile_tasks(pair_rows, tasks)
    planning_sec = time.perf_counter() - plan_start

    print(f"[goal3492] execute {len(tasks)} tile tasks over {len(pair_rows)} component-pair rows", flush=True)
    cp.cuda.Stream.null.synchronize()
    input_prepare_sec = 0.0
    executor_repeats = max(1, int(args.executor_repeats))
    executor_repeat_secs: list[float] = []
    if args.resident_cupy_inputs:
        input_prepare_start = time.perf_counter()
        resident_inputs = rt.prepare_overlay_area_tile_task_cupy_inputs(
            left_payload,
            right_payload,
            tasks,
            relation_row_count=len(left_ordinals),
        )
        cp.cuda.Stream.null.synchronize()
        input_prepare_sec = time.perf_counter() - input_prepare_start
        result = None
        for repeat in range(executor_repeats):
            print(f"[goal3492] resident executor repeat {repeat + 1}/{executor_repeats}", flush=True)
            execute_start = time.perf_counter()
            result = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(resident_inputs)
            cp.cuda.Stream.null.synchronize()
            executor_repeat_secs.append(time.perf_counter() - execute_start)
        assert result is not None
        executor_sec = sum(executor_repeat_secs)
    else:
        execute_start = time.perf_counter()
        result = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(
            left_payload,
            right_payload,
            tasks,
            relation_row_count=len(left_ordinals),
        )
        cp.cuda.Stream.null.synchronize()
        executor_sec = time.perf_counter() - execute_start
        executor_repeat_secs.append(executor_sec)
    relation_areas = cp.asnumpy(result.relation_areas).astype("float64", copy=False)
    metadata = result.to_metadata()

    errors = [abs(float(observed) - float(expected)) for observed, expected in zip(relation_areas, exact_areas)]
    max_abs_error = max(errors, default=0.0)
    total_observed_area = float(relation_areas.sum())
    total_exact_area = float(sum(exact_areas))
    positive_threshold = rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE
    observed_positive_rows = int(sum(1 for area in relation_areas if float(area) > positive_threshold))
    exact_positive_rows = int(sum(1 for area in exact_areas if float(area) > positive_threshold))
    largest_error_rows = sorted(
        (
            {
                "relation_row": int(row),
                "left_ordinal": int(left_ordinals[row]),
                "right_ordinal": int(right_ordinals[row]),
                "observed_area": float(relation_areas[row]),
                "exact_area": float(exact_areas[row]),
                "abs_error": float(errors[row]),
            }
            for row in range(len(errors))
        ),
        key=lambda item: item["abs_error"],
        reverse=True,
    )[:10]

    schema = (
        "rtdl.goal3493.overlay_area_active_shape_payload_construction.v1"
        if args.active_shapes_only
        else "rtdl.goal3492.overlay_area_public_cdb_tile_task_executor.v1"
    )
    goal = 3493 if args.active_shapes_only else 3492

    return {
        "schema": schema,
        "goal": goal,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "shapely_version": shapely_version,
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "active_shapes_only": bool(args.active_shapes_only),
        "max_rows": int(args.max_rows),
        "max_triangle_pairs_per_task": int(args.max_triangle_pairs_per_task),
        "resident_cupy_inputs": bool(args.resident_cupy_inputs),
        "executor_repeats": executor_repeats,
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "prepared_left_shape_count": len(left_geometry_map),
        "prepared_right_shape_count": len(right_geometry_map),
        "left_geometry_status_counts": left_geometry_status,
        "right_geometry_status_counts": right_geometry_status,
        "left_prepared_status_counts": left_prepared_status,
        "right_prepared_status_counts": right_prepared_status,
        "left_payload_triangle_count": left_payload.triangle_count,
        "right_payload_triangle_count": right_payload.triangle_count,
        "relation_row_count": int(len(left_ordinals)),
        "supported_relation_row_count": int(len(left_ordinals) - unsupported_rows),
        "unsupported_relation_row_count": unsupported_rows,
        "unsupported_positive_relation_row_count": unsupported_positive_rows,
        "component_pair_row_count": len(pair_rows),
        "tile_task_count": len(tasks),
        "planned_triangle_pair_count": int(task_summary["planned_triangle_pair_count"]),
        "expected_triangle_pair_count": int(task_summary["expected_triangle_pair_count"]),
        "task_summary": task_summary,
        "executor_metadata": metadata,
        "observed_total_area": total_observed_area,
        "exact_total_area": total_exact_area,
        "total_area_abs_error": abs(total_observed_area - total_exact_area),
        "observed_positive_row_count": observed_positive_rows,
        "exact_positive_row_count": exact_positive_rows,
        "positive_row_count_match": observed_positive_rows == exact_positive_rows,
        "max_relation_abs_error": max_abs_error,
        "relation_abs_error_percentiles": {
            "p50": _percentile(errors, 0.50),
            "p90": _percentile(errors, 0.90),
            "p99": _percentile(errors, 0.99),
        },
        "largest_error_rows": largest_error_rows,
        "timing_sec": {
            "geometry_build": geometry_build_sec,
            "payload_build": payload_build_sec,
            "relation_discovery": relation_discovery_sec,
            "exact_oracle": exact_oracle_sec,
            "planning": planning_sec,
            "cupy_tile_task_input_prepare": input_prepare_sec,
            "cupy_tile_task_executor": executor_sec,
            "cupy_tile_task_executor_repeat_secs": executor_repeat_secs,
            "cupy_tile_task_executor_best_repeat": min(executor_repeat_secs) if executor_repeat_secs else 0.0,
        },
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "Executes the prepared simple-polygon overlay-area tile-task plan over the public-CDB "
            "active relation stream and compares scalar relation areas with the external Shapely/GEOS oracle."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3492 public-CDB prepared tile-task overlay-area executor.")
    parser.add_argument("--left-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--max-triangle-pairs-per-task", type=int, default=512)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--resident-cupy-inputs", action="store_true")
    parser.add_argument("--executor-repeats", type=int, default=1)
    parser.add_argument(
        "--active-shapes-only",
        action="store_true",
        help="Prepare only shapes referenced by the active relation stream instead of the whole CDB.",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

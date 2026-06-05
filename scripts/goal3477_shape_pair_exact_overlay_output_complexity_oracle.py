from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from goal3474_shape_pair_exact_overlay_area_shapely_oracle import (  # noqa: E402
    _build_oracle_polygons,
    _claim_boundary,
    _import_shapely,
)
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def _add_count(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1


def _geometry_complexity(geometry) -> dict[str, int]:
    geom_type = str(getattr(geometry, "geom_type", "unknown"))
    if getattr(geometry, "is_empty", False):
        return {
            "polygon_components": 0,
            "line_components": 0,
            "point_components": 0,
            "total_output_vertices": 0,
        }
    if geom_type == "Polygon":
        exterior = len(geometry.exterior.coords) - 1
        holes = sum(len(ring.coords) - 1 for ring in geometry.interiors)
        return {
            "polygon_components": 1,
            "line_components": 0,
            "point_components": 0,
            "total_output_vertices": int(exterior + holes),
        }
    if geom_type == "MultiPolygon":
        result = {
            "polygon_components": 0,
            "line_components": 0,
            "point_components": 0,
            "total_output_vertices": 0,
        }
        for part in geometry.geoms:
            child = _geometry_complexity(part)
            for key, value in child.items():
                result[key] += int(value)
        return result
    if geom_type == "LineString":
        return {
            "polygon_components": 0,
            "line_components": 1,
            "point_components": 0,
            "total_output_vertices": max(0, len(geometry.coords)),
        }
    if geom_type == "MultiLineString":
        return {
            "polygon_components": 0,
            "line_components": len(geometry.geoms),
            "point_components": 0,
            "total_output_vertices": sum(len(part.coords) for part in geometry.geoms),
        }
    if geom_type == "Point":
        return {
            "polygon_components": 0,
            "line_components": 0,
            "point_components": 1,
            "total_output_vertices": 1,
        }
    if geom_type == "MultiPoint":
        return {
            "polygon_components": 0,
            "line_components": 0,
            "point_components": len(geometry.geoms),
            "total_output_vertices": len(geometry.geoms),
        }
    if geom_type == "GeometryCollection":
        result = {
            "polygon_components": 0,
            "line_components": 0,
            "point_components": 0,
            "total_output_vertices": 0,
        }
        for part in geometry.geoms:
            child = _geometry_complexity(part)
            for key, value in child.items():
                result[key] += int(value)
        return result
    return {
        "polygon_components": 0,
        "line_components": 0,
        "point_components": 0,
        "total_output_vertices": 0,
    }


def _compute_output_complexity(
    *,
    left_geometries,
    right_geometries,
    left_ordinals,
    right_ordinals,
    progress_every: int,
) -> dict[str, object]:
    row_count = int(len(left_ordinals))
    geometry_type_counts: dict[str, int] = {}
    positive_geometry_type_counts: dict[str, int] = {}
    empty_rows = 0
    boundary_only_rows = 0
    positive_rows = 0
    exception_count = 0
    total_area = 0.0
    max_area = 0.0
    total_polygon_components = 0
    max_polygon_components = 0
    total_output_vertices = 0
    max_output_vertices = 0
    max_complexity_samples: list[dict[str, object]] = []
    started = time.perf_counter()

    for index, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        if progress_every > 0 and index > 0 and index % progress_every == 0:
            elapsed = time.perf_counter() - started
            print(f"[goal3477] exact_output_rows={index}/{row_count} elapsed={elapsed:.3f}s", flush=True)
        try:
            intersection = left_geometries[int(left_ordinal)].intersection(right_geometries[int(right_ordinal)])
            area = float(intersection.area)
        except Exception as exc:  # pragma: no cover - captured in pod artifacts
            exception_count += 1
            if len(max_complexity_samples) < 8:
                max_complexity_samples.append(
                    {
                        "row": int(index),
                        "left_ordinal": int(left_ordinal),
                        "right_ordinal": int(right_ordinal),
                        "exception": f"{type(exc).__name__}: {exc}",
                    }
                )
            continue

        geom_type = str(intersection.geom_type)
        _add_count(geometry_type_counts, geom_type)
        complexity = _geometry_complexity(intersection)
        polygon_components = int(complexity["polygon_components"])
        output_vertices = int(complexity["total_output_vertices"])
        total_polygon_components += polygon_components
        total_output_vertices += output_vertices
        if output_vertices > max_output_vertices:
            max_complexity_samples = []
        max_polygon_components = max(max_polygon_components, polygon_components)
        max_output_vertices = max(max_output_vertices, output_vertices)
        total_area += area
        max_area = max(max_area, area)

        if area > 0.0:
            positive_rows += 1
            _add_count(positive_geometry_type_counts, geom_type)
        elif intersection.is_empty:
            empty_rows += 1
        else:
            boundary_only_rows += 1

        if output_vertices == max_output_vertices and output_vertices > 0 and len(max_complexity_samples) < 8:
            max_complexity_samples.append(
                {
                    "row": int(index),
                    "left_ordinal": int(left_ordinal),
                    "right_ordinal": int(right_ordinal),
                    "geometry_type": geom_type,
                    "area": area,
                    "polygon_components": polygon_components,
                    "total_output_vertices": output_vertices,
                }
            )

    return {
        "row_count": row_count,
        "positive_area_row_count": positive_rows,
        "empty_row_count": empty_rows,
        "boundary_only_row_count": boundary_only_rows,
        "exception_count": exception_count,
        "total_exact_area": total_area,
        "max_row_area": max_area,
        "geometry_type_counts": geometry_type_counts,
        "positive_geometry_type_counts": positive_geometry_type_counts,
        "total_polygon_components": total_polygon_components,
        "max_polygon_components_per_row": max_polygon_components,
        "total_output_vertices": total_output_vertices,
        "max_output_vertices_per_row": max_output_vertices,
        "max_complexity_samples": max_complexity_samples,
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    build_start = time.perf_counter()
    left_geometries, left_geometry_status = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
    right_geometries, right_geometry_status = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
    geometry_build_sec = time.perf_counter() - build_start

    relation_times: list[float] = []
    copy_times: list[float] = []
    oracle_times: list[float] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3477 exact overlay output-complexity oracle over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            relation_start = time.perf_counter()
            with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
                cp.cuda.Stream.null.synchronize()
                relation_sec = time.perf_counter() - relation_start
                copy_start = time.perf_counter()
                ordinals = columns.as_cupy_ordinal_columns()
                left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
                right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)
                cp.cuda.Stream.null.synchronize()
                copy_sec = time.perf_counter() - copy_start

            oracle_start = time.perf_counter()
            complexity = _compute_output_complexity(
                left_geometries=left_geometries,
                right_geometries=right_geometries,
                left_ordinals=left_ordinals,
                right_ordinals=right_ordinals,
                progress_every=int(args.progress_every),
            )
            oracle_sec = time.perf_counter() - oracle_start
            relation_times.append(relation_sec)
            copy_times.append(copy_sec)
            oracle_times.append(oracle_sec)
            runs.append(
                {
                    "iteration": index,
                    "relation_columns_sec": relation_sec,
                    "ordinal_copy_to_host_sec": copy_sec,
                    "shapely_output_complexity_oracle_sec": oracle_sec,
                    "complexity": complexity,
                    "claim_boundary": _claim_boundary(),
                }
            )
            print(
                "[goal3477] "
                f"iteration={index} rows={complexity['row_count']} positive={complexity['positive_area_row_count']} "
                f"empty={complexity['empty_row_count']} boundary_only={complexity['boundary_only_row_count']} "
                f"types={complexity['geometry_type_counts']} "
                f"max_components={complexity['max_polygon_components_per_row']} "
                f"max_vertices={complexity['max_output_vertices_per_row']} "
                f"oracle={oracle_sec:.6f}s",
                flush=True,
            )

    first = runs[0]["complexity"] if runs else {}
    return {
        "schema": "rtdl.goal3477.shape_pair_exact_overlay_output_complexity_oracle.v1",
        "goal": 3477,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "shapely_version": shapely_version,
        "oracle_dependency_scope": "external_cpu_output_complexity_oracle_not_rtdl_runtime_dependency",
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "left_geometry_status_counts": left_geometry_status,
        "right_geometry_status_counts": right_geometry_status,
        "geometry_build_sec": geometry_build_sec,
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "first_run_complexity": first,
        "relation_columns_sec": _stats(relation_times),
        "ordinal_copy_to_host_sec": _stats(copy_times),
        "shapely_output_complexity_oracle_sec": _stats(oracle_times),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3477 Shapely output-complexity oracle over RTDL relation rows.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    complexity = payload["first_run_complexity"]
    if int(complexity.get("exception_count", 1)) != 0:
        raise SystemExit(1)
    if int(complexity.get("positive_area_row_count", 0)) <= 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

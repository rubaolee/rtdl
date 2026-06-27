from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from goal3474_shape_pair_exact_overlay_area_shapely_oracle import (  # noqa: E402
    _build_oracle_polygons,
    _claim_boundary,
    _import_shapely,
)
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _add(counts: dict[str, int], key: str, value: int = 1) -> None:
    counts[key] = counts.get(key, 0) + int(value)


def _exterior_vertices(polygon) -> tuple[tuple[float, float], ...]:
    coords = tuple((float(x), float(y)) for x, y in polygon.exterior.coords)
    if len(coords) >= 2 and coords[0] == coords[-1]:
        return coords[:-1]
    return coords


def _classify_prepared_components(geometry) -> dict[str, object]:
    geom_type = str(getattr(geometry, "geom_type", "unknown"))
    if getattr(geometry, "is_empty", False):
        return {"status": "unsupported_empty", "component_count": 0, "triangle_count": 0, "geom_type": geom_type}
    if geom_type == "Polygon":
        parts = (geometry,)
    elif geom_type == "MultiPolygon":
        parts = tuple(geometry.geoms)
    else:
        return {
            "status": f"unsupported_geometry_type_{geom_type}",
            "component_count": 0,
            "triangle_count": 0,
            "geom_type": geom_type,
        }

    component_count = 0
    triangle_count = 0
    max_vertices = 0
    for part in parts:
        if len(part.interiors) != 0:
            return {
                "status": "unsupported_holes",
                "component_count": component_count,
                "triangle_count": triangle_count,
                "geom_type": geom_type,
            }
        vertices = _exterior_vertices(part)
        try:
            triangles = triangulate_simple_polygon_ear_clip(vertices)
        except Exception:
            return {
                "status": "unsupported_triangulation_failed",
                "component_count": component_count,
                "triangle_count": triangle_count,
                "geom_type": geom_type,
            }
        component_count += 1
        triangle_count += len(triangles)
        max_vertices = max(max_vertices, len(vertices))
    return {
        "status": "prepared_simple_components",
        "component_count": component_count,
        "triangle_count": triangle_count,
        "max_vertices_per_component": max_vertices,
        "geom_type": geom_type,
    }


def _summarize_geometries(geometries) -> tuple[tuple[dict[str, object], ...], dict[str, int]]:
    summaries: list[dict[str, object]] = []
    status_counts: dict[str, int] = {}
    for geometry in geometries:
        summary = _classify_prepared_components(geometry)
        summaries.append(summary)
        _add(status_counts, str(summary["status"]))
    return tuple(summaries), status_counts


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    build_start = time.perf_counter()
    left_geometries, left_geometry_status = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
    right_geometries, right_geometry_status = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
    left_prepared, left_prepared_status = _summarize_geometries(left_geometries)
    right_prepared, right_prepared_status = _summarize_geometries(right_geometries)
    geometry_build_sec = time.perf_counter() - build_start

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3488 prepared-payload feasibility probe over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
            cp.cuda.Stream.null.synchronize()
            ordinals = columns.as_cupy_ordinal_columns()
            left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
            right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)

    row_count = int(len(left_ordinals))
    supported_rows = 0
    unsupported_reason_counts: dict[str, int] = {}
    supported_positive_rows = 0
    supported_total_area = 0.0
    all_positive_rows = 0
    all_total_area = 0.0
    max_supported_triangle_pairs = 0
    samples: list[dict[str, object]] = []
    started = time.perf_counter()
    for index, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        if int(args.progress_every) > 0 and index > 0 and index % int(args.progress_every) == 0:
            print(f"[goal3488] rows={index}/{row_count} elapsed={time.perf_counter() - started:.3f}s", flush=True)
        left_summary = left_prepared[int(left_ordinal)]
        right_summary = right_prepared[int(right_ordinal)]
        area = float(left_geometries[int(left_ordinal)].intersection(right_geometries[int(right_ordinal)]).area)
        all_total_area += area
        if area > 0.0:
            all_positive_rows += 1
        if left_summary["status"] == "prepared_simple_components" and right_summary["status"] == "prepared_simple_components":
            supported_rows += 1
            supported_total_area += area
            if area > 0.0:
                supported_positive_rows += 1
            max_supported_triangle_pairs = max(
                max_supported_triangle_pairs,
                int(left_summary["triangle_count"]) * int(right_summary["triangle_count"]),
            )
        else:
            reason = f"left={left_summary['status']}|right={right_summary['status']}"
            _add(unsupported_reason_counts, reason)
            if len(samples) < 12:
                samples.append(
                    {
                        "row": int(index),
                        "left_ordinal": int(left_ordinal),
                        "right_ordinal": int(right_ordinal),
                        "left_status": left_summary,
                        "right_status": right_summary,
                        "area": area,
                    }
                )

    return {
        "schema": "rtdl.goal3488.overlay_area_prepared_payload_feasibility.v1",
        "goal": 3488,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "shapely_version": shapely_version,
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "left_geometry_status_counts": left_geometry_status,
        "right_geometry_status_counts": right_geometry_status,
        "left_prepared_status_counts": left_prepared_status,
        "right_prepared_status_counts": right_prepared_status,
        "geometry_build_and_classify_sec": geometry_build_sec,
        "row_count": row_count,
        "supported_prepared_payload_row_count": supported_rows,
        "unsupported_prepared_payload_row_count": row_count - supported_rows,
        "supported_positive_area_row_count": supported_positive_rows,
        "all_positive_area_row_count": all_positive_rows,
        "supported_total_exact_area": supported_total_area,
        "all_total_exact_area": all_total_area,
        "supported_area_fraction": supported_total_area / all_total_area if all_total_area else 0.0,
        "supported_positive_row_fraction": supported_positive_rows / all_positive_rows if all_positive_rows else 0.0,
        "max_supported_triangle_pairs_per_row": max_supported_triangle_pairs,
        "unsupported_reason_counts": unsupported_reason_counts,
        "unsupported_samples": samples,
        "interpretation": (
            "Measures how much of the public-CDB active relation stream can be lowered to the "
            "current no-hole prepared simple polygon component payload before adding hole/full "
            "topology support."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3488 prepared-payload feasibility over public CDB relation rows.")
    parser.add_argument("--left-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--progress-every", type=int, default=500)
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

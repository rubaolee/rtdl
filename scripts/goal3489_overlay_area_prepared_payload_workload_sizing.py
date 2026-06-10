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
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
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


def _exterior_vertices(polygon) -> tuple[tuple[float, float], ...]:
    coords = tuple((float(x), float(y)) for x, y in polygon.exterior.coords)
    if len(coords) >= 2 and coords[0] == coords[-1]:
        return coords[:-1]
    return coords


def _component_triangle_counts(geometry) -> tuple[str, tuple[int, ...]]:
    geom_type = str(getattr(geometry, "geom_type", "unknown"))
    if getattr(geometry, "is_empty", False):
        return "unsupported_empty", ()
    if geom_type == "Polygon":
        parts = (geometry,)
    elif geom_type == "MultiPolygon":
        parts = tuple(geometry.geoms)
    else:
        return f"unsupported_geometry_type_{geom_type}", ()
    counts: list[int] = []
    for part in parts:
        if len(part.interiors) != 0:
            return "unsupported_holes", tuple(counts)
        try:
            counts.append(len(triangulate_simple_polygon_ear_clip(_exterior_vertices(part))))
        except Exception:
            return "unsupported_triangulation_failed", tuple(counts)
    return "prepared_simple_components", tuple(counts)


def _percentile(values: list[int], q: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return int(ordered[index])


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    build_start = time.perf_counter()
    left_geometries, _ = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
    right_geometries, _ = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
    left_counts = tuple(_component_triangle_counts(geometry) for geometry in left_geometries)
    right_counts = tuple(_component_triangle_counts(geometry) for geometry in right_geometries)
    build_sec = time.perf_counter() - build_start

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3489 prepared-payload workload sizing over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
            cp.cuda.Stream.null.synchronize()
            ordinals = columns.as_cupy_ordinal_columns()
            left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
            right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)

    supported_rows = 0
    unsupported_rows = 0
    total_component_pair_rows = 0
    total_triangle_pairs = 0
    max_component_pair_rows = 0
    max_triangle_pairs = 0
    triangle_pair_values: list[int] = []
    component_pair_values: list[int] = []
    unsupported_reason_counts: dict[str, int] = {}
    max_samples: list[dict[str, object]] = []
    for row, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        left_status, left_triangles = left_counts[int(left_ordinal)]
        right_status, right_triangles = right_counts[int(right_ordinal)]
        if left_status != "prepared_simple_components" or right_status != "prepared_simple_components":
            unsupported_rows += 1
            reason = f"left={left_status}|right={right_status}"
            unsupported_reason_counts[reason] = unsupported_reason_counts.get(reason, 0) + 1
            continue
        supported_rows += 1
        component_pair_count = len(left_triangles) * len(right_triangles)
        triangle_pair_count = sum(left_triangles) * sum(right_triangles)
        total_component_pair_rows += component_pair_count
        total_triangle_pairs += triangle_pair_count
        component_pair_values.append(component_pair_count)
        triangle_pair_values.append(triangle_pair_count)
        if triangle_pair_count > max_triangle_pairs:
            max_samples = []
        max_component_pair_rows = max(max_component_pair_rows, component_pair_count)
        max_triangle_pairs = max(max_triangle_pairs, triangle_pair_count)
        if triangle_pair_count == max_triangle_pairs and len(max_samples) < 8:
            max_samples.append(
                {
                    "row": int(row),
                    "left_ordinal": int(left_ordinal),
                    "right_ordinal": int(right_ordinal),
                    "left_component_count": len(left_triangles),
                    "right_component_count": len(right_triangles),
                    "left_triangle_count": sum(left_triangles),
                    "right_triangle_count": sum(right_triangles),
                    "component_pair_count": component_pair_count,
                    "triangle_pair_count": triangle_pair_count,
                }
            )

    return {
        "schema": "rtdl.goal3489.overlay_area_prepared_payload_workload_sizing.v1",
        "goal": 3489,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "shapely_version": shapely_version,
        "geometry_build_and_classify_sec": build_sec,
        "row_count": int(len(left_ordinals)),
        "supported_row_count": supported_rows,
        "unsupported_row_count": unsupported_rows,
        "total_component_pair_rows": total_component_pair_rows,
        "total_triangle_pairs": total_triangle_pairs,
        "max_component_pair_rows_per_relation": max_component_pair_rows,
        "max_triangle_pairs_per_relation": max_triangle_pairs,
        "triangle_pairs_per_relation_percentiles": {
            "p50": _percentile(triangle_pair_values, 0.50),
            "p90": _percentile(triangle_pair_values, 0.90),
            "p99": _percentile(triangle_pair_values, 0.99),
        },
        "component_pairs_per_relation_percentiles": {
            "p50": _percentile(component_pair_values, 0.50),
            "p90": _percentile(component_pair_values, 0.90),
            "p99": _percentile(component_pair_values, 0.99),
        },
        "unsupported_reason_counts": unsupported_reason_counts,
        "max_triangle_pair_samples": max_samples,
        "interpretation": (
            "Measures the component-pair and triangle-pair expansion that the exact scalar overlay "
            "continuation must process after public-CDB relation discovery."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3489 prepared-payload workload sizing over public CDB rows.")
    parser.add_argument("--left-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=65536)
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

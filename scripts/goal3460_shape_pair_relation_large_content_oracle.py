from __future__ import annotations

import argparse
import ctypes
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


@dataclass(frozen=True)
class _PolyView:
    ordinal: int
    polygon_id: int
    vertices: tuple[tuple[float, float], ...]
    bounds: tuple[float, float, float, float]


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def _f32(value: float) -> float:
    return ctypes.c_float(float(value)).value


def _bounds(vertices: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in vertices]
    ys = [point[1] for point in vertices]
    return min(xs), min(ys), max(xs), max(ys)


def _views(polygons: tuple[rt.Polygon, ...]) -> tuple[_PolyView, ...]:
    views = []
    for index, polygon in enumerate(polygons):
        vertices = tuple((_f32(x), _f32(y)) for x, y in polygon.vertices)
        views.append(
            _PolyView(
                ordinal=index,
                polygon_id=int(polygon.id),
                vertices=vertices,
                bounds=_bounds(vertices),
            )
        )
    return tuple(views)


def _bounds_overlap(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> bool:
    return not (left[2] < right[0] or right[2] < left[0] or left[3] < right[1] or right[3] < left[1])


def _segment_intersection_flag(
    ax0: float,
    ay0: float,
    ax1: float,
    ay1: float,
    bx0: float,
    by0: float,
    bx1: float,
    by1: float,
) -> bool:
    ax0 = _f32(ax0)
    ay0 = _f32(ay0)
    ax1 = _f32(ax1)
    ay1 = _f32(ay1)
    bx0 = _f32(bx0)
    by0 = _f32(by0)
    bx1 = _f32(bx1)
    by1 = _f32(by1)
    rx = _f32(ax1 - ax0)
    ry = _f32(ay1 - ay0)
    sx = _f32(bx1 - bx0)
    sy = _f32(by1 - by0)
    denom = _f32(_f32(rx * sy) - _f32(ry * sx))
    if abs(denom) < 1.0e-7:
        return False
    qpx = _f32(bx0 - ax0)
    qpy = _f32(by0 - ay0)
    t = _f32(_f32(_f32(qpx * sy) - _f32(qpy * sx)) / denom)
    u = _f32(_f32(_f32(qpx * ry) - _f32(qpy * rx)) / denom)
    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def _point_on_segment(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
) -> bool:
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    if abs(cross) > 1.0e-5:
        return False
    min_x = ax if ax < bx else bx
    max_x = ax if ax > bx else bx
    min_y = ay if ay < by else by
    max_y = ay if ay > by else by
    return px >= min_x - 1.0e-5 and px <= max_x + 1.0e-5 and py >= min_y - 1.0e-5 and py <= max_y + 1.0e-5


def _point_in_polygon_inclusive(
    px: float,
    py: float,
    polygon: _PolyView,
) -> bool:
    vertices = polygon.vertices
    if not vertices:
        return False
    for index, (xi, yi) in enumerate(vertices):
        xj, yj = vertices[index - 1]
        if _point_on_segment(px, py, xi, yi, xj, yj):
            return True
    inside = False
    for index, (xi, yi) in enumerate(vertices):
        xj, yj = vertices[index - 1]
        if ((yi > py) != (yj > py)) and (
            px <= (xj - xi) * (py - yi) / ((yj - yi) if (yj - yi) != 0.0 else 1.0e-20) + xi
        ):
            inside = not inside
    return inside


def _point_inside_bounds(
    bounds: tuple[float, float, float, float],
    x: float,
    y: float,
) -> bool:
    return x >= bounds[0] - 1.0e-6 and x <= bounds[2] + 1.0e-6 and y >= bounds[1] - 1.0e-6 and y <= bounds[3] + 1.0e-6


def _edge_pairs_intersect(left: _PolyView, right: _PolyView) -> bool:
    left_vertices = left.vertices
    right_vertices = right.vertices
    for left_index, (ax0, ay0) in enumerate(left_vertices):
        ax1, ay1 = left_vertices[(left_index + 1) % len(left_vertices)]
        for right_index, (bx0, by0) in enumerate(right_vertices):
            bx1, by1 = right_vertices[(right_index + 1) % len(right_vertices)]
            if _segment_intersection_flag(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1):
                return True
    return False


def _containment_required(left: _PolyView, right: _PolyView) -> bool:
    if left.vertices:
        lx, ly = left.vertices[0]
        if _point_inside_bounds(right.bounds, lx, ly) and _point_in_polygon_inclusive(lx, ly, right):
            return True
    if right.vertices:
        rx, ry = right.vertices[0]
        if _point_inside_bounds(left.bounds, rx, ry) and _point_in_polygon_inclusive(rx, ry, left):
            return True
    return False


def _host_oracle_rows(
    left_views: tuple[_PolyView, ...],
    right_views: tuple[_PolyView, ...],
    *,
    progress_every: int,
) -> tuple[list[dict[str, int]], dict[str, int]]:
    rows: list[dict[str, int]] = []
    bbox_candidate_count = 0
    segment_count = 0
    containment_count = 0
    for left_index, left in enumerate(left_views):
        if progress_every > 0 and left_index % progress_every == 0:
            print(
                f"[goal3460] host_oracle left_index={left_index}/{len(left_views)} rows={len(rows)} "
                f"bbox_candidates={bbox_candidate_count}",
                flush=True,
            )
        for right in right_views:
            if not _bounds_overlap(left.bounds, right.bounds):
                continue
            bbox_candidate_count += 1
            requires_segment = 1 if _edge_pairs_intersect(left, right) else 0
            requires_containment = 0
            if not requires_segment:
                requires_containment = 1 if _containment_required(left, right) else 0
            if not requires_segment and not requires_containment:
                continue
            segment_count += requires_segment
            containment_count += requires_containment
            rows.append(
                {
                    "left_id": left.polygon_id,
                    "right_id": right.polygon_id,
                    "left_ordinal": left.ordinal,
                    "right_ordinal": right.ordinal,
                    "requires_segment_intersection": requires_segment,
                    "requires_point_containment": requires_containment,
                }
            )
    rows.sort(key=lambda item: (item["left_id"], item["right_id"]))
    stats = {
        "bbox_candidate_count": bbox_candidate_count,
        "segment_relation_count": segment_count,
        "containment_relation_count": containment_count,
    }
    return rows, stats


def _device_rows(columns) -> list[dict[str, int]]:
    import cupy as cp  # type: ignore

    cupy_columns = columns.as_cupy_columns()
    ordinals = columns.as_cupy_ordinal_columns()
    cp.cuda.Stream.null.synchronize()
    rows = [
        {
            "left_id": int(left_id),
            "right_id": int(right_id),
            "left_ordinal": int(left_ordinal),
            "right_ordinal": int(right_ordinal),
            "requires_segment_intersection": int(segment),
            "requires_point_containment": int(containment),
        }
        for left_id, right_id, left_ordinal, right_ordinal, segment, containment in zip(
            cp.asnumpy(cupy_columns["left_id"]).tolist(),
            cp.asnumpy(cupy_columns["right_id"]).tolist(),
            cp.asnumpy(ordinals["left_ordinal"]).tolist(),
            cp.asnumpy(ordinals["right_ordinal"]).tolist(),
            cp.asnumpy(cupy_columns["requires_segment_intersection"]).tolist(),
            cp.asnumpy(cupy_columns["requires_point_containment"]).tolist(),
        )
    ]
    rows.sort(key=lambda item: (item["left_id"], item["right_id"]))
    return rows


def _diff_rows(
    host_rows: list[dict[str, int]],
    device_rows: list[dict[str, int]],
    *,
    sample_limit: int,
) -> dict[str, object]:
    host_by_pair = {(row["left_id"], row["right_id"]): row for row in host_rows}
    device_by_pair = {(row["left_id"], row["right_id"]): row for row in device_rows}
    missing_pairs = sorted(set(host_by_pair) - set(device_by_pair))
    extra_pairs = sorted(set(device_by_pair) - set(host_by_pair))
    flag_mismatches = []
    for pair in sorted(set(host_by_pair) & set(device_by_pair)):
        host = host_by_pair[pair]
        device = device_by_pair[pair]
        if (
            host["requires_segment_intersection"] != device["requires_segment_intersection"]
            or host["requires_point_containment"] != device["requires_point_containment"]
            or host["left_ordinal"] != device["left_ordinal"]
            or host["right_ordinal"] != device["right_ordinal"]
        ):
            flag_mismatches.append({"pair": pair, "host": host, "device": device})
    return {
        "missing_pair_count": len(missing_pairs),
        "extra_pair_count": len(extra_pairs),
        "flag_mismatch_count": len(flag_mismatches),
        "missing_pairs_sample": missing_pairs[:sample_limit],
        "extra_pairs_sample": extra_pairs[:sample_limit],
        "flag_mismatches_sample": flag_mismatches[:sample_limit],
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    left_polygons = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_polygons = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    if args.left_limit is not None:
        left_polygons = left_polygons[: int(args.left_limit)]
    if args.right_limit is not None:
        right_polygons = right_polygons[: int(args.right_limit)]
    left_views = _views(left_polygons)
    right_views = _views(right_polygons)

    host_start = time.perf_counter()
    host_rows, host_stats = _host_oracle_rows(
        left_views,
        right_views,
        progress_every=int(args.progress_every),
    )
    host_sec = time.perf_counter() - host_start

    device_start = time.perf_counter()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right_polygons,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3460 large public CDB content oracle.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_polygons)
        with prepared.active_relation_device_columns(
            packed_left,
            max_rows=int(args.max_rows),
        ) as columns:
            device_rows = _device_rows(columns)
            metadata = columns.to_metadata()
    device_sec = time.perf_counter() - device_start

    diff = _diff_rows(host_rows, device_rows, sample_limit=int(args.sample_limit))
    rows_match = (
        diff["missing_pair_count"] == 0
        and diff["extra_pair_count"] == 0
        and diff["flag_mismatch_count"] == 0
    )
    return {
        "schema": "rtdl.goal3460.shape_pair_relation_large_content_oracle.v1",
        "goal": 3460,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_polygons),
        "right_shape_count": len(right_polygons),
        "max_rows": int(args.max_rows),
        "host_oracle_row_count": len(host_rows),
        "device_row_count": len(device_rows),
        "rows_match": rows_match,
        "host_oracle_stats": host_stats,
        "diff": diff,
        "host_oracle_sec": host_sec,
        "device_relation_column_extract_sec": device_sec,
        "metadata_schema_id": metadata["v2_8_typed_producer_metadata"]["schema_id"],
        "metadata_geometry_payload_device_resident": bool(metadata["runtime"]["geometry_payload"]["device_resident"]),
        "metadata_ordinal_columns_device_resident": bool(metadata["runtime"]["ordinal_columns"]["device_resident"]),
        "device_rows_sample": device_rows[: int(args.sample_limit)],
        "host_rows_sample": host_rows[: int(args.sample_limit)],
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3460 large public-CDB shape-pair relation content oracle.")
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
    parser.add_argument("--left-limit", type=int, default=None)
    parser.add_argument("--right-limit", type=int, default=None)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["rows_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

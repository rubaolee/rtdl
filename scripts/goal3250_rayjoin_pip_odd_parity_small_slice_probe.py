#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)
from rtdsl.reference import Ray2D, Segment  # noqa: E402


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _repo_state() -> dict[str, object]:
    def run(args: list[str]) -> str:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()

    try:
        commit = run(["git", "rev-parse", "HEAD"])
    except Exception:
        commit = "unknown"
    try:
        status = run(["git", "status", "--short"])
    except Exception:
        status = ""
    return {
        "commit": commit,
        "source_dirty": [line for line in status.splitlines() if line.strip()],
    }


def _boundary_segments(polygons) -> tuple[tuple[Segment, ...], tuple[int, ...]]:
    segments: list[Segment] = []
    group_ids: list[int] = []
    next_segment_id = 0
    for polygon in polygons:
        vertices = tuple((float(x), float(y)) for x, y in polygon.vertices)
        if len(vertices) < 3:
            continue
        ring = vertices
        if vertices[0] != vertices[-1]:
            ring = (*vertices, vertices[0])
        group_id = int(polygon.id)
        if group_id < 0 or group_id > 0xFFFFFFFF:
            raise ValueError("polygon ids must fit uint32 for segment group ids")
        for start, end in zip(ring, ring[1:]):
            x0, y0 = start
            x1, y1 = end
            if x0 == x1 and y0 == y1:
                continue
            segments.append(Segment(next_segment_id, x0, y0, x1, y1))
            group_ids.append(group_id)
            next_segment_id += 1
    return tuple(segments), tuple(group_ids)


def _horizontal_rays(points, segments) -> tuple[Ray2D, ...]:
    if segments:
        max_x = max(max(segment.x0, segment.x1) for segment in segments)
        min_x = min(min(segment.x0, segment.x1) for segment in segments)
        span = max(1.0, max_x - min_x)
    else:
        max_x = 1.0
        span = 1.0
    tmax_pad = span + 1.0
    rays = []
    for point in points:
        ox = float(point.x)
        oy = float(point.y)
        tmax = max(1.0, (max_x - ox) + tmax_pad)
        rays.append(Ray2D(id=int(point.id), ox=ox, oy=oy, dx=1.0, dy=0.0, tmax=tmax))
    return tuple(rays)


def _rows_to_set(rows, *, left_name: str, right_names: tuple[str, ...]) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for row in rows:
        right_name = next((name for name in right_names if name in row), None)
        if right_name is None:
            raise KeyError(f"row lacks any right-side id field from {right_names}: {row}")
        result.add((int(row[left_name]), int(row[right_name])))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe the old prepared ray/segment odd-parity route on the bounded RayJoin PIP slice."
    )
    parser.add_argument(
        "--dataset",
        default="/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb",
        help="PIP CDB dataset path.",
    )
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    print(f"[goal3250] loading dataset: {args.dataset}", flush=True)
    case = _load_rayjoin_case("pip", args.dataset)
    points = tuple(case.inputs["points"])
    polygons = tuple(case.inputs["polygons"])
    segments, segment_group_ids = _boundary_segments(polygons)
    rays = _horizontal_rays(points, segments)
    print(
        f"[goal3250] loaded points={len(points)} polygons={len(polygons)} "
        f"boundary_segments={len(segments)}",
        flush=True,
    )

    from rtdsl.optix_runtime import get_last_phase_timings
    from rtdsl.optix_runtime import pack_points
    from rtdsl.optix_runtime import pack_polygons
    from rtdsl.optix_runtime import pack_rays
    from rtdsl.optix_runtime import pack_segments
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix
    from rtdsl.optix_runtime import prepare_ray_segment_group_count_2d_optix

    phase_sec: dict[str, float] = {}
    start = time.perf_counter()
    packed_points = pack_points(records=points, dimension=2)
    phase_sec["pack_points_sec"] = time.perf_counter() - start

    start = time.perf_counter()
    packed_polygons = pack_polygons(records=polygons)
    phase_sec["pack_polygons_sec"] = time.perf_counter() - start

    start = time.perf_counter()
    packed_rays = pack_rays(records=rays, dimension=2)
    phase_sec["pack_rays_sec"] = time.perf_counter() - start

    start = time.perf_counter()
    packed_segments = pack_segments(records=segments)
    phase_sec["pack_boundary_segments_sec"] = time.perf_counter() - start

    print("[goal3250] preparing closed-shape membership", flush=True)
    start = time.perf_counter()
    closed = prepare_point_closed_shape_membership_2d_optix(packed_polygons)
    phase_sec["closed_prepare_sec"] = time.perf_counter() - start
    try:
        print("[goal3250] materializing closed-shape reference rows", flush=True)
        start = time.perf_counter()
        reference_view = closed.run_raw(packed_points, result_mode="positive_hits")
        reference_query_sec = time.perf_counter() - start
        try:
            reference_rows = tuple(reference_view.to_dict_rows())
        finally:
            reference_view.close()
        reference_set = _rows_to_set(reference_rows, left_name="point_id", right_names=("shape_id", "polygon_id"))

        closed_count_samples: list[float] = []
        for index in range(args.warmup):
            _ = closed.count(packed_points)
            print(f"[goal3250] closed count warmup {index + 1}/{args.warmup}", flush=True)
        closed_count_values: list[int] = []
        closed_native_samples: list[dict[str, object]] = []
        for index in range(args.repeat):
            start = time.perf_counter()
            count = int(closed.count(packed_points))
            elapsed = time.perf_counter() - start
            closed_count_samples.append(elapsed)
            closed_count_values.append(count)
            closed_native_samples.append(dict(get_last_phase_timings()))
            print(
                f"[goal3250] closed count repeat {index + 1}/{args.repeat}: "
                f"{elapsed * 1000.0:.6f} ms count={count}",
                flush=True,
            )
    finally:
        closed.close()

    print("[goal3250] preparing boundary ray/segment group-count scene", flush=True)
    start = time.perf_counter()
    grouped = prepare_ray_segment_group_count_2d_optix(packed_segments, segment_group_ids)
    phase_sec["odd_parity_prepare_sec"] = time.perf_counter() - start
    try:
        for index in range(args.warmup):
            rows = grouped.run_odd_parity(packed_rays)
            print(f"[goal3250] odd-parity warmup {index + 1}/{args.warmup}: rows={len(rows)}", flush=True)

        odd_samples: list[float] = []
        odd_counts: list[int] = []
        odd_sets_match: list[bool] = []
        odd_missing_counts: list[int] = []
        odd_extra_counts: list[int] = []
        odd_first_rows: tuple[dict[str, int], ...] = ()
        for index in range(args.repeat):
            start = time.perf_counter()
            rows = grouped.run_odd_parity(packed_rays)
            elapsed = time.perf_counter() - start
            odd_set = _rows_to_set(rows, left_name="ray_id", right_names=("group_id",))
            missing = reference_set - odd_set
            extra = odd_set - reference_set
            odd_samples.append(elapsed)
            odd_counts.append(len(rows))
            odd_sets_match.append(not missing and not extra)
            odd_missing_counts.append(len(missing))
            odd_extra_counts.append(len(extra))
            if index == 0:
                odd_first_rows = tuple(dict(row) for row in rows[:8])
            print(
                f"[goal3250] odd-parity repeat {index + 1}/{args.repeat}: "
                f"{elapsed * 1000.0:.6f} ms rows={len(rows)} "
                f"match={not missing and not extra} missing={len(missing)} extra={len(extra)}",
                flush=True,
            )
    finally:
        grouped.close()

    payload = {
        "goal": 3250,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_state": _repo_state(),
        "dataset": args.dataset,
        "env": {
            "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
            "RTDL_OPTIX_LIB": os.environ.get("RTDL_OPTIX_LIB"),
            "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT": os.environ.get(
                "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT"
            ),
        },
        "inputs": {
            "point_count": len(points),
            "polygon_count": len(polygons),
            "boundary_segment_count": len(segments),
            "ray_count": len(rays),
        },
        "phase_sec": phase_sec,
        "closed_shape_reference": {
            "positive_rows": len(reference_rows),
            "reference_query_sec": reference_query_sec,
            "count_values": closed_count_values,
            "count_median_sec": _median(closed_count_samples),
            "native_phase_samples": closed_native_samples,
        },
        "odd_parity_route": {
            "row_count_values": odd_counts,
            "query_median_sec": _median(odd_samples),
            "sets_match_all": all(odd_sets_match),
            "missing_counts": odd_missing_counts,
            "extra_counts": odd_extra_counts,
            "sample_rows": list(odd_first_rows),
            "route_status": (
                "candidate_current_small_slice_fallback"
                if all(odd_sets_match) and _median(odd_samples) is not None
                else "negative_or_correctness_failed"
            ),
        },
        "ratios": {
            "odd_parity_over_closed_count_median": (
                (_median(odd_samples) / _median(closed_count_samples))
                if _median(odd_samples) and _median(closed_count_samples)
                else None
            ),
        },
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3250] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import socket
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_barnes_hut_force_app as barnes_app


GOAL = "Goal1106 Barnes-Hut chunked Embree timing baseline"
DATE = "2026-04-29"
SCHEMA_VERSION = "goal1101_current_contract_non_optix_baseline_v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs/reports/goal1101_current_contract_non_optix_baselines/"
    / "barnes_hut_depth8_20m_embree_timing_baseline.json"
)


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _host() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def _source_commit() -> str | None:
    if os.environ.get("RTDL_SOURCE_COMMIT"):
        return os.environ["RTDL_SOURCE_COMMIT"]
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode == 0:
        value = completed.stdout.strip()
        return value or None
    source_file = ROOT / ".rtdl_source_commit"
    if source_file.exists():
        value = source_file.read_text(encoding="utf-8").strip()
        return value or None
    return None


def _generated_body_xy(index: int, *, body_count: int, grid: int | None = None) -> tuple[float, float]:
    if index < 0 or index >= body_count:
        raise ValueError("body index out of range")
    effective_grid = int(math.ceil(math.sqrt(body_count))) if grid is None else grid
    gx = index % effective_grid
    gy = index // effective_grid
    x = (gx / max(1, effective_grid - 1)) * 4.0 - 2.0
    y = (gy / max(1, effective_grid - 1)) * 4.0 - 2.0
    x += ((index * 17) % 11 - 5) * 0.001
    y += ((index * 31) % 13 - 6) * 0.001
    return x, y


def _generated_body_points_range(start: int, stop: int, *, body_count: int, grid: int) -> tuple[rt.Point, ...]:
    return tuple(
        rt.Point(id=index + 1, x=x, y=y)
        for index in range(start, stop)
        for x, y in (_generated_body_xy(index, body_count=body_count, grid=grid),)
    )


def _generated_body_bounds(body_count: int) -> tuple[float, float, float, float]:
    grid = int(math.ceil(math.sqrt(body_count)))
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf
    for index in range(body_count):
        x, y = _generated_body_xy(index, body_count=body_count, grid=grid)
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    return min_x, max_x, min_y, max_y


def _fixed_depth_node_points_for_generated_bodies(body_count: int, *, depth: int) -> tuple[rt.Point, ...]:
    if depth < 1:
        raise ValueError("depth must be at least 1")
    min_x, max_x, min_y, max_y = _generated_body_bounds(body_count)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    half_size = max(max_x - min_x, max_y - min_y) / 2.0 + 0.25
    cells_per_axis = 1 << depth
    cell_size = (2.0 * half_size) / cells_per_axis
    min_square_x = center_x - half_size
    min_square_y = center_y - half_size

    points: list[rt.Point] = []
    node_id = 1
    for y_index in range(cells_per_axis):
        cy = min_square_y + (y_index + 0.5) * cell_size
        for x_index in range(cells_per_axis):
            cx = min_square_x + (x_index + 0.5) * cell_size
            points.append(rt.Point(id=node_id, x=cx, y=cy))
            node_id += 1
    return tuple(points)


def _chunk_ranges(total: int, chunk_size: int) -> Iterable[tuple[int, int]]:
    for start in range(0, total, chunk_size):
        yield start, min(total, start + chunk_size)


def run_chunked_profile(
    *,
    body_count: int,
    chunk_size: int,
    iterations: int,
    radius: float,
    barnes_tree_depth: int,
    hit_threshold: int,
) -> dict[str, Any]:
    if body_count < 1:
        raise ValueError("body_count must be at least 1")
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if barnes_tree_depth < 1:
        raise ValueError("barnes_tree_depth must be at least 1")
    if hit_threshold < 1:
        raise ValueError("hit_threshold must be at least 1")

    grid = int(math.ceil(math.sqrt(body_count)))
    node_points, input_sec = _time_call(
        lambda: _fixed_depth_node_points_for_generated_bodies(body_count, depth=barnes_tree_depth)
    )
    prepared, prepare_sec = _time_call(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(node_points))

    query_totals: list[float] = []
    pack_totals: list[float] = []
    postprocess_totals: list[float] = []
    reached_totals: list[int] = []
    chunk_query_samples: list[float] = []
    chunk_pack_samples: list[float] = []
    chunk_count = math.ceil(body_count / chunk_size)
    close_sec = 0.0
    try:
        for _ in range(iterations):
            iteration_query_sec = 0.0
            iteration_pack_sec = 0.0
            iteration_postprocess_sec = 0.0
            iteration_reached = 0
            for start, stop in _chunk_ranges(body_count, chunk_size):
                query_points, pack_sec = _time_call(
                    lambda start=start, stop=stop: _generated_body_points_range(
                        start,
                        stop,
                        body_count=body_count,
                        grid=grid,
                    )
                )
                rows, query_sec = _time_call(
                    lambda query_points=query_points: prepared.run(
                        query_points,
                        radius=radius,
                        threshold=hit_threshold,
                    )
                )
                reached, postprocess_sec = _time_call(
                    lambda rows=rows: sum(1 for row in rows if int(row["threshold_reached"]) != 0)
                )
                iteration_pack_sec += pack_sec
                iteration_query_sec += query_sec
                iteration_postprocess_sec += postprocess_sec
                iteration_reached += int(reached)
                chunk_pack_samples.append(pack_sec)
                chunk_query_samples.append(query_sec)
            pack_totals.append(iteration_pack_sec)
            query_totals.append(iteration_query_sec)
            postprocess_totals.append(iteration_postprocess_sec)
            reached_totals.append(iteration_reached)
    finally:
        _, close_sec = _time_call(prepared.close)

    last_reached = reached_totals[-1] if reached_totals else 0
    all_covered = last_reached == body_count
    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "backend": "embree",
        "source_commit": _source_commit(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": _host(),
        "parameters": {
            "scenario": "barnes_hut_node_coverage",
            "backend": "embree",
            "body_count": body_count,
            "chunk_size": chunk_size,
            "chunk_count": chunk_count,
            "iterations": iterations,
            "radius": radius,
            "barnes_tree_depth": barnes_tree_depth,
            "hit_threshold": hit_threshold,
            "skip_validation": True,
            "timing_only": True,
        },
        "scenario": {
            "scenario": "barnes_hut_node_coverage",
            "mode": "embree",
            "timings_sec": {
                "input_build_sec": input_sec,
                "point_pack_sec": _stats(pack_totals),
                "backend_prepare_sec": prepare_sec,
                "native_query_sec": _stats(query_totals),
                "python_postprocess_sec": _stats(postprocess_totals),
                "validation_sec": _stats([]),
                "backend_close_sec": close_sec,
                "chunk_point_pack_sec": _stats(chunk_pack_samples),
                "chunk_native_query_sec": _stats(chunk_query_samples),
            },
            "result": {
                "radius": radius,
                "query_count": body_count,
                "build_count": len(node_points),
                "node_count": len(node_points),
                "barnes_tree_depth": barnes_tree_depth,
                "hit_threshold": hit_threshold,
                "threshold_reached_count": int(last_reached),
                "all_queries_reached_threshold": all_covered,
                "oracle_all_queries_reached_threshold": None,
                "matches_oracle": None,
            },
        },
        "chunking": {
            "enabled": True,
            "chunk_size": chunk_size,
            "chunk_count": chunk_count,
            "reason": (
                "The 20M Barnes-Hut timing baseline must preserve the same prepared Embree "
                "node-coverage query contract without materializing all query bodies as Python "
                "objects in one process."
            ),
        },
        "public_speedup_claim_authorized": False,
        "boundary": (
            "Goal1106 produces the missing Goal1101-compatible timing-only Embree baseline. "
            "It validates bounded-memory execution mechanics but does not authorize public RTX "
            "speedup claims or imply full Barnes-Hut force reduction is native."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run chunked Barnes-Hut Embree timing baseline.")
    parser.add_argument("--body-count", type=int, default=20_000_000)
    parser.add_argument("--chunk-size", type=int, default=250_000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--radius", type=float, default=0.1)
    parser.add_argument("--barnes-tree-depth", type=int, default=8)
    parser.add_argument("--hit-threshold", type=int, default=4)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    payload = run_chunked_profile(
        body_count=args.body_count,
        chunk_size=args.chunk_size,
        iterations=args.iterations,
        radius=args.radius,
        barnes_tree_depth=args.barnes_tree_depth,
        hit_threshold=args.hit_threshold,
    )
    output = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "scenario": payload["scenario"]["scenario"],
                "backend": payload["backend"],
                "query_count": payload["scenario"]["result"]["query_count"],
                "output_json": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

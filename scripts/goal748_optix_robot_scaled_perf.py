#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_robot_collision_screening_app as robot_app


BACKENDS = ("cpu_rows", "embree_rows", "optix_rows", "optix_prepared_count")


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": float(min(samples)),
        "median_sec": float(statistics.median(samples)),
        "max_sec": float(max(samples)),
    }


def _rows_hit_count(rows: tuple[dict[str, object], ...]) -> int:
    return sum(1 for row in rows if bool(row["any_hit"]))


def _run_rows_backend(
    backend: str,
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
) -> tuple[dict[str, object], ...]:
    if backend == "cpu_rows":
        return rt.ray_triangle_any_hit_cpu(edge_rays, obstacle_triangles)
    if backend == "embree_rows":
        return robot_app._run_backend("embree", edge_rays, obstacle_triangles)
    if backend == "optix_rows":
        return robot_app._run_backend("optix", edge_rays, obstacle_triangles)
    raise ValueError(f"unsupported row backend `{backend}`")


def _profile_rows_backend(
    *,
    backend: str,
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
    repeats: int,
    warmups: int,
) -> dict[str, object]:
    for _ in range(warmups):
        _run_rows_backend(backend, edge_rays, obstacle_triangles)

    samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(repeats):
        last_rows, elapsed = _time_call(lambda: _run_rows_backend(backend, edge_rays, obstacle_triangles))
        samples.append(elapsed)

    row_count = len(last_rows)
    hit_count = _rows_hit_count(last_rows)
    median = statistics.median(samples) if samples else 0.0
    return {
        "backend": backend,
        "status": "ok",
        "output_shape": "per_ray_dict_rows",
        "row_count": row_count,
        "hit_edge_count": hit_count,
        "timing_sec": _stats(samples),
        "rows_per_sec_median": (row_count / median) if median > 0.0 else 0.0,
        "boundary": "Rows backends include native traversal plus per-ray Python dict row materialization.",
    }


def _profile_optix_prepared_count(
    *,
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
    repeats: int,
    warmups: int,
) -> dict[str, object]:
    prepared_scene, prepare_scene_sec = _time_call(lambda: rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles))
    try:
        prepared_rays, prepare_rays_sec = _time_call(lambda: rt.prepare_optix_rays_2d(edge_rays))
        try:
            for _ in range(warmups):
                prepared_scene.count(prepared_rays)

            samples: list[float] = []
            last_hit_count = 0
            for _ in range(repeats):
                last_hit_count, elapsed = _time_call(lambda: prepared_scene.count(prepared_rays))
                samples.append(elapsed)

            median = statistics.median(samples) if samples else 0.0
            return {
                "backend": "optix_prepared_count",
                "status": "ok",
                "output_shape": "native_scalar_hit_edge_count",
                "row_count": 0,
                "hit_edge_count": int(last_hit_count),
                "prepare_scene_sec": float(prepare_scene_sec),
                "prepare_rays_sec": float(prepare_rays_sec),
                "timing_sec": _stats(samples),
                "rays_per_sec_median": (len(edge_rays) / median) if median > 0.0 else 0.0,
                "boundary": "Prepared count excludes scene/ray preparation from execute timing and returns only a scalar hit-edge count.",
            }
        finally:
            prepared_rays.close()
    finally:
        prepared_scene.close()


def _profile_backend(
    *,
    backend: str,
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
    repeats: int,
    warmups: int,
) -> dict[str, object]:
    if backend == "optix_prepared_count":
        return _profile_optix_prepared_count(
            edge_rays=edge_rays,
            obstacle_triangles=obstacle_triangles,
            repeats=repeats,
            warmups=warmups,
        )
    return _profile_rows_backend(
        backend=backend,
        edge_rays=edge_rays,
        obstacle_triangles=obstacle_triangles,
        repeats=repeats,
        warmups=warmups,
    )


def run_suite(
    *,
    pose_count: int,
    obstacle_count: int,
    backends: tuple[str, ...],
    repeats: int,
    warmups: int,
    validate: bool,
    strict: bool,
) -> dict[str, object]:
    case, build_sec = _time_call(lambda: robot_app.make_scaled_case(pose_count=pose_count, obstacle_count=obstacle_count))
    edge_rays = case["edge_rays"]
    obstacle_triangles = case["obstacle_triangles"]

    oracle_hit_count: int | None = None
    oracle_sec: float | None = None
    if validate:
        oracle_rows, oracle_elapsed = _time_call(lambda: rt.ray_triangle_any_hit_cpu(edge_rays, obstacle_triangles))
        oracle_hit_count = _rows_hit_count(oracle_rows)
        oracle_sec = oracle_elapsed

    results: list[dict[str, object]] = []
    for backend in backends:
        try:
            result = _profile_backend(
                backend=backend,
                edge_rays=edge_rays,
                obstacle_triangles=obstacle_triangles,
                repeats=repeats,
                warmups=warmups,
            )
            if oracle_hit_count is not None:
                result["matches_oracle"] = int(result["hit_edge_count"]) == int(oracle_hit_count)
                result["oracle_hit_edge_count"] = int(oracle_hit_count)
        except Exception as exc:
            if strict:
                raise
            result = {
                "backend": backend,
                "status": "skipped_or_failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(result)

    return {
        "suite": "goal748_optix_robot_scaled_perf",
        "pose_count": pose_count,
        "obstacle_count": obstacle_count,
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
        "repeats": repeats,
        "warmups": warmups,
        "case_build_sec": float(build_sec),
        "oracle_validation": {
            "enabled": validate,
            "hit_edge_count": oracle_hit_count,
            "time_sec": oracle_sec,
        },
        "results": results,
        "boundary": (
            "This harness is for robot-collision ray/triangle any-hit app performance. "
            "OptiX prepared_count is a true OptiX traversal shape, but RTX RT-core speedup "
            "claims still require RTX-class hardware and phase evidence. GTX 1070 runs are "
            "correctness and whole-call behavior evidence only."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal748 scaled robot collision OptiX/Embree performance harness.")
    parser.add_argument("--list-backends", action="store_true")
    parser.add_argument("--pose-count", type=int, default=2000)
    parser.add_argument("--obstacle-count", type=int, default=1000)
    parser.add_argument("--backend", action="append", choices=BACKENDS, help="backend to run; may be repeated")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--no-validate", action="store_true", help="skip CPU oracle hit-count validation")
    parser.add_argument("--strict", action="store_true", help="raise instead of recording skipped_or_failed backends")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    if args.list_backends:
        print(json.dumps({"backends": BACKENDS}, indent=2, sort_keys=True))
        return 0
    if args.pose_count < 1 or args.obstacle_count < 1:
        raise ValueError("--pose-count and --obstacle-count must be positive")
    if args.repeats < 1 or args.warmups < 0:
        raise ValueError("--repeats must be positive and --warmups must be non-negative")

    backends = tuple(args.backend) if args.backend else ("embree_rows", "optix_rows", "optix_prepared_count")
    payload = run_suite(
        pose_count=args.pose_count,
        obstacle_count=args.obstacle_count,
        backends=backends,
        repeats=args.repeats,
        warmups=args.warmups,
        validate=not args.no_validate,
        strict=args.strict,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

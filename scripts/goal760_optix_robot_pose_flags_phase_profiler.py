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


GOAL = "Goal760 OptiX robot pose-flags phase profiler"
DATE = "2026-04-22"


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


def _pose_indices(
    edge_rays: tuple[rt.Ray2D, ...],
    poses: tuple[dict[str, object], ...],
    ray_metadata: dict[int, dict[str, int]],
) -> tuple[int, ...]:
    pose_ids = tuple(int(pose["pose_id"]) for pose in poses)
    pose_index_by_id = {pose_id: index for index, pose_id in enumerate(pose_ids)}
    return tuple(pose_index_by_id[int(ray_metadata[int(ray.id)]["pose_id"])] for ray in edge_rays)


def _flag_summary(pose_flags: tuple[bool, ...], poses: tuple[dict[str, object], ...]) -> dict[str, object]:
    pose_ids = tuple(int(pose["pose_id"]) for pose in poses)
    colliding_pose_ids = tuple(pose_id for index, pose_id in enumerate(pose_ids) if pose_flags[index])
    return {
        "pose_collision_flags": tuple(
            {"pose_id": pose_id, "collides": bool(pose_flags[index])}
            for index, pose_id in enumerate(pose_ids)
        ),
        "colliding_pose_ids": colliding_pose_ids,
        "colliding_pose_count": len(colliding_pose_ids),
    }


def _cpu_pose_flags(
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
    poses: tuple[dict[str, object], ...],
    ray_metadata: dict[int, dict[str, int]],
) -> tuple[bool, ...]:
    rows = rt.ray_triangle_any_hit_cpu(edge_rays, obstacle_triangles)
    summary = robot_app._summarize_collisions(rows, poses, ray_metadata)
    return tuple(bool(row["collides"]) for row in summary["pose_collision_flags"])


def run_suite(
    *,
    mode: str,
    pose_count: int,
    obstacle_count: int,
    iterations: int,
    validate: bool,
) -> dict[str, Any]:
    if mode not in {"optix", "dry-run"}:
        raise ValueError("mode must be 'optix' or 'dry-run'")
    if pose_count <= 0:
        raise ValueError("pose_count must be positive")
    if obstacle_count <= 0:
        raise ValueError("obstacle_count must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    total_start = time.perf_counter()
    case, input_sec = _time_call(lambda: robot_app.make_scaled_case(pose_count=pose_count, obstacle_count=obstacle_count))
    edge_rays = case["edge_rays"]
    obstacle_triangles = case["obstacle_triangles"]
    poses = case["poses"]
    ray_metadata = case["ray_metadata"]
    pose_indices = _pose_indices(edge_rays, poses, ray_metadata)

    prepare_scene_sec = 0.0
    prepare_rays_sec = 0.0
    close_sec = 0.0
    run_samples: list[float] = []
    last_pose_flags: tuple[bool, ...] = ()

    if mode == "dry-run":
        for _ in range(iterations):
            last_pose_flags, elapsed = _time_call(
                lambda: _cpu_pose_flags(edge_rays, obstacle_triangles, poses, ray_metadata)
            )
            run_samples.append(elapsed)
    else:
        prepared_scene, prepare_scene_sec = _time_call(
            lambda: rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles)
        )
        prepared_rays = None
        try:
            prepared_rays, prepare_rays_sec = _time_call(lambda: rt.prepare_optix_rays_2d(edge_rays))
            for _ in range(iterations):
                raw_flags, elapsed = _time_call(
                    lambda: prepared_scene.pose_flags_packed(
                        prepared_rays,
                        pose_indices,
                        pose_count=len(poses),
                    )
                )
                last_pose_flags = tuple(bool(flag) for flag in raw_flags)
                run_samples.append(elapsed)
        finally:
            if prepared_rays is not None:
                _, rays_close_sec = _time_call(prepared_rays.close)
                close_sec += rays_close_sec
            _, scene_close_sec = _time_call(prepared_scene.close)
            close_sec += scene_close_sec

    oracle_sec = 0.0
    matches_oracle: bool | None = None
    oracle_summary: dict[str, object] | None = None
    if validate:
        oracle_flags, oracle_sec = _time_call(
            lambda: _cpu_pose_flags(edge_rays, obstacle_triangles, poses, ray_metadata)
        )
        matches_oracle = tuple(last_pose_flags) == tuple(oracle_flags)
        oracle_summary = _flag_summary(oracle_flags, poses)

    result_summary = _flag_summary(last_pose_flags, poses)
    total_sec = time.perf_counter() - total_start
    return {
        "suite": GOAL,
        "date": DATE,
        "mode": mode,
        "pose_count": len(poses),
        "obstacle_count": obstacle_count,
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
        "iterations": iterations,
        "validated": validate,
        "matches_oracle": matches_oracle,
        "phases": {
            "python_input_construction_sec": input_sec,
            "optix_prepare_scene_sec": prepare_scene_sec,
            "optix_prepare_rays_sec": prepare_rays_sec,
            "prepared_pose_flags_warm_query_sec": _stats(run_samples),
            "oracle_validate_sec": oracle_sec,
            "close_sec": close_sec,
            "total_sec": total_sec,
        },
        "result": {
            "colliding_pose_count": result_summary["colliding_pose_count"],
            "colliding_pose_ids_sample": list(result_summary["colliding_pose_ids"][:10]),
            "pose_collision_flags_sample": list(result_summary["pose_collision_flags"][:10]),
            "oracle_colliding_pose_count": None
            if oracle_summary is None
            else oracle_summary["colliding_pose_count"],
        },
        "boundary": (
            "This is a phase profiler, not a speedup claim. dry-run mode is schema/logic validation only. "
            "optix mode can support future RTX claim review only on RTX-class hardware with exported prepared "
            "OptiX any-hit symbols, and only for prepared ray/triangle pose-flag summary timing."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal760 OptiX robot pose-flags phase profiler.")
    parser.add_argument("--mode", choices=("optix", "dry-run"), default="dry-run")
    parser.add_argument("--pose-count", type=int, default=1024)
    parser.add_argument("--obstacle-count", type=int, default=64)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)

    payload = run_suite(
        mode=args.mode,
        pose_count=args.pose_count,
        obstacle_count=args.obstacle_count,
        iterations=args.iterations,
        validate=not args.skip_validation,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

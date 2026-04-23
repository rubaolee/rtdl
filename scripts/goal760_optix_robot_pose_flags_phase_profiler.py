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
SCHEMA_VERSION = "goal825_tier1_phase_contract_v1"


def _cloud_claim_contract(result_mode: str) -> dict[str, object]:
    return {
        "claim_scope": "prepared OptiX ray/triangle any-hit compact pose summary",
        "non_claim": "not continuous collision detection, full robot planning, full kinematics, witness-row speedup, or mesh-engine replacement",
        "result_mode": result_mode,
        "required_phase_groups": (
            "python_input_construction_sec",
            "optix_prepare_scene_sec",
            "optix_prepare_rays_sec",
            "optix_prepare_pose_indices_sec",
            "prepared_pose_flags_warm_query_sec",
            "oracle_validate_sec",
            "close_sec",
            "total_sec",
        ),
        "cloud_policy": "include in the single active RTX batch only after local pre-cloud readiness passes",
    }


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


def _rect_triangles(rect_id: int, x0: float, y0: float, x1: float, y1: float) -> tuple[rt.Triangle, rt.Triangle]:
    return (
        rt.Triangle(id=rect_id * 2, x0=x0, y0=y0, x1=x1, y1=y0, x2=x1, y2=y1),
        rt.Triangle(id=rect_id * 2 + 1, x0=x0, y0=y0, x1=x1, y1=y1, x2=x0, y2=y1),
    )


def _make_scaled_case_packed_arrays(*, pose_count: int, obstacle_count: int) -> dict[str, Any]:
    """Generate the scalable robot fixture without per-ray Python objects."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        raise RuntimeError("packed-array robot profiler mode requires numpy")

    grid = int(robot_app.math.ceil(robot_app.math.sqrt(obstacle_count)))
    obstacle_triangles: list[rt.Triangle] = []
    for obstacle_index in range(obstacle_count):
        gx = obstacle_index % grid
        gy = obstacle_index // grid
        x0 = gx * 1.5 + 0.35
        y0 = gy * 1.2 - 0.25
        obstacle_triangles.extend(_rect_triangles(1000 + obstacle_index, x0, y0, x0 + 0.55, y0 + 0.45))

    pose_ids = np.arange(1, pose_count + 1, dtype=np.uint32)
    pose_zero_based = np.arange(pose_count, dtype=np.uint32)
    gx = (pose_ids - 1) % grid
    gy = ((pose_ids - 1) // grid) % grid
    center_x = gx.astype(np.float64) * 1.5 + np.where((pose_ids % 2) == 0, 0.45, -0.35)
    center_y = gy.astype(np.float64) * 1.2

    half_w = 0.75 / 2.0
    half_h = 0.25 / 2.0
    ox_offsets = np.array([-half_w, half_w, half_w, -half_w], dtype=np.float64)
    oy_offsets = np.array([-half_h, -half_h, half_h, half_h], dtype=np.float64)
    dx_offsets = np.array([0.75, 0.0, -0.75, 0.0], dtype=np.float64)
    dy_offsets = np.array([0.0, 0.25, 0.0, -0.25], dtype=np.float64)
    edge_ids = np.tile(np.arange(4, dtype=np.uint32), pose_count)

    packed_rays = rt.pack_rays_2d_from_arrays(
        ids=np.repeat(pose_ids, 4) * 1000 + 10 + edge_ids,
        ox=np.repeat(center_x, 4) + np.tile(ox_offsets, pose_count),
        oy=np.repeat(center_y, 4) + np.tile(oy_offsets, pose_count),
        dx=np.tile(dx_offsets, pose_count),
        dy=np.tile(dy_offsets, pose_count),
        tmax=np.ones(pose_count * 4, dtype=np.float64),
    )
    return {
        "edge_rays": packed_rays,
        "obstacle_triangles": tuple(obstacle_triangles),
        "pose_indices": np.repeat(pose_zero_based, 4),
        "pose_ids": pose_ids,
        "pose_count": pose_count,
    }


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
    input_mode: str = "python_objects",
    result_mode: str = "pose_flags",
) -> dict[str, Any]:
    if mode not in {"optix", "dry-run"}:
        raise ValueError("mode must be 'optix' or 'dry-run'")
    if input_mode not in {"python_objects", "packed_arrays"}:
        raise ValueError("input_mode must be 'python_objects' or 'packed_arrays'")
    if result_mode not in {"pose_flags", "pose_count"}:
        raise ValueError("result_mode must be 'pose_flags' or 'pose_count'")
    if input_mode == "packed_arrays" and mode != "optix":
        raise ValueError("packed_arrays input mode is only supported with mode='optix'")
    if input_mode == "packed_arrays" and validate:
        raise ValueError("packed_arrays input mode requires --skip-validation; run python_objects mode for oracle checks")
    if result_mode == "pose_count" and mode != "optix":
        raise ValueError("pose_count result mode is only supported with mode='optix'")
    if result_mode == "pose_count" and input_mode != "packed_arrays":
        raise ValueError("pose_count result mode requires input_mode='packed_arrays'")
    if result_mode == "pose_count" and validate:
        raise ValueError("pose_count result mode requires --skip-validation")
    if pose_count <= 0:
        raise ValueError("pose_count must be positive")
    if obstacle_count <= 0:
        raise ValueError("obstacle_count must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    total_start = time.perf_counter()
    case_factory = (
        lambda: _make_scaled_case_packed_arrays(pose_count=pose_count, obstacle_count=obstacle_count)
        if input_mode == "packed_arrays"
        else robot_app.make_scaled_case(pose_count=pose_count, obstacle_count=obstacle_count)
    )
    case, input_sec = _time_call(case_factory)
    edge_rays = case["edge_rays"]
    obstacle_triangles = case["obstacle_triangles"]
    if input_mode == "packed_arrays":
        poses = tuple({"pose_id": int(pose_id), "label": ""} for pose_id in case["pose_ids"])
        ray_metadata = {}
        pose_indices = case["pose_indices"]
    else:
        poses = case["poses"]
        ray_metadata = case["ray_metadata"]
        pose_indices = _pose_indices(edge_rays, poses, ray_metadata)
    edge_ray_count = int(edge_rays.count) if not isinstance(edge_rays, tuple) else len(edge_rays)

    prepare_scene_sec = 0.0
    prepare_rays_sec = 0.0
    prepare_pose_indices_sec = 0.0
    close_sec = 0.0
    run_samples: list[float] = []
    last_pose_flags: tuple[bool, ...] = ()
    last_colliding_pose_count: int | None = None

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
        prepared_pose_indices = None
        try:
            prepared_rays, prepare_rays_sec = _time_call(lambda: rt.prepare_optix_rays_2d(edge_rays))
            if input_mode == "packed_arrays":
                prepared_pose_indices, prepare_pose_indices_sec = _time_call(
                    lambda: rt.prepare_optix_pose_indices_2d(pose_indices)
                )
            for _ in range(iterations):
                if prepared_pose_indices is None:
                    raw_flags, elapsed = _time_call(
                        lambda: prepared_scene.pose_flags_packed(
                            prepared_rays,
                            pose_indices,
                            pose_count=len(poses),
                        )
                    )
                elif result_mode == "pose_count":
                    last_colliding_pose_count, elapsed = _time_call(
                        lambda: prepared_scene.pose_count_prepared_indices(
                            prepared_rays,
                            prepared_pose_indices,
                            pose_count=len(poses),
                        )
                    )
                    run_samples.append(elapsed)
                    continue
                else:
                    raw_flags, elapsed = _time_call(
                        lambda: prepared_scene.pose_flags_prepared_indices(
                            prepared_rays,
                            prepared_pose_indices,
                            pose_count=len(poses),
                        )
                    )
                last_pose_flags = tuple(bool(flag) for flag in raw_flags)
                run_samples.append(elapsed)
        finally:
            if prepared_pose_indices is not None:
                _, pose_indices_close_sec = _time_call(prepared_pose_indices.close)
                close_sec += pose_indices_close_sec
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

    result_summary = None if result_mode == "pose_count" else _flag_summary(last_pose_flags, poses)
    total_sec = time.perf_counter() - total_start
    return {
        "suite": GOAL,
        "schema_version": SCHEMA_VERSION,
        "cloud_claim_contract": _cloud_claim_contract(result_mode),
        "date": DATE,
        "mode": mode,
        "input_mode": input_mode,
        "result_mode": result_mode,
        "pose_count": len(poses),
        "obstacle_count": obstacle_count,
        "edge_ray_count": edge_ray_count,
        "obstacle_triangle_count": len(obstacle_triangles),
        "iterations": iterations,
        "validated": validate,
        "matches_oracle": matches_oracle,
        "phases": {
            "python_input_construction_sec": input_sec,
            "optix_prepare_scene_sec": prepare_scene_sec,
            "optix_prepare_rays_sec": prepare_rays_sec,
            "optix_prepare_pose_indices_sec": prepare_pose_indices_sec,
            "prepared_pose_flags_warm_query_sec": _stats(run_samples),
            "oracle_validate_sec": oracle_sec,
            "close_sec": close_sec,
            "total_sec": total_sec,
        },
        "result": {
            "colliding_pose_count": (
                int(last_colliding_pose_count)
                if result_mode == "pose_count"
                else result_summary["colliding_pose_count"]
            ),
            "colliding_pose_ids_sample": [] if result_mode == "pose_count" else list(result_summary["colliding_pose_ids"][:10]),
            "pose_collision_flags_sample": [] if result_mode == "pose_count" else list(result_summary["pose_collision_flags"][:10]),
            "oracle_colliding_pose_count": None
            if oracle_summary is None
            else oracle_summary["colliding_pose_count"],
        },
        "boundary": (
            "This is a phase profiler, not a speedup claim. dry-run mode is schema/logic validation only. "
            "optix mode can support future RTX claim review only on RTX-class hardware with exported prepared "
            "OptiX any-hit symbols, and only for prepared ray/triangle pose-flag summary timing. "
            "packed_arrays input mode avoids per-ray Python object construction but remains app-specific. "
            "pose_count result mode returns only a scalar colliding-pose count for clean native summary timing."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal760 OptiX robot pose-flags phase profiler.")
    parser.add_argument("--mode", choices=("optix", "dry-run"), default="dry-run")
    parser.add_argument("--pose-count", type=int, default=1024)
    parser.add_argument("--obstacle-count", type=int, default=64)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--input-mode", choices=("python_objects", "packed_arrays"), default="python_objects")
    parser.add_argument("--result-mode", choices=("pose_flags", "pose_count"), default="pose_flags")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)

    payload = run_suite(
        mode=args.mode,
        pose_count=args.pose_count,
        obstacle_count=args.obstacle_count,
        iterations=args.iterations,
        validate=not args.skip_validation,
        input_mode=args.input_mode,
        result_mode=args.result_mode,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

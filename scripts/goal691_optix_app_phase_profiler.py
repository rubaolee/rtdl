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


def profile_robot_collision(iterations: int, backend: str, summary_mode: str) -> dict[str, object]:
    phase_samples: dict[str, list[float]] = {
        "python_input_construction": [],
        "native_prepare_scene": [],
        "native_prepare_rays": [],
        "native_execute": [],
        "copy_back_and_scalar_materialize": [],
        "total": [],
    }
    outputs: list[dict[str, object]] = []

    for _ in range(iterations):
        total_start = time.perf_counter()
        case, elapsed = _time_call(robot_app.make_demo_case)
        phase_samples["python_input_construction"].append(elapsed)
        edge_rays = case["edge_rays"]
        obstacle_triangles = case["obstacle_triangles"]

        if backend == "optix" and summary_mode == "prepared_count":
            prepared_scene, elapsed = _time_call(lambda: rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles))
            phase_samples["native_prepare_scene"].append(elapsed)
            try:
                prepared_rays, elapsed = _time_call(lambda: rt.prepare_optix_rays_2d(edge_rays))
                phase_samples["native_prepare_rays"].append(elapsed)
                try:
                    hit_count, elapsed = _time_call(lambda: prepared_scene.count(prepared_rays))
                    phase_samples["native_execute"].append(elapsed)
                    phase_samples["copy_back_and_scalar_materialize"].append(0.0)
                    outputs.append({"hit_edge_count": int(hit_count)})
                finally:
                    prepared_rays.close()
            finally:
                prepared_scene.close()
        else:
            payload, elapsed = _time_call(lambda: robot_app.run_app(backend, "rows"))
            phase_samples["native_execute"].append(elapsed)
            phase_samples["copy_back_and_scalar_materialize"].append(0.0)
            outputs.append(
                {
                    "matches_oracle": bool(payload["matches_oracle"]),
                    "row_count": len(payload["rows"]),
                    "colliding_pose_count": len(payload["colliding_pose_ids"]),
                }
            )

        phase_samples["total"].append(time.perf_counter() - total_start)

    return {
        "app": "robot_collision_screening",
        "backend": backend,
        "summary_mode": summary_mode,
        "iterations": iterations,
        "optix_performance_class": rt.optix_app_performance_support("robot_collision_screening").performance_class,
        "phase_stats": {phase: _stats(samples) for phase, samples in phase_samples.items()},
        "last_output": outputs[-1] if outputs else {},
        "boundary": "Prepared OptiX count mode reports scalar hit-edge count only. It avoids Python row materialization but does not emit pose-level witness rows.",
    }


def list_apps() -> dict[str, object]:
    return {
        "supported_detailed_phase_apps": ("robot_collision_screening",),
        "optix_app_performance_matrix": {
            app: {
                "performance_class": support.performance_class,
                "note": support.note,
            }
            for app, support in rt.optix_app_performance_matrix().items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal691 OptiX app phase profiler.")
    parser.add_argument("--list-apps", action="store_true")
    parser.add_argument("--app", choices=("robot_collision_screening",), default="robot_collision_screening")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree", "optix"), default="cpu_python_reference")
    parser.add_argument("--summary-mode", choices=("rows", "prepared_count"), default="rows")
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args(argv)

    if args.list_apps:
        print(json.dumps(list_apps(), indent=2, sort_keys=True))
        return 0
    if args.iterations < 1:
        raise ValueError("--iterations must be positive")
    if args.summary_mode == "prepared_count" and args.backend != "optix":
        raise ValueError("--summary-mode prepared_count requires --backend optix")

    print(json.dumps(profile_robot_collision(args.iterations, args.backend, args.summary_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

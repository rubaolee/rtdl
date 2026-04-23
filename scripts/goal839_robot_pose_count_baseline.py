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

from examples import rtdl_robot_collision_screening_app as robot_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
import rtdsl as rt


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


def _summary_from_rows(rows: tuple[dict[str, object], ...], poses: tuple[dict[str, object], ...], ray_metadata: dict[int, dict[str, int]]) -> dict[str, Any]:
    summary = robot_app._summarize_collisions(rows, poses, ray_metadata)
    return {
        "pose_count": len(poses),
        "colliding_pose_count": len(summary["colliding_pose_ids"]),
        "colliding_pose_ids_sample": list(summary["colliding_pose_ids"][:10]),
    }


def _cpu_oracle_artifact(pose_count: int, obstacle_count: int, iterations: int) -> dict[str, Any]:
    row = load_goal835_row(
        app="robot_collision_screening",
        path_name="prepared_pose_flags",
        baseline_name="cpu_oracle_pose_count",
    )
    case, input_sec = _time_call(lambda: robot_app.make_scaled_case(pose_count=pose_count, obstacle_count=obstacle_count))
    rows_query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: rt.ray_triangle_any_hit_cpu(case["edge_rays"], case["obstacle_triangles"]))
        last_summary, post_sec = _time_call(
            lambda: _summary_from_rows(last_rows, case["poses"], case["ray_metadata"])
        )
        rows_query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    artifact = build_baseline_artifact(
        row=row,
        baseline_name="cpu_oracle_pose_count",
        source_backend="cpu_oracle",
        benchmark_scale={"pose_count": pose_count, "obstacle_count": obstacle_count, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=True,
        phase_seconds={
            "pose_and_obstacle_generation": input_sec,
            "ray_pack": 0.0,
            "backend_scene_prepare": 0.0,
            "pose_index_prepare": 0.0,
            "native_anyhit_query": _stats(rows_query_samples)["median_sec"],
            "scalar_copyback": 0.0,
            "oracle_validation_separate": 0.0,
        },
        summary=last_summary,
        notes=[
            "CPU oracle uses direct ray_triangle_any_hit_cpu traversal and compact pose-count postprocess.",
            "No separate backend scene prepare or pose-index prepare phase exists on the CPU oracle path.",
        ],
        validation={
            "method": "oracle path by construction",
            "matches_reference": True,
        },
    )
    return artifact


def _embree_artifact(pose_count: int, obstacle_count: int, iterations: int) -> dict[str, Any]:
    row = load_goal835_row(
        app="robot_collision_screening",
        path_name="prepared_pose_flags",
        baseline_name="embree_anyhit_pose_count_or_equivalent_compact_summary",
    )
    case, input_sec = _time_call(lambda: robot_app.make_scaled_case(pose_count=pose_count, obstacle_count=obstacle_count))
    oracle_rows, oracle_query_sec = _time_call(lambda: rt.ray_triangle_any_hit_cpu(case["edge_rays"], case["obstacle_triangles"]))
    oracle_summary, oracle_post_sec = _time_call(
        lambda: _summary_from_rows(oracle_rows, case["poses"], case["ray_metadata"])
    )
    prepared_kernel, prepare_sec = _time_call(lambda: rt.prepare_embree(robot_app.robot_edge_any_hit_kernel).bind(
        edge_rays=case["edge_rays"],
        obstacle_triangles=case["obstacle_triangles"],
    ))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    try:
        for _ in range(iterations):
            last_rows, query_sec = _time_call(prepared_kernel.run)
            last_summary, post_sec = _time_call(
                lambda: _summary_from_rows(tuple(last_rows), case["poses"], case["ray_metadata"])
            )
            query_samples.append(query_sec)
            postprocess_samples.append(post_sec)
    finally:
        close = getattr(prepared_kernel, "close", None)
        if callable(close):
            close()
    parity = last_summary == oracle_summary
    artifact = build_baseline_artifact(
        row=row,
        baseline_name="embree_anyhit_pose_count_or_equivalent_compact_summary",
        source_backend="embree",
        benchmark_scale={"pose_count": pose_count, "obstacle_count": obstacle_count, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=parity,
        phase_seconds={
            "pose_and_obstacle_generation": input_sec,
            "ray_pack": 0.0,
            "backend_scene_prepare": prepare_sec,
            "pose_index_prepare": 0.0,
            "native_anyhit_query": _stats(query_samples)["median_sec"],
            "scalar_copyback": 0.0,
            "oracle_validation_separate": oracle_query_sec + oracle_post_sec,
        },
        summary=last_summary,
        notes=[
            "Embree baseline uses prepared RTDL kernel binding and compact pose-count postprocess.",
            "This is an equivalent compact summary baseline, not a native scalar ABI.",
        ],
        validation={
            "method": "compare Embree compact pose summary against CPU oracle compact pose summary",
            "matches_reference": parity,
        },
    )
    return artifact


def build_artifact(*, backend: str, pose_count: int, obstacle_count: int, iterations: int) -> dict[str, Any]:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if pose_count <= 0 or obstacle_count <= 0:
        raise ValueError("pose_count and obstacle_count must be positive")
    if backend == "cpu":
        return _cpu_oracle_artifact(pose_count, obstacle_count, iterations)
    if backend == "embree":
        return _embree_artifact(pose_count, obstacle_count, iterations)
    raise ValueError(f"unsupported backend {backend}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write Goal836-valid robot pose-count baseline artifacts.")
    parser.add_argument("--backend", choices=("cpu", "embree"), required=True)
    parser.add_argument("--pose-count", type=int, default=200000)
    parser.add_argument("--obstacle-count", type=int, default=1024)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)
    artifact = build_artifact(
        backend=args.backend,
        pose_count=args.pose_count,
        obstacle_count=args.obstacle_count,
        iterations=args.iterations,
    )
    write_baseline_artifact(args.output_json, artifact)
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

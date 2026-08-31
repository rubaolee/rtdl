#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.apps.robotics import rtdl_robot_collision_screening_app as app  # noqa: E402


SCHEMA = "rtdl.goal3765.robot_collision_hiprt_prepared_group_flags_probe.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3765_robot_collision_hiprt_prepared_group_flags_a5000.json"
SCOPED_SOURCE_PATHS = (
    "src/native/hiprt/rtdl_hiprt_core.cpp",
    "src/native/hiprt/rtdl_hiprt_api.cpp",
    "src/rtdsl/hiprt_runtime.py",
    "src/rtdsl/generic_primitives.py",
    "examples/current/apps/robotics/rtdl_robot_collision_screening_app.py",
    "scripts/goal3765_robot_collision_hiprt_prepared_group_flags_probe.py",
    "tests/goal3765_hiprt_prepared_grouped_anyhit_flags_test.py",
)


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "amd_hardware_perf_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timing list")
    return float(statistics.median(values))


def _run_payload(*, pose_count: int, mode: str, skip_validation: bool) -> dict[str, Any]:
    if mode == "rows":
        return app.run_app(
            "hiprt",
            output_mode="pose_flags",
            pose_count=pose_count,
            obstacle_count=pose_count,
            skip_validation=skip_validation,
        )
    if mode == "prepared_group_flags":
        return app.run_app(
            "hiprt",
            optix_summary_mode="prepared_pose_flags",
            output_mode="pose_flags",
            pose_count=pose_count,
            obstacle_count=pose_count,
            skip_validation=skip_validation,
        )
    raise ValueError(f"unsupported mode {mode!r}")


def _correctness_case(*, pose_count: int) -> dict[str, Any]:
    row_payload = _run_payload(pose_count=pose_count, mode="rows", skip_validation=False)
    prepared_payload = _run_payload(pose_count=pose_count, mode="prepared_group_flags", skip_validation=False)
    return {
        "pose_count": pose_count,
        "row_route_matches_oracle": bool(row_payload["matches_oracle"]),
        "prepared_group_flags_matches_oracle": bool(prepared_payload["matches_oracle"]),
        "same_pose_flags": tuple(row_payload["pose_collision_flags"]) == tuple(prepared_payload["prepared_summary"]["pose_collision_flags"]),
        "row_native_continuation_backend": row_payload["native_continuation_backend"],
        "prepared_native_continuation_backend": prepared_payload["native_continuation_backend"],
        "claim_boundary": _claim_boundary(),
    }


def _time_case(*, pose_count: int, mode: str, warmup: int, repeat: int) -> dict[str, Any]:
    measured: list[float] = []
    runs: list[dict[str, Any]] = []
    last_payload: dict[str, Any] | None = None
    for iteration in range(warmup + repeat):
        start = time.perf_counter()
        payload = _run_payload(pose_count=pose_count, mode=mode, skip_validation=True)
        elapsed = time.perf_counter() - start
        is_warmup = iteration < warmup
        last_payload = payload
        colliding_count = int(
            payload.get("colliding_pose_count")
            if mode == "rows"
            else payload["prepared_summary"]["colliding_pose_count"]
        )
        print(
            f"[goal3765] mode={mode} pose_count={pose_count} "
            f"{'warmup' if is_warmup else 'repeat'} {iteration + 1}/{warmup + repeat} "
            f"elapsed={elapsed:.6f}s colliding_poses={colliding_count}",
            flush=True,
        )
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "colliding_pose_count": colliding_count,
            }
        )
        if not is_warmup:
            measured.append(elapsed)
    assert last_payload is not None
    return {
        "mode": mode,
        "pose_count": pose_count,
        "edge_ray_count": int(last_payload["edge_ray_count"]),
        "obstacle_triangle_count": int(last_payload["obstacle_triangle_count"]),
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured),
        "hot_total_sec": float(sum(measured)),
        "repeat": repeat,
        "warmup": warmup,
        "validation_mode": last_payload["validation_mode"],
        "native_continuation_active": bool(last_payload["native_continuation_active"]),
        "native_continuation_backend": str(last_payload["native_continuation_backend"]),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    correctness = [_correctness_case(pose_count=count) for count in args.correctness_pose_counts]
    timings_by_count = []
    for count in args.timing_pose_counts:
        rows = _time_case(pose_count=count, mode="rows", warmup=args.warmup, repeat=args.repeat)
        prepared = _time_case(
            pose_count=count,
            mode="prepared_group_flags",
            warmup=args.warmup,
            repeat=args.repeat,
        )
        timings_by_count.append(
            {
                "pose_count": count,
                "rows": rows,
                "prepared_group_flags": prepared,
                "prepared_vs_rows_ratio": (
                    float(rows["hot_median_sec"] / prepared["hot_median_sec"])
                    if prepared["hot_median_sec"] > 0.0
                    else None
                ),
                "claim_boundary": _claim_boundary(),
            }
        )
    return {
        "schema": SCHEMA,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "goal3765_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3765_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "correctness": correctness,
        "timings_by_count": timings_by_count,
        "summary": {
            "correctness_case_count": len(correctness),
            "all_correctness_cases_match_oracle": all(
                bool(row["row_route_matches_oracle"])
                and bool(row["prepared_group_flags_matches_oracle"])
                and bool(row["same_pose_flags"])
                for row in correctness
            ),
            "timing_case_count": len(timings_by_count),
            "max_timing_pose_count": max(row["pose_count"] for row in timings_by_count),
            "best_prepared_vs_rows_ratio": max(
                float(row["prepared_vs_rows_ratio"])
                for row in timings_by_count
                if row["prepared_vs_rows_ratio"] is not None
            ),
        },
        "interpretation": (
            "HIPRT prepared grouped any-hit flags are a generic group-threshold summary over "
            "prepared ray/triangle any-hit, used by the robot-collision example to avoid "
            "per-ray Python row materialization. This is NVIDIA CUDA/Orochi path evidence, "
            "not AMD hardware evidence."
        ),
        "claim_boundary": _claim_boundary(),
    }


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("count list must not be empty")
    if any(count <= 0 for count in counts):
        raise ValueError("counts must be positive")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3765 HIPRT prepared grouped any-hit flags probe.")
    parser.add_argument("--timing-pose-counts", default="64,128,256,512,1024")
    parser.add_argument("--correctness-pose-counts", default="32,128")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.timing_pose_counts = _parse_counts(args.timing_pose_counts)
    args.correctness_pose_counts = _parse_counts(args.correctness_pose_counts)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3765] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

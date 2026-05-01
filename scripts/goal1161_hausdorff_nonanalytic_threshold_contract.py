#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.reference import Point


GOAL = "Goal1161 Hausdorff non-analytic threshold contract"
DATE = "2026-04-30"
SCHEMA_VERSION = "goal1161_hausdorff_nonanalytic_threshold_contract_v1"


def _time_call(fn):
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


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
    return None


def _host() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def make_nonanalytic_point_sets(*, point_count: int) -> dict[str, tuple[Point, ...]]:
    """Build deterministic, non-tiled point sets for Hausdorff threshold gates.

    This intentionally avoids the authored four-point tiled fixture used by the
    app demo. Coordinates are quasi-jittered so a CPU reference must inspect the
    generated point cloud rather than multiplying a tiny analytic answer.
    """
    if point_count < 4:
        raise ValueError("point_count must be at least 4")

    width = max(2, int(math.sqrt(point_count)))
    points_a: list[Point] = []
    points_b: list[Point] = []
    for index in range(point_count):
        gx = index % width
        gy = index // width
        ax = gx + 0.071 * math.sin(index * 12.9898)
        ay = gy + 0.053 * math.cos(index * 78.233)
        # Most target points are close, while deterministic outliers keep the
        # threshold decision non-trivial in both directions.
        if index % 29 == 0:
            bx = ax + 0.74 + 0.03 * math.sin(index)
            by = ay - 0.49 + 0.02 * math.cos(index)
        elif index % 17 == 0:
            bx = ax - 0.46 + 0.01 * math.cos(index * 0.7)
            by = ay + 0.39 + 0.01 * math.sin(index * 0.7)
        else:
            bx = ax + 0.12 * math.sin(index * 0.31)
            by = ay + 0.10 * math.cos(index * 0.37)
        points_a.append(Point(id=index + 1, x=ax, y=ay))
        points_b.append(Point(id=1_000_001 + index, x=bx, y=by))
    return {"points_a": tuple(points_a), "points_b": tuple(points_b)}


def _covered_count(source: tuple[Point, ...], target: tuple[Point, ...], *, radius: float) -> int:
    radius_sq = radius * radius
    covered = 0
    for source_point in source:
        if any(
            (source_point.x - target_point.x) ** 2 + (source_point.y - target_point.y) ** 2 <= radius_sq + 1e-12
            for target_point in target
        ):
            covered += 1
    return covered


def _oracle(points_a: tuple[Point, ...], points_b: tuple[Point, ...], *, radius: float) -> dict[str, object]:
    covered_ab = _covered_count(points_a, points_b, radius=radius)
    covered_ba = _covered_count(points_b, points_a, radius=radius)
    return {
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "radius": radius,
        "covered_a_to_b": covered_ab,
        "covered_b_to_a": covered_ba,
        "within_threshold": covered_ab == len(points_a) and covered_ba == len(points_b),
    }


def _optix_threshold(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    radius: float,
    iterations: int,
) -> tuple[int, dict[str, float]]:
    prepare_start = time.perf_counter()
    prepared_context = rt.prepare_optix_fixed_radius_count_threshold_2d(target, max_radius=radius)
    prepare_sec = time.perf_counter() - prepare_start
    query_sec = 0.0
    close_sec = 0.0
    covered = 0
    with prepared_context as prepared:
        for _ in range(iterations):
            query_start = time.perf_counter()
            covered = int(prepared.count_threshold_reached(source, radius=radius, threshold=1))
            query_sec += time.perf_counter() - query_start
        if hasattr(prepared, "close"):
            close_start = time.perf_counter()
            prepared.close()
            close_sec += time.perf_counter() - close_start
    return covered, {
        "optix_prepare_sec": prepare_sec,
        "optix_query_sec": query_sec,
        "optix_close_sec": close_sec,
    }


def build_payload(
    *,
    mode: str,
    point_count: int,
    radius: float,
    iterations: int,
    skip_validation: bool,
) -> dict[str, Any]:
    if mode not in {"dry-run", "optix"}:
        raise ValueError("mode must be dry-run or optix")
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    case, input_build_sec = _time_call(lambda: make_nonanalytic_point_sets(point_count=point_count))
    points_a = case["points_a"]
    points_b = case["points_b"]

    oracle_result: dict[str, object] | None = None
    validation_sec = 0.0
    if mode == "dry-run" or not skip_validation:
        oracle_result, validation_sec = _time_call(lambda: _oracle(points_a, points_b, radius=radius))

    result: dict[str, object]
    timings: dict[str, object] = {
        "input_build_sec": input_build_sec,
        "validation_sec": validation_sec,
    }
    if mode == "dry-run":
        assert oracle_result is not None
        result = dict(oracle_result)
    else:
        covered_ab, timings_ab = _optix_threshold(points_a, points_b, radius=radius, iterations=iterations)
        covered_ba, timings_ba = _optix_threshold(points_b, points_a, radius=radius, iterations=iterations)
        timings.update(
            {
                "optix_prepare_sec": timings_ab["optix_prepare_sec"] + timings_ba["optix_prepare_sec"],
                "optix_query_sec": timings_ab["optix_query_sec"] + timings_ba["optix_query_sec"],
                "optix_close_sec": timings_ab["optix_close_sec"] + timings_ba["optix_close_sec"],
            }
        )
        within = covered_ab == len(points_a) and covered_ba == len(points_b)
        result = {
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "radius": radius,
            "covered_a_to_b": covered_ab,
            "covered_b_to_a": covered_ba,
            "within_threshold": within,
            "oracle_within_threshold": None if oracle_result is None else oracle_result["within_threshold"],
            "matches_oracle": None if oracle_result is None else within == oracle_result["within_threshold"],
        }

    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_commit": _source_commit(),
        "host": _host(),
        "parameters": {
            "mode": mode,
            "point_count": point_count,
            "radius": radius,
            "iterations": iterations,
            "skip_validation": skip_validation,
        },
        "scenario": {
            "app": "hausdorff_distance",
            "path_name": "directed_threshold_prepared_nonanalytic",
            "non_analytic_fixture": True,
            "replaces_blocked_tiled_scale_contract": True,
            "native_rt_path": "prepared OptiX fixed-radius threshold traversal",
            "result": result,
            "timings_sec": timings,
        },
        "cloud_claim_contract": {
            "claim_scope": (
                "prepared OptiX fixed-radius threshold traversal for non-analytic "
                "Hausdorff <= radius decisions"
            ),
            "non_claim": (
                "not exact Hausdorff distance, not KNN-row output, not a full "
                "whole-app speedup claim, and not public wording authorization"
            ),
            "required_phase_groups": (
                "input_build_sec",
                "validation_sec",
                "optix_prepare_sec",
                "optix_query_sec",
                "optix_close_sec",
            ),
            "activation_status": "eligible_for_next_real_rtx_batch_after_2_ai_review",
        },
        "valid": (
            point_count >= 4
            and radius >= 0
            and (mode == "dry-run" or skip_validation or result.get("matches_oracle") is True)
        ),
        "boundary": (
            "Goal1161 repairs the Hausdorff pre-cloud benchmark contract by replacing "
            "the previous analytic tiled fixture with a deterministic non-analytic "
            "threshold-decision point cloud. It does not run cloud, does not authorize "
            "public RTX speedup wording, and does not claim exact Hausdorff distance."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build/run a non-analytic Hausdorff threshold contract.")
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--point-count", type=int, default=2048)
    parser.add_argument("--radius", type=float, default=0.35)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = build_payload(
        mode=args.mode,
        point_count=args.point_count,
        radius=args.radius,
        iterations=args.iterations,
        skip_validation=args.skip_validation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "output_json": str(args.output_json)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

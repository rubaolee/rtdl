#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import socket
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_road_hazard_screening as road_app
from examples.reference.rtdl_release_reference import segment_polygon_hitcount_reference
from rtdsl.baseline_runner import load_representative_case


GOAL = "Goal933 prepared segment/polygon OptiX profiler"
DATE = "2026-04-25"
SCHEMA_VERSION = "goal933_prepared_segment_polygon_optix_contract_v1"


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


def _digest(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    normalized = tuple(
        sorted((int(row["segment_id"]), int(row["hit_count"])) for row in rows)
    )
    return {
        "row_count": len(normalized),
        "hit_sum": sum(hit_count for _, hit_count in normalized),
        "positive_count": sum(1 for _, hit_count in normalized if hit_count > 0),
    }


def _cloud_claim_contract(scenario: str) -> dict[str, object]:
    return {
        "claim_scope": (
            "prepared OptiX custom-AABB segment/polygon traversal with polygon BVH "
            "built once and reused across segment batches"
        ),
        "scenario": scenario,
        "non_claim": (
            "not a public speedup claim until a real RTX artifact is compared with "
            "same-semantics CPU/Embree/PostGIS baselines and reviewed"
        ),
        "required_phase_groups": (
            "input_build_sec",
            "optix_prepare_sec",
            "optix_query_sec",
            "python_postprocess_sec",
            "validation_sec",
            "optix_close_sec",
        ),
    }


def _profile_segment_hitcount(*, copies: int, iterations: int, mode: str, skip_validation: bool) -> dict[str, object]:
    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    case, input_sec = _time_call(lambda: load_representative_case("segment_polygon_hitcount", dataset))
    segments = case.inputs["segments"]
    polygons = case.inputs["polygons"]
    if mode == "dry-run":
        expected, reference_sec = _time_call(
            lambda: rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
        )
        return {
            "scenario": "segment_polygon_hitcount_prepared",
            "mode": mode,
            "dataset": dataset,
            "timings_sec": {
                "input_build_sec": input_sec,
                "cpu_reference_total_sec": reference_sec,
            },
            "result": {
                "segment_count": len(segments),
                "polygon_count": len(polygons),
                "reference_digest": _digest(tuple(expected)),
            },
        }

    prepared, prepare_sec = _time_call(lambda: rt.prepare_optix_segment_polygon_hitcount_2d(polygons))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last_digest: dict[str, object] = {"row_count": 0, "hit_sum": 0, "positive_count": 0}
    try:
        for _ in range(iterations):
            aggregate, query_sec = _time_call(lambda: prepared.aggregate(segments, positive_threshold=1))
            query_samples.append(query_sec)
            digest, postprocess_sec = _time_call(lambda: dict(aggregate))
            postprocess_samples.append(postprocess_sec)
            last_digest = digest
        expected_digest = None
        matches_oracle = None
        if not skip_validation:
            expected, validation_sec = _time_call(
                lambda: rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
            )
            validation_samples.append(validation_sec)
            expected_digest = _digest(tuple(expected))
            matches_oracle = last_digest == expected_digest
    finally:
        _, close_sec = _time_call(prepared.close)
    return {
        "scenario": "segment_polygon_hitcount_prepared",
        "mode": mode,
        "dataset": dataset,
        "iterations": iterations,
        "timings_sec": {
            "input_build_sec": input_sec,
            "optix_prepare_sec": prepare_sec,
            "optix_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "optix_close_sec": close_sec,
        },
        "result": {
            "segment_count": len(segments),
            "polygon_count": len(polygons),
            "actual_digest": last_digest,
            "expected_digest": expected_digest,
            "matches_oracle": matches_oracle,
        },
    }


def _profile_road_hazard(*, copies: int, iterations: int, mode: str, skip_validation: bool) -> dict[str, object]:
    case, input_sec = _time_call(lambda: road_app.make_demo_case(copies=copies))
    roads = case["roads"]
    hazards = case["hazards"]
    if mode == "dry-run":
        expected, reference_sec = _time_call(
            lambda: rt.run_cpu_python_reference(road_app.road_hazard_hitcount, **case)
        )
        digest = _digest(tuple(expected))
        return {
            "scenario": "road_hazard_prepared_summary",
            "mode": mode,
            "copies": copies,
            "timings_sec": {
                "input_build_sec": input_sec,
                "cpu_reference_total_sec": reference_sec,
            },
            "result": {
                "road_count": len(roads),
                "hazard_count": len(hazards),
                "priority_segment_count": sum(1 for row in expected if int(row["hit_count"]) >= 2),
                "reference_digest": digest,
            },
        }

    prepared, prepare_sec = _time_call(lambda: rt.prepare_optix_segment_polygon_hitcount_2d(hazards))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last_priority_count = 0
    try:
        for _ in range(iterations):
            priority_count, query_sec = _time_call(lambda: prepared.count_at_least(roads, threshold=2))
            query_samples.append(query_sec)
            _, postprocess_sec = _time_call(lambda: None)
            postprocess_samples.append(postprocess_sec)
            last_priority_count = int(priority_count)
        expected_digest = None
        expected_priority_count = None
        matches_oracle = None
        if not skip_validation:
            expected, validation_sec = _time_call(
                lambda: rt.run_cpu_python_reference(road_app.road_hazard_hitcount, **case)
            )
            validation_samples.append(validation_sec)
            expected_digest = _digest(tuple(expected))
            expected_priority_count = sum(1 for row in expected if int(row["hit_count"]) >= 2)
            matches_oracle = last_priority_count == expected_priority_count
    finally:
        _, close_sec = _time_call(prepared.close)
    return {
        "scenario": "road_hazard_prepared_summary",
        "mode": mode,
        "copies": copies,
        "iterations": iterations,
        "timings_sec": {
            "input_build_sec": input_sec,
            "optix_prepare_sec": prepare_sec,
            "optix_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "optix_close_sec": close_sec,
        },
        "result": {
            "road_count": len(roads),
            "hazard_count": len(hazards),
            "priority_segment_count": last_priority_count,
            "actual_digest": None,
            "expected_digest": expected_digest,
            "expected_priority_segment_count": expected_priority_count,
            "matches_oracle": matches_oracle,
        },
    }


def run_profile(
    *,
    scenario: str,
    copies: int,
    iterations: int,
    mode: str,
    skip_validation: bool,
) -> dict[str, object]:
    if scenario not in {"segment_polygon_hitcount_prepared", "road_hazard_prepared_summary"}:
        raise ValueError("unsupported scenario")
    if copies <= 0:
        raise ValueError("copies must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if mode not in {"dry-run", "run"}:
        raise ValueError("mode must be 'dry-run' or 'run'")
    profile = (
        _profile_segment_hitcount(copies=copies, iterations=iterations, mode=mode, skip_validation=skip_validation)
        if scenario == "segment_polygon_hitcount_prepared"
        else _profile_road_hazard(copies=copies, iterations=iterations, mode=mode, skip_validation=skip_validation)
    )
    result = profile.get("result", {})
    strict_failures: list[str] = []
    if mode == "run" and not skip_validation and result.get("matches_oracle") is not True:
        strict_failures.append("prepared OptiX rows did not match CPU reference digest")
    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": _host(),
        "cloud_claim_contract": _cloud_claim_contract(scenario),
        "strict_failures": strict_failures,
        "strict_pass": not strict_failures,
        "status": "pass" if not strict_failures else "fail",
        **profile,
        "boundary": (
            "This profiler only separates prepared OptiX setup from warm query "
            "execution. It does not promote road/segment apps or authorize speedup "
            "claims without real RTX artifact review."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile prepared OptiX segment/polygon traversal.")
    parser.add_argument(
        "--scenario",
        choices=("segment_polygon_hitcount_prepared", "road_hazard_prepared_summary"),
        default="segment_polygon_hitcount_prepared",
    )
    parser.add_argument("--copies", type=int, default=64)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--mode", choices=("dry-run", "run"), default="dry-run")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_profile(
        scenario=args.scenario,
        copies=args.copies,
        iterations=args.iterations,
        mode=args.mode,
        skip_validation=args.skip_validation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output_json": str(args.output_json)}, sort_keys=True))
    return 1 if payload["strict_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

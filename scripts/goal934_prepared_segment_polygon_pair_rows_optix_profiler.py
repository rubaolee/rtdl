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
from rtdsl.baseline_runner import load_representative_case
from rtdsl.reference import segment_polygon_anyhit_rows_cpu


GOAL = "Goal934 prepared segment/polygon pair-row OptiX profiler"
DATE = "2026-04-25"
SCHEMA_VERSION = "goal934_prepared_segment_polygon_pair_rows_optix_contract_v1"


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
        sorted((int(row["segment_id"]), int(row["polygon_id"])) for row in rows)
    )
    return {
        "row_count": len(normalized),
        "segment_id_sum": sum(segment_id for segment_id, _ in normalized),
        "polygon_id_sum": sum(polygon_id for _, polygon_id in normalized),
        "unique_segment_count": len({segment_id for segment_id, _ in normalized}),
        "unique_polygon_count": len({polygon_id for _, polygon_id in normalized}),
    }


def _cloud_claim_contract() -> dict[str, object]:
    return {
        "claim_scope": (
            "prepared OptiX custom-AABB segment/polygon pair-row traversal with "
            "polygon BVH built once, bounded output, and warm segment batches"
        ),
        "non_claim": (
            "not an unbounded row-output speedup claim until real RTX artifacts "
            "prove no overflow, CPU-reference parity, and same-semantics baseline review"
        ),
        "required_phase_groups": (
            "input_build_sec",
            "cpu_reference_total_sec",
            "optix_prepare_sec",
            "optix_query_sec",
            "python_postprocess_sec",
            "validation_sec",
            "optix_close_sec",
            "emitted_count",
            "copied_count",
            "overflowed",
        ),
    }


def run_profile(
    *,
    copies: int,
    iterations: int,
    output_capacity: int,
    mode: str,
    skip_validation: bool,
) -> dict[str, object]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")
    if mode not in {"dry-run", "run"}:
        raise ValueError("mode must be 'dry-run' or 'run'")

    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    case, input_sec = _time_call(lambda: load_representative_case("segment_polygon_anyhit_rows", dataset))
    segments = case.inputs["segments"]
    polygons = case.inputs["polygons"]
    expected, cpu_reference_sec = _time_call(lambda: segment_polygon_anyhit_rows_cpu(**case.inputs))
    expected_digest = _digest(tuple(expected))
    strict_failures: list[str] = []
    if len(expected) > output_capacity:
        strict_failures.append(
            f"output_capacity {output_capacity} is smaller than CPU reference row count {len(expected)}"
        )

    if mode == "dry-run":
        return {
            "goal": GOAL,
            "date": DATE,
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "host": _host(),
            "scenario": "segment_polygon_anyhit_rows_prepared_bounded",
            "mode": mode,
            "dataset": dataset,
            "iterations": iterations,
            "output_capacity": output_capacity,
            "cloud_claim_contract": _cloud_claim_contract(),
            "timings_sec": {
                "input_build_sec": input_sec,
                "cpu_reference_total_sec": cpu_reference_sec,
            },
            "result": {
                "segment_count": len(segments),
                "polygon_count": len(polygons),
                "expected_digest": expected_digest,
                "emitted_count": len(expected),
                "copied_count": min(len(expected), output_capacity),
                "overflowed": len(expected) > output_capacity,
                "matches_oracle": None,
            },
            "strict_failures": strict_failures,
            "strict_pass": not strict_failures,
            "status": "pass" if not strict_failures else "fail",
            "boundary": (
                "Dry-run validates the bounded-output contract and CPU reference only; "
                "it is not RTX execution evidence."
            ),
        }

    prepared, prepare_sec = _time_call(lambda: rt.prepare_optix_segment_polygon_anyhit_rows_2d(polygons))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last_result: dict[str, object] = {
        "rows": (),
        "emitted_count": 0,
        "copied_count": 0,
        "overflowed": False,
    }
    try:
        for _ in range(iterations):
            result, query_sec = _time_call(
                lambda: prepared.run_with_metadata(segments, output_capacity=output_capacity)
            )
            query_samples.append(query_sec)
            _, postprocess_sec = _time_call(lambda: _digest(tuple(result["rows"])))
            postprocess_samples.append(postprocess_sec)
            last_result = result
        actual_rows = tuple(last_result["rows"])
        actual_digest = _digest(actual_rows)
        validation_sec = 0.0
        matches_oracle = None
        if not skip_validation:
            _, validation_sec = _time_call(lambda: actual_digest == expected_digest)
            validation_samples.append(validation_sec)
            matches_oracle = actual_digest == expected_digest
            if matches_oracle is not True:
                strict_failures.append("prepared OptiX pair rows did not match CPU reference digest")
        if last_result["overflowed"]:
            strict_failures.append(
                f"prepared OptiX pair rows overflowed output capacity {output_capacity}; "
                f"emitted {last_result['emitted_count']}"
            )
    finally:
        _, close_sec = _time_call(prepared.close)

    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": _host(),
        "scenario": "segment_polygon_anyhit_rows_prepared_bounded",
        "mode": mode,
        "dataset": dataset,
        "iterations": iterations,
        "output_capacity": output_capacity,
        "cloud_claim_contract": _cloud_claim_contract(),
        "timings_sec": {
            "input_build_sec": input_sec,
            "cpu_reference_total_sec": cpu_reference_sec,
            "optix_prepare_sec": prepare_sec,
            "optix_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "optix_close_sec": close_sec,
        },
        "result": {
            "segment_count": len(segments),
            "polygon_count": len(polygons),
            "expected_digest": expected_digest,
            "actual_digest": actual_digest,
            "matches_oracle": matches_oracle,
            "emitted_count": last_result["emitted_count"],
            "copied_count": last_result["copied_count"],
            "overflowed": last_result["overflowed"],
        },
        "strict_failures": strict_failures,
        "strict_pass": not strict_failures,
        "status": "pass" if not strict_failures else "fail",
        "boundary": (
            "This profiler separates prepared OptiX setup from warm bounded pair-row "
            "query execution. It does not authorize public speedup claims without "
            "real RTX artifact intake and same-semantics baseline review."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile prepared OptiX segment/polygon pair-row traversal.")
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output-capacity", type=int, default=4096)
    parser.add_argument("--mode", choices=("dry-run", "run"), default="dry-run")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_profile(
        copies=args.copies,
        iterations=args.iterations,
        output_capacity=args.output_capacity,
        mode=args.mode,
        skip_validation=args.skip_validation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output_json": str(args.output_json)}, sort_keys=True))
    return 1 if payload["strict_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

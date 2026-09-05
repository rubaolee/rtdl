#!/usr/bin/env python3
"""Nonformal steady profile for the pinned PyOptiX relation baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time


def _measure(action):
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    args = parser.parse_args()
    if min(args.warmups, args.repetitions) <= 0:
        raise ValueError("positive timing counts required")

    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
    )
    from experiments.goal5798_premeasurement.workload import relation_workload

    fixture = relation_workload()
    ptx, compile_ns = _measure(
        lambda: baseline.compile_ptx(
            args.device_source.resolve(strict=True),
            args.optix_include.resolve(strict=True),
            args.cuda_include.resolve(strict=True),
        )
    )

    def create_pipeline():
        context, logger = baseline.make_context()
        pipeline, groups, logs = baseline.build_pipeline(
            context, ptx, task="relation"
        )
        sbt, keepalive = baseline.make_sbt(groups)
        return context, logger, pipeline, groups, logs, sbt, keepalive

    state, pipeline_ns = _measure(create_pipeline)
    context, _logger, pipeline, _groups, _logs, sbt, _keepalive = state
    prepared, prepare_ns = _measure(
        lambda: PyOptixRelationPrepared(
            baseline, context, pipeline, sbt, fixture
        )
    )

    def execute():
        return prepared.execute(validate_expected=False)

    def validate(result):
        if result["output"] != fixture["expected_rows"]:
            raise RuntimeError("PyOptiX relation output differs from oracle")
        if result["device_status"] or result["device_overflow"]:
            raise RuntimeError("PyOptiX relation device status failed")

    first, first_ns = _measure(execute)
    validate(first)
    for _ in range(args.warmups):
        validate(execute())
    samples = []
    for _ in range(args.repetitions):
        result, elapsed = _measure(execute)
        validate(result)
        samples.append(elapsed)
    print(json.dumps({
        "schema": "rtdl.goal5845.pyoptix_relation_profile.v1",
        "status": "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        "query_count": len(fixture["sources"]),
        "row_count": len(fixture["expected_rows"]),
        "first_public_ns": first_ns,
        "steady": {
            "sample_count": len(samples),
            "minimum_ns": min(samples),
            "median_ns": int(statistics.median(samples)),
            "maximum_ns": max(samples),
        },
        "setup_ns": {
            "device_compile": compile_ns,
            "pipeline": pipeline_ns,
            "prepare": prepare_ns,
        },
        "claim_boundary": {
            "formal_performance_claim_authorized": False,
            "external_review_complete": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

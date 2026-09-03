#!/usr/bin/env python3
"""Run the Goal5842R1 nonformal public-reuse/scalar-path diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

from experiments.goal5842_causal_admission.contracts import TRIANGLE_TASK
from experiments.goal5842_causal_admission.tasks import (
    build_task,
    build_triangle_auxiliary_program,
)
from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain
from rtdsl.v4_callback_numba_codegen import (
    FORMAL_NUMBA_CACHE_ENV,
    FORMAL_NUMBA_CACHE_MANIFEST_ENV,
    FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV,
    formal_numba_leaf_cache_lifecycle_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.goal5842r1.public_reuse_scalar_diagnostic.v1"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _milliseconds(samples_ns: list[int]) -> list[float]:
    return [value / 1_000_000.0 for value in samples_ns]


def _summary(samples_ns: list[int]) -> dict[str, object]:
    samples_ms = _milliseconds(samples_ns)
    return {
        "sample_count": len(samples_ms),
        "samples_ms": samples_ms,
        "median_ms": statistics.median(samples_ms),
        "minimum_ms": min(samples_ms),
        "maximum_ms": max(samples_ms),
    }


def _timed(callable_):
    started = time.perf_counter_ns()
    value = callable_()
    return value, time.perf_counter_ns() - started


def _materialize_samples(program, *, target, toolchain, repetitions: int):
    durations = []
    latest = None
    for _ in range(repetitions):
        latest, duration = _timed(
            lambda: program.materialize(target=target, toolchain=toolchain)
        )
        durations.append(duration)
    return latest, durations


def _execute_one(prepared, batch, *, diagnostics: bool):
    result, duration = _timed(
        lambda: prepared.execute(batch, include_diagnostics=diagnostics)
    )
    return result, duration


def _require_clean_exact_source() -> str:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise RuntimeError("Goal5842R1 runner requires a clean exact source checkout")
    return commit


def _gpu_row() -> dict[str, str]:
    fields = "name,uuid,compute_cap,driver_version,memory.total"
    row = subprocess.run(
        [
            "nvidia-smi",
            f"--query-gpu={fields}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()
    if len(row) != 1:
        raise RuntimeError("exactly one visible GPU is required")
    name, uuid, capability, driver, memory_mib = (
        item.strip() for item in row[0].split(",")
    )
    return {
        "name": name,
        "uuid": uuid,
        "compute_capability": capability,
        "driver_version": driver,
        "memory_total_mib": memory_mib,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--materialize-repetitions", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    args = parser.parse_args()
    if args.materialize_repetitions < 1 or args.warmups < 1 or args.repetitions < 2:
        raise ValueError("positive materialize/warmup counts and at least two repeats required")
    for name in (
        FORMAL_NUMBA_CACHE_ENV,
        FORMAL_NUMBA_CACHE_MANIFEST_ENV,
        FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV,
    ):
        if os.environ.get(name):
            raise RuntimeError(f"process-global cache configuration is forbidden: {name}")
    source_commit = _require_clean_exact_source()
    gpu = _gpu_row()
    capability = tuple(int(item) for item in gpu["compute_capability"].split("."))
    native = args.native.resolve(strict=True)
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
    )
    no_cache_toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
    )
    cache_root = args.cache_root.absolute()
    if cache_root.exists() or cache_root.is_symlink():
        raise FileExistsError(f"cache root must not exist before the run: {cache_root}")
    cache_policy = FormalNumbaLeafCachePolicy(cache_root)
    cached_toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        formal_leaf_cache=cache_policy,
    )
    task = build_task(TRIANGLE_TASK)
    expected_scalar = int(task.expected_output["weighted_sum"])
    expected_per_ray = tuple(int(value) for value in task.expected_output["per_ray"])
    program = build_triangle_auxiliary_program()

    _unused, no_cache_ns = _materialize_samples(
        program,
        target=target,
        toolchain=no_cache_toolchain,
        repetitions=args.materialize_repetitions,
    )
    cache_before = formal_numba_leaf_cache_lifecycle_metadata()
    _cache_fill, cache_fill_ns = _materialize_samples(
        program, target=target, toolchain=cached_toolchain, repetitions=1
    )
    cache_after_fill = formal_numba_leaf_cache_lifecycle_metadata()
    scalar_materialized, cache_warm_ns = _materialize_samples(
        program,
        target=target,
        toolchain=cached_toolchain,
        repetitions=args.materialize_repetitions,
    )
    diagnostic_materialized, diagnostic_materialize_ns = _materialize_samples(
        program, target=target, toolchain=cached_toolchain, repetitions=1
    )
    cache_after_warm = formal_numba_leaf_cache_lifecycle_metadata()

    scalar_prepared, scalar_prepare_ns = _timed(
        lambda: scalar_materialized.prepare(task.static_input)
    )
    diagnostic_prepared, diagnostic_prepare_ns = _timed(
        lambda: diagnostic_materialized.prepare(task.static_input)
    )
    try:
        scalar_first, scalar_first_ns = _execute_one(
            scalar_prepared, task.batch, diagnostics=False
        )
        diagnostic_first, diagnostic_first_ns = _execute_one(
            diagnostic_prepared, task.batch, diagnostics=True
        )
        if scalar_first.output != expected_scalar or diagnostic_first.output != expected_scalar:
            raise RuntimeError("first execution scalar mismatch")
        if scalar_first.details:
            raise RuntimeError("scalar path exposed diagnostic detail")
        if tuple(diagnostic_first.details["per_ray_u64"]) != expected_per_ray:
            raise RuntimeError("diagnostic per-ray oracle mismatch")
        for _ in range(args.warmups):
            scalar = scalar_prepared.execute(task.batch)
            diagnostic = diagnostic_prepared.execute(
                task.batch, include_diagnostics=True
            )
            if scalar.output != expected_scalar or diagnostic.output != expected_scalar:
                raise RuntimeError("warmup output mismatch")

        scalar_steady_ns: list[int] = []
        diagnostic_steady_ns: list[int] = []
        for index in range(args.repetitions):
            order = (False, True) if index % 2 == 0 else (True, False)
            for diagnostics in order:
                prepared = diagnostic_prepared if diagnostics else scalar_prepared
                result, duration = _execute_one(
                    prepared, task.batch, diagnostics=diagnostics
                )
                if result.output != expected_scalar:
                    raise RuntimeError("steady output mismatch")
                (diagnostic_steady_ns if diagnostics else scalar_steady_ns).append(
                    duration
                )
        scalar_boundary = scalar_prepared.lifecycle_receipt["provider_execution"]
        diagnostic_boundary = diagnostic_prepared.lifecycle_receipt["provider_execution"]
    finally:
        scalar_prepared.close()
        diagnostic_prepared.close()

    if scalar_boundary != {
        "schema": "rtdl.v4.triangle_reduction_execution_boundary.v1",
        "execution_path": "device_resident_checked_u64_scalar_v4",
        "prepared_query_input_reused": True,
        "per_ray_u64_materialized_on_host": False,
        "event_rows_materialized_on_host": False,
        "public_output_scalar_bytes": 8,
    }:
        raise RuntimeError(f"unexpected scalar execution boundary: {scalar_boundary!r}")
    if (
        diagnostic_boundary["execution_path"] != "diagnostic_per_ray_v2"
        or diagnostic_boundary["prepared_query_input_reused"] is not True
        or diagnostic_boundary["per_ray_u64_materialized_on_host"] is not True
    ):
        raise RuntimeError(f"unexpected diagnostic execution boundary: {diagnostic_boundary!r}")

    scalar_steady = _summary(scalar_steady_ns)
    diagnostic_steady = _summary(diagnostic_steady_ns)
    result = {
        "schema": SCHEMA,
        "status": "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        "source_commit": source_commit,
        "hardware": gpu,
        "toolchain": {
            "python": sys.version.split()[0],
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "optix_sdk": args.optix_sdk,
            "optix_include": str(args.optix_include.resolve(strict=True)),
            "cuda_include": str(args.cuda_include.resolve(strict=True)),
        },
        "native": {
            "path": str(native),
            "sha256": _sha256_file(native),
        },
        "workload": {
            "task": TRIANGLE_TASK,
            "input_sha256": task.input_sha256,
            "query_count": len(task.batch.queries),
            "triangle_count": len(task.static_input.triangles),
            "expected_scalar": expected_scalar,
            "expected_per_ray_sha256": hashlib.sha256(
                json.dumps(expected_per_ray, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
        },
        "cache": {
            "policy": "explicit_content_addressed_unsealed_create_then_reuse",
            "root": str(cache_root),
            "before": cache_before,
            "after_fill": cache_after_fill,
            "after_warm": cache_after_warm,
            "fill_materialize": _summary(cache_fill_ns),
            "uncached_materialize": _summary(no_cache_ns),
            "warm_materialize": _summary(cache_warm_ns),
            "diagnostic_owner_warm_materialize": _summary(
                diagnostic_materialize_ns
            ),
        },
        "prepare": {
            "scalar_owner_ms": scalar_prepare_ns / 1_000_000.0,
            "diagnostic_owner_ms": diagnostic_prepare_ns / 1_000_000.0,
        },
        "execute": {
            "scalar_first_ms": scalar_first_ns / 1_000_000.0,
            "diagnostic_first_ms": diagnostic_first_ns / 1_000_000.0,
            "scalar_steady": scalar_steady,
            "diagnostic_steady": diagnostic_steady,
            "diagnostic_over_scalar_steady_median": (
                diagnostic_steady["median_ms"] / scalar_steady["median_ms"]
            ),
            "scalar_boundary": scalar_boundary,
            "diagnostic_boundary": diagnostic_boundary,
        },
        "correctness": {
            "scalar_matches_exact_oracle": True,
            "diagnostic_scalar_matches_exact_oracle": True,
            "diagnostic_per_ray_matches_exact_oracle": True,
            "same_program_and_input_contract": True,
        },
        "claim_boundary": {
            "formal_performance_evidence": False,
            "paper_or_public_speedup_authorized": False,
            "goal5842_v12_modified": False,
            "purpose": "implementation repair diagnosis before a fresh formal baseline",
        },
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["result_sha256"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

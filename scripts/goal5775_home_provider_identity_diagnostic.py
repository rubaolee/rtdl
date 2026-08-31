#!/usr/bin/env python3
"""Observation-only causal screen for Goal5775 provider identity reuse."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import time

from goal5774_prepared_three_way_frontdoors import LANES, V2, V4, prepare_three_way
from rtdsl.v4_callback_numba_codegen import formal_numba_leaf_cache_lifecycle_metadata


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def run(
    *, runtime_path: Path, output: Path, label: str, repeat: int, method: str
) -> Path:
    if repeat < 2:
        raise ValueError("repeat must be at least two")
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    native = Path(runtime["native_library_path"]).resolve()
    if hashlib.sha256(native.read_bytes()).hexdigest() != runtime["native_library_sha256"]:
        raise RuntimeError("diagnostic native identity mismatch")
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)

    from rtdsl import physical_execution_provenance as provenance
    from rtdsl import optix_runtime
    library = optix_runtime._load_optix_library()

    def execute(owner, lane_id: str, call_index: int):
        if method == V4:
            call = owner.execute(call_index)
            receipt = call["raw_metadata"]["traversal_receipt"]
            return call, receipt
        with provenance.OptixTraversalAuditSession.open(
            library=library, library_path=native
        ) as audit:
            call = owner.execute(call_index)
            receipt = audit.finish(
                semantic_digest=call["dynamic_input_sha256"],
                output_digest=call["output_sha256"],
                route_identity=f"goal5775:{lane_id}:{method}:call{call_index}",
            )
        return call, receipt

    rows = []
    cache_before = formal_numba_leaf_cache_lifecycle_metadata()
    for lane in LANES:
        prepare_started = time.perf_counter()
        owner = prepare_three_way(lane.lane_id, method, runtime=runtime)
        prepare_seconds = time.perf_counter() - prepare_started
        try:
            activation, _activation_receipt = execute(owner, lane.lane_id, 2)
            if activation["matched"] is not True:
                raise RuntimeError(f"{lane.lane_id} activation mismatch")

            sha_calls = 0
            sha_seconds = 0.0
            read_calls = 0
            read_seconds = 0.0
            original_sha = provenance._sha256
            original_read_bytes = Path.read_bytes

            def observed_sha(path: Path) -> str:
                nonlocal sha_calls, sha_seconds
                started = time.perf_counter()
                result = original_sha(path)
                elapsed = time.perf_counter() - started
                if Path(path).resolve() == native:
                    sha_calls += 1
                    sha_seconds += elapsed
                return result

            def observed_read_bytes(path: Path) -> bytes:
                nonlocal read_calls, read_seconds
                started = time.perf_counter()
                result = original_read_bytes(path)
                elapsed = time.perf_counter() - started
                if Path(path).resolve() == native:
                    read_calls += 1
                    read_seconds += elapsed
                return result

            provenance._sha256 = observed_sha
            Path.read_bytes = observed_read_bytes
            calls = []
            try:
                for index in range(repeat):
                    call_index = index % 2
                    started = time.perf_counter()
                    call, receipt = execute(owner, lane.lane_id, call_index)
                    outer = time.perf_counter() - started
                    if call["matched"] is not True:
                        raise RuntimeError(f"{lane.lane_id} output mismatch")
                    if receipt["physical_executor_classification"] != "optix_traversal_observed":
                        raise RuntimeError(f"{lane.lane_id} traversal receipt failed")
                    calls.append({
                        "call_index": call_index,
                        "registered_seconds": call["registered_prepared_execution_seconds"],
                        "outer_seconds": outer,
                        "output_sha256": call["output_sha256"],
                        "provider_library_sha256": receipt["provider_library_sha256"],
                        "receipt_sha256": receipt["receipt_sha256"],
                    })
            finally:
                provenance._sha256 = original_sha
                Path.read_bytes = original_read_bytes
            if len({item["receipt_sha256"] for item in calls}) != len(calls):
                raise RuntimeError(f"{lane.lane_id} receipts were not fresh")
            seconds = [float(item["registered_seconds"]) for item in calls]
            rows.append({
                "lane_id": lane.lane_id,
                "app": lane.app,
                "paper_algorithm": lane.paper_algorithm,
                "prepare_seconds": prepare_seconds,
                "calls": calls,
                "registered_seconds_median": statistics.median(seconds),
                "native_provider_sha256_function_calls": sha_calls,
                "native_provider_sha256_function_seconds": sha_seconds,
                "native_provider_read_bytes_calls": read_calls,
                "native_provider_read_bytes_seconds": read_seconds,
                "native_provider_file_access_seconds": sha_seconds + read_seconds,
            })
        finally:
            owner.close()

    payload = {
        "schema": "rtdl.goal5775.home_provider_identity_diagnostic.v1",
        "label": label,
        "method": method,
        "observation_only": True,
        "formal_performance_row_created": False,
        "predicted_saving_claimed": False,
        "python_version": platform.python_version(),
        "native_library_sha256": runtime["native_library_sha256"],
        "repeat_per_lane": repeat,
        "lane_count": len(rows),
        "rows": rows,
        "formal_leaf_cache_before": cache_before,
        "formal_leaf_cache_after": formal_numba_leaf_cache_lifecycle_metadata(),
    }
    payload["result_sha256"] = _digest(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"diagnostic output already exists: {output}")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--repeat", type=int, default=6)
    parser.add_argument("--method", choices=(V2, V4), default=V4)
    args = parser.parse_args()
    print(run(
        runtime_path=args.runtime, output=args.output,
        label=args.label, repeat=args.repeat, method=args.method,
    ))


if __name__ == "__main__":
    main()

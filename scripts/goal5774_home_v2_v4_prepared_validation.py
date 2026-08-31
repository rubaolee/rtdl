#!/usr/bin/env python3
"""Home functional gate for the Goal5774 V2-direct/V4 prepared cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

import numba
import numpy as np

from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

from goal5774_prepared_three_way_frontdoors import (
    LANES, METHODS, V2, V4, prepare_three_way,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"]
        == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _runtime(native: Path, optix_include: Path, cuda_include: Path):
    return {
        "target": ReferenceTargetProfile(
            provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
            native_sha256=_sha(native), supports_custom_aabb=True,
            supports_builtin_triangle=True),
        "compute_capability": (6, 1),
        "optix_include": optix_include,
        "cuda_include": cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    runtime = _runtime(native, args.optix_include, args.cuda_include)

    from rtdsl import optix_runtime
    library = optix_runtime._load_optix_library()
    records = []
    for lane in LANES:
        for method in METHODS:
            owner = prepare_three_way(lane.lane_id, method, runtime=runtime)
            try:
                if method == V2:
                    with OptixTraversalAuditSession.open(
                        library=library, library_path=native) as audit:
                        activation = owner.execute(2)
                        activation_receipt = audit.finish(
                            semantic_digest=activation["dynamic_input_sha256"],
                            output_digest=activation["output_sha256"],
                            route_identity=(
                                f"goal5774:{lane.lane_id}:{method}:activation"),
                        )
                else:
                    activation = owner.execute(2)
                    activation_receipt = dict(
                        activation["raw_metadata"]["traversal_receipt"])
                if (
                    activation["matched"] is not True
                    or not _receipt_ok(activation_receipt)
                    or activation["registered_performance_observation"] is not False
                    or activation.get("activation_only") is not True
                ):
                    raise RuntimeError(
                        f"{lane.lane_id}:{method}:activation failed admission")
                activation["behavioral_traversal_receipt"] = activation_receipt
                calls = []
                for call_index in (0, 1):
                    if method == V2:
                        with OptixTraversalAuditSession.open(
                            library=library, library_path=native) as audit:
                            call = owner.execute(call_index)
                            receipt = audit.finish(
                                semantic_digest=call["dynamic_input_sha256"],
                                output_digest=call["output_sha256"],
                                route_identity=(
                                    f"goal5774:{lane.lane_id}:{method}:"
                                    f"call{call_index}"),
                            )
                    else:
                        call = owner.execute(call_index)
                        receipt = dict(call["raw_metadata"]["traversal_receipt"])
                    if call["matched"] is not True or not _receipt_ok(receipt):
                        raise RuntimeError(
                            f"{lane.lane_id}:{method}:call{call_index} failed admission")
                    call["behavioral_traversal_receipt"] = receipt
                    calls.append(call)
                if calls[0]["dynamic_input_sha256"] == calls[1]["dynamic_input_sha256"]:
                    raise RuntimeError(
                        f"{lane.lane_id}:{method} reused one dynamic request")
                if activation["dynamic_input_sha256"] in {
                    call["dynamic_input_sha256"] for call in calls
                }:
                    raise RuntimeError(
                        f"{lane.lane_id}:{method} activation request was not distinct")
                records.append({
                    "lane_id": lane.lane_id,
                    "app": lane.app,
                    "paper_algorithm": lane.paper_algorithm,
                    "method": method,
                    "prepare_count": 1,
                    "activation_count": 1,
                    "execute_count": 2,
                    "activation": activation,
                    "calls": calls,
                })
            finally:
                owner.close()

    if len(records) != 26 or sum(len(row["calls"]) for row in records) != 52:
        raise RuntimeError("Goal5774 Home cohort shape mismatch")
    native_shas = {
        call["behavioral_traversal_receipt"]["provider_library_sha256"]
        for row in records for call in row["calls"]
    }
    native_shas.update(
        row["activation"]["behavioral_traversal_receipt"]
        ["provider_library_sha256"] for row in records)
    if native_shas != {_sha(native)}:
        raise RuntimeError("Goal5774 Home cohort mixed native identities")
    result = {
        "schema": "rtdl.goal5774.home_v2_v4_prepared_functional.v1",
        "host": platform.node(),
        "gpu_scope": "Home GTX1070 CC6.1 behavioral OptiX; no RT silicon claim",
        "methods": list(METHODS),
        "lane_count": len(LANES),
        "owner_count": len(records),
        "call_count": 52,
        "activation_call_count": 26,
        "correct_call_count": 52,
        "correct_activation_call_count": 26,
        "behavioral_true_optix_call_count": 52,
        "behavioral_true_optix_activation_call_count": 26,
        "distinct_dynamic_request_pair_count": 26,
        "native_library_sha256": _sha(native),
        "records": records,
        "formal_worker": False,
        "registered_performance_observation": False,
        "timings_for_cost_estimation_only": True,
        "v3_required_or_executed": False,
        "pod_used_or_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        key: result[key] for key in (
            "lane_count", "owner_count", "call_count", "correct_call_count",
            "activation_call_count", "correct_activation_call_count",
            "behavioral_true_optix_call_count",
            "behavioral_true_optix_activation_call_count",
            "distinct_dynamic_request_pair_count", "native_library_sha256",
        )
    }, sort_keys=True))


if __name__ == "__main__":
    main()

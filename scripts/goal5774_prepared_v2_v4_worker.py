#!/usr/bin/env python3
"""One fresh-process prepared V2-direct or V4 formal worker."""

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

from goal5774_prepared_three_way_frontdoors import (
    LANE_BY_ID, METHODS, V2, prepare_three_way,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_receipt(receipt: dict[str, object]) -> None:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    if (
        receipt["physical_executor_classification"]
        != "optix_traversal_observed"
        or successful <= 0
        or int(snapshot["complete_context_launch_count"]) != successful
        or any(int(snapshot[name]) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        or not snapshot["first_traversable"]
        or not snapshot["last_traversable"]
    ):
        raise RuntimeError("formal prepared call lacks bound OptiX traversal")


def run_worker(
    *, lane_id: str, method: str, block_index: int,
    runtime_path: Path, output: Path,
) -> Path:
    if output.exists():
        raise FileExistsError(output)
    if lane_id not in LANE_BY_ID or method not in METHODS:
        raise ValueError("unknown Goal5774 lane or method")
    if not isinstance(block_index, int) or not 0 <= block_index < 8:
        raise ValueError("block_index must be in [0, 8)")
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    python_executable = Path(sys.executable).resolve()
    if (
        platform.python_version() != runtime["expected_python_version"]
        or numba.__version__ != runtime["expected_numba_version"]
        or np.__version__ != runtime["expected_numpy_version"]
        or _sha(python_executable) != runtime["python_executable_sha256"]
    ):
        raise RuntimeError("formal worker Python/Numba/NumPy identity mismatch")
    native = Path(str(runtime["native_library_path"])).resolve()
    if not native.is_file() or _sha(native) != runtime["native_library_sha256"]:
        raise RuntimeError("formal worker native identity mismatch")
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    from rtdsl import optix_runtime
    library = optix_runtime._load_optix_library()

    owner = prepare_three_way(lane_id, method, runtime=runtime)
    try:
        if method == V2:
            with OptixTraversalAuditSession.open(
                library=library, library_path=native) as audit:
                activation = owner.execute(2)
                activation_receipt = audit.finish(
                    semantic_digest=activation["dynamic_input_sha256"],
                    output_digest=activation["output_sha256"],
                    route_identity=(
                        f"goal5774:{lane_id}:{method}:block{block_index}:"
                        "activation"),
                )
        else:
            activation = owner.execute(2)
            activation_receipt = dict(
                activation["raw_metadata"]["traversal_receipt"])
        _validate_receipt(activation_receipt)
        if (
            activation["matched"] is not True
            or activation["registered_performance_observation"] is not False
            or activation.get("activation_only") is not True
        ):
            raise RuntimeError("formal activation failed admission")
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
                            f"goal5774:{lane_id}:{method}:block{block_index}:"
                            f"call{call_index}"),
                    )
            else:
                call = owner.execute(call_index)
                receipt = dict(call["raw_metadata"]["traversal_receipt"])
            _validate_receipt(receipt)
            call["behavioral_traversal_receipt"] = receipt
            calls.append(call)
    finally:
        owner.close()
    if calls[0]["dynamic_input_sha256"] == calls[1]["dynamic_input_sha256"]:
        raise RuntimeError("formal worker did not execute two distinct requests")
    if activation["dynamic_input_sha256"] in {
        call["dynamic_input_sha256"] for call in calls
    }:
        raise RuntimeError("formal activation request was not distinct")
    if any(call["matched"] is not True for call in calls):
        raise RuntimeError("formal worker output mismatch")

    payload = {
        "schema": "rtdl.goal5774.prepared_v2_v4_formal_worker.v1",
        "lane_id": lane_id,
        "app": LANE_BY_ID[lane_id].app,
        "paper_algorithm": LANE_BY_ID[lane_id].paper_algorithm,
        "method": method,
        "block_index": block_index,
        "parent_pid": os.getpid(),
        "python_executable": str(python_executable),
        "python_version": platform.python_version(),
        "runtime_sha256": _sha(runtime_path),
        "native_library_sha256": _sha(native),
        "bundle_sha256": runtime["bundle_sha256"],
        "prepared_identity_sha256": runtime["prepared_identity_sha256"],
        "target_identity_sha256": runtime["target_identity_sha256"],
        "formal_identity_sha256": runtime["formal_identity_sha256"],
        "prepare_count": 1,
        "activation_count": 1,
        "execute_count": 2,
        "activation": activation,
        "calls": calls,
        "comparator_inside_registered_timer": False,
        "formal_worker": True,
        "cold_result_replaced": False,
        "prepare_is_free": False,
        "v3_used_or_required": False,
        "default_selected_between_application_algorithms": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-id", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--block-index", type=int, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(run_worker(
        lane_id=args.lane_id, method=args.method,
        block_index=args.block_index, runtime_path=args.runtime,
        output=args.output))


if __name__ == "__main__":
    main()

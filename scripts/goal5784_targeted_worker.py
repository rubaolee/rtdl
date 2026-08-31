#!/usr/bin/env python3
"""Fresh-process Goal5784 worker, reusing the audited Goal5776 endpoint validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

import goal5776_real_scale_formal_worker as base
from goal5784_targeted_formal_contract import (
    UNIT_BY_ID, V2, V4, contract_sha256, schedule,
)
from goal5784_mechanism_binding import validate_triangle_reduction_receipts


def run_endpoint_with_mechanism_binding(
    *, unit_id: str, method: str, lifecycle: str,
    runtime: Mapping[str, object],
) -> dict[str, object]:
    import goal5776_real_scale_frontdoors as frontdoors

    unit = UNIT_BY_ID[unit_id]
    if method == V2:
        endpoint = dict(frontdoors.run_real_scale_endpoint(
            unit_id=unit_id, method=method, lifecycle=lifecycle,
            runtime=runtime))
        endpoint["goal5784_mechanism_binding"] = {
            "mode": "not_applicable_to_v2_direct",
        }
        return endpoint
    if method != V4:
        raise RuntimeError("Goal5784 unknown method for mechanism binding")
    if unit.app != "triangle_counting":
        endpoint = dict(frontdoors.run_real_scale_endpoint(
            unit_id=unit_id, method=method, lifecycle=lifecycle,
            runtime=runtime))
        endpoint["goal5784_mechanism_binding"] = {
            "schema": "rtdl.goal5784.mechanism_binding.v1",
            "mechanism_id": "canonical_packed_hierarchy_output_binding",
            "evidence_level": "frozen_source_route__not_fusion",
            "execution_source_sha256": runtime["execution_source_sha256"],
            "rt_barneshut_is_fusion": False,
        }
        return endpoint

    captured: list[dict[str, object]] = []
    patches: list[tuple[object, object]] = []
    original_load = frontdoors._load

    def observing_load(path: Path, name: str):
        module = original_load(path, name)
        if name == "goal5776_formal_triangle_v4":
            owner_type = module.PreparedSegmentedTriangleCountingV4
            original_execute = owner_type.execute

            def observed_execute(owner):
                result = original_execute(owner)
                segments = result.get("segments")
                if not isinstance(segments, list):
                    raise RuntimeError("Goal5784 Triangle result omitted segments")
                for segment in segments:
                    receipt = segment.get("checked_u64_weighted_reduction") \
                        if isinstance(segment, dict) else None
                    if not isinstance(receipt, dict):
                        raise RuntimeError(
                            "Goal5784 Triangle segment omitted checked reduction")
                    captured.append(dict(receipt))
                return result

            owner_type.execute = observed_execute
            patches.append((owner_type, original_execute))
        return module

    frontdoors._load = observing_load
    try:
        endpoint = dict(frontdoors.run_real_scale_endpoint(
            unit_id=unit_id, method=method, lifecycle=lifecycle,
            runtime=runtime))
    finally:
        frontdoors._load = original_load
        for owner_type, original_execute in reversed(patches):
            owner_type.execute = original_execute
    endpoint["goal5784_mechanism_binding"] = (
        validate_triangle_reduction_receipts(captured))
    return endpoint


def run_worker(*, runtime_path: Path, worker_index: int, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    base.schedule = schedule
    base.contract_sha256 = contract_sha256
    temporary = output.with_name(f".{output.name}.goal5776_base")
    if temporary.exists():
        raise FileExistsError(temporary)
    observed: dict[str, object] = {}

    def runner(**kwargs):
        endpoint = run_endpoint_with_mechanism_binding(**kwargs)
        observed["binding"] = endpoint["goal5784_mechanism_binding"]
        return endpoint

    base.run_worker(runtime_path=runtime_path, worker_index=worker_index,
                    output=temporary, runner=runner)
    payload = json.loads(temporary.read_text(encoding="utf-8"))
    payload["schema"] = "rtdl.goal5784.targeted_formal_worker.v1"
    payload["run_goal_id"] = 5784
    payload["mechanism_binding"] = observed["binding"]
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    payload["preregistration_sha256"] = runtime["preregistration_sha256"]
    payload["runtime_budget_sha256"] = runtime["runtime_budget_sha256"]
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.unlink()
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--worker-index", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(run_worker(
        runtime_path=args.runtime, worker_index=args.worker_index,
        output=args.output))


if __name__ == "__main__":
    main()

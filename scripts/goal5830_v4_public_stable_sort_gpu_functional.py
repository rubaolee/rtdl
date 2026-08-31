#!/usr/bin/env python3
"""Untimed functional GPU matrix for the public V4 stable-sort demo."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import subprocess
import sys

import examples.current.v4_public_stable_sort as stable_sort_module
from examples.current.v4_public_stable_sort import execute_stable_sort


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _machine_record() -> dict[str, str]:
    nvidia_smi = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,uuid,compute_cap",
            "--format=csv,noheader",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "nvidia_smi": nvidia_smi,
    }


def _case(
    case_id: str,
    values: tuple[int, ...],
    indexed_order: tuple[int, ...],
    source_order: tuple[int, ...],
    args: argparse.Namespace,
) -> dict[str, object]:
    result = execute_stable_sort(
        values,
        native=args.native,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
        any_hit_proof_sha256=args.any_hit_proof_sha256,
        indexed_order=indexed_order,
        source_order=source_order,
    )
    if result["sorted_records"] != result["python_stable_oracle"]:
        raise RuntimeError(f"{case_id}: stable oracle mismatch")
    if result["expected_rows_passed_into_execution"] is not False:
        raise RuntimeError(f"{case_id}: application oracle leaked into execution")
    if result["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError(f"{case_id}: no bound OptiX traversal receipt")
    return {"case_id": case_id, **result}


def run(args: argparse.Namespace) -> dict[str, object]:
    cases = [
        _case(
            "MAIN_DUPLICATE_DERANGED",
            (2, 1, 2, 0),
            (2, 0, 3, 1),
            (3, 2, 1, 0),
            args,
        ),
        _case(
            "MAIN_SECOND_PHYSICAL_ORDER",
            (2, 1, 2, 0),
            (1, 3, 0, 2),
            (1, 3, 0, 2),
            args,
        ),
        _case(
            "SIGNED_DUPLICATE",
            (-2, 0, -2, 1),
            (1, 3, 0, 2),
            (2, 0, 3, 1),
            args,
        ),
        _case("SINGLETON", (7,), (0,), (0,), args),
        _case(
            "MAXIMUM_EXACT_BINARY32_QUARTER_GRID",
            (1_398_101, 0),
            (1, 0),
            (0, 1),
            args,
        ),
    ]

    random_case_ids = []
    for seed in range(16):
        generator = random.Random(seed)
        count = 2 + seed % 7
        values = tuple(generator.randint(-8, 8) for _ in range(count))
        indexed_order = list(range(count))
        source_order = list(range(count))
        generator.shuffle(indexed_order)
        generator.shuffle(source_order)
        case_id = f"FROZEN_RANDOM_{seed:02d}"
        cases.append(_case(
            case_id,
            values,
            tuple(indexed_order),
            tuple(source_order),
            args,
        ))
        random_case_ids.append(case_id)

    overflow_result = None
    overflow_error = None
    try:
        overflow_result = execute_stable_sort(
            (2, 1, 2, 0),
            native=args.native,
            optix_include=args.optix_include,
            cuda_include=args.cuda_include,
            optix_sdk=args.optix_sdk,
            compute_capability=args.compute_capability,
            any_hit_proof_sha256=args.any_hit_proof_sha256,
            indexed_order=(2, 0, 3, 1),
            source_order=(3, 2, 1, 0),
            capacity_override=9,
        )
    except ValueError as error:
        overflow_error = {
            "type": type(error).__name__,
            "code": getattr(error, "code", None),
            "path": getattr(error, "path", None),
            "message": str(error),
        }
    if overflow_result is not None or overflow_error is None:
        raise RuntimeError("capacity 9 returned a partial application result")
    expected_overflow = {
        "type": "BoundedRelationError",
        "code": "capacity_overflow",
        "path": "rows",
    }
    if any(overflow_error.get(key) != value for key, value in expected_overflow.items()):
        raise RuntimeError(
            f"capacity failure had the wrong exact classification: {overflow_error}")
    for literal in ("observed_unique_count=10", "materialized=9", "capacity=9"):
        if literal not in overflow_error["message"]:
            raise RuntimeError(
                f"capacity failure omitted {literal!r}: {overflow_error}")

    main = cases[0]
    if main["primitive_index_attack"]["matches_oracle"] is not False:
        raise RuntimeError("main physical derangement did not expose primitive-index attack")

    return {
        "schema": "rtdl.goal5830.public_stable_sort_gpu_functional.v2",
        "status": "PASS",
        "main_case_id": "MAIN_DUPLICATE_DERANGED",
        "case_count": len(cases),
        "frozen_random_case_ids": random_case_ids,
        "cases": cases,
        "capacity_boundary": {
            "complete_capacity": 10,
            "complete_case_returned": True,
            "overflow_capacity": 9,
            "overflow_case_returned_result": False,
            "overflow_error": overflow_error,
        },
        "native_sha256": _sha256(args.native),
        "machine": _machine_record(),
        "example_source_path": str(Path(stable_sort_module.__file__).resolve()),
        "example_source_sha256": _sha256(Path(stable_sort_module.__file__).resolve()),
        "runner_source_sha256": _sha256(Path(__file__)),
        "any_hit_proof_authority_sha256": args.any_hit_proof_sha256,
        "proof_authority_scope": (
            "INHERITED_FROZEN_DIGEST__PROOF_BYTES_AND_SEMANTICS_NOT_REVALIDATED_"
            "BY_GOAL5830"
        ),
        "expected_rows_passed_into_execution": False,
        "sorting_algorithm_proved": False,
        "arbitrary_sorting_supported": False,
        "application_mapping_verified_by_rtdl": False,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--any-hit-proof-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    if args.output.exists():
        raise FileExistsError("Goal5830 result is create-only")
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

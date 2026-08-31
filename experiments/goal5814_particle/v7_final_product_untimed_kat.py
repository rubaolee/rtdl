#!/usr/bin/env python3
"""Untimed final-product qualification for Goal5814 v7.

This successor binds every repository-local module imported by the KAT, runs
the repaired public RTDL product on one exact success, one exact-core success,
and one deterministic device-status failure, and records no timing.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .formal_worker import _bundle_paths
from .measurement_protocol import (
    canonical_document,
    file_record,
    validate_live_target,
    validate_target_manifest,
)
from .untimed_dual_arm_kat import (
    _exact_core_caller_boundary,
    _run_exact_core_success,
    _run_expected_miss,
    _run_success,
    load_durable_particle_kat,
    prepare_public_verified_rtdlexe_kat_arm,
)


SCHEMA = "rtdl.goal5814.particle_v7_final_product_untimed_kat.v1"


class QualificationError(RuntimeError):
    """The exact v7 untimed qualification contract was violated."""


def _strict_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical_document(value) != raw:
        raise QualificationError(f"noncanonical JSON: {path}")
    return value


def _require_record(path: Path, record: Mapping[str, Any], label: str) -> None:
    expected = file_record(path.resolve(strict=True))
    if not isinstance(record, Mapping) \
            or record.get("bytes") != expected["bytes"] \
            or record.get("sha256") != expected["sha256"]:
        raise QualificationError(f"{label} identity differs")


def _control(value: tuple[int, int, int, int]) -> dict[str, int]:
    return {
        "validated_row_count": value[0],
        "first_error": value[1],
        "error_code": value[2],
        "status": value[3],
    }


def _success(value: Any) -> dict[str, Any]:
    return {
        "arm": value.arm,
        "control": _control(value.control),
        "exact": value.exact,
        "output_read_only": value.output_read_only,
        "ledger": asdict(value.ledger),
    }


def _failure(value: Any) -> dict[str, Any]:
    return {
        "arm": value.arm,
        "control": _control(value.control),
        "device_status_failure": value.device_status_failure,
        "ledger": asdict(value.ledger),
    }


def run(
    *, authority_root: Path, execution_root: Path, target: Path,
    preaction: Path,
) -> dict[str, Any]:
    authority_root = authority_root.resolve(strict=True)
    execution_root = execution_root.resolve(strict=True)
    target = target.resolve(strict=True)
    preaction = preaction.resolve(strict=True)
    source = Path(__file__).resolve(strict=True)
    value = _strict_json(preaction)
    if value.get("schema") != (
            "rtdl.goal5814.particle_v7_final_product_untimed_kat_"
            "preaction.v1") \
            or value.get("status") != (
                "FROZEN_FINAL_PRODUCT_UNTIMED_SUCCESS_FAILURE_QUALIFICATION") \
            or value.get("registered_timing_count") != 0:
        raise QualificationError("preaction semantic boundary differs")
    _require_record(source, value["source"], "qualification source")
    _require_record(target, value["target_manifest"], "target manifest")
    records = value.get("execution_dependencies")
    if not isinstance(records, Mapping) or not records:
        raise QualificationError("execution dependency records missing")
    for relative, record in records.items():
        if not isinstance(relative, str) or Path(relative).is_absolute() \
                or ".." in Path(relative).parts:
            raise QualificationError("execution dependency path invalid")
        _require_record(
            execution_root / relative, record,
            f"execution dependency {relative}")

    target_value = validate_target_manifest(
        target, root=authority_root, rehash=True, rehash_wheels=True)
    live_target = validate_live_target(target_value)
    bundle = load_durable_particle_kat(_bundle_paths(target_value))

    complete_arm = prepare_public_verified_rtdlexe_kat_arm(bundle)
    try:
        complete_success = _run_success(complete_arm, bundle)
        device_failure = _run_expected_miss(complete_arm, bundle)
    finally:
        complete_arm.close()

    core_arm = prepare_public_verified_rtdlexe_kat_arm(bundle)
    try:
        admitted = core_arm.admit_exact_core_input(
            bundle.success_queries, bundle.expected_output)
        exact_core_success = _run_exact_core_success(
            core_arm, bundle, admitted, _exact_core_caller_boundary)
    finally:
        core_arm.close()

    if device_failure.ledger.output_d2h_bytes != 0 \
            or device_failure.ledger.output_d2h_after_status_failure != 0:
        raise QualificationError("failure exposed output bytes")
    return {
        "schema": SCHEMA,
        "status": "PASS__REPAIRED_PRODUCT_EXACT_SUCCESS_AND_FAIL_CLOSED",
        "source": file_record(source),
        "preaction": file_record(preaction),
        "target_manifest": file_record(target),
        "live_target": live_target,
        "execution_dependencies": records,
        "steps": {
            "COMPLETE_PUBLIC_SUCCESS": _success(complete_success),
            "COMPLETE_PUBLIC_DEVICE_MISS": _failure(device_failure),
            "EXACT_CORE_PREVALIDATED_SUCCESS": _success(exact_core_success),
        },
        "execution_order": [
            "COMPLETE_PUBLIC_SUCCESS",
            "COMPLETE_PUBLIC_DEVICE_MISS",
            "EXACT_CORE_PREVALIDATED_SUCCESS",
        ],
        "registered_timing_count": 0,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-root", type=Path, required=True)
    parser.add_argument("--execution-root", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--preaction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output
    if output.exists():
        raise QualificationError("output already exists")
    encoded = canonical_document(run(
        authority_root=args.authority_root,
        execution_root=args.execution_root,
        target=args.target,
        preaction=args.preaction,
    ))
    descriptor = os.open(
        output, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644)
    try:
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise QualificationError("short output write")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    print(hashlib.sha256(encoded).hexdigest(), len(encoded))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

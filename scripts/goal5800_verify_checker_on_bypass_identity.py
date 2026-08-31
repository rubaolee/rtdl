#!/usr/bin/env python3
"""Fail closed unless checker-ON and bypass runs are structurally identical."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED = {
    "artifacts": {
        "device_source_sha256", "ptx_sha256",
        "module_compile_options_sha256", "program_group_manifest_sha256",
        "pipeline_manifest_sha256", "sbt_bytes_sha256",
        "gas_input_sha256", "gas_build_options_sha256",
        "launch_params_bytes_sha256",
    },
    "actions": {
        "launch_dimensions", "launch_count", "synchronization_count",
        "output_copy_api", "status_read_before_output", "oracle_sha256",
    },
    "observations": {
        "status_bytes_sha256", "output_bytes_sha256", "oracle_pass",
    },
}
TOP_LEVEL = {
    "schema", "checker_mode", "checker_decision", "structural_identity",
}


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_receipt(receipt: dict[str, Any], mode: str) -> None:
    if set(receipt) != TOP_LEVEL:
        raise RuntimeError(f"{mode} top-level schema is not exact")
    if receipt["schema"] != "rtdl.checker_on_bypass_execution_receipt.v1":
        raise RuntimeError(f"{mode} receipt schema mismatch")
    if receipt["checker_mode"] != mode:
        raise RuntimeError(f"{mode} receipt mode mismatch")
    if mode == "ON" and receipt["checker_decision"] != "ACCEPT":
        raise RuntimeError("checker-ON receipt did not accept")
    if mode == "BYPASS" and receipt["checker_decision"] != "NOT_RUN":
        raise RuntimeError("bypass receipt incorrectly carries a checker decision")
    identity = receipt["structural_identity"]
    if set(identity) != set(REQUIRED):
        raise RuntimeError(f"{mode} identity sections are not exact")
    for section, keys in REQUIRED.items():
        if set(identity[section]) != keys:
            raise RuntimeError(f"{mode} {section} keys are not exact")
    if identity["actions"]["launch_count"] < 1:
        raise RuntimeError(f"{mode} receipt has no launch")
    if identity["actions"]["synchronization_count"] < \
            identity["actions"]["launch_count"]:
        raise RuntimeError(f"{mode} receipt does not synchronize every launch")
    if identity["actions"]["status_read_before_output"] is not True:
        raise RuntimeError(f"{mode} reads output before status")
    if identity["observations"]["oracle_pass"] is not True:
        raise RuntimeError(f"{mode} oracle failed")


def verify(on: dict[str, Any], bypass: dict[str, Any]) -> dict[str, Any]:
    validate_receipt(on, "ON")
    validate_receipt(bypass, "BYPASS")
    on_identity = canonical(on["structural_identity"])
    bypass_identity = canonical(bypass["structural_identity"])
    if on_identity != bypass_identity:
        differing = []
        for section in REQUIRED:
            for key in REQUIRED[section]:
                if on["structural_identity"][section][key] != \
                        bypass["structural_identity"][section][key]:
                    differing.append(f"{section}.{key}")
        raise RuntimeError(f"checker ON/bypass structural mismatch: {differing}")
    return {
        "schema": "rtdl.goal5800.checker_on_bypass_structural_identity.v1",
        "status": "PASS__ARTIFACT_ACTION_OUTPUT_ORACLE_STRUCTURALLY_IDENTICAL",
        "identity_sha256": sha256_bytes(on_identity),
        "only_authorized_difference": "checker_mode_and_checker_decision",
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", type=Path, required=True)
    parser.add_argument("--bypass", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = verify(
        json.loads(args.on.read_bytes()), json.loads(args.bypass.read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

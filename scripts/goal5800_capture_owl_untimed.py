#!/usr/bin/env python3
"""Capture one untimed OWL residual execution and classify validation logs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


VALIDATION_ERROR_RE = re.compile(
    rb"^\[\s*(?:1|2)\]\[[^\]\r\n]+\]:", re.MULTILINE,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def command_output(argv: list[str]) -> dict[str, Any]:
    completed = subprocess.run(argv, capture_output=True, check=False)
    return {
        "argv": argv,
        "returncode": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", errors="replace"),
        "stderr": completed.stderr.decode("utf-8", errors="replace"),
    }


def verify_source_manifest(source_root: Path) -> tuple[dict[str, Any], str]:
    manifest_path = source_root / "GOAL5800_SOURCE_MANIFEST.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["schema"] != "rtdl.goal5800.owl_source_manifest.v1":
        raise RuntimeError("unexpected Goal5800 source manifest schema")
    expected_paths = set()
    for row in manifest["files"]:
        relative = row["path"]
        if relative in expected_paths:
            raise RuntimeError(f"duplicate manifest path: {relative}")
        expected_paths.add(relative)
        path = source_root / relative
        value = path.read_bytes()
        if len(value) != row["bytes"] or sha256_bytes(value) != row["sha256"]:
            raise RuntimeError(f"source manifest mismatch: {relative}")
    actual_paths = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            f"source path set mismatch: missing={sorted(expected_paths-actual_paths)}, "
            f"extra={sorted(actual_paths-expected_paths)}")
    return manifest, sha256_bytes(manifest_bytes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.binary.is_file():
        raise FileNotFoundError(args.binary)
    args.result_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.result_dir / "owl_raw_result.json"
    stdout_path = args.result_dir / "owl_runtime_stdout.bin"
    stderr_path = args.result_dir / "owl_runtime_stderr.bin"
    final_path = args.result_dir / "goal5800_owl_untimed_result.json"
    for path in (raw_path, stdout_path, stderr_path, final_path):
        if path.exists():
            raise FileExistsError(path)

    source_manifest, source_manifest_sha = verify_source_manifest(
        args.source_root)
    identity_path = args.source_root / "GOAL5800_STAGE_IDENTITY.json"
    identity_bytes = identity_path.read_bytes()
    identity = json.loads(identity_bytes)

    completed = subprocess.run(
        [str(args.binary), str(raw_path)], capture_output=True, check=False,
    )
    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"OWL residual executable failed: exit={completed.returncode}; "
            f"stderr_sha256={sha256_bytes(completed.stderr)}")
    raw = json.loads(raw_path.read_bytes())
    if raw.get("status") != "PASS":
        raise RuntimeError("OWL raw result did not pass")
    controls = raw.get("behavioral_controls", {})
    expected_controls = {
        "role_effect_closure",
        "payload_attribute_abi_ownership",
        "physical_geometry_binding",
        "device_status_continuation",
        "checked_program_executable_identity",
    }
    if set(controls) != expected_controls:
        raise RuntimeError("OWL control set is not exactly the frozen five")
    if not all(row.get("owl_accepted_and_executed") is True
               for row in controls.values()):
        raise RuntimeError("not every OWL control executed")

    validation_error_messages = VALIDATION_ERROR_RE.findall(completed.stderr)
    if validation_error_messages:
        raise RuntimeError(
            f"OptiX validation error/fatal messages: "
            f"{len(validation_error_messages)}")
    if raw["runtime_diagnostics"][
            "optix_validation_mode_requested_by_source_overlay"] != "ALL":
        raise RuntimeError("raw result did not bind validation mode ALL")

    machine = {
        "uname": command_output(["uname", "-a"]),
        "nvidia_smi": command_output([
            "nvidia-smi",
            "--query-gpu=name,compute_cap,driver_version",
            "--format=csv,noheader",
        ]),
        "nvcc": command_output(["nvcc", "--version"]),
        "cmake": command_output(["cmake", "--version"]),
    }
    for name, receipt in machine.items():
        if receipt["returncode"] != 0:
            raise RuntimeError(f"machine identity command failed: {name}")
    gpu_line = machine["nvidia_smi"]["stdout"].strip()
    pascal_no_rt_core = "GTX 1070" in gpu_line and ", 6.1," in gpu_line
    if not pascal_no_rt_core:
        raise RuntimeError(f"unexpected functional host GPU: {gpu_line!r}")

    final = {
        "schema": "rtdl.goal5800.owl_executable_residual.result.v1",
        "status": "PASS__FIVE_OF_FIVE_OWL_ACCEPTED_EXECUTED_WRONG__VALID_CONTROL_EXACT",
        "scope": {
            "untimed_functional_execution_only": True,
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
            "modern_rt_core_execution_claimed": False,
            "host_is_pascal_without_hardware_rt_cores": True,
            "optix_semantics_not_rtx_silicon_performance": True,
        },
        "owl_upstream": identity["owl_upstream"],
        "source_custody": {
            "source_manifest_sha256": source_manifest_sha,
            "source_file_count_excluding_manifest": len(source_manifest["files"]),
            "stage_identity_sha256": sha256_bytes(identity_bytes),
            "validation_overlay": identity["validation_overlay"],
            "harness": identity["harness"],
        },
        "executable": {
            "path_name": args.binary.name,
            "bytes": args.binary.stat().st_size,
            "sha256": sha256_file(args.binary),
            "process_exit_code": completed.returncode,
        },
        "runtime_capture": {
            "stdout_bytes": len(completed.stdout),
            "stdout_sha256": sha256_bytes(completed.stdout),
            "stderr_bytes": len(completed.stderr),
            "stderr_sha256": sha256_bytes(completed.stderr),
            "optix_validation_mode": "ALL",
            "optix_validation_error_or_fatal_message_count": 0,
            "optix_validation_error_classifier": (
                r"(?m)^\[\s*(?:1|2)\]\[[^\]\r\n]+\]:"
            ),
            "cuda_last_error": "SUCCESS",
        },
        "machine": machine,
        "nearby_valid": raw["nearby_valid"],
        "behavioral_controls": controls,
        "executed_residual_mechanism_count": len(controls),
        "goal5799_minimum_required_count": 3,
        "minimum_met": len(controls) >= 3,
        "claim_boundary": {
            "proves_owl_composition_accepts_these_protocol_defects": True,
            "proves_rtdl_rejection": False,
            "rtdl_rejection_authority_is_goal5797": True,
            "proves_owl_performance": False,
            "proves_rtdl_performance": False,
            "proves_modern_rtx_behavior": False,
        },
    }
    final_path.write_bytes(
        json.dumps(final, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": final["status"],
        "result_sha256": sha256_file(final_path),
        "executed_residual_mechanism_count": len(controls),
        "validation_error_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

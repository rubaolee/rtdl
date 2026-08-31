#!/usr/bin/env python3
"""Independent raw-byte verification of the Goal5800 OWL v5 result."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import re
import tarfile


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
BUNDLE = HISTORY / "goal5800_owl_untimed_functional_bundle_v5_20260824.tar.gz"
TWIN = HISTORY / "goal5800_owl_untimed_functional_bundle_v5_twin_20260824.tar.gz"
RECEIPT = HISTORY / "goal5800_owl_untimed_functional_bundle_v5_receipt_20260824.json"
RESULT_DIR = HISTORY / "goal5800_owl_v5_lx1_untimed_result_20260824"
TABLE = HISTORY / "goal5800_three_arm_responsibility_and_executable_residual_result_v5_20260824.json"
OUTPUT = HISTORY / "goal5800_owl_v5_independent_verification_v4_20260824.json"
VALIDATION_RE = re.compile(rb"^\[\s*(?:1|2)\]\[[^\]\r\n]+\]:", re.MULTILINE)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    bundle_bytes = BUNDLE.read_bytes()
    if bundle_bytes != TWIN.read_bytes():
        raise RuntimeError("v5 bundle twin is not byte-identical")
    receipt = json.loads(RECEIPT.read_bytes())
    if sha256_bytes(bundle_bytes) != receipt["bundle"]["sha256"]:
        raise RuntimeError("v5 bundle receipt mismatch")

    members: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(bundle_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported bundle member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"could not extract: {member.name}")
            members[member.name] = stream.read()
    root = "goal5800_owl_source/"
    manifest_bytes = members[root + "GOAL5800_SOURCE_MANIFEST.json"]
    manifest = json.loads(manifest_bytes)
    expected = set()
    for row in manifest["files"]:
        name = root + row["path"]
        expected.add(name)
        value = members[name]
        if len(value) != row["bytes"] or sha256_bytes(value) != row["sha256"]:
            raise RuntimeError(f"bundle source mismatch: {row['path']}")
    actual = set(members) - {root + "GOAL5800_SOURCE_MANIFEST.json"}
    if actual != expected:
        raise RuntimeError("bundle source path-set mismatch")
    if sha256_bytes(manifest_bytes) != receipt["source_manifest"]["sha256"]:
        raise RuntimeError("source manifest receipt mismatch")

    final_path = RESULT_DIR / "goal5800_owl_untimed_result.json"
    raw_path = RESULT_DIR / "owl_raw_result.json"
    build_path = RESULT_DIR / "goal5800_owl_build_receipt.json"
    final = json.loads(final_path.read_bytes())
    raw = json.loads(raw_path.read_bytes())
    build = json.loads(build_path.read_bytes())
    if build["configure"]["returncode"] != 0 or build["build"]["returncode"] != 0:
        raise RuntimeError("v5 configure/build did not pass")
    for phase in ("configure", "build"):
        for channel in ("stdout", "stderr"):
            path = RESULT_DIR / f"cmake_{phase}_{channel}.bin"
            if sha256_file(path) != build[phase][f"{channel}_sha256"]:
                raise RuntimeError(f"build log mismatch: {phase}/{channel}")
    runtime_stdout = (RESULT_DIR / "owl_runtime_stdout.bin").read_bytes()
    runtime_stderr = (RESULT_DIR / "owl_runtime_stderr.bin").read_bytes()
    if VALIDATION_RE.findall(runtime_stderr):
        raise RuntimeError("independent classifier found validation error/fatal")
    if runtime_stderr or runtime_stdout != b"GOAL5800_OWL_UNTIMED_FUNCTIONAL_PASS\n":
        raise RuntimeError("runtime stdout/stderr boundary mismatch")
    binary = RESULT_DIR / "goal5800-owl-residual"
    if sha256_file(binary) != final["executable"]["sha256"]:
        raise RuntimeError("preserved executable hash mismatch")

    expected_controls = {
        "role_effect_closure": {
            "output_per_ray": [1, 1, 0, 1], "output_weighted_sum": 11},
        "payload_attribute_abi_ownership": {"output": [[100, 0], [101, 1]]},
        "physical_geometry_binding": {"output": [[100, 20], [101, 10]]},
        "device_status_continuation": {
            "device_overflow": 1, "raw_event_count": 8,
            "returned_row_count": 7, "partial_result_consumed": True},
        "checked_program_executable_identity": {
            "output_per_ray": [6, 4, 0, 2], "output_weighted_sum": 32},
    }
    if set(final["behavioral_controls"]) != set(expected_controls):
        raise RuntimeError("final control set mismatch")
    for mechanism, fields in expected_controls.items():
        row = final["behavioral_controls"][mechanism]
        if row["owl_accepted_and_executed"] is not True:
            raise RuntimeError(f"control did not execute: {mechanism}")
        for key, value in fields.items():
            if row[key] != value:
                raise RuntimeError(f"wrong output mismatch: {mechanism}.{key}")
    if final["nearby_valid"] != {
            "relation": [[100, 10], [101, 20]],
            "triangle_per_ray": [3, 2, 0, 1],
            "triangle_weighted_sum": 16}:
        raise RuntimeError("nearby valid control mismatch")
    if raw["behavioral_controls"] != final["behavioral_controls"]:
        raise RuntimeError("raw/final behavioral controls differ")
    if final["source_custody"]["source_manifest_sha256"] != \
            sha256_bytes(manifest_bytes):
        raise RuntimeError("remote result did not bind bundle source manifest")
    if final["scope"]["registered_performance_timing_count"] != 0 or \
            final["scope"]["modern_rt_core_execution_claimed"]:
        raise RuntimeError("result scope widened")

    table = json.loads(TABLE.read_bytes())
    if table["executed_summary"] != {
            "owl_executed_protocol_invalid_count": 5,
            "owl_exact_silent_wrong_output_count": 4,
            "owl_status_before_consume_violation_count": 1,
            "owl_goal5799_minimum_required": 3,
            "owl_minimum_met": True,
            "owl_nearby_valid_control_exact": True,
            "raw_pyoptix_executed_protocol_invalid_count": 5,
            "raw_pyoptix_exact_silent_wrong_output_count": 4,
            "raw_pyoptix_status_before_consume_violation_count": 1,
            "rtdl_launch_prevented_count": 5}:
        raise RuntimeError("three-arm summary mismatch")

    result = {
        "schema": "rtdl.goal5800.owl_v5_independent_verification.v2",
        "status": (
            "PASS__RAW_BYTES_RECOUNTED__FOUR_EXACT_SILENT_WRONG_OUTPUTS__"
            "ONE_STATUS_ENFORCEMENT_VIOLATION__ZERO_VALIDATION_ERRORS"),
        "bundle_sha256": sha256_bytes(bundle_bytes),
        "bundle_twin_byte_identical": True,
        "bundle_source_files_verified": len(manifest["files"]),
        "source_manifest_sha256": sha256_bytes(manifest_bytes),
        "configure_returncode": 0,
        "build_returncode": 0,
        "runtime_returncode": final["executable"]["process_exit_code"],
        "runtime_stderr_bytes": len(runtime_stderr),
        "independent_validation_error_or_fatal_count": 0,
        "nearby_valid_control_exact": True,
        "owl_executed_protocol_invalid_count": 5,
        "owl_exact_silent_wrong_output_count": 4,
        "owl_status_before_consume_violation_count": 1,
        "goal5799_minimum_required": 3,
        "minimum_met": True,
        "preserved_executable_sha256": sha256_file(binary),
        "final_result_sha256": sha256_file(final_path),
        "three_arm_table_sha256": sha256_file(TABLE),
        "registered_performance_timing_count": 0,
        "modern_rt_core_execution_claimed": False,
    }
    OUTPUT.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

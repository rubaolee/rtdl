#!/usr/bin/env python3
"""Independent verifier for controlling Goal5801 A2 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import tarfile


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    files = {}
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() \
                    or member.islnk():
                raise RuntimeError(f"unsafe member: {member.name}")
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None or member.name in files:
                    raise RuntimeError(f"invalid member: {member.name}")
                files[member.name] = stream.read()
    manifest = json.loads(files["manifest.json"])
    if set(files) != {"manifest.json"} | {
            str(row["path"]) for row in manifest["files"]}:
        raise RuntimeError("manifest/archive path-set mismatch")
    for row in manifest["files"]:
        value = files[str(row["path"])]
        if len(value) != row["bytes"] or sha256(value) != row["sha256"]:
            raise RuntimeError(f"payload mismatch: {row['path']}")
    result = json.loads(files["evidence/lifecycle_result.json"])
    relation = result["relation"]["failed_predecessor_hostile"]
    triangle = result["triangle"]["oracle_hostile"]
    if result["registered_timing_count"] != 0 \
            or relation["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or relation["same_bytes_recovery_device_status"][
                "native_source_build_count_delta"] != 1 \
            or relation["same_bytes_recovery_device_status"][
                "prepared_input_reused"] \
            or relation["committed_repeat_device_status"][
                "native_source_build_count_delta"] != 0 \
            or not relation["committed_repeat_device_status"][
                "prepared_input_reused"] \
            or triangle["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or triangle["same_bytes_recovery_output"] != 9 \
            or triangle["same_bytes_recovery_device_status"][
                "prepared_input_reused"] \
            or files["evidence/nvrtc_lifecycle.log"]:
        raise RuntimeError("A2 functional/hostile contract mismatch")
    runtime = files["source/v4_rtdlexe.py"].decode("utf-8")
    exports = files["source/__init__.py"].decode("utf-8")
    docs = files["source/v4_rtdlexe_deployment.md"].decode("utf-8")
    trust_source = files["source/goal5801_rtdlexe_trust.py"]
    trust_tests = files["source/goal5801_rtdlexe_runtime_test.py"].decode(
        "utf-8")
    for literal in (
            "expected_reduced_u64", "RX044_NATIVE_REUSE_MISMATCH",
            "self._commit_source_cache()"):
        if literal not in runtime:
            raise RuntimeError(f"runtime repair missing: {literal}")
    for literal in (
            "RTDLExecutableBoundedRelationBatch",
            "RTDLExecutableTriangleReductionBatch"):
        if literal not in exports or literal not in docs:
            raise RuntimeError(f"distinct public name missing: {literal}")
    if sha256(trust_source) != (
            "4fde32a523264d33e5f05c14f3939c3b7bb47d3f50865a2ad60d788db547abb2") \
            or "type(authority[\"authority_version\"]) is not int" \
            not in trust_source.decode("utf-8") \
            or "test_offline_freeze_rejects_lossy_authority_scalar_types" \
            not in trust_tests:
        raise RuntimeError("hardened test-trust source/test identity mismatch")
    native_sha = sha256(files["native/librtdl_optix.so"])
    if any(receipt["provider_library_sha256"] != native_sha for receipt in (
            result["relation"]["traversal_receipt"],
            result["triangle"]["traversal_receipt"])):
        raise RuntimeError("native/receipt identity mismatch")
    print(json.dumps({
        "status": "PASS",
        "archive_sha256": sha256(open(args.archive, "rb").read()),
        "payload_count": len(manifest["files"]),
        "native_sha256": native_sha,
        "relation_recovery_build_delta": 1,
        "relation_repeat_build_delta": 0,
        "triangle_oracle_failure": triangle["failure_code"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

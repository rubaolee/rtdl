#!/usr/bin/env python3
"""Independent byte/semantic verifier for Goal5801 A1 evidence."""

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
    files: dict[str, bytes] = {}
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() \
                    or member.islnk():
                raise RuntimeError(f"unsafe archive member: {member.name}")
            if not member.isfile():
                continue
            if member.name in files:
                raise RuntimeError(f"duplicate member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable member: {member.name}")
            files[member.name] = stream.read()
    manifest = json.loads(files["manifest.json"])
    expected_names = {"manifest.json"} | {
        str(row["path"]) for row in manifest["files"]}
    if set(files) != expected_names:
        raise RuntimeError("archive/manifest payload set mismatch")
    for row in manifest["files"]:
        value = files[str(row["path"])]
        if len(value) != row["bytes"] or sha256(value) != row["sha256"]:
            raise RuntimeError(f"payload identity mismatch: {row['path']}")
    result = json.loads(files["evidence/lifecycle_result.json"])
    hostile = result["relation"]["failed_predecessor_hostile"]
    if result["registered_timing_count"] != 0 \
            or hostile["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or hostile["same_bytes_recovery_device_status"][
                "native_source_build_count_delta"] != 1 \
            or hostile["same_bytes_recovery_device_status"][
                "prepared_input_reused"] \
            or hostile["committed_repeat_device_status"][
                "native_source_build_count_delta"] != 0 \
            or not hostile["committed_repeat_device_status"][
                "prepared_input_reused"] \
            or files["evidence/nvrtc_lifecycle.log"]:
        raise RuntimeError("cache-commit hostile contract mismatch")
    native_sha = sha256(files["native/librtdl_optix.so"])
    receipts = (
        result["relation"]["traversal_receipt"],
        result["triangle"]["traversal_receipt"],
    )
    if any(row["provider_library_sha256"] != native_sha for row in receipts):
        raise RuntimeError("traversal receipt/native identity mismatch")
    print(json.dumps({
        "status": "PASS",
        "archive_sha256": sha256(open(args.archive, "rb").read()),
        "payload_count": len(manifest["files"]),
        "native_sha256": native_sha,
        "failed_predecessor_failure": hostile["failure_code"],
        "recovery_build_delta": 1,
        "repeat_build_delta": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

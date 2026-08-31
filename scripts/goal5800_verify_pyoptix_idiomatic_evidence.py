#!/usr/bin/env python3
"""Repository-independent verifier for Goal5800's untimed PyOptiX arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import tarfile


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


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
                raise RuntimeError(f"duplicate archive member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            files[member.name] = stream.read()
    manifest = json.loads(files["MANIFEST.json"])
    result_bytes = files["idiomatic_pyoptix_untimed.json"]
    environment_bytes = files["environment.json"]
    if sha256(result_bytes) != manifest["result"]["sha256"] \
            or len(result_bytes) != manifest["result"]["bytes"] \
            or sha256(environment_bytes) != manifest["environment"]["sha256"] \
            or len(environment_bytes) != manifest["environment"]["bytes"]:
        raise RuntimeError("top-level evidence identity mismatch")
    result = json.loads(result_bytes)
    environment = json.loads(environment_bytes)
    distribution_rows = []
    for name, value in sorted(files.items()):
        prefix = "installed_distribution/"
        if name.startswith(prefix):
            distribution_rows.append({
                "path": name.removeprefix(prefix),
                "bytes": len(value),
                "sha256": sha256(value),
            })
    executed_rows = []
    for name, value in sorted(files.items()):
        prefix = "executed_source/"
        if name.startswith(prefix):
            executed_rows.append({
                "path": name.removeprefix(prefix),
                "bytes": len(value),
                "sha256": sha256(value),
            })
    if distribution_rows != result["pyoptix_loaded_distribution_manifest"]["files"] \
            or sha256(canonical(distribution_rows)) != manifest[
                "installed_distribution_files_sha256"]:
        raise RuntimeError("installed distribution payload mismatch")
    if executed_rows != environment["executed_sources"] \
            or sha256(canonical(executed_rows)) != manifest[
                "executed_source_files_sha256"]:
        raise RuntimeError("executed source payload mismatch")
    expected = {
        "status": "PASS__UNTIMED_FUNCTIONAL",
        "arm": "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API__IDIOMATIC_BULK",
        "pyoptix_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
        "pyoptix_tree": "0bf0ec24efb4a43f129aee25dd265aa8149374e3",
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "optix_validation": "PASS",
        "optix_validation_error_message_count": 0,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise RuntimeError(f"result claim mismatch: {key}")
    if result["relation"]["launch_count"] != 2 \
            or len(result["relation"]["output"]) != 4096 \
            or result["triangle"]["launch_count"] != 1 \
            or len(result["triangle"]["per_ray"]) != 16384 \
            or result["triangle"]["weighted_sum"] != 65530:
        raise RuntimeError("functional output shape/value mismatch")
    print(json.dumps({
        "status": "PASS",
        "archive_sha256": sha256(open(args.archive, "rb").read()),
        "distribution_file_count": len(distribution_rows),
        "executed_source_file_count": len(executed_rows),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

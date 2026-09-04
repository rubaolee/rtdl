#!/usr/bin/env python3
"""Safely verify and independently recount a downloaded Goal5843 archive."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
from typing import Any

from experiments.goal5843_post_r1_baseline.contracts import (
    BOUND_ARTIFACTS_SCHEMA,
    CACHE_PREPARATION_SCHEMA,
    EXECUTION_AUTHORITY_SCHEMA,
    ORACLE_WITNESS_SCHEMA,
    digest,
    load_preregistration,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json
from scripts.goal5843_independent_recount import build_recount


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_VERIFICATION_SCHEMA = "rtdl.goal5843.downloaded_archive_verification.v1"
KEY_EXPORTS = (
    "CACHE_PREPARATION.json",
    "INDEPENDENT_ORACLE_WITNESS.json",
    "EXECUTION_AUTHORITY.json",
    "BOUND_ARTIFACTS.json",
    "TRANSACTION_STATUS.json",
    "POD_RECOUNT.json",
)


def safe_member_path(name: str) -> PurePosixPath:
    if not name or name.startswith("/") or "\\" in name:
        raise RuntimeError(f"unsafe archive member path: {name!r}")
    path = PurePosixPath(name)
    if not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise RuntimeError(f"unsafe archive member path: {name!r}")
    return path


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def verify_seal(value: dict[str, Any], field: str, label: str) -> None:
    observed = value.get(field)
    unsealed = dict(value)
    unsealed.pop(field, None)
    if not isinstance(observed, str) or digest(unsealed) != observed:
        raise RuntimeError(f"{label} seal mismatch")


def export_create_only(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with source.open("rb") as input_stream, os.fdopen(
            descriptor, "wb", closefd=False
        ) as output_stream:
            for block in iter(lambda: input_stream.read(1024 * 1024), b""):
                output_stream.write(block)
            output_stream.flush()
            os.fsync(output_stream.fileno())
    finally:
        os.close(descriptor)


def expected_preserved_artifacts(authority: dict[str, Any]) -> dict[str, dict[str, object]]:
    paths = authority["execution_paths"]
    pyoptix = authority["pyoptix"]
    expected = {
        "execution_paths.native_library": {
            "archived_path": "native/librtdl_optix.so",
            "sha256": paths["native_library_sha256"],
        },
        "execution_paths.native_build_manifest": {
            "archived_path": "native/NATIVE_BUILD_MANIFEST.json",
            "sha256": paths["native_build_manifest_sha256"],
        },
        "execution_paths.direct_binary": {
            "archived_path": "direct/goal5843_direct_measurement",
            "sha256": paths["direct_binary_sha256"],
        },
    }
    for row in pyoptix["module_tree"]["files"]:
        relative = str(row["path"])
        expected[f"pyoptix.module_tree:{relative}"] = {
            "archived_path": f"pyoptix_module/{relative}",
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        }
    cupy = pyoptix["cupy_module_file"]
    expected["pyoptix.cupy_module_file"] = {
        "archived_path": f"cupy_module/{Path(str(cupy['path'])).name}",
        "bytes": cupy["bytes"],
        "sha256": cupy["sha256"],
    }
    return expected


def verify_preserved_artifacts(transaction_root: Path, authority: dict[str, Any]) -> int:
    receipt = read_json(transaction_root / "BOUND_ARTIFACTS.json")
    verify_seal(receipt, "custody_sha256", "bound-artifact custody")
    if (
        receipt.get("schema") != BOUND_ARTIFACTS_SCHEMA
        or receipt.get("source_commit") != authority["source_commit"]
        or receipt.get("preregistration_sha256")
        != authority["preregistration_sha256"]
        or receipt.get("execution_authority_sha256") != authority["authority_sha256"]
        or receipt.get("gpu_complete_execution_count") != 0
        or receipt.get("goal5843_registered_estimand_timing_observation_count") != 0
    ):
        raise RuntimeError("bound-artifact custody contract mismatch")
    rows = receipt.get("artifacts")
    if not isinstance(rows, list) or receipt.get("artifact_count") != len(rows):
        raise RuntimeError("bound-artifact row count mismatch")
    expected = expected_preserved_artifacts(authority)
    observed = {str(row.get("authority_binding")): row for row in rows}
    if len(observed) != len(rows) or set(observed) != set(expected):
        raise RuntimeError("bound-artifact authority bindings differ")
    root = transaction_root / "bound_artifacts"
    for binding, expected_row in expected.items():
        row = observed[binding]
        relative = safe_member_path(str(row.get("archived_path", "")))
        if relative.as_posix() != expected_row["archived_path"]:
            raise RuntimeError(f"bound-artifact archive path mismatch: {binding}")
        path = root.joinpath(*relative.parts)
        if not path.is_file():
            raise RuntimeError(f"bound artifact missing: {binding}")
        if (
            path.stat().st_size != row.get("bytes")
            or sha256_file(path) != row.get("sha256")
            or row.get("sha256") != expected_row["sha256"]
            or (
                "bytes" in expected_row
                and row.get("bytes") != expected_row["bytes"]
            )
            or path.stat().st_mode & 0o777 != row.get("source_mode")
        ):
            raise RuntimeError(f"bound-artifact bytes differ: {binding}")
    return len(rows)


def verify_portable_preworker_authority(
    transaction_root: Path,
    preregistration: Path,
    prereg: dict[str, Any],
    authority: dict[str, Any],
) -> None:
    if (
        authority.get("preregistration_sha256") != prereg["preregistration_sha256"]
        or authority.get("preregistration_file_sha256") != sha256_file(preregistration)
    ):
        raise RuntimeError("execution authority preregistration binding mismatch")
    cache_binding = authority.get("formal_leaf_cache")
    if not isinstance(cache_binding, dict):
        raise RuntimeError("formal cache authority binding missing")
    cache_preparation_path = transaction_root / "CACHE_PREPARATION.json"
    cache_preparation = read_json(cache_preparation_path)
    verify_seal(cache_preparation, "preparation_sha256", "cache preparation")
    manifest_path = transaction_root / "FORMAL_LEAF_CACHE_MANIFEST.json"
    manifest = read_json(manifest_path)
    if (
        cache_preparation.get("schema") != CACHE_PREPARATION_SCHEMA
        or cache_preparation.get("source_commit") != authority["source_commit"]
        or cache_preparation.get("preregistration_sha256")
        != prereg["preregistration_sha256"]
        or cache_preparation.get("native_library_sha256")
        != authority["execution_paths"]["native_library_sha256"]
        or cache_preparation.get("manifest_file_sha256") != sha256_file(manifest_path)
        or cache_preparation.get("preparation_sha256")
        != cache_binding["preparation_sha256"]
        or sha256_file(cache_preparation_path)
        != cache_binding["preparation_receipt_file_sha256"]
        or cache_preparation.get("sealed_verification_miss_count") != 0
        or cache_preparation.get("gpu_complete_execution_count") != 0
        or cache_preparation.get(
            "goal5843_registered_estimand_timing_observation_count"
        )
        != 0
    ):
        raise RuntimeError("portable cache preparation binding mismatch")
    entries = manifest.get("entries")
    if (
        manifest.get("schema") != "rtdl.v4.formal_numba_leaf_cache_manifest.v1"
        or not isinstance(entries, list)
        or manifest.get("entry_count") != len(entries)
        or manifest.get("entry_count") != cache_binding["entry_count"]
        or manifest.get("entries_sha256") != digest(entries)
        or manifest.get("entries_sha256") != cache_binding["entries_sha256"]
        or sha256_file(manifest_path) != cache_binding["manifest_file_sha256"]
    ):
        raise RuntimeError("portable formal cache manifest mismatch")
    cache_root = transaction_root / "formal_leaf_cache"
    expected_keys = sorted(str(row.get("key_sha256", "")) for row in entries)
    if (
        not cache_root.is_dir()
        or sorted(path.name for path in cache_root.iterdir()) != expected_keys
    ):
        raise RuntimeError("portable formal cache membership mismatch")
    for row in entries:
        key = str(row.get("key_sha256", ""))
        if len(key) != 64 or any(character not in "0123456789abcdef" for character in key):
            raise RuntimeError("formal cache key is not canonical SHA-256")
        artifact = cache_root / key / "artifact.json"
        if (
            not (cache_root / key).is_dir()
            or [path.name for path in (cache_root / key).iterdir()] != ["artifact.json"]
            or not artifact.is_file()
            or artifact.stat().st_size != row.get("artifact_json_size_bytes")
            or sha256_file(artifact) != row.get("artifact_json_sha256")
        ):
            raise RuntimeError("portable formal cache entry mismatch")

    oracle_path = transaction_root / "INDEPENDENT_ORACLE_WITNESS.json"
    oracle = read_json(oracle_path)
    verify_seal(oracle, "witness_sha256", "independent oracle witness")
    oracle_binding = authority.get("independent_oracle_witness")
    if (
        not isinstance(oracle_binding, dict)
        or oracle.get("schema") != ORACLE_WITNESS_SCHEMA
        or oracle.get("source_commit") != authority["source_commit"]
        or oracle.get("preregistration_sha256") != prereg["preregistration_sha256"]
        or oracle.get("implementation_route_import_count") != 0
        or oracle.get("registered_timing_observation_count") != 0
        or oracle.get("witness_sha256") != oracle_binding.get("witness_sha256")
        or oracle.get("tasks") != oracle_binding.get("tasks")
        or sha256_file(oracle_path) != oracle_binding.get("file_sha256")
    ):
        raise RuntimeError("portable independent oracle binding mismatch")


def validate_transaction_status(transaction_root: Path) -> None:
    value = read_json(transaction_root / "TRANSACTION_STATUS.json")
    expected_stages = [
        "00_prepare_formal_leaf_cache",
        "01_build_independent_oracle_witness",
        "02_bind_execution_authority",
        "03_preserve_bound_artifacts",
        "04_formal_worker_zero_and_baseline",
        "05_independent_pod_recount",
    ]
    if (
        value.get("schema") != "rtdl.goal5843.transaction_status.v1"
        or value.get("status") != "PASS__FORMAL_TRANSACTION_AND_POD_RECOUNT_COMPLETE"
        or value.get("stage_count") != len(expected_stages)
        or [row.get("stage") for row in value.get("stages", [])] != expected_stages
        or any(
            row.get("returncode") != 0 or row.get("retry_permitted") is not False
            for row in value.get("stages", [])
        )
        or value.get("worker_zero_reached") is not True
        or value.get("post_worker_zero_retry_used") is not False
        or value.get("post_worker_zero_retry_permitted") is not False
        or value.get("all_adverse_rows_retained") is not True
        or value.get("failure_stage") is not None
    ):
        raise RuntimeError("formal transaction status is not a complete no-retry pass")


def verify_archive(
    archive: Path,
    preregistration: Path,
) -> tuple[Path, tempfile.TemporaryDirectory[str], list[dict[str, object]]]:
    load_preregistration(preregistration, ROOT, verify_files=True)
    temporary = tempfile.TemporaryDirectory(prefix="goal5843_archive_")
    extraction = Path(temporary.name)
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        normalized = []
        roots = set()
        for member in members:
            path = safe_member_path(member.name)
            if not (member.isfile() or member.isdir()) or member.issym() or member.islnk():
                raise RuntimeError(f"unsupported archive member type: {member.name}")
            normalized.append(path.as_posix())
            roots.add(path.parts[0])
        if len(normalized) != len(set(normalized)) or len(roots) != 1:
            raise RuntimeError("archive requires unique members under one root")
        stream.extractall(extraction, filter="data")
    transaction_root = extraction / next(iter(roots))
    if not transaction_root.is_dir():
        raise RuntimeError("archive transaction root missing")
    manifest = []
    for name in sorted(normalized):
        path = extraction.joinpath(*PurePosixPath(name).parts)
        if path.is_file():
            manifest.append(
                {
                    "path": name,
                    "type": "file",
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
        else:
            manifest.append({"path": name, "type": "directory"})
    return transaction_root, temporary, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--local-recount-output", type=Path, required=True)
    parser.add_argument("--verification-output", type=Path, required=True)
    args = parser.parse_args()
    archive = args.archive.resolve(strict=True)
    preregistration = args.preregistration.resolve(strict=True)
    transaction_root, temporary, member_manifest = verify_archive(
        archive, preregistration
    )
    try:
        prereg = load_preregistration(preregistration, ROOT, verify_files=True)
        validate_transaction_status(transaction_root)
        authority = read_json(transaction_root / "EXECUTION_AUTHORITY.json")
        verify_seal(authority, "authority_sha256", "execution authority")
        if authority.get("schema") != EXECUTION_AUTHORITY_SCHEMA:
            raise RuntimeError("execution authority schema mismatch")
        verify_portable_preworker_authority(
            transaction_root, preregistration, prereg, authority
        )
        artifact_count = verify_preserved_artifacts(transaction_root, authority)
        local = build_recount(
            preregistration,
            transaction_root / "EXECUTION_AUTHORITY.json",
            transaction_root / "baseline",
        )
        pod = read_json(transaction_root / "POD_RECOUNT.json")
        if local != pod:
            raise RuntimeError("local independent recount differs from pod recount")
        evidence_root = args.evidence_root.absolute()
        for name in KEY_EXPORTS:
            export_create_only(transaction_root / name, evidence_root / name)
        create_json(args.local_recount_output, local)
        if args.local_recount_output.read_bytes() != (
            transaction_root / "POD_RECOUNT.json"
        ).read_bytes():
            raise RuntimeError("pod and local recount bytes differ")
        result: dict[str, object] = {
            "schema": ARCHIVE_VERIFICATION_SCHEMA,
            "status": "PASS__SAFE_ARCHIVE_AND_BYTE_IDENTICAL_LOCAL_RECOUNT",
            "archive_sha256": sha256_file(archive),
            "archive_bytes": archive.stat().st_size,
            "archive_member_count": len(member_manifest),
            "archive_member_manifest_sha256": digest(member_manifest),
            "transaction_root_name": transaction_root.name,
            "source_commit": authority["source_commit"],
            "preregistration_sha256": authority["preregistration_sha256"],
            "execution_authority_sha256": authority["authority_sha256"],
            "bound_artifact_count": artifact_count,
            "key_exports": list(KEY_EXPORTS),
            "pod_local_recount_byte_identical": True,
            "public_performance_claim_authorized": False,
            "manuscript_performance_claim_authorized": False,
        }
        result["verification_sha256"] = digest(result)
        create_json(args.verification_output, result)
        print(json.dumps(result, sort_keys=True))
    finally:
        temporary.cleanup()


if __name__ == "__main__":
    main()

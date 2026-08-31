#!/usr/bin/env python3
"""Build a deterministic, exact-source Goal5800 OWL functional bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from typing import Any


OWL_COMMIT = "df7390b16bce5244b7352ca6d3e320f838297072"
OWL_TREE = "c31d2c7510050fc3d57a4c4e0a4d4d84bc7b03ff"
OWL_REPOSITORY = "https://github.com/NVIDIA/OWL"
ROOT_NAME = "goal5800_owl_source"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
    ).stdout


def archive_files(repo: Path) -> tuple[dict[str, bytes], dict[str, int]]:
    archive = git(repo, "archive", "--format=tar", "HEAD")
    files: dict[str, bytes] = {}
    modes: dict[str, int] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        for member in source.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported upstream tar member: {member.name}")
            extracted = source.extractfile(member)
            if extracted is None:
                raise RuntimeError(f"could not read upstream member: {member.name}")
            files[member.name] = extracted.read()
            modes[member.name] = member.mode
    return files, modes


def add_file(files: dict[str, bytes], modes: dict[str, int],
             path: str, source: Path, mode: int = 0o644) -> None:
    if path in files:
        raise RuntimeError(f"overlay path already exists: {path}")
    files[path] = source.read_bytes()
    modes[path] = mode


def build_tar(files: dict[str, bytes], modes: dict[str, int]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as out:
        for path in sorted(files):
            value = files[path]
            info = tarfile.TarInfo(f"{ROOT_NAME}/{path}")
            info.size = len(value)
            info.mode = modes[path]
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            out.addfile(info, io.BytesIO(value))
    compressed = io.BytesIO()
    with gzip.GzipFile(
            filename="", mode="wb", fileobj=compressed, mtime=0) as stream:
        stream.write(raw.getvalue())
    return compressed.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owl-repo", type=Path, required=True)
    parser.add_argument("--harness-dir", type=Path, required=True)
    parser.add_argument("--capture-script", type=Path, required=True)
    parser.add_argument("--remote-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.receipt):
        if path.exists():
            raise FileExistsError(path)
    commit = git(args.owl_repo, "rev-parse", "HEAD").decode().strip()
    tree = git(args.owl_repo, "rev-parse", "HEAD^{tree}").decode().strip()
    status = git(args.owl_repo, "status", "--porcelain").decode()
    if commit != OWL_COMMIT or tree != OWL_TREE or status:
        raise RuntimeError(
            f"pinned OWL identity mismatch: {commit}/{tree}/{status!r}")

    files, modes = archive_files(args.owl_repo)
    device_path = "owl/DeviceContext.cpp"
    original_device = files[device_path]
    newline = b"\r\n" if b"\r\n" in original_device else b"\n"
    old = (
        b"    OPTIX_CHECK(optixDeviceContextCreate(cudaContext, 0, &optixContext));"
        + newline
        + b"    OPTIX_CHECK(optixDeviceContextSetLogCallback"
        + newline
        + b"                (optixContext,context_log_cb,this,4));"
        + newline
    )
    new = (
        newline.join((
            b"    OptixDeviceContextOptions options = {};",
            b"    options.logCallbackFunction = context_log_cb;",
            b"    options.logCallbackData = this;",
            b"    options.logCallbackLevel = 4;",
            b"    options.validationMode = OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_ALL;",
            b"    OPTIX_CHECK(optixDeviceContextCreate(cudaContext, &options,",
            b"                                        &optixContext));",
            b"",
        ))
    )
    if original_device.count(old) != 1:
        raise RuntimeError("OWL validation overlay anchor is not exact and unique")
    files[device_path] = original_device.replace(old, new, 1)

    sample_root = "samples/cmdline/s99-goal5800-owl-residual"
    harness_names = ("CMakeLists.txt", "Goal5800Types.h", "deviceCode.cu",
                     "hostCode.cpp")
    for name in harness_names:
        add_file(files, modes, f"{sample_root}/{name}",
                 args.harness_dir / name)
    patch_source = args.harness_dir / "owl_validation_mode_all.patch"
    add_file(files, modes, "goal5800_evidence/owl_validation_mode_all.patch",
             patch_source)
    add_file(files, modes,
             "goal5800_tools/goal5800_capture_owl_untimed.py",
             args.capture_script, 0o755)
    add_file(files, modes,
             "goal5800_tools/goal5800_remote_build_and_run.py",
             args.remote_script, 0o755)

    identity: dict[str, Any] = {
        "schema": "rtdl.goal5800.owl_stage_identity.v1",
        "owl_upstream": {
            "repository": OWL_REPOSITORY,
            "commit": commit,
            "tree": tree,
            "working_tree_clean_before_archive": True,
        },
        "validation_overlay": {
            "diagnostic_only": True,
            "changed_upstream_paths": [device_path],
            "patch_sha256": sha256_bytes(patch_source.read_bytes()),
            "original_device_context_sha256": sha256_bytes(original_device),
            "overlaid_device_context_sha256": sha256_bytes(files[device_path]),
            "optix_validation_mode": "ALL",
            "callback_emits_only_error_or_fatal_levels": [1, 2],
            "does_not_change_program_pipeline_sbt_gas_launch_or_output": True,
        },
        "harness": {
            name: {
                "bytes": len(files[f"{sample_root}/{name}"]),
                "sha256": sha256_bytes(files[f"{sample_root}/{name}"]),
            }
            for name in harness_names
        },
        "scope": {
            "untimed_functional_execution_only": True,
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
            "upstream_unmodified_claimed": False,
        },
    }
    identity_bytes = json.dumps(
        identity, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    files["GOAL5800_STAGE_IDENTITY.json"] = identity_bytes
    modes["GOAL5800_STAGE_IDENTITY.json"] = 0o644

    manifest_rows = [
        {"path": path, "bytes": len(files[path]),
         "sha256": sha256_bytes(files[path])}
        for path in sorted(files)
    ]
    manifest = {
        "schema": "rtdl.goal5800.owl_source_manifest.v1",
        "owl_commit": commit,
        "owl_tree": tree,
        "files": manifest_rows,
        "files_sha256": sha256_bytes(canonical(manifest_rows)),
        "file_count_excluding_manifest": len(manifest_rows),
    }
    manifest_bytes = json.dumps(
        manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    files["GOAL5800_SOURCE_MANIFEST.json"] = manifest_bytes
    modes["GOAL5800_SOURCE_MANIFEST.json"] = 0o644

    bundle = build_tar(files, modes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(bundle)
    receipt = {
        "schema": "rtdl.goal5800.owl_untimed_bundle_receipt.v1",
        "status": "PASS__EXACT_PINNED_OWL_PLUS_DECLARED_DIAGNOSTIC_OVERLAY",
        "bundle": {
            "path": args.output.as_posix(),
            "bytes": len(bundle),
            "sha256": sha256_bytes(bundle),
            "root": ROOT_NAME,
        },
        "owl_upstream": identity["owl_upstream"],
        "validation_overlay": identity["validation_overlay"],
        "source_manifest": {
            "bytes": len(manifest_bytes),
            "sha256": sha256_bytes(manifest_bytes),
            "file_count_excluding_manifest": len(manifest_rows),
            "files_sha256": manifest["files_sha256"],
        },
        "stage_identity_sha256": sha256_bytes(identity_bytes),
        "scope": identity["scope"],
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

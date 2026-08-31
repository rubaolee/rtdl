#!/usr/bin/env python3
"""Freeze the untimed PyOptiX arm, loaded wheel bytes, and source identities."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def add_bytes(archive: tarfile.TarFile, name: str, value: bytes,
              mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(value))


def git(path: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def command(*arguments: str) -> str:
    return subprocess.run(
        list(arguments), check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def build(args: argparse.Namespace) -> bytes:
    result_bytes = args.result.read_bytes()
    result = json.loads(result_bytes)
    if result["status"] != "PASS__UNTIMED_FUNCTIONAL" \
            or result["registered_performance_timing_count"] != 0:
        raise RuntimeError("untimed PyOptiX result is not closeable")

    source_root = args.source_root.resolve()
    pyoptix_source = args.pyoptix_source_root.resolve()
    distribution = importlib.metadata.distribution("pyoptix")
    frozen: list[tuple[str, bytes, int]] = []
    rows = []
    for relative in sorted(distribution.files or (), key=str):
        path = Path(distribution.locate_file(relative))
        if not path.is_file():
            continue
        value = path.read_bytes()
        name = str(relative).replace("\\", "/")
        rows.append({"path": name, "bytes": len(value), "sha256": sha256(value)})
        frozen.append((f"installed_distribution/{name}", value, 0o644))
    if rows != result["pyoptix_loaded_distribution_manifest"]["files"]:
        raise RuntimeError("loaded distribution changed after execution")

    executed_sources = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts \
                or path.suffix in (".pyc", ".pyo"):
            continue
        relative = path.relative_to(source_root).as_posix()
        value = path.read_bytes()
        executed_sources.append({
            "path": relative, "bytes": len(value), "sha256": sha256(value),
        })
        frozen.append((f"executed_source/{relative}", value, 0o644))

    environment = {
        "schema": "rtdl.goal5800.pyoptix_idiomatic_environment.v1",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": os.path.realpath(os.sys.executable),
        "gpu_csv": command(
            "nvidia-smi", "--query-gpu=name,compute_cap,driver_version",
            "--format=csv,noheader"),
        "pyoptix_source": {
            "commit": git(pyoptix_source, "rev-parse", "HEAD"),
            "tree": git(pyoptix_source, "rev-parse", "HEAD^{tree}"),
            "status_porcelain": git(
                pyoptix_source, "status", "--porcelain=v1",
                "--untracked-files=all"),
        },
        "executed_sources": executed_sources,
        "loaded_distribution_files_sha256": hashlib.sha256(
            canonical(rows)).hexdigest(),
        "registered_performance_timing_count": 0,
    }
    if environment["pyoptix_source"] != {
            "commit": result["pyoptix_commit"],
            "tree": result["pyoptix_tree"],
            "status_porcelain": ""}:
        raise RuntimeError("PyOptiX source identity changed after execution")
    environment_bytes = (
        json.dumps(environment, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    manifest = {
        "schema": "rtdl.goal5800.pyoptix_idiomatic_evidence_manifest.v1",
        "result": {"bytes": len(result_bytes), "sha256": sha256(result_bytes)},
        "environment": {
            "bytes": len(environment_bytes), "sha256": sha256(environment_bytes)},
        "installed_distribution_file_count": len(rows),
        "installed_distribution_files_sha256": hashlib.sha256(
            canonical(rows)).hexdigest(),
        "executed_source_file_count": len(executed_sources),
        "executed_source_files_sha256": hashlib.sha256(
            canonical(executed_sources)).hexdigest(),
        "registered_performance_timing_count": 0,
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")

    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        add_bytes(archive, "MANIFEST.json", manifest_bytes)
        add_bytes(archive, "environment.json", environment_bytes)
        add_bytes(archive, "idiomatic_pyoptix_untimed.json", result_bytes)
        for name, value, mode in frozen:
            add_bytes(archive, name, value, mode)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    return compressed.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--pyoptix-source-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    value = build(args)
    args.output.write_bytes(value)
    print(json.dumps({
        "output": str(args.output), "bytes": len(value), "sha256": sha256(value),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

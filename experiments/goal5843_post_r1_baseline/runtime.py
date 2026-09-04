"""Create-only runtime and authority helpers for Goal5843."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any

from .contracts import (
    EXECUTION_AUTHORITY_SCHEMA,
    Goal5843ContractError,
    digest,
    load_preregistration,
    sha256_file,
)


def create_json(path: Path, value: Mapping[str, object]) -> None:
    destination = path.absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    temporary = destination.with_name(
        f".{destination.name}.tmp.{os.getpid()}.{time.monotonic_ns()}"
    )
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        payload = (
            json.dumps(
                value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False
            ).encode("ascii")
            + b"\n"
        )
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)
    finally:
        os.close(descriptor)
        temporary.unlink(missing_ok=True)


def create_text(path: Path, value: str) -> None:
    destination = path.absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def command_output(command: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.run(
        command, cwd=cwd, check=True, text=True, capture_output=True
    ).stdout.strip()


def git_head(root: Path) -> str:
    return command_output(["git", "rev-parse", "HEAD"], cwd=root)


def git_status_short(root: Path) -> tuple[str, ...]:
    output = command_output(["git", "status", "--short"], cwd=root)
    return tuple(row for row in output.splitlines() if row)


def verify_seal(value: Mapping[str, object], field: str, label: str) -> None:
    observed = value.get(field)
    unsealed = dict(value)
    unsealed.pop(field, None)
    if not isinstance(observed, str) or digest(unsealed) != observed:
        raise Goal5843ContractError(f"{label} seal mismatch")


def _verify_bound_file(paths: Mapping[str, object], key: str, digest_key: str) -> Path:
    path = Path(str(paths.get(key, ""))).resolve()
    if not path.is_file() or sha256_file(path) != paths.get(digest_key):
        raise Goal5843ContractError(f"execution file identity mismatch: {key}")
    return path


def _verify_module_tree(tree: object, label: str) -> None:
    if not isinstance(tree, dict) or not isinstance(tree.get("files"), list):
        raise Goal5843ContractError(f"{label} module tree missing")
    root = Path(str(tree.get("root", ""))).resolve()
    rows = tree["files"]
    if not rows or tree.get("file_count") != len(rows) or digest(rows) != tree.get(
        "tree_sha256"
    ):
        raise Goal5843ContractError(f"{label} module tree seal mismatch")
    for row in rows:
        relative = Path(str(row.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise Goal5843ContractError(f"{label} module tree path unsafe")
        path = root / relative
        if (
            not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or sha256_file(path) != row.get("sha256")
        ):
            raise Goal5843ContractError(f"{label} module tree drift: {relative}")


def _verify_formal_cache(authority: Mapping[str, object]) -> None:
    cache = authority.get("formal_leaf_cache")
    if not isinstance(cache, dict):
        raise Goal5843ContractError("formal leaf cache binding missing")
    root = Path(str(cache.get("root", ""))).resolve()
    manifest_path = Path(str(cache.get("manifest", ""))).resolve()
    if not root.is_dir() or root.is_symlink():
        raise Goal5843ContractError("formal leaf cache root invalid")
    if not manifest_path.is_file() or sha256_file(manifest_path) != cache.get(
        "manifest_file_sha256"
    ):
        raise Goal5843ContractError("formal leaf cache manifest identity mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != "rtdl.v4.formal_numba_leaf_cache_manifest.v1"
        or Path(str(manifest.get("cache_root", ""))).resolve() != root
        or manifest.get("entry_count") != len(manifest.get("entries", []))
        or manifest.get("entries_sha256") != digest(manifest.get("entries", []))
        or manifest.get("entry_count") != cache.get("entry_count")
        or manifest.get("entries_sha256") != cache.get("entries_sha256")
    ):
        raise Goal5843ContractError("formal leaf cache manifest contract mismatch")
    for row in manifest["entries"]:
        entry = root / str(row.get("key_sha256", "")) / "artifact.json"
        if (
            not entry.is_file()
            or entry.stat().st_size != row.get("artifact_json_size_bytes")
            or sha256_file(entry) != row.get("artifact_json_sha256")
        ):
            raise Goal5843ContractError("formal leaf cache entry identity mismatch")


def load_execution_authority(
    path: Path,
    *,
    preregistration_path: Path,
    root: Path,
    require_clean_repository: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    prereg = load_preregistration(
        preregistration_path.resolve(), root, verify_files=True
    )
    authority = json.loads(path.resolve().read_text(encoding="utf-8"))
    if not isinstance(authority, dict):
        raise Goal5843ContractError("execution authority must be an object")
    verify_seal(authority, "authority_sha256", "execution authority")
    if (
        authority.get("schema") != EXECUTION_AUTHORITY_SCHEMA
        or authority.get("status") != "AUTHORIZED_FOR_GOAL5843_FORMAL_WORKER_ZERO"
        or authority.get("owner_authorized_goal5843_execution") is not True
    ):
        raise Goal5843ContractError("execution authority does not authorize Goal5843")
    if authority.get("repository_status_short") != []:
        raise Goal5843ContractError("authority was not issued from a clean repository")
    if authority.get("source_commit") != git_head(root):
        raise Goal5843ContractError("authority source commit differs from current HEAD")
    if require_clean_repository and git_status_short(root):
        raise Goal5843ContractError("formal repository is dirty")
    if (
        authority.get("preregistration_sha256") != prereg["preregistration_sha256"]
        or authority.get("preregistration_file_sha256")
        != sha256_file(preregistration_path.resolve())
    ):
        raise Goal5843ContractError("authority preregistration binding mismatch")
    paths = authority.get("execution_paths")
    if not isinstance(paths, dict):
        raise Goal5843ContractError("execution paths missing")
    for key, digest_key in (
        ("native_library", "native_library_sha256"),
        ("native_build_manifest", "native_build_manifest_sha256"),
        ("direct_binary", "direct_binary_sha256"),
        ("device_source", "device_source_sha256"),
    ):
        _verify_bound_file(paths, key, digest_key)
    for directory_key, file_name, digest_key in (
        ("optix_include", "optix.h", "optix_h_sha256"),
        ("cuda_include", "cuda.h", "cuda_h_sha256"),
    ):
        header = Path(str(paths.get(directory_key, ""))).resolve() / file_name
        if not header.is_file() or sha256_file(header) != paths.get(digest_key):
            raise Goal5843ContractError(f"header identity mismatch: {directory_key}")
    host = authority.get("host")
    if not isinstance(host, dict) or Path(str(host.get("python_executable", ""))).resolve() != Path(
        sys.executable
    ).resolve():
        raise Goal5843ContractError("Python executable differs from authority")
    pyoptix = authority.get("pyoptix")
    if not isinstance(pyoptix, dict):
        raise Goal5843ContractError("PyOptiX binding missing")
    _verify_module_tree(pyoptix.get("module_tree"), "PyOptiX")
    cupy_file = pyoptix.get("cupy_module_file")
    if not isinstance(cupy_file, dict):
        raise Goal5843ContractError("CuPy file binding missing")
    cupy_path = Path(str(cupy_file.get("path", ""))).resolve()
    if (
        not cupy_path.is_file()
        or cupy_path.stat().st_size != cupy_file.get("bytes")
        or sha256_file(cupy_path) != cupy_file.get("sha256")
    ):
        raise Goal5843ContractError("CuPy file binding drift")
    _verify_formal_cache(authority)
    oracle = authority.get("independent_oracle_witness")
    if not isinstance(oracle, dict):
        raise Goal5843ContractError("independent oracle witness binding missing")
    oracle_path = Path(str(oracle.get("path", ""))).resolve()
    if not oracle_path.is_file() or sha256_file(oracle_path) != oracle.get(
        "file_sha256"
    ):
        raise Goal5843ContractError("independent oracle witness file drift")
    oracle_value = json.loads(oracle_path.read_text(encoding="utf-8"))
    verify_seal(oracle_value, "witness_sha256", "independent oracle witness")
    if (
        oracle_value.get("witness_sha256") != oracle.get("witness_sha256")
        or oracle_value.get("tasks") != oracle.get("tasks")
    ):
        raise Goal5843ContractError("independent oracle witness content drift")
    for name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    ):
        if os.environ.get(name):
            raise Goal5843ContractError(f"ambient formal cache authority forbidden: {name}")
    return prereg, authority


def require_bound_path(
    authority: Mapping[str, object], key: str, supplied: Path
) -> Path:
    paths = authority.get("execution_paths")
    if not isinstance(paths, Mapping) or not isinstance(paths.get(key), str):
        raise Goal5843ContractError(f"authority path binding missing: {key}")
    expected = Path(str(paths[key])).resolve()
    actual = supplied.resolve(strict=True)
    if actual != expected:
        raise Goal5843ContractError(f"execution path differs from authority: {key}")
    return actual


def bind_authorized_native_library(
    authority: Mapping[str, object],
    supplied: Path,
    *,
    environment: MutableMapping[str, str] | None = None,
) -> Path:
    native = require_bound_path(authority, "native_library", supplied)
    target = os.environ if environment is None else environment
    target["RTDL_OPTIX_LIB"] = str(native)
    target["RTDL_OPTIX_LIBRARY"] = str(native)
    return native


def require_idle_bound_gpu(authority: Mapping[str, object]) -> None:
    hardware = authority.get("hardware")
    if not isinstance(hardware, Mapping):
        raise Goal5843ContractError("hardware binding missing")
    rows = command_output(
        ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader,nounits"]
    ).splitlines()
    if len(rows) != 1 or rows[0].strip() != hardware.get("gpu_uuid"):
        raise Goal5843ContractError("live GPU UUID differs from authority")
    processes = command_output(
        [
            "nvidia-smi",
            "--query-compute-apps=pid",
            "--format=csv,noheader,nounits",
        ]
    )
    if processes and "No running" not in processes:
        raise Goal5843ContractError(f"foreign GPU compute process present: {processes}")


__all__ = [
    "bind_authorized_native_library",
    "command_output",
    "create_json",
    "create_text",
    "git_head",
    "git_status_short",
    "load_execution_authority",
    "require_bound_path",
    "require_idle_bound_gpu",
    "verify_seal",
]

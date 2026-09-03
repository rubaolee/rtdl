"""Create-only runtime helpers for Goal5842 formal evidence."""

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
    WORKER_RECEIPT_SCHEMA,
    Goal5842ContractError,
    digest,
    load_preregistration,
    sha256_file,
)


def create_json(path: Path, value: Mapping[str, object]) -> None:
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
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
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def create_text(path: Path, value: str) -> None:
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def git_status_short(root: Path) -> tuple[str, ...]:
    output = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    return tuple(row for row in output.splitlines() if row)


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
    seal = authority.get("authority_sha256")
    unsealed = dict(authority)
    unsealed.pop("authority_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise Goal5842ContractError("execution authority seal mismatch")
    if authority.get("schema") != EXECUTION_AUTHORITY_SCHEMA:
        raise Goal5842ContractError("execution authority schema mismatch")
    if authority.get("status") != "AUTHORIZED_FOR_FORMAL_WORKER_ZERO":
        raise Goal5842ContractError(
            "execution authority does not authorize worker zero"
        )
    if authority.get("owner_authorized_goal5842_execution") is not True:
        raise Goal5842ContractError("owner authorization absent")
    if authority.get("repository_status_short") != []:
        raise Goal5842ContractError("authority was not issued from a clean repository")
    if authority.get("preregistration_sha256") != prereg["preregistration_sha256"]:
        raise Goal5842ContractError("authority preregistration seal mismatch")
    if authority.get("preregistration_file_sha256") != sha256_file(
        preregistration_path.resolve()
    ):
        raise Goal5842ContractError("authority preregistration file mismatch")
    current_head = git_head(root)
    if authority.get("source_commit") != current_head:
        raise Goal5842ContractError(
            f"authority source commit mismatch: {authority.get('source_commit')} != {current_head}"
        )
    if require_clean_repository:
        dirty = git_status_short(root)
        if dirty:
            raise Goal5842ContractError(f"formal repository is dirty: {dirty!r}")
    hardware = authority.get("hardware")
    if not isinstance(hardware, dict):
        raise Goal5842ContractError("authority hardware binding missing")
    for key in (
        "gpu_model",
        "gpu_uuid",
        "driver_version",
        "compute_capability",
        "architecture_generation",
    ):
        if not isinstance(hardware.get(key), str) or not hardware[key]:
            raise Goal5842ContractError(f"authority hardware field missing: {key}")
    paths = authority.get("execution_paths")
    if not isinstance(paths, dict):
        raise Goal5842ContractError("authority execution paths missing")
    for path_key, digest_key in (
        ("native_library", "native_library_sha256"),
        ("native_build_manifest", "native_build_manifest_sha256"),
        ("direct_binary", "direct_binary_sha256"),
        ("device_source", "device_source_sha256"),
    ):
        bound = Path(str(paths.get(path_key, ""))).resolve()
        if not bound.is_file() or sha256_file(bound) != paths.get(digest_key):
            raise Goal5842ContractError(
                f"authority execution file identity mismatch: {path_key}"
            )
    for directory_key, file_name, digest_key in (
        ("optix_include", "optix.h", "optix_h_sha256"),
        ("cuda_include", "cuda.h", "cuda_h_sha256"),
    ):
        header = Path(str(paths.get(directory_key, ""))).resolve() / file_name
        if not header.is_file() or sha256_file(header) != paths.get(digest_key):
            raise Goal5842ContractError(
                f"authority header identity mismatch: {directory_key}/{file_name}"
            )
    host = authority.get("host")
    if not isinstance(host, dict):
        raise Goal5842ContractError("authority host binding missing")
    if (
        Path(str(host.get("python_executable", ""))).resolve()
        != Path(sys.executable).resolve()
    ):
        raise Goal5842ContractError("current Python executable differs from authority")
    pyoptix = authority.get("pyoptix")
    if not isinstance(pyoptix, dict):
        raise Goal5842ContractError("authority PyOptiX binding missing")
    module_tree = pyoptix.get("module_tree")
    if not isinstance(module_tree, dict) or not isinstance(
        module_tree.get("files"), list
    ):
        raise Goal5842ContractError("authority PyOptiX module tree missing")
    module_root = Path(str(module_tree.get("root", ""))).resolve()
    rows = module_tree["files"]
    if module_tree.get("file_count") != len(rows) or not rows:
        raise Goal5842ContractError("authority PyOptiX tree count mismatch")
    if digest(rows) != module_tree.get("tree_sha256"):
        raise Goal5842ContractError("authority PyOptiX tree seal mismatch")
    for row in rows:
        if not isinstance(row, dict):
            raise Goal5842ContractError("authority PyOptiX tree row invalid")
        relative = Path(str(row.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise Goal5842ContractError("authority PyOptiX tree path unsafe")
        target = module_root / relative
        if (
            not target.is_file()
            or target.stat().st_size != row.get("bytes")
            or sha256_file(target) != row.get("sha256")
        ):
            raise Goal5842ContractError(
                f"authority PyOptiX module identity mismatch: {relative}"
            )
    cupy_file = pyoptix.get("cupy_module_file")
    if not isinstance(cupy_file, dict):
        raise Goal5842ContractError("authority CuPy module identity missing")
    cupy_path = Path(str(cupy_file.get("path", ""))).resolve()
    if (
        not cupy_path.is_file()
        or cupy_path.stat().st_size != cupy_file.get("bytes")
        or sha256_file(cupy_path) != cupy_file.get("sha256")
    ):
        raise Goal5842ContractError("authority CuPy module identity mismatch")
    toolchain = authority.get("toolchain")
    if not isinstance(toolchain, dict):
        raise Goal5842ContractError("authority toolchain binding missing")
    if (
        toolchain.get("optix_h_sha256") != paths.get("optix_h_sha256")
        or toolchain.get("cuda_h_sha256") != paths.get("cuda_h_sha256")
        or toolchain.get("optix_sdk") != pyoptix.get("optix_api_version")
    ):
        raise Goal5842ContractError("authority toolchain identities disagree")
    return prereg, authority


def schedule_row(prereg: Mapping[str, object], worker_id: str) -> dict[str, Any]:
    rows = prereg.get("causal_schedule")
    if not isinstance(rows, list):
        raise Goal5842ContractError("causal schedule missing")
    matches = [dict(row) for row in rows if row.get("worker_id") == worker_id]
    if len(matches) != 1:
        raise Goal5842ContractError(f"worker id is not unique: {worker_id}")
    return matches[0]


def require_bound_path(
    authority: Mapping[str, object], key: str, supplied: Path
) -> Path:
    paths = authority.get("execution_paths")
    if not isinstance(paths, Mapping) or not isinstance(paths.get(key), str):
        raise Goal5842ContractError(f"authority path binding missing: {key}")
    expected = Path(str(paths[key])).resolve()
    actual = supplied.resolve(strict=True)
    if actual != expected:
        raise Goal5842ContractError(
            f"execution argument path differs from authority: {key}"
        )
    return actual


def bind_authorized_native_library(
    authority: Mapping[str, object],
    supplied: Path,
    *,
    environment: MutableMapping[str, str] | None = None,
) -> Path:
    """Force legacy loaders to use the DSO already bound by the authority."""

    native = require_bound_path(authority, "native_library", supplied)
    target = os.environ if environment is None else environment
    for name in ("RTDL_OPTIX_LIB", "RTDL_OPTIX_LIBRARY"):
        target[name] = str(native)
    return native


def require_idle_bound_gpu(authority: Mapping[str, object]) -> None:
    hardware = authority.get("hardware")
    if not isinstance(hardware, Mapping):
        raise Goal5842ContractError("authority hardware binding missing")
    uuid_rows = subprocess.run(
        ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader,nounits"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    if len(uuid_rows) != 1 or uuid_rows[0].strip() != hardware.get("gpu_uuid"):
        raise Goal5842ContractError("live GPU UUID differs from execution authority")
    process_rows = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if process_rows and "No running" not in process_rows:
        raise Goal5842ContractError(
            f"foreign GPU compute process present: {process_rows}"
        )


def validate_worker_receipt(
    receipt: object,
    *,
    prereg: Mapping[str, object],
    authority: Mapping[str, object],
    row: Mapping[str, object],
) -> None:
    if not isinstance(receipt, dict):
        raise Goal5842ContractError("worker receipt must be an object")
    seal = receipt.get("receipt_sha256")
    unsealed = dict(receipt)
    unsealed.pop("receipt_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise Goal5842ContractError("worker receipt seal mismatch")
    exact = {
        "schema": WORKER_RECEIPT_SCHEMA,
        "status": "PASS",
        "worker_id": row["worker_id"],
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "position": row["position"],
        "arm_sample_index": row["arm_sample_index"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
    }
    for key, expected in exact.items():
        if receipt.get(key) != expected:
            raise Goal5842ContractError(f"worker receipt mismatch: {key}")
    phases = receipt.get("phases_ns")
    if not isinstance(phases, dict):
        raise Goal5842ContractError("worker phases missing")
    required = {
        "route_declaration_and_artifact_binding",
        "provider_projection_and_public_admission_or_unchecked_construction",
    }
    if set(phases) != required or any(
        type(phases[key]) is not int or phases[key] < 0 for key in required
    ):
        raise Goal5842ContractError("worker phase vector invalid")
    signature = receipt.get("program_signature")
    reference = receipt.get("post_estimand_public_admission_signature")
    if not isinstance(signature, dict) or signature != reference:
        raise Goal5842ContractError("worker program identity differs from reference")
    expected_signature_fields = {
        "plan_sha256",
        "artifacts_sha256",
        "provider_projection_sha256",
        "provider_descriptor_sha256",
    }
    if set(signature) != expected_signature_fields or any(
        not isinstance(value, str) or len(value) != 64 for value in signature.values()
    ):
        raise Goal5842ContractError("worker program signature invalid")
    input_sha = receipt.get("input_sha256")
    if not isinstance(input_sha, str) or len(input_sha) != 64:
        raise Goal5842ContractError("worker input identity invalid")
    if receipt.get("registered_admission_total_ns") != sum(phases.values()):
        raise Goal5842ContractError("worker admission total differs from phases")
    if receipt.get("normal_reference_admission_after_estimand") is not True:
        raise Goal5842ContractError(
            "worker reference admission timing boundary missing"
        )
    if receipt.get("garbage_collector_disabled_during_registered_phases") is not True:
        raise Goal5842ContractError("worker garbage-collector boundary missing")
    if receipt.get("clock") != "time.perf_counter_ns":
        raise Goal5842ContractError("worker clock differs from preregistration")
    if receipt.get("gpu_imported_or_executed") is not False:
        raise Goal5842ContractError("causal worker imported or executed GPU work")


__all__ = [
    "create_json",
    "create_text",
    "git_head",
    "git_status_short",
    "load_execution_authority",
    "require_bound_path",
    "require_idle_bound_gpu",
    "schedule_row",
    "validate_worker_receipt",
]

#!/usr/bin/env python3
"""One fresh-process Goal5791 same-source fusion-ablation worker.

The worker owns exactly one frozen schedule arm.  It deliberately separates
five mutually exclusive measured phases from the post-timer evidence phase.
In particular, every recursive fusion-plan/target/recipe/operation-contract
check and every process-local execution-token admission happens in
``preparation``.  ``execute`` is one continuous ``perf_counter`` interval and
uses only pre-admitted, single-use tokens.  Receipt hashing, receipt JSON
construction, and comparison with the independent oracle happen after that
interval and after owner close.

This module is safe to import on a CPU-only machine: all application, NumPy,
Numba, CuPy, CUDA, and RTDL product imports are lazy and occur in a measured
phase of a real worker.  Tests can inject a backend without importing any GPU
package.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import sys
import time
from typing import Callable, Mapping, Protocol

from scripts.goal5791_formal_contract import (
    CACHE_POLICY,
    COLD,
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT,
    DATASET_IDS,
    FORMAL_WORKER_ENVIRONMENT_CONTRACT,
    FUSION_OFF,
    FUSION_ON,
    FORMAL_EXECUTION_POLICY,
    GOAL,
    IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT,
    NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT,
    PREPARED,
    SEGMENT_PLAN_INPUT_CONTRACT,
    SOURCE_ADMISSION_POLICY,
    contract_sha256,
    digest,
    file_sha256,
    lifecycle_contract,
    lifecycle_contract_sha256,
    load_preexecution_authority,
    oracle_contract_sha256,
    output_contract_sha256,
    schedule,
    schedule_sha256,
    timer_contract,
    timer_contract_sha256,
    validate_data_authority,
    validate_phase_accounting,
    validate_runtime_budget_authority,
)


WORKER_SCHEMA = "rtdl.goal5791.formal_worker.v1"
RUNTIME_SCHEMA = "rtdl.goal5791.formal_runtime.v1"
RUNTIME_STATUS = "TARGET_PREPARED__FORMAL_AUTHORITY_STILL_REQUIRED"
U64_MAX = (1 << 64) - 1

_RUNTIME_KEYS = {
    "schema", "goal", "status", "formal_contract_sha256",
    "schedule_sha256", "preexecution_authority_file_sha256",
    "target_materialization_binding_sha256", "formal_identity_sha256",
    "runtime_budget_authority_sha256", "execution_source_root",
    "execution_source_manifest_path",
    "execution_source_manifest_file_sha256", "formal_identity_record",
    "python_executable", "python_executable_sha256", "python_version",
    "numba_version", "llvmlite_version", "numpy_version", "cupy_version",
    "native_library_path", "native_library_sha256", "optix_include",
    "cuda_include", "compute_capability", "optix_sdk_version",
    "shared_contract_freeze_path", "shared_contract_freeze_file_sha256",
    "target_materialization_authority_path",
    "target_materialization_authority_file_sha256",
    "max_relation_rows", "datasets", "neutral_prewarm",
    "formal_worker_environment", "worker_timeout_seconds",
    "formal_conservative_budget_seconds", "runtime_sha256",
}
_DATASET_KEYS = {
    "edge_path", "input_sha256", "size_bytes",
    "expected_triangle_count", "oracle_authority_sha256",
}
_PREWARM_KEYS = {
    "edge_path", "input_sha256", "size_bytes", "expected_triangle_count",
    "purpose", "formal_input", "variant_order",
}
DATA_ADMISSION_SCHEMA = "rtdl.goal5791.data_admission.v1"
SOURCE_ADMISSION_SCHEMA = "rtdl.goal5791.source_admission.v1"
CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA = str(
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["schema"])
DATA_AUTHORITY_SCHEMA = (
    "rtdl.goal5791.frozen_triangle_data_and_oracle_authority.v1"
)
FORMAL_WORKER_ENVIRONMENT_KEYS = frozenset(
    str(name) for name in FORMAL_WORKER_ENVIRONMENT_CONTRACT["frozen_keys"]
)
FORMAL_WORKER_DYNAMIC_ENVIRONMENT_KEYS = tuple(
    str(name) for name in FORMAL_WORKER_ENVIRONMENT_CONTRACT["dynamic_keys"]
)
if FORMAL_WORKER_DYNAMIC_ENVIRONMENT_KEYS != (
    "CUPY_CACHE_DIR", "NUMBA_CACHE_DIR",
):
    raise RuntimeError("Goal5791 formal dynamic environment contract drifted")
CUPY_CACHE_ENVIRONMENT_KEY = FORMAL_WORKER_DYNAMIC_ENVIRONMENT_KEYS[0]
NUMBA_CACHE_ENVIRONMENT_KEY = FORMAL_WORKER_DYNAMIC_ENVIRONMENT_KEYS[1]
FORMAL_SOURCE_PATHS = (
    "scripts/goal5791_formal_contract.py",
    "scripts/goal5791_segment_descriptors.py",
    "scripts/goal5791_formal_worker.py",
    "scripts/goal5791_formal_controller.py",
    "scripts/goal5791_formal_evaluate.py",
    "scripts/goal5791_formal_independent_recount.py",
)
SOURCE_MANIFEST_RELATIVE_PATH = (
    "history/internal_docs/goal5791_portable_source_manifest_v1_20260817.json"
)
_SOURCE_MANIFEST_KEYS = {
    "schema", "goal", "status", "base_source_archive_sha256",
    "base_source_manifest_sha256", "base_source_tree_sha256",
    "base_source_file_count_excluding_manifest", "old_source_manifest_removed",
    "product_delta_paths", "product_delta",
    "nonproduct_overlay_count_including_builder", "deep_blob_audit",
    "manifest_is_non_self_referential", "file_count_excluding_this_manifest",
    "source_tree_sha256", "home_or_target_execution_count",
    "formal_worker_count", "registered_performance_timing_count", "files",
}


class Goal5791WorkerError(RuntimeError):
    """Fail-closed error raised before a worker JSON is created."""


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Goal5791WorkerError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                Goal5791WorkerError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Goal5791WorkerError(f"cannot load strict JSON: {path}") from exc
    if not isinstance(value, dict):
        raise Goal5791WorkerError(f"expected one JSON object: {path}")
    return value


def _require_exact_keys(
    value: Mapping[str, object], expected: set[str], label: str,
) -> None:
    observed = set(value)
    if observed != expected:
        raise Goal5791WorkerError(
            f"{label} keys drifted: missing={sorted(expected-observed)!r}, "
            f"extra={sorted(observed-expected)!r}"
        )


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value != "0" * 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_sha256(value: object, label: str) -> str:
    if not _is_sha256(value):
        raise Goal5791WorkerError(f"{label} must be a non-placeholder SHA-256")
    return str(value)


def _resolve_file(path_value: object, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise Goal5791WorkerError(f"{label} must be a nonempty path")
    candidate = Path(path_value)
    try:
        observed = candidate.lstat()
    except OSError as exc:
        raise Goal5791WorkerError(f"{label} cannot be inspected") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if candidate.is_symlink() or bool(
        reparse_flag
        and getattr(observed, "st_file_attributes", 0) & reparse_flag
    ):
        raise Goal5791WorkerError(f"{label} may not be a symlink/reparse path")
    resolved = candidate.resolve()
    if not resolved.is_file():
        raise Goal5791WorkerError(f"{label} is not a regular file")
    return resolved


def _resolve_directory(path_value: object, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise Goal5791WorkerError(f"{label} must be a nonempty path")
    candidate = Path(path_value)
    try:
        observed = candidate.lstat()
    except OSError as exc:
        raise Goal5791WorkerError(f"{label} cannot be inspected") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if candidate.is_symlink() or bool(
        reparse_flag
        and getattr(observed, "st_file_attributes", 0) & reparse_flag
    ):
        raise Goal5791WorkerError(f"{label} may not be a symlink/reparse path")
    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise Goal5791WorkerError(f"{label} is not a directory")
    return resolved


def _canonical_write_create_only(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _sealed_payload(payload: Mapping[str, object], field: str) -> dict[str, object]:
    if field in payload:
        raise Goal5791WorkerError(f"payload already has seal field {field}")
    result = dict(payload)
    result[field] = digest(payload)
    return result


@dataclass(frozen=True)
class WorkerAuthorityContext:
    preexecution: dict[str, object]
    formal: dict[str, object]
    preexecution_file_sha256: str
    formal_authority_file_sha256: str
    target_binding: dict[str, object]
    repository_root: Path


def _load_authority_context(
    *, repository_root: Path, preexecution_path: Path,
    formal_authority_path: Path,
) -> WorkerAuthorityContext:
    """Use the shared contract's strict loaders; never duplicate authority law."""

    preexecution_file_sha = file_sha256(preexecution_path)
    preexecution = load_preexecution_authority(
        preexecution_path,
        repository_root=repository_root,
        require_target_binding=True,
    )
    target = preexecution.get("target_materialization_binding")
    if not isinstance(target, dict):
        raise Goal5791WorkerError("preexecution authority omitted target binding")

    # The owner-authority loader is added to the same frozen contract module.
    # Importing it here (rather than copying its checks into this worker) keeps
    # exactly one authority interpretation for worker and controller.
    from scripts import goal5791_formal_contract as formal_contract

    loader = getattr(
        formal_contract, "load_owner_formal_execution_authority", None)
    if loader is None:
        raise Goal5791WorkerError(
            "shared formal-contract owner-authority loader is unavailable"
        )
    formal = loader(
        formal_authority_path,
        preexecution_authority=preexecution,
        preexecution_authority_file_sha256=preexecution_file_sha,
    )
    if not isinstance(formal, dict):
        raise Goal5791WorkerError("formal authority loader returned no object")
    return WorkerAuthorityContext(
        preexecution=dict(preexecution),
        formal=dict(formal),
        preexecution_file_sha256=preexecution_file_sha,
        formal_authority_file_sha256=file_sha256(formal_authority_path),
        target_binding=dict(target),
        repository_root=repository_root.resolve(),
    )


def dataset_oracle_record(
    dataset_id: str, record: Mapping[str, object],
) -> dict[str, object]:
    """Canonical per-dataset oracle payload pinned by preexecution authority."""

    return {
        "schema": "rtdl.goal5791.dataset_oracle_contract.v1",
        "dataset_id": dataset_id,
        "input_sha256": record["sha256"],
        "expected_triangle_count": record["expected_triangle_count"],
        "oracle_authority_id": record["oracle_authority_id"],
        "paper_algorithm": "RT-2A1",
    }


def _load_data_authority(
    authority: WorkerAuthorityContext,
) -> tuple[dict[str, object], Path]:
    record = authority.preexecution["authority_records"]["data_authority"]
    relative = Path(*str(record["path"]).split("/"))
    path = (authority.repository_root / relative).resolve()
    value = validate_data_authority(path)
    expected_keys = {
        "schema", "goal", "date", "status", "paper_algorithm",
        "data_bundle", "edge_record_contract", "datasets", "scope",
        "authorization", "authority_sha256",
    }
    _require_exact_keys(value, expected_keys, "data authority")
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    if (
        value["schema"] != DATA_AUTHORITY_SCHEMA
        or value["goal"] != GOAL
        or value["paper_algorithm"] != "RT-2A1"
        or not isinstance(value["status"], str)
        or "NOT_EXECUTION_AUTHORITY" not in value["status"]
        or digest(unsigned) != claimed
        or file_sha256(path) != record["sha256"]
        or path.stat().st_size != record["bytes"]
    ):
        raise Goal5791WorkerError("frozen data authority drifted")
    edge_contract = value["edge_record_contract"]
    if not isinstance(edge_contract, dict) or (
        edge_contract.get("encoding") != "little_endian_signed_int32_pair"
        or edge_contract.get("bytes_per_record") != 8
        or edge_contract.get("loader")
            != "build_segmented_rt_graph_csr_binary"
        or edge_contract.get("max_relation_rows") != 1_000_000
        or edge_contract.get("max_directed_edge_rows") != 1_000_000
    ):
        raise Goal5791WorkerError("frozen data loader contract drifted")
    datasets = value["datasets"]
    if not isinstance(datasets, dict) or set(datasets) != set(DATASET_IDS):
        raise Goal5791WorkerError("frozen data authority dataset set drifted")
    pre_inputs = authority.preexecution["dataset_input_sha256"]
    pre_oracles = authority.preexecution["oracle_authority_sha256"]
    for dataset_id in DATASET_IDS:
        dataset = datasets[dataset_id]
        if not isinstance(dataset, dict) or set(dataset) != {
            "display_id", "member", "sha256", "bytes",
            "expected_triangle_count", "oracle_authority_id",
            "oracle_contract", "oracle_authority_sha256",
        }:
            raise Goal5791WorkerError(
                f"frozen data authority record drifted: {dataset_id}"
            )
        if (
            dataset["sha256"] != pre_inputs[dataset_id]
            or dataset["oracle_contract"]
                != dataset_oracle_record(dataset_id, dataset)
            or digest(dataset["oracle_contract"])
                != dataset["oracle_authority_sha256"]
            or dataset["oracle_authority_sha256"] != pre_oracles[dataset_id]
            or type(dataset["bytes"]) is not int
            or dataset["bytes"] <= 0
            or type(dataset["expected_triangle_count"]) is not int
            or dataset["expected_triangle_count"] <= 0
        ):
            raise Goal5791WorkerError(
                f"frozen input/oracle mapping drifted: {dataset_id}"
            )
    return value, path


def _load_data_admission(
    path: Path,
    *,
    authority: WorkerAuthorityContext,
    data_authority: Mapping[str, object],
) -> dict[str, object]:
    value = _load_json(path)
    _require_exact_keys(
        value,
        {
            "schema", "goal", "status", "data_authority_file_sha256",
            "data_authority_sha256", "datasets", "created_before_worker_zero",
            "full_rehash_complete", "unscheduled_bundle_members_opened",
            "drop_caches_or_page_cache_control_used", "admission_sha256",
        },
        "data admission",
    )
    unsigned = dict(value)
    claimed = unsigned.pop("admission_sha256", None)
    data_record = authority.preexecution["authority_records"]["data_authority"]
    if (
        value["schema"] != DATA_ADMISSION_SCHEMA
        or value["goal"] != GOAL
        or value["status"] != "PASS__ALL_SCHEDULED_EDGE_BYTES_REHASHED_BEFORE_WORKER_ZERO"
        or value["data_authority_file_sha256"] != data_record["sha256"]
        or value["data_authority_sha256"]
            != data_authority["authority_sha256"]
        or value["created_before_worker_zero"] is not True
        or value["full_rehash_complete"] is not True
        or value["unscheduled_bundle_members_opened"] is not False
        or value["drop_caches_or_page_cache_control_used"] is not False
        or digest(unsigned) != claimed
    ):
        raise Goal5791WorkerError("data admission header or seal drifted")
    admitted = value["datasets"]
    if not isinstance(admitted, dict) or set(admitted) != set(DATASET_IDS):
        raise Goal5791WorkerError("data admission dataset set drifted")
    for dataset_id in DATASET_IDS:
        row = admitted[dataset_id]
        frozen = data_authority["datasets"][dataset_id]
        if not isinstance(row, dict) or set(row) != {
            "resolved_path", "sha256", "bytes", "st_dev", "st_ino",
            "st_mtime_ns", "st_mode", "read_only", "full_rehash_complete",
        }:
            raise Goal5791WorkerError(
                f"data admission record malformed: {dataset_id}"
            )
        if (
            row["sha256"] != frozen["sha256"]
            or row["bytes"] != frozen["bytes"]
            or row["read_only"] is not True
            or row["full_rehash_complete"] is not True
            or any(type(row[name]) is not int or row[name] < 0 for name in (
                "st_dev", "st_ino", "st_mtime_ns", "st_mode",
            ))
        ):
            raise Goal5791WorkerError(
                f"data admission record differs from authority: {dataset_id}"
            )
    return value


def _normalized_manifest_member(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise Goal5791WorkerError("source manifest member path is empty")
    pure = PurePosixPath(value)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    normalized = "/".join(parts)
    if pure.is_absolute() or ".." in parts or normalized != value:
        raise Goal5791WorkerError(
            f"source manifest member path is unsafe: {value!r}")
    return normalized


def _load_source_manifest(
    runtime: Mapping[str, object],
) -> tuple[dict[str, object], Path, tuple[dict[str, object], ...]]:
    source_root = _resolve_directory(
        runtime["execution_source_root"], "execution source root")
    manifest_path = _resolve_file(
        runtime["execution_source_manifest_path"],
        "execution source manifest",
    )
    expected_path = source_root.joinpath(
        *PurePosixPath(SOURCE_MANIFEST_RELATIVE_PATH).parts
    ).resolve()
    if manifest_path != expected_path:
        raise Goal5791WorkerError("execution source manifest path drifted")
    expected_file_sha = _require_sha256(
        runtime["execution_source_manifest_file_sha256"],
        "execution_source_manifest_file_sha256",
    )
    if file_sha256(manifest_path) != expected_file_sha:
        raise Goal5791WorkerError("execution source manifest bytes drifted")
    value = _load_json(manifest_path)
    _require_exact_keys(value, _SOURCE_MANIFEST_KEYS, "source manifest")
    raw_rows = value["files"]
    if not isinstance(raw_rows, list):
        raise Goal5791WorkerError("source manifest files are not a list")
    rows: list[dict[str, object]] = []
    observed_names: list[str] = []
    folded: set[str] = set()
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, dict):
            raise Goal5791WorkerError(
                f"source manifest row {index} is not an object")
        _require_exact_keys(
            raw, {"path", "size_bytes", "sha256"},
            f"source manifest row {index}",
        )
        name = _normalized_manifest_member(raw["path"])
        folded_name = name.casefold()
        if folded_name in folded:
            raise Goal5791WorkerError("source manifest has a path collision")
        size = raw["size_bytes"]
        if type(size) is not int or size < 0:
            raise Goal5791WorkerError("source manifest byte count is invalid")
        sha = _require_sha256(raw["sha256"], "source manifest member sha256")
        rows.append({"path": name, "size_bytes": size, "sha256": sha})
        observed_names.append(name)
        folded.add(folded_name)
    if observed_names != sorted(observed_names) \
            or SOURCE_MANIFEST_RELATIVE_PATH.casefold() in folded:
        raise Goal5791WorkerError("source manifest order/self-membership drifted")
    if (
        value["schema"] != "rtdl.goal5791.portable_source_manifest.v1"
        or value["goal"] != GOAL
        or value["status"]
            != "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED"
        or value["manifest_is_non_self_referential"] is not True
        or value["file_count_excluding_this_manifest"] != len(rows)
        or value["home_or_target_execution_count"] != 0
        or value["formal_worker_count"] != 0
        or value["registered_performance_timing_count"] != 0
        or digest(rows) != value["source_tree_sha256"]
    ):
        raise Goal5791WorkerError("execution source manifest contract drifted")
    return value, manifest_path, tuple(rows)


def _rehash_execution_source_manifest(
    runtime: Mapping[str, object],
) -> dict[str, object]:
    """Rehash and exact-set audit the complete immutable execution source.

    The portable manifest is intentionally non-self-referential.  Therefore
    the only permitted regular files are its rows plus the manifest itself;
    the only permitted directories are the root and parents implied by those
    files.  This rejects late ``.pyc``/``__pycache__`` materialization as well
    as arbitrary unmanifested payloads before any product import.
    """

    value, manifest_path, rows = _load_source_manifest(runtime)
    source_root = Path(str(runtime["execution_source_root"])).resolve()
    expected_files = {str(row["path"]) for row in rows}
    expected_files.add(SOURCE_MANIFEST_RELATIVE_PATH)
    expected_directories: set[str] = set()
    for name in expected_files:
        parts = PurePosixPath(name).parts[:-1]
        for length in range(1, len(parts) + 1):
            expected_directories.add(PurePosixPath(*parts[:length]).as_posix())

    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)

    def link_or_reparse(path: Path, observed: os.stat_result) -> bool:
        return path.is_symlink() or bool(
            reparse_flag
            and getattr(observed, "st_file_attributes", 0) & reparse_flag
        )

    try:
        root_stat = source_root.lstat()
    except OSError as exc:
        raise Goal5791WorkerError(
            "execution source root cannot be inspected") from exc
    if (
        link_or_reparse(source_root, root_stat)
        or not stat.S_ISDIR(root_stat.st_mode)
    ):
        raise Goal5791WorkerError(
            "execution source root is a link/reparse/special path")
    if root_stat.st_mode & 0o222:
        raise Goal5791WorkerError("execution source root remains writable")

    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    folded_paths: set[str] = set()
    pending = [source_root]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise Goal5791WorkerError(
                f"execution source directory cannot be inspected: {directory}"
            ) from exc
        for entry in entries:
            path = Path(entry.path)
            try:
                observed = entry.stat(follow_symlinks=False)
                relative = path.relative_to(source_root).as_posix()
            except (OSError, ValueError) as exc:
                raise Goal5791WorkerError(
                    f"execution source path cannot be admitted: {path}") from exc
            folded = relative.casefold()
            if folded in folded_paths:
                raise Goal5791WorkerError(
                    "execution source contains a case-folded path collision")
            folded_paths.add(folded)
            if link_or_reparse(path, observed):
                raise Goal5791WorkerError(
                    f"execution source contains a link/reparse path: {relative}")
            if stat.S_ISREG(observed.st_mode):
                actual_files.add(relative)
            elif stat.S_ISDIR(observed.st_mode):
                actual_directories.add(relative)
                pending.append(path)
            else:
                raise Goal5791WorkerError(
                    f"execution source contains a special path: {relative}")
            if observed.st_mode & 0o222:
                raise Goal5791WorkerError(
                    f"execution source path remains writable: {relative}")

    unexpected = sorted(
        (actual_files - expected_files)
        | (actual_directories - expected_directories)
    )
    missing_files = sorted(expected_files - actual_files)
    missing_directories = sorted(expected_directories - actual_directories)
    if unexpected or missing_files or missing_directories:
        raise Goal5791WorkerError(
            "execution source exact path set drifted: "
            f"unexpected={unexpected!r}, missing_files={missing_files!r}, "
            f"missing_directories={missing_directories!r}"
        )

    payload_bytes = 0
    for row in rows:
        path = source_root.joinpath(
            *PurePosixPath(str(row["path"])).parts)
        if path.is_symlink() or not path.is_file():
            raise Goal5791WorkerError(
                f"execution source payload is absent/non-regular: {row['path']}")
        try:
            path.resolve().relative_to(source_root)
        except ValueError as exc:
            raise Goal5791WorkerError(
                f"execution source payload escapes root: {row['path']}") from exc
        observed = path.stat()
        if (
            observed.st_size != row["size_bytes"]
            or observed.st_mode & 0o222
            or file_sha256(path) != row["sha256"]
        ):
            raise Goal5791WorkerError(
                f"execution source payload bytes/mode drifted: {row['path']}")
        payload_bytes += int(row["size_bytes"])
    if manifest_path.stat().st_mode & 0o222:
        raise Goal5791WorkerError("execution source manifest is writable")
    return {
        "execution_source_root": str(source_root),
        "execution_source_manifest_file_sha256": file_sha256(manifest_path),
        "execution_source_tree_sha256": value["source_tree_sha256"],
        "manifest_payload_count": len(rows),
        "manifest_payload_bytes": payload_bytes,
        "full_manifest_rehash_complete": True,
        "all_manifest_payloads_read_only": True,
        "manifest_file_read_only": True,
        "exact_regular_file_set_verified": True,
        "exact_implied_directory_set_verified": True,
        "unmanifested_path_count": 0,
        "missing_manifest_payload_count": 0,
        "symlink_or_special_path_count": 0,
        "all_source_paths_without_write_bits": True,
        "regular_file_count": len(actual_files),
        "source_directory_count_including_root": len(actual_directories) + 1,
        "source_path_count": (
            len(actual_files) + len(actual_directories) + 1),
    }


def _validate_no_gpu_process_state_observation(
    value: object, *, phase: str,
) -> None:
    contract = NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT
    if not isinstance(value, dict) or set(value) != set(contract["fields"]):
        raise Goal5791WorkerError("no-GPU process-state fields drifted")
    names = value.get("loaded_module_names")
    lines = value.get("proc_self_maps_lines")
    prefixes = list(contract["forbidden_module_prefixes"])
    markers = list(contract["forbidden_dso_map_markers"])
    if (
        value.get("schema") != contract["schema"]
        or value.get("phase") != phase
        or value.get("forbidden_module_prefixes") != prefixes
        or value.get("forbidden_dso_map_markers") != markers
        or not isinstance(names, list)
        or names != sorted(set(names))
        or any(not isinstance(name, str) or not name for name in names)
        or not isinstance(lines, list) or not lines
        or any(not isinstance(line, str) or not line or "\n" in line
               or "\r" in line for line in lines)
    ):
        raise Goal5791WorkerError("no-GPU process-state identity drifted")
    reconstructed = ("\n".join(lines) + "\n").encode("utf-8")
    module_matches = sorted({
        name for name in names
        if any(name == prefix or name.startswith(prefix + ".")
               for prefix in prefixes)
    })
    dso_matches = [
        line for line in lines
        if any(marker in line.lower() for marker in markers)
    ]
    if (
        value.get("proc_self_maps_sha256")
            != hashlib.sha256(reconstructed).hexdigest()
        or value.get("forbidden_module_matches") != module_matches
        or value.get("forbidden_dso_map_matches") != dso_matches
        or module_matches or dso_matches
    ):
        raise Goal5791WorkerError("forbidden GPU process state was observed")


def _validate_immutable_control_file_observations(
    value: object, *, control_paths: Mapping[str, Path],
) -> None:
    contract = IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT
    roles = tuple(str(name) for name in contract["roles"])
    fields = set(contract["fields"])
    if not isinstance(value, dict) or set(value) != set(roles) \
            or set(control_paths) != set(roles):
        raise Goal5791WorkerError("immutable control-file roles drifted")
    for role in roles:
        row = value[role]
        path = control_paths[role]
        if not isinstance(row, dict) or set(row) != fields:
            raise Goal5791WorkerError(
                f"immutable control-file fields drifted: {role}")
        if path.is_symlink() or not path.is_file():
            raise Goal5791WorkerError(
                f"immutable control file is not regular: {role}")
        observed = path.stat()
        if (
            row.get("resolved_path") != str(path.resolve())
            or row.get("file_sha256") != file_sha256(path)
            or row.get("bytes") != observed.st_size
            or row.get("st_dev") != observed.st_dev
            or row.get("st_ino") != observed.st_ino
            or row.get("st_mtime_ns") != observed.st_mtime_ns
            or row.get("st_mode") != observed.st_mode
            or row.get("regular_nonlink") is not True
            or row.get("read_only") is not True
            or not stat.S_ISREG(observed.st_mode)
            or observed.st_mode & 0o222
        ):
            raise Goal5791WorkerError(
                f"immutable control-file observation drifted: {role}")


def _load_source_admission(
    path: Path,
    *,
    runtime: Mapping[str, object],
    runtime_file_sha256: str,
    control_paths: Mapping[str, Path],
) -> dict[str, object]:
    source_manifest, _manifest_path, _rows = _load_source_manifest(runtime)
    value = _load_json(path)
    _require_exact_keys(
        value,
        {
            "schema", "goal", "status", "runtime_file_sha256",
            "runtime_sha256", "execution_source_root",
            "execution_source_manifest_file_sha256",
            "execution_source_tree_sha256", "manifest_payload_count",
            "manifest_payload_bytes", "full_manifest_rehash_complete",
            "all_manifest_payloads_read_only", "manifest_file_read_only",
            "exact_regular_file_set_verified",
            "exact_implied_directory_set_verified",
            "unmanifested_path_count", "missing_manifest_payload_count",
            "symlink_or_special_path_count",
            "all_source_paths_without_write_bits", "regular_file_count",
            "source_directory_count_including_root", "source_path_count",
            "controller_bootstrap_observation",
            "created_before_worker_zero", "same_host_root_race_excluded",
            "tcb_boundary", "admission_sha256",
        },
        "source admission",
    )
    unsigned = dict(value)
    claimed = unsigned.pop("admission_sha256", None)
    controller = value.get("controller_bootstrap_observation")
    expected_controller_sources = set(
        CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT[
            "loaded_harness_source_paths"])
    loaded_sources = (
        controller.get("loaded_harness_sources")
        if isinstance(controller, dict) else None
    )
    controller_valid = (
        isinstance(controller, dict)
        and set(controller) == set(
            CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["fields"])
        and controller.get("schema")
            == CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA
        and controller.get("controller_environment_sha256")
            == digest(runtime["formal_worker_environment"])
        and controller.get(
            "controller_environment_exact_frozen_14_keys_verified") is True
        and controller.get("controller_environment_key_count") == 14
        and controller.get("controller_cupy_cache_dir_absent") is True
        and controller.get("preimport_stdlib_bootstrap_verified") is True
        and isinstance(loaded_sources, dict)
        and set(loaded_sources) == expected_controller_sources
        and controller.get(
            "loaded_harness_paths_and_hashes_match_formal_identity_record"
        ) is True
        and controller.get("cuda_context_or_product_import_used") is False
        and controller.get(
            "completed_after_transaction_marker_before_worker_zero") is True
    )
    if controller_valid:
        source_root = Path(str(runtime["execution_source_root"])).resolve()
        formal_sources = runtime["formal_identity_record"]["formal_sources"]
        controller_valid = all(
            isinstance(loaded_sources[name], dict)
            and set(loaded_sources[name]) == {"resolved_path", "file_sha256"}
            and loaded_sources[name]["resolved_path"]
                == str(source_root / Path(*name.split("/")))
            and loaded_sources[name]["file_sha256"] == formal_sources[name]
            for name in expected_controller_sources
        )
    if controller_valid:
        try:
            _validate_immutable_control_file_observations(
                controller["immutable_control_file_observations"],
                control_paths=control_paths,
            )
            _validate_no_gpu_process_state_observation(
                controller["no_gpu_product_process_state_observation"],
                phase="after_shared_import_before_target_probe",
            )
        except (Goal5791WorkerError, KeyError, TypeError):
            controller_valid = False
    if (
        value["schema"] != SOURCE_ADMISSION_SCHEMA
        or value["goal"] != GOAL
        or value["status"]
            != "PASS__FULL_EXECUTION_SOURCE_REHASHED_BEFORE_WORKER_ZERO"
        or value["runtime_file_sha256"] != runtime_file_sha256
        or value["runtime_sha256"] != runtime["runtime_sha256"]
        or value["execution_source_root"]
            != str(Path(str(runtime["execution_source_root"])).resolve())
        or value["execution_source_manifest_file_sha256"]
            != runtime["execution_source_manifest_file_sha256"]
        or value["execution_source_tree_sha256"]
            != source_manifest["source_tree_sha256"]
        or value["full_manifest_rehash_complete"] is not True
        or value["all_manifest_payloads_read_only"] is not True
        or value["manifest_file_read_only"] is not True
        or value["exact_regular_file_set_verified"] is not True
        or value["exact_implied_directory_set_verified"] is not True
        or value["unmanifested_path_count"] != 0
        or value["missing_manifest_payload_count"] != 0
        or value["symlink_or_special_path_count"] != 0
        or value["all_source_paths_without_write_bits"] is not True
        or value["created_before_worker_zero"] is not True
        or value["same_host_root_race_excluded"]
            != SOURCE_ADMISSION_POLICY[
                "same_host_malicious_root_race_excluded"]
        or value["tcb_boundary"]
            != SOURCE_ADMISSION_POLICY["tcb_boundary"]
        or not controller_valid
        or digest(unsigned) != claimed
    ):
        raise Goal5791WorkerError("source admission identity or seal drifted")
    for name in (
        "manifest_payload_count", "manifest_payload_bytes",
        "regular_file_count", "source_directory_count_including_root",
        "source_path_count",
    ):
        if type(value[name]) is not int or value[name] <= 0:
            raise Goal5791WorkerError(f"source admission {name} is invalid")
    expected_directories = {""}
    for row in _rows:
        parts = PurePosixPath(str(row["path"])).parts[:-1]
        expected_directories.update(
            PurePosixPath(*parts[:length]).as_posix()
            for length in range(1, len(parts) + 1)
        )
    manifest_parts = PurePosixPath(SOURCE_MANIFEST_RELATIVE_PATH).parts[:-1]
    expected_directories.update(
        PurePosixPath(*manifest_parts[:length]).as_posix()
        for length in range(1, len(manifest_parts) + 1)
    )
    if (
        value["regular_file_count"] != value["manifest_payload_count"] + 1
        or value["source_directory_count_including_root"]
            != len(expected_directories)
        or value["source_path_count"]
            != value["regular_file_count"]
            + value["source_directory_count_including_root"]
    ):
        raise Goal5791WorkerError("source admission exact-set counts drifted")
    return value


def _validate_formal_worker_environment(
    environment: object, *, native: Path,
) -> None:
    if not isinstance(environment, dict) \
            or set(environment) != FORMAL_WORKER_ENVIRONMENT_KEYS or any(
        not isinstance(key, str)
        or not isinstance(item, str)
        or (
            key != "LD_PRELOAD"
            and not item
        )
        for key, item in environment.items()
    ):
        raise Goal5791WorkerError("formal worker environment is malformed")
    if (
        environment["PYTHONHASHSEED"] != "0"
        or environment["PYTHONDONTWRITEBYTECODE"] != "1"
        or environment["PYTHONNOUSERSITE"] != "1"
        or environment["LC_ALL"]
            != FORMAL_WORKER_ENVIRONMENT_CONTRACT["lc_all"]
        or environment["LD_PRELOAD"]
            != FORMAL_WORKER_ENVIRONMENT_CONTRACT["ld_preload"]
        or Path(environment["RTDL_OPTIX_LIB"]).resolve() != native
        or Path(environment["RTDL_OPTIX_LIBRARY"]).resolve() != native
    ):
        raise Goal5791WorkerError("formal worker environment policy drifted")


def _validate_runtime(
    runtime_path: Path,
    *, authority: WorkerAuthorityContext,
    data_authority: Mapping[str, object],
) -> dict[str, object]:
    value = _load_json(runtime_path)
    _require_exact_keys(value, _RUNTIME_KEYS, "runtime")
    observed_runtime_file_sha256 = file_sha256(runtime_path)
    if (
        value["schema"] != RUNTIME_SCHEMA
        or value["goal"] != GOAL
        or value["status"] != RUNTIME_STATUS
        or value["formal_contract_sha256"] != contract_sha256()
        or value["schedule_sha256"] != schedule_sha256()
        or value["preexecution_authority_file_sha256"]
            != authority.preexecution_file_sha256
        or value["target_materialization_binding_sha256"]
            != authority.target_binding.get("binding_sha256")
        or value["formal_identity_sha256"]
            != authority.target_binding.get("hashes", {}).get(
                "formal_identity_sha256")
        or observed_runtime_file_sha256
            != authority.formal.get("runtime_file_sha256")
        or value["runtime_sha256"] != authority.formal.get("runtime_sha256")
    ):
        raise Goal5791WorkerError("runtime/formal authority identity mismatch")

    budget_record = authority.preexecution.get("authority_records", {}).get(
        "runtime_budget_authority", {})
    if value["runtime_budget_authority_sha256"] != budget_record.get("sha256"):
        raise Goal5791WorkerError("runtime budget authority identity mismatch")
    budget_path = (
        authority.repository_root
        / Path(*str(budget_record.get("path", "")).split("/"))
    ).resolve()
    budget_authority = validate_runtime_budget_authority(budget_path)
    if (
        file_sha256(budget_path) != budget_record.get("sha256")
        or budget_path.stat().st_size != budget_record.get("bytes")
    ):
        raise Goal5791WorkerError("runtime budget authority bytes drifted")
    frozen_budget = budget_authority["frozen_budget"]
    target_hashes = authority.target_binding.get("hashes")
    target_versions = authority.target_binding.get("versions")
    if not isinstance(target_hashes, dict) or not isinstance(target_versions, dict):
        raise Goal5791WorkerError("target binding identities are malformed")

    runtime_sha = _require_sha256(value["runtime_sha256"], "runtime_sha256")
    unsigned = dict(value)
    del unsigned["runtime_sha256"]
    if digest(unsigned) != runtime_sha:
        raise Goal5791WorkerError("runtime self-seal mismatch")

    source_root = _resolve_directory(value["execution_source_root"], "source root")
    python = _resolve_file(value["python_executable"], "python executable")
    native = _resolve_file(value["native_library_path"], "native library")
    optix_include = _resolve_directory(value["optix_include"], "OptiX include")
    cuda_include = _resolve_directory(value["cuda_include"], "CUDA include")
    if not (optix_include / "optix.h").is_file() \
            or not (cuda_include / "cuda.h").is_file():
        raise Goal5791WorkerError("target include trees are incomplete")
    if (
        python != Path(sys.executable).resolve()
        or file_sha256(python) != value["python_executable_sha256"]
        or platform.python_version() != value["python_version"]
        or file_sha256(native) != value["native_library_sha256"]
        or value["native_library_sha256"]
            != target_hashes.get("native_library_sha256")
        or value["python_version"] != target_versions.get("python_version")
        or value["cupy_version"] != target_versions.get("cupy_version")
        or value["optix_sdk_version"] != target_versions.get("optix_sdk_version")
        or value["compute_capability"] != target_versions.get(
            "compute_capability")
    ):
        raise Goal5791WorkerError("live or target runtime identity drifted")

    for version_name in (
        "numba_version", "llvmlite_version", "numpy_version", "cupy_version",
    ):
        if not isinstance(value[version_name], str) or not value[version_name]:
            raise Goal5791WorkerError(f"runtime {version_name} is empty")
    if value["llvmlite_version"] != "0.47.0":
        raise Goal5791WorkerError("Goal5791 requires frozen llvmlite 0.47.0")
    if value["compute_capability"] != "8.9" \
            or value["optix_sdk_version"] != "9.0.0":
        raise Goal5791WorkerError("Goal5791 requires the frozen RTX 4000 Ada target")

    target_authority_path = _resolve_file(
        value["target_materialization_authority_path"],
        "target materialization authority",
    )
    if (
        file_sha256(target_authority_path)
            != value["target_materialization_authority_file_sha256"]
        or value["target_materialization_authority_file_sha256"]
            != target_hashes.get("target_materialization_authority_sha256")
    ):
        raise Goal5791WorkerError("target materialization authority bytes drifted")
    shared_freeze = _resolve_file(
        value["shared_contract_freeze_path"], "shared contract freeze")
    if file_sha256(shared_freeze) != value["shared_contract_freeze_file_sha256"]:
        raise Goal5791WorkerError("shared contract freeze bytes drifted")

    source_manifest, _source_manifest_path, source_rows = (
        _load_source_manifest(value)
    )
    if (
        value["execution_source_manifest_file_sha256"]
            != target_hashes.get("execution_source_manifest_sha256")
        or source_manifest["source_tree_sha256"]
            != target_hashes.get("execution_source_tree_sha256")
    ):
        raise Goal5791WorkerError("execution source manifest/binding drifted")
    identity = value["formal_identity_record"]
    identity_keys = {
        "schema", "prepared_identity_sha256", "runtime_identity_sha256",
        "formal_contract_sha256", "schedule_sha256", "formal_sources",
        "formal_worker_count", "independent_row_count",
        "formal_identity_sha256",
    }
    if not isinstance(identity, dict):
        raise Goal5791WorkerError("formal identity record is malformed")
    _require_exact_keys(identity, identity_keys, "formal identity record")
    identity_unsigned = dict(identity)
    identity_sha = identity_unsigned.pop("formal_identity_sha256", None)
    formal_sources = identity["formal_sources"]
    source_sha_by_name = {
        str(row["path"]): str(row["sha256"]) for row in source_rows
    }
    if (
        identity["schema"] != "rtdl.goal5791.formal_identity.v1"
        or identity["prepared_identity_sha256"]
            != target_hashes.get("prepared_identity_sha256")
        or identity["runtime_identity_sha256"]
            != target_hashes.get("runtime_identity_sha256")
        or identity["formal_contract_sha256"] != contract_sha256()
        or identity["schedule_sha256"] != schedule_sha256()
        or identity["formal_worker_count"] != len(schedule())
        or identity["independent_row_count"] != 6
        or identity_sha != target_hashes.get("formal_identity_sha256")
        or identity_sha != value["formal_identity_sha256"]
        or digest(identity_unsigned) != identity_sha
        or not isinstance(formal_sources, dict)
        or set(formal_sources) != set(FORMAL_SOURCE_PATHS)
        or any(
            formal_sources[name] != source_sha_by_name.get(name)
            for name in FORMAL_SOURCE_PATHS
        )
    ):
        raise Goal5791WorkerError("formal identity source record drifted")

    max_rows = value["max_relation_rows"]
    if type(max_rows) is not int or max_rows != 1_000_000:
        raise Goal5791WorkerError("max_relation_rows drifted")
    datasets = value["datasets"]
    if not isinstance(datasets, dict) or set(datasets) != set(DATASET_IDS):
        raise Goal5791WorkerError("runtime dataset set drifted")
    pre_inputs = authority.preexecution.get("dataset_input_sha256")
    pre_oracles = authority.preexecution.get("oracle_authority_sha256")
    for dataset_id in DATASET_IDS:
        record = datasets[dataset_id]
        frozen = data_authority["datasets"][dataset_id]
        if not isinstance(record, dict):
            raise Goal5791WorkerError(f"runtime dataset {dataset_id} is malformed")
        _require_exact_keys(record, _DATASET_KEYS, f"datasets.{dataset_id}")
        edge = _resolve_file(record["edge_path"], f"datasets.{dataset_id}.edge")
        if (
            record["input_sha256"] != pre_inputs.get(dataset_id)
            or record["oracle_authority_sha256"] != pre_oracles.get(dataset_id)
            or record["input_sha256"] != frozen["sha256"]
            or record["size_bytes"] != frozen["bytes"]
            or record["expected_triangle_count"]
                != frozen["expected_triangle_count"]
            or record["oracle_authority_sha256"]
                != frozen["oracle_authority_sha256"]
            or edge.stat().st_size != record["size_bytes"]
            or type(record["expected_triangle_count"]) is not int
            or record["expected_triangle_count"] < 0
        ):
            raise Goal5791WorkerError(f"runtime dataset {dataset_id} drifted")

    prewarm = value["neutral_prewarm"]
    if not isinstance(prewarm, dict):
        raise Goal5791WorkerError("neutral prewarm is malformed")
    _require_exact_keys(prewarm, _PREWARM_KEYS, "neutral_prewarm")
    prewarm_edge = _resolve_file(prewarm["edge_path"], "neutral prewarm edge")
    if (
        file_sha256(prewarm_edge) != prewarm["input_sha256"]
        or prewarm_edge.stat().st_size != prewarm["size_bytes"]
        or type(prewarm["expected_triangle_count"]) is not int
        or prewarm["expected_triangle_count"] <= 0
        or prewarm["purpose"] != "recipe_jit_cache_neutralization_only"
        or prewarm["formal_input"] is not False
        or prewarm["variant_order"] != [FUSION_OFF, FUSION_ON]
    ):
        raise Goal5791WorkerError("neutral prewarm contract drifted")

    _validate_formal_worker_environment(
        value["formal_worker_environment"], native=native)
    for numeric_name in (
        "worker_timeout_seconds", "formal_conservative_budget_seconds",
    ):
        number = value[numeric_name]
        if isinstance(number, bool) or not isinstance(number, (int, float)) \
                or not math.isfinite(float(number)) or float(number) <= 0:
            raise Goal5791WorkerError(f"runtime {numeric_name} is invalid")
    if value["formal_conservative_budget_seconds"] != frozen_budget[
        "formal_conservative_budget_seconds"
    ]:
        raise Goal5791WorkerError(
            "runtime formal budget differs from frozen budget authority")
    if value["worker_timeout_seconds"] != FORMAL_EXECUTION_POLICY[
        "per_worker_timeout_seconds"
    ]:
        raise Goal5791WorkerError(
            "runtime worker timeout differs from formal execution policy")
    return value


def _validate_cache_dir(cache_dir: Path, *, worker_index: int) -> Path:
    if cache_dir.is_symlink():
        raise Goal5791WorkerError("worker cache root may not be a symlink")
    resolved = cache_dir.resolve()
    if not resolved.is_dir():
        raise Goal5791WorkerError("worker cache root is absent")
    children = {entry.name: entry for entry in resolved.iterdir()}
    if set(children) != {"cupy", "numba"}:
        raise Goal5791WorkerError(
            "worker cache root must contain exact cupy/numba siblings")
    for name, environment_key in (
        ("cupy", CUPY_CACHE_ENVIRONMENT_KEY),
        ("numba", NUMBA_CACHE_ENVIRONMENT_KEY),
    ):
        child = children[name]
        if child.is_symlink() or not child.is_dir() or any(child.iterdir()):
            raise Goal5791WorkerError(
                f"worker {name} cache is unsafe or not initially empty")
        observed = os.environ.get(environment_key)
        if observed is None or Path(observed).resolve() != child.resolve():
            raise Goal5791WorkerError(
                f"{environment_key} does not bind this worker cache")
    expected_suffix = f"worker_{worker_index:04d}"
    if resolved.name != expected_suffix:
        raise Goal5791WorkerError("worker cache name does not bind schedule index")
    return resolved


def _validate_live_worker_environment(
    runtime: Mapping[str, object], *, cache_dir: Path,
) -> None:
    """Require the exec environment to be exactly the frozen allowlist.

    The controller deliberately starts workers with no inherited ambient
    variables.  CUPY_CACHE_DIR and NUMBA_CACHE_DIR are the sole dynamic
    exceptions and are bound to distinct, schedule-indexed, initially empty
    sibling directories outside the execution source.
    """

    frozen = runtime["formal_worker_environment"]
    expected = {str(key): str(value) for key, value in frozen.items()}
    expected[CUPY_CACHE_ENVIRONMENT_KEY] = str(cache_dir / "cupy")
    expected[NUMBA_CACHE_ENVIRONMENT_KEY] = str(cache_dir / "numba")
    observed = dict(os.environ)
    if observed != expected:
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        mismatched = sorted(
            key for key in set(expected) & set(observed)
            if observed[key] != expected[key]
        )
        raise Goal5791WorkerError(
            "live formal worker environment differs from the exact allowlist: "
            f"missing={missing!r}, extra={extra!r}, mismatched={mismatched!r}"
        )


class WorkerBackend(Protocol):
    """The phase interface used by the orchestration and CPU-only tests."""

    def load(self) -> None: ...
    def prepare(self) -> None: ...
    def prewarm(self) -> None: ...
    def execute(self) -> None: ...
    def close(self) -> None: ...
    def seal(self) -> dict[str, object]: ...
    def abort(self) -> None: ...


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Goal5791WorkerError(f"cannot load application module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class _ProductionBackend:
    """Lazy real RT-2A1 backend used only by an authorized target worker."""

    def __init__(
        self,
        *,
        runtime: Mapping[str, object],
        authority: WorkerAuthorityContext,
        worker_spec: Mapping[str, object],
        data_admission: Mapping[str, object],
    ) -> None:
        self.runtime = runtime
        self.authority = authority
        self.worker_spec = worker_spec
        self.data_admission = data_admission
        self.app = None
        self.benchmark = None
        self.graph = None
        self.prewarm_graph = None
        self.executor = None
        self.freeze = None
        self.target_authority = None
        self.descriptors: list[dict[str, object]] = []
        self.descriptor_hashes: list[str] = []
        self.plans: list[object] = []
        self.plan_input_bindings: list[dict[str, object]] = []
        self.tokens: list[object] = []
        self.nonces: list[str] = []
        self.prewarm_descriptors: list[dict[str, object]] = []
        self.prewarm_plans: dict[str, object] = {}
        self.prewarm_tokens: dict[str, object] = {}
        self.prewarm_nonces: dict[str, str] = {}
        self.pending: list[dict[str, object]] = []
        self.scalar_sum = 0
        self.prewarm_receipt: dict[str, object] = {
            "performed": False,
            "order": [],
            "input_sha256": None,
            "rows": [],
            "prepared_only": True,
        }
        self.input_file_observation: dict[str, object] | None = None
        self._closed = False

    @property
    def _dataset(self) -> Mapping[str, object]:
        value = self.runtime["datasets"][self.worker_spec["dataset_id"]]
        if not isinstance(value, Mapping):
            raise Goal5791WorkerError("selected dataset runtime is malformed")
        return value

    def _ensure_source_imports(self) -> None:
        source = Path(str(self.runtime["execution_source_root"])).resolve()
        for candidate in (source / "src", source, source / "scripts"):
            spelling = str(candidate)
            if spelling not in sys.path:
                sys.path.insert(0, spelling)

    def load(self) -> None:
        self._ensure_source_imports()

        # These imports intentionally occur after the loading phase starts.
        import numba
        import llvmlite
        import numpy as np
        import cupy as cp

        if (
            numba.__version__ != self.runtime["numba_version"]
            or llvmlite.__version__ != self.runtime["llvmlite_version"]
            or np.__version__ != self.runtime["numpy_version"]
            or cp.__version__ != self.runtime["cupy_version"]
        ):
            raise Goal5791WorkerError("live NumPy/Numba/CuPy identity drifted")
        source = Path(str(self.runtime["execution_source_root"])).resolve()
        app_path = (
            source / "Paper-reproduction-apps" / "triangle-counting-paper"
            / "v4_whole_app.py"
        )
        self.app = _load_module(
            app_path,
            f"goal5791_triangle_app_{os.getpid()}_{self.worker_spec['worker_index']}",
        )
        self.benchmark = self.app._benchmark()
        dataset = self._dataset
        admitted = self.data_admission["datasets"][
            self.worker_spec["dataset_id"]
        ]
        input_path = Path(str(dataset["edge_path"])).resolve()
        descriptor = os.open(input_path, os.O_RDONLY)
        try:
            before = os.fstat(descriptor)
            observed = {
                "resolved_path": str(input_path),
                "bytes": before.st_size,
                "st_dev": before.st_dev,
                "st_ino": before.st_ino,
                "st_mtime_ns": before.st_mtime_ns,
                "st_mode": before.st_mode,
            }
            if any(observed[name] != admitted[name] for name in observed):
                raise Goal5791WorkerError(
                    "selected dataset fstat differs from pre-worker-zero admission"
                )
            proc_fd = Path(f"/proc/self/fd/{descriptor}")
            if not proc_fd.exists():
                raise Goal5791WorkerError(
                    "formal Linux worker cannot bind loader to its admitted file descriptor"
                )
            loader_path = proc_fd
            self.graph = self.benchmark.build_segmented_rt_graph_csr_binary(
                loader_path,
                expected_triangle_count=int(dataset["expected_triangle_count"]),
            )
            after = os.fstat(descriptor)
            if any(getattr(after, f"st_{name}") != getattr(before, f"st_{name}")
                   for name in ("dev", "ino", "size", "mtime_ns", "mode")):
                raise Goal5791WorkerError(
                    "selected dataset metadata changed during loading"
                )
            self.input_file_observation = {
                "dataset_id": self.worker_spec["dataset_id"],
                **observed,
                "read_only": (before.st_mode & 0o222) == 0,
                "observed_before_loader_read": True,
                "pre_and_post_loader_fstat_equal": True,
                "proc_self_fd_used": loader_path == proc_fd,
            }
        finally:
            os.close(descriptor)
        if self.worker_spec["lifecycle"] == PREPARED:
            prewarm = self.runtime["neutral_prewarm"]
            self.prewarm_graph = self.benchmark.build_segmented_rt_graph_csr_binary(
                prewarm["edge_path"],
                expected_triangle_count=int(prewarm["expected_triangle_count"]),
            )

    def _compile_executor(self):
        from rtdsl.v4_triangle_reduction_device_runtime import (
            VerifiedTriangleDeviceColumnCountExecutor,
        )
        from rtdsl.v4_triangle_standard_library import (
            compile_count_callback,
            compile_standard_triangle_program,
            weighted_hit_count_schema,
        )
        from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

        callback = compile_count_callback()
        schema = weighted_hit_count_schema(callback)
        proof = self.app._proof(callback)
        native = Path(str(self.runtime["native_library_path"])).resolve()
        target = ReferenceTargetProfile(
            provider="optix",
            optix_sdk=str(self.runtime["optix_sdk_version"]),
            compute_capability=str(self.runtime["compute_capability"]),
            native_sha256=str(self.runtime["native_library_sha256"]),
            supports_custom_aabb=True,
            supports_builtin_triangle=True,
        )
        capability = tuple(
            int(part) for part in str(self.runtime["compute_capability"]).split(".")
        )
        program = compile_standard_triangle_program(
            callback,
            schema,
            target,
            proof,
            compute_capability=capability,
            optix_include=Path(str(self.runtime["optix_include"])).resolve(),
            cuda_include=Path(str(self.runtime["cuda_include"])).resolve(),
            expected_python_version=str(self.runtime["python_version"]),
            expected_numba_version=str(self.runtime["numba_version"]),
            expected_numpy_version=str(self.runtime["numpy_version"]),
        )
        return VerifiedTriangleDeviceColumnCountExecutor(
            authority=program.authority,
            contract=program.contract,
            abi=program.abi,
            any_hit_proof_authority=program.proof,
            executable=program.executable,
            native_library_path=native,
        )

    def _validate_product_target_authority(self) -> None:
        from rtdsl.v4_fusion_ablation import (
            load_verified_shared_contract_freeze,
            verify_target_materialization_authority,
        )

        freeze_path = Path(str(self.runtime["shared_contract_freeze_path"]))
        self.freeze = load_verified_shared_contract_freeze(freeze_path.read_bytes())
        target_path = Path(
            str(self.runtime["target_materialization_authority_path"])
        )
        self.target_authority = verify_target_materialization_authority(
            _load_json(target_path)
        )
        hashes = self.authority.target_binding["hashes"]
        nonces = self.authority.target_binding["nonces"]
        expected = {
            "execution_source_archive_sha256": (
                self.target_authority.execution_source_archive_sha256),
            "execution_source_tree_sha256": (
                self.target_authority.execution_source_tree_sha256),
            "native_library_sha256": self.target_authority.native_library_sha256,
            "native_payload_sha256": self.target_authority.native_payload_sha256,
            "target_identity_sha256": self.target_authority.target_identity_sha256,
            "callback_ir_sha256": self.target_authority.callback_ir_sha256,
            "contract_sha256": self.target_authority.contract_sha256,
            "abi_sha256": self.target_authority.abi_sha256,
            "composed_program_sha256": (
                self.target_authority.composed_program_sha256),
            "materializer_sha256": (
                self.target_authority.materializer_source_sha256),
            "target_source_manifest_sha256": (
                self.target_authority.source_manifest_sha256),
        }
        mismatches = {
            name: {"binding": hashes.get(name), "product": observed}
            for name, observed in expected.items()
            if hashes.get(name) != observed
        }
        if (
            mismatches
            or nonces.get("callback_authority_nonce")
                != self.target_authority.callback_authority_nonce
            or self.freeze.freeze_sha256
                != self.target_authority.shared_contract_freeze_sha256
        ):
            raise Goal5791WorkerError(
                "product target authority differs from Goal5791 binding: "
                + repr(mismatches)
            )
        for variant, prefix in (
            (FUSION_OFF, "fusion_off"), (FUSION_ON, "fusion_on")
        ):
            recipe = getattr(
                self.target_authority,
                prefix + "_downstream_operation_recipe",
            ).to_dict()
            recipe_sha = getattr(
                self.target_authority,
                prefix + "_downstream_operation_recipe_sha256",
            )
            binding_recipe = self.authority.target_binding["recipes"][variant]
            if (
                binding_recipe["actual_recipe"] != recipe
                or binding_recipe["actual_recipe_sha256"] != recipe_sha
                or hashes[prefix + "_recipe_sha256"] != recipe_sha
            ):
                raise Goal5791WorkerError(
                    f"product {variant} recipe differs from target binding")

    def _validate_executor_identity(self) -> None:
        hashes = self.authority.target_binding["hashes"]
        nonces = self.authority.target_binding["nonces"]
        expected = {
            "native_library_sha256": self.executor.native_library_sha256,
            "target_identity_sha256": self.executor.target_identity_sha256,
            "callback_ir_sha256": self.executor.callback_ir_sha256,
            "contract_sha256": self.executor.contract_sha256,
            "abi_sha256": self.executor.abi_sha256,
            "composed_program_sha256": self.executor.composed_program_sha256,
        }
        if any(hashes.get(name) != observed for name, observed in expected.items()) \
                or nonces.get("callback_authority_nonce") \
                    != self.executor.callback_authority_nonce:
            raise Goal5791WorkerError("live executor differs from target binding")

    def _build_plan(
        self, descriptor: Mapping[str, object], variant: str,
        *, formal_input: bool, oracle_sha256: str | None = None,
    ) -> tuple[object, dict[str, object]]:
        from rtdsl.v4_fusion_ablation import (
            FusionVariant,
            build_checked_u64_product_sum_ablation_plan,
        )

        source_input_sha256 = (
            self._dataset["input_sha256"]
            if formal_input
            else self.runtime["neutral_prewarm"]["input_sha256"]
        )
        plan_input_binding = self._segment_plan_input_binding(
            descriptor=descriptor,
            source_input_sha256=str(source_input_sha256),
            formal_input=formal_input,
        )
        plan = build_checked_u64_product_sum_ablation_plan(
            self.freeze,
            variant=FusionVariant(variant),
            target_materialization=self.target_authority,
            input_sha256=digest(plan_input_binding),
            output_contract_sha256=output_contract_sha256(),
            oracle_sha256=(
                str(oracle_sha256)
                if oracle_sha256 is not None
                else str(
                    self.authority.preexecution["oracle_authority_sha256"][
                        self.worker_spec["dataset_id"]
                    ]
                )
            ),
            timer_contract_sha256=timer_contract_sha256(
                str(self.worker_spec["lifecycle"])
            ),
            lifecycle_contract_sha256=lifecycle_contract_sha256(
                str(self.worker_spec["lifecycle"])
            ),
            value_count=int(descriptor["query_count"]),
        )
        if plan.input_sha256 != digest(plan_input_binding):
            raise Goal5791WorkerError("segment plan input binding drifted")
        return plan, plan_input_binding

    @staticmethod
    def _segment_plan_input_binding(
        *, descriptor: Mapping[str, object], source_input_sha256: str,
        formal_input: bool,
    ) -> dict[str, object]:
        if type(formal_input) is not bool:
            raise Goal5791WorkerError(
                "segment plan formal_input must be an exact boolean")
        binding = {
            "schema": SEGMENT_PLAN_INPUT_CONTRACT["schema"],
            "source_input_sha256": _require_sha256(
                source_input_sha256, "segment plan source input sha256"),
            "segment_descriptor_sha256": digest(descriptor),
            "formal_input": formal_input,
        }
        if list(binding) != SEGMENT_PLAN_INPUT_CONTRACT["fields"]:
            raise Goal5791WorkerError(
                "segment plan input fields differ from formal contract")
        return binding

    def _nonce(self, *, variant: str, segment_id: int, prewarm: bool) -> str:
        scope = "prewarm" if prewarm else "formal"
        return (
            f"goal5791-{scope}-{self.authority.formal_authority_file_sha256[:16]}-"
            f"pid{os.getpid()}-w{int(self.worker_spec['worker_index']):04d}-"
            f"{variant}-s{segment_id:06d}"
        )

    def prepare(self) -> None:
        if self.graph is None or (
            self.worker_spec["lifecycle"] == PREPARED
            and self.prewarm_graph is None
        ):
            raise Goal5791WorkerError("loading did not construct graph contracts")
        self._validate_product_target_authority()
        self.executor = self._compile_executor()
        self._validate_executor_identity()

        from scripts.goal5791_segment_descriptors import (
            iter_rt2a1_segment_descriptors,
        )

        max_rows = int(self.runtime["max_relation_rows"])
        self.descriptors = [
            dict(item) for item in iter_rt2a1_segment_descriptors(
                self.graph,
                max_relation_rows=max_rows,
                max_directed_edge_rows=max_rows,
            )
        ]
        if not self.descriptors:
            raise Goal5791WorkerError("formal input has no physical segments")
        self.descriptor_hashes = [digest(item) for item in self.descriptors]
        variant = str(self.worker_spec["variant"])
        for descriptor, descriptor_sha in zip(
            self.descriptors, self.descriptor_hashes, strict=True
        ):
            plan, plan_input_binding = self._build_plan(
                descriptor, variant, formal_input=True)
            segment_id = int(descriptor["segment_id"])
            nonce = self._nonce(
                variant=variant, segment_id=segment_id, prewarm=False)
            token = self.executor.admit_fusion_execution_token(
                plan,
                operation_execution_nonce=nonce,
                segment_ordinal=segment_id,
                primitive_count=int(descriptor["primitive_count"]),
                query_count=int(descriptor["query_count"]),
                segment_descriptor_sha256=descriptor_sha,
                plan_input_binding_sha256=digest(plan_input_binding),
            )
            if token.state != "fresh" \
                    or token.plan_input_sha256 != plan.input_sha256:
                raise Goal5791WorkerError("formal token was not freshly admitted")
            self.plans.append(plan)
            self.plan_input_bindings.append(plan_input_binding)
            self.tokens.append(token)
            self.nonces.append(nonce)

        if self.worker_spec["lifecycle"] == PREPARED:
            self.prewarm_descriptors = [
                dict(item) for item in iter_rt2a1_segment_descriptors(
                    self.prewarm_graph,
                    max_relation_rows=max_rows,
                    max_directed_edge_rows=max_rows,
                )
            ]
            if len(self.prewarm_descriptors) != 1:
                raise Goal5791WorkerError(
                    "neutral prewarm must have exactly one segment")
            descriptor = self.prewarm_descriptors[0]
            for prewarm_variant in (FUSION_OFF, FUSION_ON):
                plan, _plan_input_binding = self._build_plan(
                    descriptor,
                    prewarm_variant,
                    formal_input=False,
                    oracle_sha256=digest({
                        "schema": "rtdl.goal5791.neutral_prewarm_oracle.v1",
                        "input_sha256": self.runtime[
                            "neutral_prewarm"]["input_sha256"],
                        "expected_triangle_count": self.runtime[
                            "neutral_prewarm"]["expected_triangle_count"],
                        "formal_input": False,
                    }),
                )
                nonce = self._nonce(
                    variant=prewarm_variant,
                    segment_id=int(descriptor["segment_id"]),
                    prewarm=True,
                )
                token = self.executor.admit_fusion_execution_token(
                    plan,
                    operation_execution_nonce=nonce,
                    segment_ordinal=int(descriptor["segment_id"]),
                    primitive_count=int(descriptor["primitive_count"]),
                    query_count=int(descriptor["query_count"]),
                    segment_descriptor_sha256=digest(descriptor),
                    plan_input_binding_sha256=digest(_plan_input_binding),
                )
                if token.state != "fresh" \
                        or token.plan_input_sha256 != plan.input_sha256:
                    raise Goal5791WorkerError(
                        "prewarm token was not freshly admitted")
                self.prewarm_plans[prewarm_variant] = plan
                self.prewarm_tokens[prewarm_variant] = token
                self.prewarm_nonces[prewarm_variant] = nonce

    def prewarm(self) -> None:
        """Launch, synchronize, and free both recipes in fixed OFF -> ON order."""

        import cupy as cp
        from scripts.goal5791_segment_descriptors import validate_observed_segment

        descriptor = self.prewarm_descriptors[0]
        rows: list[dict[str, object]] = []
        for variant in (FUSION_OFF, FUSION_ON):
            iterator = self.benchmark.iter_segmented_rt_graph_device_geometry(
                self.prewarm_graph,
                paper_algorithm="RT-2A1",
                max_relation_rows=int(self.runtime["max_relation_rows"]),
                max_directed_edge_rows=int(self.runtime["max_relation_rows"]),
            )
            segment = next(iterator)
            try:
                validate_observed_segment(descriptor, segment)
                token = self.prewarm_tokens[variant]
                unsealed = self.executor.execute_segment_unsealed(
                    segment["triangles"],
                    segment["rays"],
                    ray_weights=segment["ray_weights"],
                    fusion_execution_token=token,
                    segment_ordinal=int(descriptor["segment_id"]),
                    segment_descriptor_sha256=digest(descriptor),
                )
                if unsealed.state != "device_complete_unsealed" \
                        or token.state != "consumed":
                    unsealed.abort()
                    raise Goal5791WorkerError("prewarm token/device phase incomplete")
                if int(unsealed.reduced_output) != int(
                    self.runtime["neutral_prewarm"][
                        "expected_triangle_count"]
                ):
                    unsealed.abort()
                    raise Goal5791WorkerError(
                        "neutral prewarm output disagrees with its oracle")
                # Prewarm evidence is intentionally discarded, not promoted to
                # a formal receipt.  Device completion was already captured.
                unsealed.abort()
                cp.cuda.get_current_stream().synchronize()
                try:
                    unexpected = next(iterator)
                except StopIteration:
                    pass
                else:
                    del unexpected
                    raise Goal5791WorkerError(
                        "neutral prewarm generator added a segment")
            finally:
                iterator.close()
                del segment
                cp.get_default_memory_pool().free_all_blocks()
            rows.append({
                "variant": variant,
                "token_pre_admitted_in_preparation": True,
                "token_consumed_once": True,
                "launch_completed": True,
                "synchronized": True,
                "device_pool_freed": True,
                "output_exact": True,
                "formal_evidence_created": False,
            })
        self.prewarm_receipt = {
            "performed": True,
            "order": [FUSION_OFF, FUSION_ON],
            "input_sha256": self.runtime["neutral_prewarm"]["input_sha256"],
            "rows": rows,
            "prepared_only": True,
        }

    def execute(self) -> None:
        """Consume the complete generator under one caller-owned timer."""

        from scripts.goal5791_segment_descriptors import validate_observed_segment

        iterator = self.benchmark.iter_segmented_rt_graph_device_geometry(
            self.graph,
            paper_algorithm="RT-2A1",
            max_relation_rows=int(self.runtime["max_relation_rows"]),
            max_directed_edge_rows=int(self.runtime["max_relation_rows"]),
        )
        scalar_sum = 0
        pending: list[dict[str, object]] = []
        index = 0
        try:
            while True:
                try:
                    # Resuming the generator also executes the preceding
                    # segment's finally/free block.  The terminal next() runs
                    # final cleanup before StopIteration.  Both stay timed.
                    segment = next(iterator)
                except StopIteration:
                    break
                if index >= len(self.descriptors):
                    raise Goal5791WorkerError("device generator added a segment")
                descriptor = self.descriptors[index]
                validate_observed_segment(descriptor, segment)
                token = self.tokens[index]
                plan = self.plans[index]
                if token.state != "fresh":
                    raise Goal5791WorkerError("formal token was consumed early")
                unsealed = self.executor.execute_segment_unsealed(
                    segment["triangles"],
                    segment["rays"],
                    ray_weights=segment["ray_weights"],
                    fusion_execution_token=token,
                    segment_ordinal=int(descriptor["segment_id"]),
                    segment_descriptor_sha256=self.descriptor_hashes[index],
                )
                if unsealed.state != "device_complete_unsealed" \
                        or token.state != "consumed":
                    unsealed.abort()
                    raise Goal5791WorkerError("formal device/token phase incomplete")
                value = int(unsealed.reduced_output)
                if value < 0 or scalar_sum > U64_MAX - value:
                    unsealed.abort()
                    raise OverflowError("Goal5791 segmented U64 scalar sum overflow")
                scalar_sum += value
                pending.append({
                    "unsealed": unsealed,
                    "descriptor": descriptor,
                    "descriptor_sha256": self.descriptor_hashes[index],
                    "plan": plan,
                    "plan_input_binding": self.plan_input_bindings[index],
                    "nonce": self.nonces[index],
                    "token_state_before_execute": "fresh",
                    "token_state_after_execute": token.state,
                })
                del segment
                index += 1
        except BaseException:
            iterator.close()
            for row in pending:
                row["unsealed"].abort()
            raise
        if index != len(self.descriptors) or not pending:
            for row in pending:
                row["unsealed"].abort()
            raise Goal5791WorkerError("device generator segment cardinality drifted")
        self.pending = pending
        self.scalar_sum = scalar_sum

    def close(self) -> None:
        if self.executor is None:
            raise Goal5791WorkerError("close occurred before executor preparation")
        self.executor.close()
        self._closed = True

    @staticmethod
    def _validate_traversal(receipt: Mapping[str, object]) -> None:
        snapshot = receipt.get("native_snapshot")
        if not isinstance(snapshot, Mapping):
            raise Goal5791WorkerError("segment omitted native traversal snapshot")
        successful = int(snapshot.get("successful_launch_count", -1))
        complete = int(snapshot.get("complete_context_launch_count", -1))
        if (
            receipt.get("physical_executor_classification")
                != "optix_traversal_observed"
            or successful <= 0
            or complete != successful
            or any(int(snapshot.get(name, -1)) != 0 for name in (
                "failed_launch_count", "incomplete_context_launch_count",
                "pending_context_at_finish", "session_error",
            ))
            or not snapshot.get("first_traversable")
            or not snapshot.get("last_traversable")
        ):
            raise Goal5791WorkerError(
                "segment lacked complete bound OptiX traversal")

    def seal(self) -> dict[str, object]:
        if not self._closed:
            raise Goal5791WorkerError("evidence sealing preceded owner close")
        if self.input_file_observation is None:
            raise Goal5791WorkerError("selected input file observation is absent")
        from rtdsl.v4_operation_evidence import (
            receipt_from_mapping,
            verify_operation_evidence_receipt,
        )

        input_file_receipt = _sealed_payload(
            {
                "schema": "rtdl.goal5791.worker_input_file_receipt.v1",
                **self.input_file_observation,
            },
            "receipt_sha256",
        )
        segments: list[dict[str, object]] = []
        for row in self.pending:
            unsealed = row["unsealed"]
            descriptor = row["descriptor"]
            plan = row["plan"]
            semantic_binding = {
                "authority": unsealed.authority_nonce,
                "contract": unsealed.contract_sha256,
                "abi": unsealed.abi_sha256,
                "composed_ptx": unsealed.composed_program_sha256,
                "native": unsealed.native_library_sha256,
                "device_column_count": True,
            }
            executed = unsealed.seal()
            if unsealed.state != "sealed" \
                    or executed["fusion_ablation_plan_sha256"] \
                        != plan.plan_sha256:
                raise Goal5791WorkerError("post-timer evidence sealing drifted")
            operation = receipt_from_mapping(
                dict(executed["operation_evidence_receipt"])
            )
            verify_operation_evidence_receipt(
                operation,
                plan.operation_contract(),
                expected_execution_nonce=str(row["nonce"]),
            )
            traversal = dict(executed["traversal_receipt"])
            self._validate_traversal(traversal)
            if int(executed["triangle_count"]) \
                    != int(descriptor["primitive_count"]) \
                    or int(executed["query_count"]) \
                        != int(descriptor["query_count"]):
                raise Goal5791WorkerError(
                    "sealed segment count differs from plan")
            segments.append({
                "segment_id": descriptor["segment_id"],
                "descriptor": descriptor,
                "segment_descriptor_sha256": row["descriptor_sha256"],
                "partition": descriptor["partition"],
                "relation_count": descriptor["relation_count"],
                "primitive_count": descriptor["primitive_count"],
                "query_count": descriptor["query_count"],
                "host_geometry_bytes": descriptor["host_geometry_bytes"],
                "scalar_sum": int(executed["reduced_output"]),
                "output_sha256": executed["output_sha256"],
                "fusion_ablation_plan": plan.to_dict(),
                "plan_input_binding": row["plan_input_binding"],
                "token_admission": {
                    "pre_admitted_in_preparation": True,
                    "admitted_during_phase": "preparation",
                    "creator_pid": os.getpid(),
                    "segment_ordinal": descriptor["segment_id"],
                    "descriptor_sha256": row["descriptor_sha256"],
                    "plan_sha256": plan.plan_sha256,
                    "plan_input_sha256": plan.input_sha256,
                    "operation_execution_nonce": row["nonce"],
                    "state_before_execute": row[
                        "token_state_before_execute"],
                    "state_after_execute": row["token_state_after_execute"],
                    "single_use": True,
                },
                "operation_evidence_receipt": operation.to_dict(),
                "checked_u64_weighted_reduction": executed[
                    "checked_u64_weighted_reduction"],
                "traversal_receipt": traversal,
                "traversal_semantic_binding": semantic_binding,
                "device_phase_terminal_state": "device_complete_unsealed",
                "evidence_phase_terminal_state": "sealed",
                "evidence_sealed_after_device_phase": True,
            })
        expected = int(self._dataset["expected_triangle_count"])
        if not segments or self.scalar_sum != expected:
            raise Goal5791WorkerError(
                "formal output disagrees with the frozen independent oracle"
            )
        return {
            "output_scalar_u64": self.scalar_sum,
            "output_sha256": digest(self.scalar_sum),
            "oracle_output_scalar_u64": expected,
            "oracle_output_sha256": digest(expected),
            "segment_evidence": segments,
            "segment_count": len(segments),
            "prewarm_receipt": dict(self.prewarm_receipt),
            "input_file_receipt": input_file_receipt,
        }

    def abort(self) -> None:
        for row in self.pending:
            try:
                row["unsealed"].abort()
            except BaseException:
                pass
        if self.executor is not None and not self._closed:
            try:
                self.executor.close()
            except BaseException:
                pass
        self._closed = True


def _timed_phase(
    phase: str,
    action: Callable[[], None] | None,
    *,
    clock_ns: Callable[[], int],
) -> tuple[float, dict[str, object]]:
    started = clock_ns()
    if type(started) is not int or started < 0:
        raise Goal5791WorkerError("phase clock returned an invalid start")
    if action is not None:
        action()
        ended = clock_ns()
    else:
        # A structurally absent phase has a true zero-width interval.  Taking a
        # second clock sample would manufacture a positive cold prewarm value.
        ended = started
    if type(ended) is not int or ended < started:
        raise Goal5791WorkerError("phase clock moved backwards")
    seconds = (ended - started) / 1_000_000_000.0
    return seconds, {
        "phase": phase,
        "started_ns": started,
        "ended_ns": ended,
        "seconds": seconds,
    }


def _cache_receipt(
    *,
    cache_dir: Path,
    worker_index: int,
    lifecycle: str,
    initially_empty: bool,
    cold_empty_before_execute: bool,
) -> dict[str, object]:
    payload = {
        "schema": "rtdl.goal5791.worker_cache_receipt.v2",
        "worker_index": worker_index,
        "cupy_cache_dir_identity": digest({
            "worker_index": worker_index,
            "directory_name": cache_dir.name,
        }),
        "cupy_cache_dir_name": cache_dir.name,
        "cupy_cache_relative_path": "cupy",
        "numba_cache_relative_path": "numba",
        "numba_cache_dir_identity": digest({
            "worker_index": worker_index,
            "directory_name": cache_dir.name,
            "relative_path": "numba",
        }),
        "initially_empty_before_product_import": initially_empty,
        "cold_empty_immediately_before_execute": (
            cold_empty_before_execute if lifecycle == COLD else False
        ),
        "cold_empty_before_execute_applicable": lifecycle == COLD,
        "shared_between_workers_or_measured_arms": CACHE_POLICY[
            "shared_cache_between_workers_or_measured_arms"],
        "unique_per_worker": True,
        "prepared_same_worker_cache_contains_both_variant_recipes": (
            lifecycle == PREPARED
        ),
        "selected_recipe_first_compile_inside_execute": lifecycle == COLD,
        "measurement_started_after_both_prewarms": lifecycle == PREPARED,
        "cold_definition": CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": list(CACHE_POLICY["cold_claim_excludes"]),
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"],
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]
        ),
    }
    return _sealed_payload(payload, "receipt_sha256")


def _prewarm_receipt(
    value: Mapping[str, object],
    *,
    lifecycle: str,
    seconds: float,
) -> dict[str, object]:
    if lifecycle == COLD:
        payload = {
            "schema": "rtdl.goal5791.worker_prewarm_receipt.v1",
            "performed": False,
            "order": [],
            "input_sha256": None,
            "rows": [],
            "reported_seconds": 0.0,
        }
    else:
        rows = value.get("rows")
        if (
            value.get("performed") is not True
            or value.get("order")
                != CACHE_POLICY["prepared_neutral_recipe_prewarm_order"]
            or not _is_sha256(value.get("input_sha256"))
            or not isinstance(rows, list)
            or len(rows) != 2
            or seconds <= 0.0
        ):
            raise Goal5791WorkerError("prepared prewarm receipt is incomplete")
        row_keys = {
            "variant", "token_pre_admitted_in_preparation",
            "token_consumed_once", "launch_completed", "synchronized",
            "device_pool_freed", "output_exact", "formal_evidence_created",
        }
        for index, (row, variant) in enumerate(zip(
            rows,
            CACHE_POLICY["prepared_neutral_recipe_prewarm_order"],
            strict=True,
        )):
            if not isinstance(row, Mapping):
                raise Goal5791WorkerError(
                    f"prepared prewarm row {index} is not a mapping")
            _require_exact_keys(row, row_keys, f"prepared prewarm row {index}")
            if (
                row["variant"] != variant
                or any(row[name] is not True for name in (
                    "token_pre_admitted_in_preparation",
                    "token_consumed_once", "launch_completed", "synchronized",
                    "device_pool_freed", "output_exact",
                ))
                or row["formal_evidence_created"] is not False
            ):
                raise Goal5791WorkerError(
                    f"prepared prewarm row {index} is incomplete")
        payload = {
            "schema": "rtdl.goal5791.worker_prewarm_receipt.v1",
            "performed": True,
            "order": list(
                CACHE_POLICY["prepared_neutral_recipe_prewarm_order"]),
            "input_sha256": value["input_sha256"],
            "rows": rows,
            "reported_seconds": seconds,
        }
    return _sealed_payload(payload, "receipt_sha256")


def run_worker(
    *,
    repository_root: Path,
    runtime_path: Path,
    preexecution_path: Path,
    formal_authority_path: Path,
    data_admission_path: Path,
    source_admission_path: Path,
    cache_dir: Path,
    worker_index: int,
    output: Path,
    backend_factory: Callable[..., WorkerBackend] | None = None,
    clock_ns: Callable[[], int] = time.perf_counter_ns,
) -> Path:
    """Run one exact schedule arm and create its JSON only after full success."""

    if output.exists():
        raise FileExistsError(output)
    if not output.parent.is_dir():
        raise Goal5791WorkerError("worker output parent must already exist")
    frozen_schedule = schedule()
    if type(worker_index) is not int or not 0 <= worker_index < len(frozen_schedule):
        raise Goal5791WorkerError("worker index is outside the frozen schedule")
    worker_spec = frozen_schedule[worker_index]

    authority = _load_authority_context(
        repository_root=repository_root.resolve(),
        preexecution_path=preexecution_path.resolve(),
        formal_authority_path=formal_authority_path.resolve(),
    )
    data_authority, _data_authority_path = _load_data_authority(authority)
    runtime = _validate_runtime(
        runtime_path.resolve(),
        authority=authority,
        data_authority=data_authority,
    )
    data_admission = _load_data_admission(
        data_admission_path.resolve(),
        authority=authority,
        data_authority=data_authority,
    )
    runtime_file_sha = file_sha256(runtime_path.resolve())
    source_admission = _load_source_admission(
        source_admission_path.resolve(),
        runtime=runtime,
        runtime_file_sha256=runtime_file_sha,
        control_paths={
            "runtime": runtime_path.resolve(),
            "preexecution_authority": preexecution_path.resolve(),
            "formal_authority": formal_authority_path.resolve(),
        },
    )
    source_observation = _rehash_execution_source_manifest(runtime)
    for name in (
        "execution_source_root", "execution_source_manifest_file_sha256",
        "execution_source_tree_sha256", "manifest_payload_count",
        "manifest_payload_bytes", "full_manifest_rehash_complete",
        "all_manifest_payloads_read_only", "manifest_file_read_only",
        "exact_regular_file_set_verified",
        "exact_implied_directory_set_verified",
        "unmanifested_path_count", "missing_manifest_payload_count",
        "symlink_or_special_path_count",
        "all_source_paths_without_write_bits", "regular_file_count",
        "source_directory_count_including_root", "source_path_count",
    ):
        if source_observation[name] != source_admission[name]:
            raise Goal5791WorkerError(
                f"worker source rehash differs from source admission: {name}")
    source_rehash_receipt = _sealed_payload(
        {
            "schema": "rtdl.goal5791.worker_source_rehash_receipt.v1",
            "worker_index": worker_index,
            "source_admission_sha256": source_admission["admission_sha256"],
            **source_observation,
            "observed_before_product_import": True,
            "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
                "same_host_malicious_root_race_excluded"],
            "tcb_boundary": SOURCE_ADMISSION_POLICY["tcb_boundary"],
        },
        "receipt_sha256",
    )
    selected_admission = data_admission["datasets"][worker_spec["dataset_id"]]
    if Path(str(runtime["datasets"][worker_spec["dataset_id"]][
            "edge_path"])).resolve() != Path(
                str(selected_admission["resolved_path"])).resolve():
        raise Goal5791WorkerError("selected runtime path differs from data admission")

    cache = _validate_cache_dir(cache_dir, worker_index=worker_index)
    _validate_live_worker_environment(runtime, cache_dir=cache)
    initially_empty = (
        not any((cache / "cupy").iterdir())
        and not any((cache / "numba").iterdir())
    )
    if not initially_empty:
        raise Goal5791WorkerError("worker cache changed before product import")

    factory = backend_factory or _ProductionBackend
    backend = factory(
        runtime=runtime,
        authority=authority,
        worker_spec=worker_spec,
        data_admission=data_admission,
    )
    phase_seconds: dict[str, float] = {}
    phase_sequence: list[dict[str, object]] = []
    cold_empty_before_execute = False
    try:
        for phase, action in (
            ("loading", backend.load),
            ("preparation", backend.prepare),
        ):
            seconds, row = _timed_phase(phase, action, clock_ns=clock_ns)
            phase_seconds[phase] = seconds
            phase_sequence.append(row)

        lifecycle = str(worker_spec["lifecycle"])
        if lifecycle == COLD:
            cold_empty_before_execute = not any((cache / "cupy").iterdir())
            if not cold_empty_before_execute:
                raise Goal5791WorkerError(
                    "cold recipe cache was populated before execute")
            seconds, row = _timed_phase(
                "prewarm", None, clock_ns=clock_ns)
        else:
            seconds, row = _timed_phase(
                "prewarm", backend.prewarm, clock_ns=clock_ns)
        phase_seconds["prewarm"] = seconds
        phase_sequence.append(row)

        seconds, row = _timed_phase(
            "execute", backend.execute, clock_ns=clock_ns)
        phase_seconds["execute"] = seconds
        phase_sequence.append(row)
        seconds, row = _timed_phase("close", backend.close, clock_ns=clock_ns)
        phase_seconds["close"] = seconds
        phase_sequence.append(row)

        # Cold is one complete, continuous outer endpoint.  In particular,
        # phase-dispatch bookkeeping and the cold-cache check between the five
        # raw phase intervals stay inside the registered endpoint; summing the
        # per-phase durations would silently exclude that work.  Prepared keeps
        # its separately registered first post-preparation execute interval.
        registered = (
            (
                int(phase_sequence[-1]["ended_ns"])
                - int(phase_sequence[0]["started_ns"])
            ) / 1_000_000_000.0
            if lifecycle == COLD else phase_seconds["execute"]
        )
        validate_phase_accounting(
            lifecycle, phase_seconds, registered, phase_sequence)

        # Everything below is deliberately post-timer: seal receipts, hash,
        # serialize, and compare with the independent oracle.
        evidence = backend.seal()
        prewarm = _prewarm_receipt(
            evidence["prewarm_receipt"],
            lifecycle=lifecycle,
            seconds=phase_seconds["prewarm"],
        )
        if lifecycle == PREPARED and prewarm["input_sha256"] \
                != runtime["neutral_prewarm"]["input_sha256"]:
            raise Goal5791WorkerError(
                "prepared prewarm receipt binds the wrong neutral input")
        cache_evidence = _cache_receipt(
            cache_dir=cache,
            worker_index=worker_index,
            lifecycle=lifecycle,
            initially_empty=initially_empty,
            cold_empty_before_execute=cold_empty_before_execute,
        )
        if evidence["output_scalar_u64"] != evidence["oracle_output_scalar_u64"] \
                or evidence["output_sha256"] != evidence["oracle_output_sha256"]:
            raise Goal5791WorkerError("post-timer oracle comparison failed")
    except BaseException:
        try:
            backend.abort()
        finally:
            # A failed invocation never creates or partially serializes output.
            if output.exists():
                raise Goal5791WorkerError(
                    "failed worker unexpectedly created an output")
        raise

    target = authority.target_binding
    formal = authority.formal
    runtime_budget_sha = runtime["runtime_budget_authority_sha256"]
    runtime_file_sha = file_sha256(runtime_path.resolve())
    if runtime_file_sha != formal["runtime_file_sha256"]:
        raise Goal5791WorkerError("runtime bytes changed during the worker")
    payload = {
        "schema": WORKER_SCHEMA,
        "goal": GOAL,
        "status": "COMPLETE",
        "formal_worker": True,
        "worker_index": worker_index,
        "row_index": worker_spec["row_index"],
        "row_id": worker_spec["row_id"],
        "dataset_id": worker_spec["dataset_id"],
        "lifecycle": worker_spec["lifecycle"],
        "pair_index": worker_spec["pair_index"],
        "order_ordinal": worker_spec["order_ordinal"],
        "variant": worker_spec["variant"],
        "paper_algorithm": worker_spec["paper_algorithm"],
        "mechanism_id": worker_spec["mechanism_id"],
        "parent_pid": os.getpid(),
        "registered_complete_endpoint_seconds": registered,
        "registered_endpoint_is_one_continuous_interval": True,
        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check": (
            lifecycle == COLD
        ),
        "phase_seconds": phase_seconds,
        "phase_sequence": phase_sequence,
        "timer_contract_sha256": timer_contract_sha256(lifecycle),
        "timer_contract": timer_contract(lifecycle),
        "lifecycle_contract_sha256": lifecycle_contract_sha256(lifecycle),
        "lifecycle_contract": lifecycle_contract(lifecycle),
        "input_sha256": authority.preexecution["dataset_input_sha256"][
            worker_spec["dataset_id"]],
        "output_scalar_u64": evidence["output_scalar_u64"],
        "output_sha256": evidence["output_sha256"],
        "oracle_output_scalar_u64": evidence["oracle_output_scalar_u64"],
        "oracle_output_sha256": evidence["oracle_output_sha256"],
        "output_contract_sha256": output_contract_sha256(),
        "oracle_contract_sha256": oracle_contract_sha256(),
        "dataset_oracle_authority_sha256": authority.preexecution[
            "oracle_authority_sha256"][worker_spec["dataset_id"]],
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "runtime_sha256": runtime["runtime_sha256"],
        "runtime_file_sha256": runtime_file_sha,
        "llvmlite_version": runtime["llvmlite_version"],
        "preexecution_authority_file_sha256": (
            authority.preexecution_file_sha256),
        "preexecution_authority_sha256": authority.preexecution[
            "authority_sha256"],
        "target_materialization_binding_sha256": target["binding_sha256"],
        "target_materialization_authority_file_sha256": runtime[
            "target_materialization_authority_file_sha256"],
        "formal_authority_file_sha256": authority.formal_authority_file_sha256,
        "formal_authority_sha256": formal["authority_sha256"],
        "formal_identity_sha256": target["hashes"]["formal_identity_sha256"],
        "runtime_budget_authority_sha256": runtime_budget_sha,
        "data_admission_sha256": data_admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "source_rehash_receipt": source_rehash_receipt,
        "data_authority_file_sha256": authority.preexecution[
            "authority_records"]["data_authority"]["sha256"],
        "input_file_receipt": evidence["input_file_receipt"],
        "target_materialization_binding": target,
        "cache_receipt": cache_evidence,
        "prewarm_receipt": prewarm,
        "segment_count": evidence["segment_count"],
        "segment_evidence": evidence["segment_evidence"],
        "two_phase_execution_evidence_seal_enforced": True,
        "evidence_hashing_or_serialization_inside_registered_timer": False,
        "comparator_inside_registered_timer": False,
        "receipt_serialization_inside_registered_timer": False,
        "execute_timer_continuous_without_pause": True,
        "deep_verification_inside_execute": False,
        "constant_time_pre_admitted_token_binding_only_inside_execute": True,
        "evidence_seal_started_after_registered_endpoint": True,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    sealed = _sealed_payload(payload, "worker_sha256")
    _canonical_write_create_only(output, sealed)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--preexecution-authority", type=Path, required=True)
    parser.add_argument("--formal-authority", type=Path, required=True)
    parser.add_argument("--data-admission", type=Path, required=True)
    parser.add_argument("--source-admission", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--worker-index", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(run_worker(
        repository_root=args.repository_root,
        runtime_path=args.runtime,
        preexecution_path=args.preexecution_authority,
        formal_authority_path=args.formal_authority,
        data_admission_path=args.data_admission,
        source_admission_path=args.source_admission,
        cache_dir=args.cache_dir,
        worker_index=args.worker_index,
        output=args.output,
    ))


if __name__ == "__main__":
    main()

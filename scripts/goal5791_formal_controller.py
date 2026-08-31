#!/usr/bin/env python3
"""Exactly-once, create-only controller for the 96-worker Goal5791 cohort.

The controller never prepares a target and never opens a POD.  It can run only
after the separate target-preparation output and owner formal authority exist.
It rehashes all three scheduled edge files before worker zero, records a sealed
data admission, then launches the frozen schedule sequentially with one fresh
process and one fresh CuPy cache per arm.  A failed or timed-out child is
terminal: there is no retry, resume, replacement, row drop, or relabel path.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time
from typing import Callable, Mapping

# This bootstrap deliberately duplicates only the frozen environment key names
# and fixed locale/loader values.  It runs before any Goal5791/shared import
# when (and only when) this exact file is the Python entrypoint.  The richer
# runtime-bound check below then binds every value and loaded module hash.
_EARLY_FROZEN_ENVIRONMENT_KEYS = frozenset({
    "PYTHONPATH", "PATH", "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE",
    "PYTHONNOUSERSITE", "LC_ALL", "CUDA_HOME", "CUDA_PATH",
    "LD_LIBRARY_PATH", "LD_PRELOAD", "RTDL_OPTIX_LIB",
    "RTDL_OPTIX_LIBRARY", "RTDL_V4_CUDA_PREFIX", "RTDL_V4_OPTIX_PREFIX",
})


def _early_stdlib_controller_bootstrap() -> dict[str, object]:
    entrypoint = Path(__file__).resolve()
    source_root = entrypoint.parents[1]
    expected_entrypoint = (
        source_root / "scripts" / "goal5791_formal_controller.py")
    expected_pythonpath = os.pathsep.join((
        str(source_root / "src"), str(source_root),
        str(source_root / "scripts"),
    ))
    live = dict(os.environ)
    fixed = {
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "LC_ALL": "C.UTF-8",
        "LD_PRELOAD": "",
    }
    if (
        entrypoint != expected_entrypoint
        or Path(__file__).is_symlink()
        or not entrypoint.is_file()
        or set(live) != _EARLY_FROZEN_ENVIRONMENT_KEYS
        or live.get("PYTHONPATH") != expected_pythonpath
        or any(live.get(name) != value for name, value in fixed.items())
        or any(
            not isinstance(live.get(name), str) or not live[name]
            for name in _EARLY_FROZEN_ENVIRONMENT_KEYS - {"LD_PRELOAD"}
        )
    ):
        raise RuntimeError(
            "Goal5791 controller stdlib bootstrap rejected its entrypoint/environment"
        )
    return {
        "entrypoint_path": str(entrypoint),
        "source_root": str(source_root),
        "environment_key_count": 14,
        "unexpected_or_missing_environment_key_count": 0,
        "shared_goal5791_module_import_started_after_this_gate": True,
    }


_EARLY_CONTROLLER_BOOTSTRAP = (
    _early_stdlib_controller_bootstrap() if __name__ == "__main__" else None
)

from scripts import goal5791_formal_contract as _formal_contract_module
from scripts import goal5791_formal_worker as _formal_worker_module
from scripts.goal5791_formal_contract import (
    AUTHORITY_ROLES,
    CACHE_POLICY,
    COLD,
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT,
    DATASET_IDS,
    FORMAL_OUTPUT_LAYOUT_CONTRACT,
    FORMAL_WORKER_ENVIRONMENT_CONTRACT,
    FUSION_OFF,
    FUSION_ON,
    GOAL,
    INDEPENDENT_RECOUNT_REVIEW_STATUS,
    IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT,
    LIFECYCLES,
    NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT,
    PAPER_OUTCOME_CONSEQUENCE_CONTRACT,
    PAIR_COUNT,
    contract_document,
    contract_sha256,
    digest,
    file_sha256,
    schedule,
    schedule_document,
    schedule_sha256,
    RESOURCE_ADMISSION_CONTRACT,
    SOURCE_ADMISSION_POLICY,
    statistical_rows,
    TARGET_RUNTIME_ADMISSION_CONTRACT,
    TRACE_INSTRUMENTATION_CONTRACT,
    result_lifecycle_label,
    result_row_id,
)
from scripts.goal5791_formal_worker import (
    CUPY_CACHE_ENVIRONMENT_KEY,
    NUMBA_CACHE_ENVIRONMENT_KEY,
    DATA_ADMISSION_SCHEMA,
    FORMAL_SOURCE_PATHS,
    SOURCE_ADMISSION_SCHEMA,
    WorkerAuthorityContext,
    _load_authority_context,
    _load_data_authority,
    _load_json,
    _rehash_execution_source_manifest,
    _sealed_payload,
    _validate_runtime,
)


RESULT_SCHEMA = "rtdl.goal5791.formal_controller_result.v1"
COHORT_MANIFEST_SCHEMA = "rtdl.goal5791.formal_cohort_manifest.v1"
RAW_AUTHORITY_MANIFEST_SCHEMA = "rtdl.goal5791.raw_authority_manifest.v1"
RESOURCE_ADMISSION_SCHEMA = str(RESOURCE_ADMISSION_CONTRACT["schema"])
RESOURCE_ADMISSION_STATUS = str(RESOURCE_ADMISSION_CONTRACT["status"])
TARGET_RUNTIME_ADMISSION_SCHEMA = str(
    TARGET_RUNTIME_ADMISSION_CONTRACT["schema"])
TARGET_RUNTIME_ADMISSION_STATUS = str(
    TARGET_RUNTIME_ADMISSION_CONTRACT["status"])
CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA = str(
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["schema"])
MINIMUM_FORMAL_FREE_DISK_BYTES = int(
    FORMAL_OUTPUT_LAYOUT_CONTRACT["minimum_required_free_disk_bytes"])
NVIDIA_SMI_EXECUTABLE = str(
    TARGET_RUNTIME_ADMISSION_CONTRACT["nvidia_smi_executable"])
NVIDIA_SMI_QUERY = str(
    TARGET_RUNTIME_ADMISSION_CONTRACT["nvidia_smi_query"])

EXECUTION_TARGET_KEYS = frozenset(
    str(name)
    for name in FORMAL_OUTPUT_LAYOUT_CONTRACT["execution_target_fields"])
RESOURCE_CONFIRMATION_KEYS = frozenset(
    str(name)
    for name in FORMAL_OUTPUT_LAYOUT_CONTRACT["resource_confirmation_fields"])
CONTROLLER_BOOTSTRAP_SOURCE_PATHS = tuple(
    str(name) for name in CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT[
        "loaded_harness_source_paths"])
FORBIDDEN_GPU_PRODUCT_MODULE_PREFIXES = tuple(
    str(name) for name in NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
        "forbidden_module_prefixes"])
FORBIDDEN_GPU_DSO_MAP_MARKERS = tuple(
    str(name) for name in NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
        "forbidden_dso_map_markers"])


class Goal5791ControllerError(RuntimeError):
    """Terminal controller failure; callers must not retry this transaction."""


def _write_json_create_only(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _copy_create_only(
    source: Path,
    destination: Path,
    *,
    expected_sha256: str | None = None,
    expected_bytes: int | None = None,
) -> None:
    before = source.stat()
    if expected_bytes is not None and before.st_size != expected_bytes:
        raise Goal5791ControllerError(f"authority byte count drifted: {source}")
    with source.open("rb") as read, destination.open("xb") as write:
        shutil.copyfileobj(read, write, length=8 * 1024 * 1024)
    source_sha = file_sha256(source)
    destination_sha = file_sha256(destination)
    os.chmod(destination, stat.S_IMODE(before.st_mode) & ~0o222)
    destination_stat = destination.stat()
    after = source.stat()
    if (
        any(getattr(before, name) != getattr(after, name) for name in (
            "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode",
        ))
        or source_sha != destination_sha
        or (expected_sha256 is not None and source_sha != expected_sha256)
        or (expected_bytes is not None and destination.stat().st_size != expected_bytes)
        or not stat.S_ISREG(destination_stat.st_mode)
        or destination_stat.st_mode & 0o222
    ):
        raise Goal5791ControllerError(f"authority copy drifted: {source}")


def _read_only(mode: int) -> bool:
    return (mode & 0o222) == 0


def _lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _validate_immutable_control_files(
    *, runtime_path: Path, preexecution_path: Path,
    formal_authority_path: Path,
) -> tuple[tuple[Path, Path, Path], dict[str, dict[str, object]]]:
    """Admit the three Stage-B control files before transaction creation."""

    if FORMAL_OUTPUT_LAYOUT_CONTRACT[
        "runtime_preexecution_and_formal_authority_are_canonical_distinct_read_only_regular_nonlink_files_before_marker"
    ] is not True:
        raise Goal5791ControllerError("immutable control-file policy drifted")
    roles = tuple(
        str(name) for name in IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT[
            "roles"])
    inputs = (
        ("runtime", runtime_path),
        ("preexecution_authority", preexecution_path),
        ("formal_authority", formal_authority_path),
    )
    if tuple(name for name, _path in inputs) != roles:
        raise Goal5791ControllerError("immutable control-file roles drifted")
    resolved: list[Path] = []
    observations: dict[str, dict[str, object]] = {}
    for label, raw in inputs:
        canonical = raw.resolve()
        before = raw.stat() if raw.exists() and not raw.is_symlink() else None
        if (
            before is None
            or not raw.is_absolute()
            or raw != canonical
            or raw.is_symlink()
            or not raw.is_file()
            or not stat.S_ISREG(before.st_mode)
            or before.st_mode & 0o222
        ):
            raise Goal5791ControllerError(
                f"{label} is not one canonical read-only regular file")
        observed_sha = file_sha256(raw)
        after = raw.stat()
        stat_fields = (
            "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode")
        if any(
            getattr(before, field) != getattr(after, field)
            for field in stat_fields
        ):
            raise Goal5791ControllerError(
                f"{label} changed during immutable control-file rehash")
        resolved.append(canonical)
        observations[label] = {
            "resolved_path": str(canonical),
            "file_sha256": observed_sha,
            "bytes": before.st_size,
            "st_dev": before.st_dev,
            "st_ino": before.st_ino,
            "st_mtime_ns": before.st_mtime_ns,
            "st_mode": before.st_mode,
            "regular_nonlink": True,
            "read_only": True,
        }
    if len(set(resolved)) != 3:
        raise Goal5791ControllerError("Stage-B control files are not distinct")
    expected_fields = set(
        IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT["fields"])
    if set(observations) != set(roles) or any(
        set(row) != expected_fields for row in observations.values()
    ):
        raise Goal5791ControllerError(
            "immutable control-file observation schema drifted")
    return (resolved[0], resolved[1], resolved[2]), observations


def _verify_immutable_control_files_unchanged(
    observations: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    roles = tuple(
        str(name) for name in IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT[
            "roles"])
    if not isinstance(observations, dict) or set(observations) != set(roles):
        raise Goal5791ControllerError(
            "immutable control-file observations are malformed")
    paths = {
        name: Path(str(observations[name]["resolved_path"]))
        for name in roles
    }
    (_resolved, current) = _validate_immutable_control_files(
        runtime_path=paths["runtime"],
        preexecution_path=paths["preexecution_authority"],
        formal_authority_path=paths["formal_authority"],
    )
    if current != observations:
        raise Goal5791ControllerError(
            "immutable control files changed across transaction marker")
    return current


def _observe_no_gpu_product_process_state(
    *, phase: str, module_names: object | None = None,
    proc_self_maps_bytes: bytes | None = None,
) -> dict[str, object]:
    """Capture a complete, offline-recountable module/maps observation."""

    phases = tuple(
        str(name) for name in NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
            "phases"])
    if phase not in phases:
        raise Goal5791ControllerError("no-GPU process-state phase drifted")
    raw_names = list(sys.modules) if module_names is None else list(module_names)
    if any(not isinstance(name, str) or not name for name in raw_names):
        raise Goal5791ControllerError("loaded module-name observation is invalid")
    names = sorted(set(raw_names))
    if proc_self_maps_bytes is None:
        maps_path = Path("/proc/self/maps")
        if os.name != "posix" or not maps_path.is_file():
            raise Goal5791ControllerError(
                "formal controller requires a real Linux /proc/self/maps")
        proc_self_maps_bytes = maps_path.read_bytes()
    if not isinstance(proc_self_maps_bytes, bytes) or not proc_self_maps_bytes:
        raise Goal5791ControllerError("process maps observation is empty")
    try:
        maps_text = proc_self_maps_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise Goal5791ControllerError(
            "process maps observation is not strict UTF-8") from exc
    if not maps_text.endswith("\n") or "\r" in maps_text:
        raise Goal5791ControllerError(
            "process maps observation is not canonical LF text")
    lines = maps_text[:-1].split("\n")
    if not lines or any(not line for line in lines):
        raise Goal5791ControllerError(
            "process maps observation contains an empty line")
    reconstructed = ("\n".join(lines) + "\n").encode("utf-8")
    if reconstructed != proc_self_maps_bytes:
        raise Goal5791ControllerError(
            "process maps lines do not reconstruct the observed bytes")
    module_matches = sorted({
        name for name in names
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in FORBIDDEN_GPU_PRODUCT_MODULE_PREFIXES
        )
    })
    dso_matches = [
        line for line in lines
        if any(
            marker in line.lower() for marker in FORBIDDEN_GPU_DSO_MAP_MARKERS
        )
    ]
    observation = {
        "schema": NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["schema"],
        "phase": phase,
        "forbidden_module_prefixes": list(
            FORBIDDEN_GPU_PRODUCT_MODULE_PREFIXES),
        "forbidden_dso_map_markers": list(FORBIDDEN_GPU_DSO_MAP_MARKERS),
        "loaded_module_names": names,
        "proc_self_maps_lines": lines,
        "proc_self_maps_sha256": hashlib.sha256(
            proc_self_maps_bytes).hexdigest(),
        "forbidden_module_matches": module_matches,
        "forbidden_dso_map_matches": dso_matches,
    }
    if set(observation) != set(
        NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["fields"]
    ):
        raise Goal5791ControllerError(
            "no-GPU process-state observation schema drifted")
    if module_matches:
        raise Goal5791ControllerError(
            "controller imported a forbidden CUDA/product module")
    if dso_matches:
        raise Goal5791ControllerError(
            "controller process mapped a forbidden CUDA/OptiX/native GPU DSO")
    return _validate_no_gpu_product_process_state_observation(
        observation, phase=phase)


def _validate_no_gpu_product_process_state_observation(
    value: object, *, phase: str,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != set(
        NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["fields"]
    ):
        raise Goal5791ControllerError(
            "no-GPU process-state observation fields drifted")
    module_names = value.get("loaded_module_names")
    maps_lines = value.get("proc_self_maps_lines")
    if (
        value.get("schema")
            != NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["schema"]
        or value.get("phase") != phase
        or value.get("forbidden_module_prefixes")
            != list(FORBIDDEN_GPU_PRODUCT_MODULE_PREFIXES)
        or value.get("forbidden_dso_map_markers")
            != list(FORBIDDEN_GPU_DSO_MAP_MARKERS)
        or not isinstance(module_names, list)
        or module_names != sorted(set(module_names))
        or any(not isinstance(name, str) or not name for name in module_names)
        or not isinstance(maps_lines, list)
        or not maps_lines
        or any(not isinstance(line, str) or not line or "\n" in line
               or "\r" in line for line in maps_lines)
    ):
        raise Goal5791ControllerError(
            "no-GPU process-state observation identity drifted")
    reconstructed = ("\n".join(maps_lines) + "\n").encode("utf-8")
    module_matches = sorted({
        name for name in module_names
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in FORBIDDEN_GPU_PRODUCT_MODULE_PREFIXES
        )
    })
    dso_matches = [
        line for line in maps_lines
        if any(
            marker in line.lower() for marker in FORBIDDEN_GPU_DSO_MAP_MARKERS
        )
    ]
    if (
        value.get("proc_self_maps_sha256")
            != hashlib.sha256(reconstructed).hexdigest()
        or value.get("forbidden_module_matches") != module_matches
        or value.get("forbidden_dso_map_matches") != dso_matches
        or module_matches
        or dso_matches
    ):
        raise Goal5791ControllerError(
            "no-GPU process-state forbidden-state audit failed")
    return dict(value)


def _validate_execution_layout(
    *, repository_root: Path, runtime_path: Path,
    preexecution_path: Path, formal_authority_path: Path,
    runtime: Mapping[str, object], authority: WorkerAuthorityContext,
    requested_output_root: Path,
) -> tuple[Path, Path, Path, Path]:
    """Bind existing Stage-A materialization to a distinct formal output."""

    target = authority.formal.get("execution_target")
    if not isinstance(target, dict) or set(target) != EXECUTION_TARGET_KEYS:
        raise Goal5791ControllerError("formal execution target is malformed")
    try:
        raw_roots = (
            Path(str(target["target_materialization_root"])),
            Path(str(target["create_only_formal_output_root"])),
            Path(str(target["controller_incomplete_staging_root"])),
        )
    except KeyError as exc:
        raise Goal5791ControllerError(
            "formal execution target root binding is incomplete") from exc
    resolved = tuple(path.resolve() for path in raw_roots)
    materialization, formal_output, formal_staging = resolved
    expected_staging = formal_output.with_name(
        f".{formal_output.name}.goal5791_incomplete")
    if (
        any(
            not raw.is_absolute() or raw != resolved_path
            for raw, resolved_path in zip(raw_roots, resolved, strict=True)
        )
        or len(set(resolved)) != 3
        or len({path.parent for path in resolved}) != 1
        or any(
            _overlaps(left, right)
            for index, left in enumerate(resolved)
            for right in resolved[index + 1:]
        )
        or formal_staging != expected_staging
        or requested_output_root != formal_output
        or raw_roots[0].is_symlink()
        or not materialization.is_dir()
        or _lexists(formal_output)
        or _lexists(formal_staging)
        or target.get(
            "target_materialization_root_observed_existing_and_bound_at_authority_creation"
        ) is not True
        or target.get(
            "formal_output_root_observed_absent_at_authority_creation"
        ) is not True
        or target.get(
            "controller_incomplete_staging_root_observed_absent_at_authority_creation"
        ) is not True
        or target.get(
            "preexisting_or_shared_formal_output_root_allowed") is not False
    ):
        raise Goal5791ControllerError(
            "Stage-A materialization/formal-output layout drifted")
    parent = formal_output.parent
    if parent.is_symlink() or not parent.is_dir() or parent.resolve() != parent:
        raise Goal5791ControllerError("formal-output parent is not a stable directory")
    source_root = Path(str(runtime["execution_source_root"])).resolve()
    if (
        source_root != materialization / "source"
        or repository_root.resolve() != source_root
        or _overlaps(source_root, formal_output)
        or _overlaps(source_root, formal_staging)
    ):
        raise Goal5791ControllerError(
            "runtime source and formal output roots overlap or drifted")
    for label, path in (
        ("runtime", runtime_path),
        ("preexecution authority", preexecution_path),
        ("formal authority", formal_authority_path),
    ):
        try:
            path.resolve().relative_to(materialization)
        except ValueError as exc:
            raise Goal5791ControllerError(
                f"{label} is outside the bound materialization root") from exc
    resources = authority.formal.get("resource_confirmation")
    if (
        not isinstance(resources, dict)
        or set(resources) != RESOURCE_CONFIRMATION_KEYS
        or resources.get("formal_output_parent_resolved_path") != str(parent)
    ):
        raise Goal5791ControllerError(
            "formal-output parent differs from owner resource confirmation")
    return materialization, formal_output, formal_staging, parent


def build_resource_admission(
    *, authority: WorkerAuthorityContext, materialization_root: Path,
    formal_output_root: Path, formal_staging_root: Path,
    formal_output_parent: Path,
) -> dict[str, object]:
    """Recheck the owner-bound output-parent capacity before worker zero."""

    resources = authority.formal["resource_confirmation"]
    if not isinstance(resources, dict) \
            or set(resources) != RESOURCE_CONFIRMATION_KEYS:
        raise Goal5791ControllerError(
            "owner resource confirmation fields drifted")
    confirmed = resources["confirmed_free_disk_bytes"]
    authority_observed = resources[
        "formal_output_parent_free_bytes_observed_at_authority_creation"]
    minimum = resources["minimum_required_free_disk_bytes"]
    if (
        type(confirmed) is not int
        or type(authority_observed) is not int
        or type(minimum) is not int
        or minimum != MINIMUM_FORMAL_FREE_DISK_BYTES
        or authority_observed < confirmed
        or confirmed < minimum
    ):
        raise Goal5791ControllerError(
            "owner formal-output capacity confirmation drifted")
    observed = shutil.disk_usage(formal_output_parent).free
    if type(observed) is not int or observed < confirmed or observed < minimum:
        raise Goal5791ControllerError(
            "formal-output parent capacity is insufficient before worker zero")
    payload = {
        "schema": RESOURCE_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": RESOURCE_ADMISSION_STATUS,
        "formal_authority_file_sha256": (
            authority.formal_authority_file_sha256),
        "formal_authority_sha256": authority.formal["authority_sha256"],
        "target_materialization_root": str(materialization_root),
        "create_only_formal_output_root": str(formal_output_root),
        "controller_incomplete_staging_root": str(formal_staging_root),
        "formal_output_parent_resolved_path": str(formal_output_parent),
        "authority_confirmed_free_disk_bytes": confirmed,
        "authority_observed_free_disk_bytes_at_authority_creation": (
            authority_observed),
        "controller_observed_free_disk_bytes_before_worker_zero": observed,
        "minimum_required_free_disk_bytes": minimum,
        "same_parent_sibling_roots_verified": True,
        "controller_observation_meets_authority_confirmed_threshold": True,
        "controller_observation_meets_minimum_required_threshold": True,
        "created_before_worker_zero": True,
    }
    if set(payload) | {"admission_sha256"} != set(
        RESOURCE_ADMISSION_CONTRACT["fields"]
    ):
        raise Goal5791ControllerError("resource admission schema drifted")
    return _sealed_payload(payload, "admission_sha256")


def validate_controller_bootstrap(
    *, repository_root: Path, runtime: Mapping[str, object],
    immutable_control_file_observations: Mapping[str, object],
    process_state_observer: Callable[[str], Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Fail closed on ambient environment or preloaded harness drift.

    This check intentionally happens in the already-loaded controller.  It
    therefore proves the live module paths and bytes that Python selected; it
    does not claim protection against a malicious same-host root before Python
    startup.  The complete source exact-set audit remains a separate gate.
    """

    early = _EARLY_CONTROLLER_BOOTSTRAP
    expected_entrypoint = (
        repository_root.resolve()
        / "scripts" / "goal5791_formal_controller.py"
    )
    if (
        not isinstance(early, dict)
        or early.get("entrypoint_path") != str(expected_entrypoint)
        or early.get("source_root") != str(repository_root.resolve())
        or early.get("environment_key_count") != 14
        or early.get("unexpected_or_missing_environment_key_count") != 0
        or early.get(
            "shared_goal5791_module_import_started_after_this_gate") is not True
    ):
        raise Goal5791ControllerError(
            "controller was not admitted by its pre-import stdlib bootstrap")

    expected_environment = _controlled_environment(runtime)
    frozen_keys = tuple(
        str(name)
        for name in FORMAL_WORKER_ENVIRONMENT_CONTRACT["frozen_keys"]
    )
    live_environment = dict(os.environ)
    if (
        len(frozen_keys) != 14
        or len(set(frozen_keys)) != 14
        or set(expected_environment) != set(frozen_keys)
        or live_environment != expected_environment
        or CUPY_CACHE_ENVIRONMENT_KEY in live_environment
    ):
        raise Goal5791ControllerError(
            "controller live environment differs from the frozen 14-key env")
    verified_control_files = _verify_immutable_control_files_unchanged(
        immutable_control_file_observations)
    if process_state_observer is None:
        process_state_observer = lambda phase: (
            _observe_no_gpu_product_process_state(phase=phase))
    process_state = _validate_no_gpu_product_process_state_observation(
        process_state_observer("after_shared_import_before_target_probe"),
        phase="after_shared_import_before_target_probe",
    )
    gpu_product_used = bool(
        process_state["forbidden_module_matches"]
        or process_state["forbidden_dso_map_matches"])
    if gpu_product_used:
        raise Goal5791ControllerError(
            "controller bootstrap observed forbidden GPU product state")

    formal_identity = runtime.get("formal_identity_record")
    formal_sources = (
        formal_identity.get("formal_sources")
        if isinstance(formal_identity, dict) else None
    )
    if not isinstance(formal_sources, dict) \
            or set(formal_sources) != set(FORMAL_SOURCE_PATHS):
        raise Goal5791ControllerError(
            "controller formal source identity is malformed")
    module_files = {
        "scripts/goal5791_formal_controller.py": __file__,
        "scripts/goal5791_formal_contract.py": getattr(
            _formal_contract_module, "__file__", None),
        "scripts/goal5791_formal_worker.py": getattr(
            _formal_worker_module, "__file__", None),
    }
    observed: dict[str, dict[str, str]] = {}
    source_root = repository_root.resolve()
    for relative in CONTROLLER_BOOTSTRAP_SOURCE_PATHS:
        raw_loaded_path = module_files[relative]
        if not isinstance(raw_loaded_path, str) or not raw_loaded_path:
            raise Goal5791ControllerError(
                f"controller harness module has no file path: {relative}")
        expected_path = source_root / Path(*relative.split("/"))
        loaded_path = Path(raw_loaded_path).resolve()
        expected_hash = formal_sources[relative]
        if (
            expected_path.is_symlink()
            or not expected_path.is_file()
            or loaded_path != expected_path
            or file_sha256(loaded_path) != expected_hash
        ):
            raise Goal5791ControllerError(
                f"controller harness module path/hash drifted: {relative}")
        observed[relative] = {
            "resolved_path": str(loaded_path),
            "file_sha256": str(expected_hash),
        }
    result = {
        "schema": CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA,
        "controller_environment_sha256": digest(expected_environment),
        "controller_environment_exact_frozen_14_keys_verified": True,
        "controller_environment_key_count": 14,
        "controller_cupy_cache_dir_absent": True,
        "preimport_stdlib_bootstrap_verified": True,
        "loaded_harness_sources": observed,
        "loaded_harness_paths_and_hashes_match_formal_identity_record": True,
        "immutable_control_file_observations": verified_control_files,
        "no_gpu_product_process_state_observation": process_state,
        "cuda_context_or_product_import_used": gpu_product_used,
        "completed_after_transaction_marker_before_worker_zero": True,
    }
    if set(result) != set(
        CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["fields"]
    ):
        raise Goal5791ControllerError(
            "controller bootstrap observation schema drifted")
    return result


def build_target_runtime_admission(
    *, authority: WorkerAuthorityContext, runtime: Mapping[str, object],
    environment: Mapping[str, str],
    probe_runner: Callable[..., object] | None = None,
    process_state_observer: Callable[[str], Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Recheck the one visible GPU without importing a CUDA product stack."""

    expected_environment = _controlled_environment(runtime)
    frozen_keys = {
        str(name)
        for name in FORMAL_WORKER_ENVIRONMENT_CONTRACT["frozen_keys"]
    }
    if (
        dict(environment) != expected_environment
        or len(expected_environment) != 14
        or set(expected_environment) != frozen_keys
        or CUPY_CACHE_ENVIRONMENT_KEY in environment
    ):
        raise Goal5791ControllerError(
            "target-runtime probe environment differs from frozen 14-key env")
    if process_state_observer is None:
        process_state_observer = lambda phase: (
            _observe_no_gpu_product_process_state(phase=phase))
    before_process_state = _validate_no_gpu_product_process_state_observation(
        process_state_observer("before_nvidia_smi"),
        phase="before_nvidia_smi",
    )
    if probe_runner is None:
        probe_runner = subprocess.run
    completed = probe_runner(
        [
            NVIDIA_SMI_EXECUTABLE,
            f"--query-gpu={NVIDIA_SMI_QUERY}",
            "--format=csv,noheader",
        ],
        env=dict(environment),
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=True,
        timeout=30,
    )
    stdout = getattr(completed, "stdout", None)
    returncode = getattr(completed, "returncode", 0)
    after_process_state = _validate_no_gpu_product_process_state_observation(
        process_state_observer("after_nvidia_smi"),
        phase="after_nvidia_smi",
    )
    gpu_product_used = any(
        observation["forbidden_module_matches"]
        or observation["forbidden_dso_map_matches"]
        for observation in (before_process_state, after_process_state)
    )
    if gpu_product_used:
        raise Goal5791ControllerError(
            "target-runtime admission observed forbidden GPU product state")
    lines = stdout.splitlines() if isinstance(stdout, str) else []
    if returncode != 0 or len(lines) != 1 or not lines[0].strip():
        raise Goal5791ControllerError(
            "target-runtime probe did not return exactly one visible GPU")
    parts = [item.strip() for item in lines[0].split(",")]
    if len(parts) != 3 or any(not item for item in parts):
        raise Goal5791ControllerError(
            "target-runtime probe row is malformed")
    observed_uuid, observed_driver, observed_compute = parts
    versions = authority.target_binding.get("versions")
    target = authority.formal.get("execution_target")
    if (
        not isinstance(versions, dict)
        or not isinstance(target, dict)
        or observed_uuid != versions.get("gpu_uuid")
        or observed_driver != versions.get("driver_version")
        or observed_compute != versions.get("compute_capability")
    ):
        raise Goal5791ControllerError(
            "live target identity differs from the frozen target binding")
    payload = {
        "schema": TARGET_RUNTIME_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": TARGET_RUNTIME_ADMISSION_STATUS,
        "formal_authority_file_sha256": (
            authority.formal_authority_file_sha256),
        "formal_authority_sha256": authority.formal["authority_sha256"],
        "target_materialization_binding_sha256": authority.target_binding[
            "binding_sha256"],
        "pod_endpoint": target["pod_endpoint"],
        "nvidia_smi_executable": NVIDIA_SMI_EXECUTABLE,
        "nvidia_smi_query": NVIDIA_SMI_QUERY,
        "visible_gpu_row_count": 1,
        "observed_gpu_uuid": observed_uuid,
        "observed_driver_version": observed_driver,
        "observed_compute_capability": observed_compute,
        "controlled_environment_sha256": digest(expected_environment),
        "controlled_environment_exact_14_keys_verified": True,
        "cupy_cache_dir_absent": True,
        "no_gpu_product_process_state_before_nvidia_smi": (
            before_process_state),
        "no_gpu_product_process_state_after_nvidia_smi": (
            after_process_state),
        "cuda_context_or_product_import_used": gpu_product_used,
        "created_before_worker_zero": True,
    }
    if set(payload) | {"admission_sha256"} != set(
        TARGET_RUNTIME_ADMISSION_CONTRACT["fields"]
    ):
        raise Goal5791ControllerError(
            "target-runtime admission schema drifted")
    return _sealed_payload(payload, "admission_sha256")


def build_data_admission(
    *,
    runtime: Mapping[str, object],
    authority: WorkerAuthorityContext,
    data_authority: Mapping[str, object],
) -> dict[str, object]:
    """Rehash all and only the three scheduled inputs before worker zero."""

    rows: dict[str, dict[str, object]] = {}
    for dataset_id in DATASET_IDS:
        runtime_row = runtime["datasets"][dataset_id]
        frozen = data_authority["datasets"][dataset_id]
        path = Path(str(runtime_row["edge_path"])).resolve()
        if path.is_symlink() or not path.is_file():
            raise Goal5791ControllerError(
                f"scheduled input is not one regular file: {dataset_id}")
        before = path.stat()
        observed_sha = file_sha256(path)
        after = path.stat()
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode")
        if any(getattr(before, field) != getattr(after, field) for field in fields):
            raise Goal5791ControllerError(
                f"scheduled input changed during full rehash: {dataset_id}")
        if (
            observed_sha != frozen["sha256"]
            or before.st_size != frozen["bytes"]
            or not _read_only(before.st_mode)
        ):
            raise Goal5791ControllerError(
                f"scheduled input differs from frozen authority: {dataset_id}")
        rows[dataset_id] = {
            "resolved_path": str(path),
            "sha256": observed_sha,
            "bytes": before.st_size,
            "st_dev": before.st_dev,
            "st_ino": before.st_ino,
            "st_mtime_ns": before.st_mtime_ns,
            "st_mode": before.st_mode,
            "read_only": True,
            "full_rehash_complete": True,
        }
    payload = {
        "schema": DATA_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": "PASS__ALL_SCHEDULED_EDGE_BYTES_REHASHED_BEFORE_WORKER_ZERO",
        "data_authority_file_sha256": authority.preexecution[
            "authority_records"]["data_authority"]["sha256"],
        "data_authority_sha256": data_authority["authority_sha256"],
        "datasets": rows,
        "created_before_worker_zero": True,
        "full_rehash_complete": True,
        "unscheduled_bundle_members_opened": False,
        "drop_caches_or_page_cache_control_used": False,
    }
    return _sealed_payload(payload, "admission_sha256")


def build_source_admission(
    *,
    runtime_path: Path,
    runtime: Mapping[str, object],
    controller_bootstrap_observation: Mapping[str, object],
) -> dict[str, object]:
    """Seal the complete exact-set source audit before worker zero."""

    observation = _rehash_execution_source_manifest(runtime)
    payload = {
        "schema": SOURCE_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": "PASS__FULL_EXECUTION_SOURCE_REHASHED_BEFORE_WORKER_ZERO",
        "runtime_file_sha256": file_sha256(runtime_path),
        "runtime_sha256": runtime["runtime_sha256"],
        "controller_bootstrap_observation": dict(
            controller_bootstrap_observation),
        **observation,
        "created_before_worker_zero": True,
        "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
            "same_host_malicious_root_race_excluded"],
        "tcb_boundary": SOURCE_ADMISSION_POLICY["tcb_boundary"],
    }
    return _sealed_payload(payload, "admission_sha256")


def _controlled_environment(runtime: Mapping[str, object]) -> dict[str, str]:
    # Do not inherit ambient CUDA/Numba/CuPy/loader switches into a formal
    # worker.  ``Popen(env=...)`` accepts an intentionally minimal mapping, so
    # the frozen runtime allowlist can be the complete child environment.  A
    # Each worker adds exactly two dynamic keys below: distinct private CuPy
    # and Numba cache siblings under one schedule-indexed worker root.
    frozen = runtime["formal_worker_environment"]
    return {str(key): str(value) for key, value in frozen.items()}


def _kill_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        os.killpg(process.pid, signal.SIGKILL)
    else:
        process.kill()
    process.wait()


def _remove_validated_worker_cache_payloads(
    *, staging: Path, cache_root: Path,
) -> None:
    """Delete cache payloads but retain 96 empty shells for raw recount.

    The shell names are part of the raw cohort topology used to prove one
    private cache per formal worker.  Their contents are explicitly
    non-authoritative and are removed only after both analysis paths pass.
    """

    expected_root = (staging / "worker_caches").resolve()
    resolved_root = cache_root.resolve()
    if (
        cache_root.is_symlink()
        or resolved_root != expected_root
        or resolved_root.parent != staging.resolve()
        or not resolved_root.is_dir()
    ):
        raise Goal5791ControllerError("worker cache payload target drifted")
    expected_names = {
        f"worker_{index:04d}" for index in range(len(schedule()))
    }
    entries = list(resolved_root.iterdir())
    if {entry.name for entry in entries} != expected_names:
        raise Goal5791ControllerError(
            "worker cache payload set differs from exact cohort")
    for entry in entries:
        if entry.is_symlink() or not entry.is_dir() \
                or entry.resolve().parent != resolved_root:
            raise Goal5791ControllerError(
                f"worker cache directory is unsafe to remove: {entry.name}")
        for descendant in entry.rglob("*"):
            if descendant.is_symlink() or (
                not descendant.is_dir() and not descendant.is_file()
            ):
                raise Goal5791ControllerError(
                    f"worker cache contains a link or special file: {entry.name}")
            try:
                descendant.resolve().relative_to(resolved_root)
            except ValueError as exc:
                raise Goal5791ControllerError(
                    f"worker cache member escapes cache root: {entry.name}"
                ) from exc
    for entry in entries:
        shutil.rmtree(entry)
        entry.mkdir()
    final_entries = list(resolved_root.iterdir())
    if (
        {entry.name for entry in final_entries} != expected_names
        or any(
            entry.is_symlink()
            or not entry.is_dir()
            or entry.resolve().parent != resolved_root
            or any(entry.iterdir())
            for entry in final_entries
        )
    ):
        raise Goal5791ControllerError(
            "worker cache payload removal did not preserve exact empty shells"
        )


def _run_child(
    command: list[str],
    *,
    environment: Mapping[str, str],
    timeout_seconds: float,
    label: str,
) -> None:
    process = subprocess.Popen(
        command,
        env=dict(environment),
        start_new_session=True,
        stdin=subprocess.DEVNULL,
    )
    try:
        returncode = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _kill_process(process)
        raise Goal5791ControllerError(
            f"{label} timed out terminally; retry is forbidden") from exc
    if returncode != 0:
        raise Goal5791ControllerError(
            f"{label} failed terminally with status {returncode}; retry is forbidden"
        )


def _validate_worker_output(
    path: Path,
    *,
    worker_spec: Mapping[str, object],
    seen_pids: set[int],
    runtime_file_sha256: str,
    source_admission_sha256: str,
    llvmlite_version: str,
) -> dict[str, object]:
    value = _load_json(path)
    unsigned = dict(value)
    claimed = unsigned.pop("worker_sha256", None)
    pid = value.get("parent_pid")
    if (
        value.get("schema") != "rtdl.goal5791.formal_worker.v1"
        or value.get("goal") != GOAL
        or value.get("status") != "COMPLETE"
        or value.get("formal_worker") is not True
        or value.get("worker_index") != worker_spec["worker_index"]
        or value.get("row_index") != worker_spec["row_index"]
        or value.get("row_id") != worker_spec["row_id"]
        or value.get("dataset_id") != worker_spec["dataset_id"]
        or value.get("lifecycle") != worker_spec["lifecycle"]
        or value.get("pair_index") != worker_spec["pair_index"]
        or value.get("order_ordinal") != worker_spec["order_ordinal"]
        or value.get("variant") != worker_spec["variant"]
        or value.get("paper_algorithm") != worker_spec["paper_algorithm"]
        or value.get("mechanism_id") != worker_spec["mechanism_id"]
        or value.get("formal_contract_sha256") != contract_sha256()
        or value.get("schedule_sha256") != schedule_sha256()
        or value.get("runtime_file_sha256") != runtime_file_sha256
        or value.get("source_admission_sha256") != source_admission_sha256
        or value.get("llvmlite_version") != llvmlite_version
        or value.get("retry_resume_replacement_row_drop_relabel_used") is not False
        or not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 0
        or pid in seen_pids
        or claimed != digest(unsigned)
    ):
        raise Goal5791ControllerError(
            f"worker output identity/seal drifted: {worker_spec['worker_index']}")
    seen_pids.add(pid)
    return value


def _registered_endpoint_nanoseconds(worker: Mapping[str, object]) -> int:
    sequence = worker.get("phase_sequence")
    if not isinstance(sequence, list) or len(sequence) != 5:
        raise Goal5791ControllerError("worker registered endpoint intervals drifted")
    if worker.get("lifecycle") == COLD:
        first = sequence[0]
        last = sequence[-1]
        if not isinstance(first, Mapping) or not isinstance(last, Mapping):
            raise Goal5791ControllerError("worker cold interval shape drifted")
        return int(last["ended_ns"]) - int(first["started_ns"])
    execute = sequence[3]
    if not isinstance(execute, Mapping) or execute.get("phase") != "execute":
        raise Goal5791ControllerError("worker execute interval shape drifted")
    return int(execute["ended_ns"]) - int(execute["started_ns"])


def _exact_integer_median(values: list[int]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        raise Goal5791ControllerError("empty exact endpoint sample")
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return Fraction(ordered[midpoint], 1)
    return Fraction(ordered[midpoint - 1] + ordered[midpoint], 2)


def _trace_gate_expectations(
    worker_rows: list[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, list[Mapping[str, object]]]] = {}
    for worker in worker_rows:
        row_id = worker.get("row_id")
        variant = worker.get("variant")
        if not isinstance(row_id, str) or variant not in {FUSION_OFF, FUSION_ON}:
            raise Goal5791ControllerError("worker trace-gate identity drifted")
        grouped.setdefault(row_id, {FUSION_OFF: [], FUSION_ON: []})[
            str(variant)
        ].append(worker)
    expected: dict[str, dict[str, object]] = {}
    max_fraction = Fraction(str(
        TRACE_INSTRUMENTATION_CONTRACT["small_relative_max_fraction"]
    ))
    per_segment_bound = int(
        TRACE_INSTRUMENTATION_CONTRACT[
            "five_extra_event_differential_bound_per_segment_ns"
        ]
    )
    for row in statistical_rows():
        row_id = str(row["row_id"])
        variants = grouped.get(row_id)
        if variants is None or any(
            len(variants[name]) != PAIR_COUNT for name in (FUSION_OFF, FUSION_ON)
        ):
            raise Goal5791ControllerError(
                f"worker trace-gate row cardinality drifted: {row_id}"
            )
        segment_counts = {
            int(worker["segment_count"])
            for name in (FUSION_OFF, FUSION_ON)
            for worker in variants[name]
        }
        if len(segment_counts) != 1:
            raise Goal5791ControllerError(
                f"worker trace-gate segment count drifted: {row_id}"
            )
        segment_count = next(iter(segment_counts))
        difference_ns = abs(
            _exact_integer_median([
                _registered_endpoint_nanoseconds(worker)
                for worker in variants[FUSION_OFF]
            ])
            - _exact_integer_median([
                _registered_endpoint_nanoseconds(worker)
                for worker in variants[FUSION_ON]
            ])
        )
        bound_ns = per_segment_bound * segment_count
        exact_fraction = (
            Fraction(bound_ns, 1) / difference_ns
            if difference_ns > 0 else None
        )
        expected[row_id] = {
            "segment_count": segment_count,
            "bound_ns": bound_ns,
            "bound_seconds": bound_ns / 1_000_000_000.0,
            "absolute_difference_seconds": float(
                difference_ns / 1_000_000_000
            ),
            "fraction": (
                float(exact_fraction) if exact_fraction is not None else None
            ),
            "small": (
                exact_fraction is not None and exact_fraction <= max_fraction
            ),
        }
    if set(grouped) != set(expected):
        raise Goal5791ControllerError("worker trace-gate row set drifted")
    return expected


def _paper_outcome_summary(rows: list[Mapping[str, object]]) -> dict[str, object]:
    paper_clear_ids: list[str] = []
    trace_inconclusive_ids: list[str] = []
    for row in rows:
        row_id = row.get("row_id")
        if not isinstance(row_id, str):
            raise Goal5791ControllerError("paper outcome row id drifted")
        eligible = row.get("mechanism_performance_statement_eligible") is True
        if eligible:
            paper_clear_ids.append(row_id)
        if row.get("classification") == "ci_clear_win" and not eligible:
            trace_inconclusive_ids.append(row_id)
    paper_clear_count = len(paper_clear_ids)
    if paper_clear_count == 0:
        branch = "zero_clear_winning_rows"
    elif paper_clear_count == len(statistical_rows()):
        branch = "all_six_clear_winning_rows"
    else:
        branch = "mixed_one_through_five_clear_winning_rows"
    selection_payload = {
        "schema": "rtdl.goal5791.paper_outcome_consequence_selection.v1",
        "paper_clear_winning_row_count": paper_clear_count,
        "paper_clear_winning_row_ids": paper_clear_ids,
        "ci_clear_win_count": paper_clear_count + len(trace_inconclusive_ids),
        "ci_clear_win_trace_cost_inconclusive_count": (
            len(trace_inconclusive_ids)
        ),
        "ci_clear_win_trace_cost_inconclusive_row_ids": (
            trace_inconclusive_ids
        ),
        "paper_outcome_consequence_contract_sha256": digest(
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT
        ),
        "paper_outcome_consequence_branch": branch,
        "paper_outcome_consequence": dict(
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT[branch]
        ),
    }
    return {
        "paper_clear_winning_row_count": paper_clear_count,
        "paper_clear_winning_row_ids": paper_clear_ids,
        "ci_clear_win_trace_cost_inconclusive_count": (
            len(trace_inconclusive_ids)
        ),
        "ci_clear_win_trace_cost_inconclusive_row_ids": (
            trace_inconclusive_ids
        ),
        "paper_outcome_consequence_selection": {
            **selection_payload,
            "selection_sha256": digest(selection_payload),
        },
    }


def _analysis_rows(
    path: Path,
    *,
    schema: str,
    status: str,
    seal_field: str,
    runtime: Mapping[str, object],
    authority: WorkerAuthorityContext,
    admission: Mapping[str, object],
    authority_manifest: Mapping[str, object],
    runtime_file_sha256: str,
    source_admission: Mapping[str, object],
    target_runtime_admission: Mapping[str, object],
    target_runtime_admission_file_sha256: str,
    resource_admission: Mapping[str, object],
    resource_admission_file_sha256: str,
    worker_rows: list[Mapping[str, object]],
    raw_worker_values: list[Mapping[str, object]],
) -> object:
    value = _load_json(path)
    unsigned = dict(value)
    claimed = unsigned.pop(seal_field, None)
    rows = value.get("rows")
    worker_count = len(schedule())
    row_count = len(statistical_rows())
    classifications = (
        value.get("ci_clear_win_count"), value.get("ci_clear_loss_count"),
        value.get("ci_crossing_count"),
    )
    recount_schema = "rtdl.goal5791.formal_independent_recount.v1"
    recount_primary_pin_valid = True
    if schema == recount_schema:
        primary_path = path.parent / "EVALUATION.json"
        primary = _load_json(primary_path)
        recount_primary_pin_valid = (
            value.get("raw_root_mode") == "analysis_stage"
            and value.get("primary_evaluation_file_sha256")
                == file_sha256(primary_path)
            and value.get("primary_evaluation_sha256")
                == primary.get("evaluation_sha256")
            and value.get(
                "primary_evaluation_authority_pins_verified") is True
        )
    if (
        value.get("schema") != schema
        or value.get("goal") != GOAL
        or value.get("status") != status
        or claimed != digest(unsigned)
        or value.get("formal_contract_sha256") != contract_sha256()
        or value.get("schedule_sha256") != schedule_sha256()
        or value.get("preexecution_authority_file_sha256")
            != authority.preexecution_file_sha256
        or value.get("target_materialization_binding_sha256")
            != authority.target_binding["binding_sha256"]
        or value.get("target_materialization_authority_file_sha256")
            != runtime["target_materialization_authority_file_sha256"]
        or value.get("formal_authority_file_sha256")
            != authority.formal_authority_file_sha256
        or value.get("runtime_sha256") != runtime["runtime_sha256"]
        or value.get("runtime_file_sha256") != runtime_file_sha256
        or value.get("data_admission_sha256") != admission["admission_sha256"]
        or value.get("raw_authority_manifest_sha256")
            != authority_manifest["manifest_sha256"]
        or value.get("source_admission_sha256")
            != source_admission["admission_sha256"]
        or value.get("target_runtime_admission_sha256")
            != target_runtime_admission["admission_sha256"]
        or value.get("target_runtime_admission_file_sha256")
            != target_runtime_admission_file_sha256
        or value.get("resource_admission_sha256")
            != resource_admission["admission_sha256"]
        or value.get("resource_admission_file_sha256")
            != resource_admission_file_sha256
        or value.get("raw_worker_set_sha256") != digest([
            row["worker_sha256"] for row in worker_rows
        ])
        or value.get("worker_count") != worker_count
        or value.get("unique_parent_pid_count") != worker_count
        or value.get("unique_worker_cache_count") != worker_count
        or value.get("exact_output_worker_count") != worker_count
        or value.get("behavioral_true_optix_worker_count") != worker_count
        or value.get("independent_row_count") != row_count
        or not isinstance(rows, list)
        or len(rows) != row_count
        or value.get("result_lifecycle_labels") != {
            lifecycle: result_lifecycle_label(lifecycle)
            for lifecycle in LIFECYCLES
        }
        or value.get("trace_cost_diagnostic_authority") != {
            "file_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_file_sha256"
            ],
            "diagnostic_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_sha256"
            ],
            "per_event_record_cost_bound_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "per_event_record_cost_bound_ns"
                ]
            ),
            "five_extra_event_differential_bound_per_segment_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "five_extra_event_differential_bound_per_segment_ns"
                ]
            ),
            "required_before_stage_b_worker_zero": True,
        }
        or value.get("independent_recount_external_review_status")
            != INDEPENDENT_RECOUNT_REVIEW_STATUS
        or value.get(
            "every_figure_caption_must_state_includes_evidence_overhead"
        ) is not True
        or any(type(count) is not int or count < 0 for count in classifications)
        or sum(classifications) != row_count
        or value.get("all_six_rows_retained") is not True
        or value.get("cross_dataset_lifecycle_or_row_compensation_used") is not False
        or value.get("operation_delta_exact_all_workers") is not True
        or value.get("same_source_target_and_optix_producer_all_workers") is not True
        or value.get("operating_system_page_cache_controlled_or_dropped")
            != CACHE_POLICY["operating_system_page_cache_controlled_or_dropped"]
        or value.get("operating_system_page_cache_scope")
            != CACHE_POLICY["operating_system_page_cache_scope"]
        or value.get("same_cohort_abba_symmetry_is_page_cache_mitigation_not_control")
            != CACHE_POLICY[
                "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control"]
        or value.get("cold_process_warm_system_definition")
            != CACHE_POLICY["cold_definition"]
        or value.get("cold_process_warm_system_excludes")
            != CACHE_POLICY["cold_claim_excludes"]
        or value.get("cuda_driver_jit_cache_controlled_or_isolated")
            != CACHE_POLICY["cuda_driver_jit_cache_controlled_or_isolated"]
        or value.get("optix_disk_cache_controlled_or_isolated")
            != CACHE_POLICY["optix_disk_cache_controlled_or_isolated"]
        or value.get(
            "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
        ) != CACHE_POLICY[
            "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]
        or value.get("same_host_root_race_excluded")
            != SOURCE_ADMISSION_POLICY[
                "same_host_malicious_root_race_excluded"]
        or value.get("cache_receipts_preserved")
            != CACHE_POLICY["cache_receipts_preserved"]
        or value.get("cache_payloads_non_authoritative")
            != (not CACHE_POLICY["cache_payloads_are_authoritative_evidence"])
        or value.get(
            "cache_payloads_must_be_removed_before_final_cohort_publication"
        ) != CACHE_POLICY[
            "successful_cohort_cache_payloads_removed_after_validation_before_publication"
        ]
        or value.get("failed_terminal_staging_may_preserve_cache_payloads")
            != CACHE_POLICY["failed_terminal_staging_may_preserve_cache_payloads"]
        or value.get(
            "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount"
        ) != CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount"
        ]
        or value.get("successful_cohort_empty_cache_directory_shell_count")
            != CACHE_POLICY[
                "successful_cohort_empty_cache_directory_shell_count"]
        or value.get("empty_cache_directory_shells_are_authoritative_evidence")
            != CACHE_POLICY[
                "empty_cache_directory_shells_are_authoritative_evidence"]
        or not recount_primary_pin_valid
        or value.get("retry_resume_replacement_row_drop_relabel_used") is not False
    ):
        raise Goal5791ControllerError(f"analysis row cardinality drifted: {path}")
    trace_gate_expectations = _trace_gate_expectations(raw_worker_values)
    for result_row, expected_row in zip(
        rows, statistical_rows(), strict=True,
    ):
        if not isinstance(result_row, dict):
            raise Goal5791ControllerError("formal result row is not an object")
        row_segment_count = result_row.get("exact_row_segment_count")
        trace_gate = trace_gate_expectations[str(expected_row["row_id"])]
        per_segment_bound = TRACE_INSTRUMENTATION_CONTRACT[
            "five_extra_event_differential_bound_per_segment_ns"
        ]
        statistical_clear_win = result_row.get("classification") == "ci_clear_win"
        trace_bound_small = result_row.get(
            "trace_cost_bound_small_relative_to_observed_difference"
        ) is True
        expected_claim_eligible = statistical_clear_win and trace_bound_small
        expected_claim_classification = (
            "eligible_clear_win"
            if expected_claim_eligible
            else (
                "trace_cost_inconclusive"
                if statistical_clear_win and not trace_bound_small
                else "not_a_statistical_clear_win"
            )
        )
        if (
            result_row.get("row_index") != expected_row["row_index"]
            or result_row.get("row_id_internal_schedule_id")
                != expected_row["row_id"]
            or result_row.get("row_id") != result_row_id(
                str(expected_row["dataset_id"]),
                str(expected_row["lifecycle"]),
            )
            or result_row.get("dataset_id") != expected_row["dataset_id"]
            or result_row.get("lifecycle_internal_schedule_id")
                != expected_row["lifecycle"]
            or result_row.get("lifecycle")
                != result_lifecycle_label(str(expected_row["lifecycle"]))
            or result_row.get(
                "trace_cost_diagnostic_authority_file_sha256"
            ) != TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_file_sha256"
            ]
            or result_row.get("trace_cost_diagnostic_authority_sha256")
                != TRACE_INSTRUMENTATION_CONTRACT[
                    "cpu_only_diagnostic_authority_sha256"
                ]
            or result_row.get("per_event_record_cost_bound_ns")
                != TRACE_INSTRUMENTATION_CONTRACT[
                    "per_event_record_cost_bound_ns"
                ]
            or result_row.get("extra_trace_event_count_per_segment") != 5
            or result_row.get(
                "five_extra_event_differential_bound_per_segment_ns"
            ) != per_segment_bound
            or type(row_segment_count) is not int
            or row_segment_count <= 0
            or row_segment_count != trace_gate["segment_count"]
            or result_row.get("row_total_trace_differential_bound_ns")
                != trace_gate["bound_ns"]
            or result_row.get("row_total_trace_differential_bound_seconds")
                != trace_gate["bound_seconds"]
            or result_row.get("absolute_median_seconds_difference")
                != trace_gate["absolute_difference_seconds"]
            or result_row.get(
                "trace_differential_fraction_of_absolute_median_seconds_difference"
            ) != trace_gate["fraction"]
            or result_row.get("trace_small_relative_max_fraction")
                != TRACE_INSTRUMENTATION_CONTRACT[
                    "small_relative_max_fraction"
                ]
            or trace_bound_small is not trace_gate["small"]
            or result_row.get(
                "diagnostic_may_change_row_statistic_ci_threshold_or_verdict"
            ) is not False
            or result_row.get(
                "statistical_classification_unchanged_by_trace_diagnostic"
            ) is not True
            or result_row.get("demonstrated_clear_win")
                is not expected_claim_eligible
            or result_row.get("mechanism_performance_statement_eligible")
                is not expected_claim_eligible
            or result_row.get(
                "mechanism_performance_statement_classification"
            ) != expected_claim_classification
            or result_row.get("estimand_includes_evidence_overhead") is not True
            or result_row.get("pure_device_kernel_timing_claimed") is not False
        ):
            raise Goal5791ControllerError(
                "formal result row presentation/trace bound drifted: "
                f"{expected_row['row_id']}"
            )
    expected_paper_outcome = _paper_outcome_summary(rows)
    if (
        any(
            value.get(name) != expected
            for name, expected in expected_paper_outcome.items()
        )
        or value.get("ci_clear_win_count")
            != expected_paper_outcome[
                "paper_outcome_consequence_selection"
            ]["ci_clear_win_count"]
    ):
        raise Goal5791ControllerError(
            f"paper outcome consequence selection drifted: {path}"
        )
    return rows


def run_controller(
    *,
    repository_root: Path,
    runtime_path: Path,
    preexecution_path: Path,
    formal_authority_path: Path,
    output_root: Path,
    child_runner: Callable[..., None] = _run_child,
    target_probe_runner: Callable[..., object] | None = None,
    process_state_observer: Callable[[str], Mapping[str, object]] | None = None,
    clock_ns: Callable[[], int] = time.perf_counter_ns,
) -> Path:
    """Execute the frozen cohort exactly once; publish raw root only on success."""

    raw_output_root = output_root
    output_root = raw_output_root.resolve()
    if not raw_output_root.is_absolute() or raw_output_root != output_root:
        raise Goal5791ControllerError(
            "formal output root must be its canonical absolute path")
    if _lexists(output_root):
        raise FileExistsError(output_root)
    staging = output_root.with_name(f".{output_root.name}.goal5791_incomplete")
    if _lexists(staging):
        raise FileExistsError(staging)

    control_paths, immutable_control_file_observations = (
        _validate_immutable_control_files(
            runtime_path=runtime_path,
            preexecution_path=preexecution_path,
            formal_authority_path=formal_authority_path,
        )
    )
    runtime_path, preexecution_path, formal_authority_path = control_paths

    authority = _load_authority_context(
        repository_root=repository_root.resolve(),
        preexecution_path=preexecution_path,
        formal_authority_path=formal_authority_path,
    )
    data_authority, data_authority_path = _load_data_authority(authority)
    runtime = _validate_runtime(
        runtime_path,
        authority=authority,
        data_authority=data_authority,
    )
    materialization, output_root, staging, output_parent = (
        _validate_execution_layout(
            repository_root=repository_root.resolve(),
            runtime_path=runtime_path,
            preexecution_path=preexecution_path,
            formal_authority_path=formal_authority_path,
            runtime=runtime,
            authority=authority,
            requested_output_root=output_root,
        )
    )
    # Immutable authority/runtime/layout checks are the only work before the
    # irreversible transaction marker.  Every environment, target, resource,
    # data, or source admission failure after this point leaves the exact
    # hidden directory terminal, so one Stage-B authority cannot be retried.
    staging.mkdir(parents=False)
    controller_bootstrap_observation = validate_controller_bootstrap(
        repository_root=repository_root.resolve(),
        runtime=runtime,
        immutable_control_file_observations=(
            immutable_control_file_observations),
        process_state_observer=process_state_observer,
    )
    base_environment = _controlled_environment(runtime)
    target_runtime_admission = build_target_runtime_admission(
        authority=authority,
        runtime=runtime,
        environment=base_environment,
        probe_runner=target_probe_runner,
        process_state_observer=process_state_observer,
    )
    _write_json_create_only(
        staging / "TARGET_RUNTIME_ADMISSION.json",
        target_runtime_admission,
    )
    target_runtime_admission_file_sha256 = file_sha256(
        staging / "TARGET_RUNTIME_ADMISSION.json")
    resource_admission = build_resource_admission(
        authority=authority,
        materialization_root=materialization,
        formal_output_root=output_root,
        formal_staging_root=staging,
        formal_output_parent=output_parent,
    )
    _write_json_create_only(
        staging / "RESOURCE_ADMISSION.json", resource_admission)
    resource_admission_file_sha256 = file_sha256(
        staging / "RESOURCE_ADMISSION.json")

    admission = build_data_admission(
        runtime=runtime,
        authority=authority,
        data_authority=data_authority,
    )
    source_admission = build_source_admission(
        runtime_path=runtime_path.resolve(),
        runtime=runtime,
        controller_bootstrap_observation=controller_bootstrap_observation,
    )

    # The named output root remains absent unless workers, both statistics
    # paths, and final cohort checks all complete exactly.
    workers = staging / "workers"
    caches = staging / "worker_caches"
    raw_authorities = staging / "AUTHORITIES"
    workers.mkdir()
    caches.mkdir()
    raw_authorities.mkdir()
    _write_json_create_only(staging / "FORMAL_CONTRACT.json", contract_document())
    _write_json_create_only(staging / "SCHEDULE.json", schedule_document())
    _write_json_create_only(staging / "TARGET_BINDING.json", authority.target_binding)
    _write_json_create_only(staging / "DATA_ADMISSION.json", admission)
    _write_json_create_only(
        staging / "SOURCE_ADMISSION.json", source_admission)
    _copy_create_only(
        preexecution_path.resolve(), staging / "PREEXECUTION_AUTHORITY.json",
        expected_sha256=authority.preexecution_file_sha256,
    )
    _copy_create_only(
        formal_authority_path.resolve(), staging / "OWNER_FORMAL_AUTHORITY.json",
        expected_sha256=authority.formal_authority_file_sha256,
    )
    runtime_file_sha256 = str(authority.formal["runtime_file_sha256"])
    _copy_create_only(
        runtime_path.resolve(), staging / "RUNTIME.json",
        expected_sha256=runtime_file_sha256,
    )
    data_record = authority.preexecution["authority_records"]["data_authority"]
    _copy_create_only(
        data_authority_path, staging / "DATA_AUTHORITY.json",
        expected_sha256=str(data_record["sha256"]),
        expected_bytes=int(data_record["bytes"]),
    )
    authority_manifest_rows: dict[str, dict[str, object]] = {}
    for role in AUTHORITY_ROLES:
        record = authority.preexecution["authority_records"][role]
        source_path = (
            authority.repository_root
            / Path(*str(record["path"]).split("/"))
        ).resolve()
        relative = f"AUTHORITIES/{role}.json"
        destination = staging / Path(*relative.split("/"))
        _copy_create_only(
            source_path,
            destination,
            expected_sha256=str(record["sha256"]),
            expected_bytes=int(record["bytes"]),
        )
        authority_manifest_rows[role] = {
            "path": relative,
            "file_sha256": str(record["sha256"]),
            "bytes": int(record["bytes"]),
        }
    authority_manifest = _sealed_payload(
        {
            "schema": RAW_AUTHORITY_MANIFEST_SCHEMA,
            "goal": GOAL,
            "preexecution_authority_file_sha256": (
                authority.preexecution_file_sha256),
            "authorities": authority_manifest_rows,
        },
        "manifest_sha256",
    )
    _write_json_create_only(
        staging / "AUTHORITY_MANIFEST.json", authority_manifest)
    target_authority = Path(
        str(runtime["target_materialization_authority_path"])).resolve()
    _copy_create_only(
        target_authority, staging / "TARGET_MATERIALIZATION_AUTHORITY.json",
        expected_sha256=str(
            runtime["target_materialization_authority_file_sha256"]),
    )

    python = str(Path(str(runtime["python_executable"])).resolve())
    source = Path(str(runtime["execution_source_root"])).resolve()
    worker_script = source / "scripts" / "goal5791_formal_worker.py"
    evaluator_script = source / "scripts" / "goal5791_formal_evaluate.py"
    recount_script = (
        source / "scripts" / "goal5791_formal_independent_recount.py")
    for script in (worker_script, evaluator_script, recount_script):
        if not script.is_file():
            raise Goal5791ControllerError(f"formal harness file is absent: {script}")
    expected_worker_script_sha256 = runtime["formal_identity_record"][
        "formal_sources"]["scripts/goal5791_formal_worker.py"]

    started = clock_ns()
    if type(started) is not int or started < 0:
        raise Goal5791ControllerError("controller clock is invalid")
    deadline_ns = started + int(
        float(runtime["formal_conservative_budget_seconds"]) * 1_000_000_000)
    timeout = float(runtime["worker_timeout_seconds"])
    seen_pids: set[int] = set()
    worker_rows: list[dict[str, object]] = []
    raw_worker_values: list[dict[str, object]] = []
    launch_attempts = 0
    for worker_spec in schedule():
        if file_sha256(worker_script) != expected_worker_script_sha256:
            raise Goal5791ControllerError(
                "formal worker script changed after source admission")
        now = clock_ns()
        if now > deadline_ns:
            raise Goal5791ControllerError(
                "formal conservative budget expired before next worker; "
                "resume/replacement is forbidden")
        index = int(worker_spec["worker_index"])
        cache = caches / f"worker_{index:04d}"
        cache.mkdir()
        cupy_cache = cache / "cupy"
        numba_cache = cache / "numba"
        cupy_cache.mkdir()
        numba_cache.mkdir()
        environment = dict(base_environment)
        environment[CUPY_CACHE_ENVIRONMENT_KEY] = str(cupy_cache)
        environment[NUMBA_CACHE_ENVIRONMENT_KEY] = str(numba_cache)
        output = workers / f"worker_{index:04d}.json"
        command = [
            python,
            str(worker_script),
            "--repository-root", str(repository_root.resolve()),
            "--runtime", str(runtime_path.resolve()),
            "--preexecution-authority", str(preexecution_path.resolve()),
            "--formal-authority", str(formal_authority_path.resolve()),
            "--data-admission", str(staging / "DATA_ADMISSION.json"),
            "--source-admission", str(staging / "SOURCE_ADMISSION.json"),
            "--cache-dir", str(cache),
            "--worker-index", str(index),
            "--output", str(output),
        ]
        launch_attempts += 1
        child_runner(
            command,
            environment=environment,
            timeout_seconds=timeout,
            label=f"Goal5791 worker {index}",
        )
        value = _validate_worker_output(
            output,
            worker_spec=worker_spec,
            seen_pids=seen_pids,
            runtime_file_sha256=runtime_file_sha256,
            source_admission_sha256=source_admission["admission_sha256"],
            llvmlite_version=str(runtime["llvmlite_version"]),
        )
        raw_worker_values.append(value)
        worker_rows.append({
            "worker_index": index,
            "parent_pid": value["parent_pid"],
            "worker_sha256": value["worker_sha256"],
            "file_sha256": file_sha256(output),
            "cache_dir_name": cache.name,
            "launch_attempt_count": 1,
        })
    if launch_attempts != len(schedule()) or len(seen_pids) != len(schedule()):
        raise Goal5791ControllerError("fresh-process worker cardinality drifted")

    analysis_environment = dict(base_environment)
    for script, source_name, name in (
        (
            evaluator_script,
            "scripts/goal5791_formal_evaluate.py",
            "EVALUATION.json",
        ),
        (
            recount_script,
            "scripts/goal5791_formal_independent_recount.py",
            "INDEPENDENT_RECOUNT.json",
        ),
    ):
        expected_analysis_sha256 = runtime["formal_identity_record"][
            "formal_sources"][source_name]
        if file_sha256(script) != expected_analysis_sha256:
            raise Goal5791ControllerError(
                f"formal analysis script changed after source admission: {source_name}")
        child_runner(
            [
                python, str(script), "--raw-root", str(staging),
                "--output", str(staging / name),
            ],
            environment=analysis_environment,
            timeout_seconds=timeout,
            label=f"Goal5791 {name}",
        )
    evaluation_rows = _analysis_rows(
        staging / "EVALUATION.json",
        schema="rtdl.goal5791.formal_primary_evaluation.v1",
        status="PASS__COMPLETE_FAIL_CLOSED_FORMAL_EVALUATION",
        seal_field="evaluation_sha256",
        runtime=runtime,
        authority=authority,
        admission=admission,
        authority_manifest=authority_manifest,
        runtime_file_sha256=runtime_file_sha256,
        source_admission=source_admission,
        target_runtime_admission=target_runtime_admission,
        target_runtime_admission_file_sha256=(
            target_runtime_admission_file_sha256),
        resource_admission=resource_admission,
        resource_admission_file_sha256=resource_admission_file_sha256,
        worker_rows=worker_rows,
        raw_worker_values=raw_worker_values,
    )
    recount_rows = _analysis_rows(
        staging / "INDEPENDENT_RECOUNT.json",
        schema="rtdl.goal5791.formal_independent_recount.v1",
        status="PASS__COMPLETE_INDEPENDENT_RAW_RECOUNT",
        seal_field="recount_sha256",
        runtime=runtime,
        authority=authority,
        admission=admission,
        authority_manifest=authority_manifest,
        runtime_file_sha256=runtime_file_sha256,
        source_admission=source_admission,
        target_runtime_admission=target_runtime_admission,
        target_runtime_admission_file_sha256=(
            target_runtime_admission_file_sha256),
        resource_admission=resource_admission,
        resource_admission_file_sha256=resource_admission_file_sha256,
        worker_rows=worker_rows,
        raw_worker_values=raw_worker_values,
    )
    if evaluation_rows != recount_rows:
        raise Goal5791ControllerError(
            "primary evaluation and independent recount statistics differ")
    paper_outcome = _paper_outcome_summary(evaluation_rows)

    _remove_validated_worker_cache_payloads(staging=staging, cache_root=caches)

    ended = clock_ns()
    if type(ended) is not int or ended < started or ended > deadline_ns:
        raise Goal5791ControllerError("formal cohort exceeded its frozen budget")
    manifest_payload = {
        "schema": COHORT_MANIFEST_SCHEMA,
        "goal": GOAL,
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "preexecution_authority_file_sha256": file_sha256(preexecution_path),
        "target_materialization_binding_sha256": authority.target_binding[
            "binding_sha256"],
        "target_materialization_authority_file_sha256": file_sha256(
            target_authority),
        "formal_authority_file_sha256": file_sha256(formal_authority_path),
        "runtime_sha256": runtime["runtime_sha256"],
        "runtime_file_sha256": runtime_file_sha256,
        "data_admission_sha256": admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "target_runtime_admission_sha256": (
            target_runtime_admission["admission_sha256"]),
        "target_runtime_admission_file_sha256": (
            target_runtime_admission_file_sha256),
        "resource_admission_sha256": resource_admission["admission_sha256"],
        "resource_admission_file_sha256": resource_admission_file_sha256,
        "raw_authority_manifest_sha256": authority_manifest["manifest_sha256"],
        "authorities": authority_manifest_rows,
        "worker_count": len(worker_rows),
        "independent_row_count": len(statistical_rows()),
        "workers": worker_rows,
        "evaluation_file_sha256": file_sha256(staging / "EVALUATION.json"),
        "independent_recount_file_sha256": file_sha256(
            staging / "INDEPENDENT_RECOUNT.json"),
        "fresh_parent_pid_count": len(seen_pids),
        "launch_attempt_count": launch_attempts,
        "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
            "same_host_malicious_root_race_excluded"],
        "cold_process_warm_system_definition": CACHE_POLICY["cold_definition"],
        "cold_process_warm_system_excludes": list(
            CACHE_POLICY["cold_claim_excludes"]),
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"],
        "operating_system_page_cache_scope": CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]
        ),
        "worker_cache_payloads_preserved": False,
        "worker_cache_payloads_removed_after_validation": CACHE_POLICY[
            "successful_cohort_cache_payloads_removed_after_validation_before_publication"],
        "cache_receipts_preserved": CACHE_POLICY["cache_receipts_preserved"],
        "cache_payloads_are_authoritative_evidence": CACHE_POLICY[
            "cache_payloads_are_authoritative_evidence"],
        "successful_cohort_cache_payloads_removed_after_validation_before_publication": (
            CACHE_POLICY[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"]
        ),
        "failed_terminal_staging_may_preserve_cache_payloads": CACHE_POLICY[
            "failed_terminal_staging_may_preserve_cache_payloads"],
        "worker_cache_empty_directory_shells_preserved": CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount"],
        "worker_cache_empty_directory_shell_count": CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shell_count"],
        "worker_cache_empty_directory_shells_are_authoritative_evidence": (
            CACHE_POLICY[
                "empty_cache_directory_shells_are_authoritative_evidence"]
        ),
        "worker_cache_empty_directory_shells_all_empty": True,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    manifest = _sealed_payload(manifest_payload, "manifest_sha256")
    _write_json_create_only(staging / "COHORT_MANIFEST.json", manifest)
    result_payload = {
        "schema": RESULT_SCHEMA,
        "goal": GOAL,
        "status": "COMPLETE__96_OF_96_EXACTLY_ONCE",
        "formal_worker_count": len(worker_rows),
        "independent_row_count": len(statistical_rows()),
        "fresh_parent_pid_count": len(seen_pids),
        "launch_attempt_count": launch_attempts,
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "runtime_file_sha256": runtime_file_sha256,
        "runtime_sha256": runtime["runtime_sha256"],
        "cohort_manifest_sha256": manifest["manifest_sha256"],
        "evaluation_file_sha256": manifest["evaluation_file_sha256"],
        "independent_recount_file_sha256": manifest[
            "independent_recount_file_sha256"],
        "primary_and_independent_rows_exactly_equal": True,
        "rows": evaluation_rows,
        "result_lifecycle_labels": {
            lifecycle: result_lifecycle_label(lifecycle)
            for lifecycle in LIFECYCLES
        },
        "trace_cost_diagnostic_authority": {
            "file_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_file_sha256"
            ],
            "diagnostic_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_sha256"
            ],
            "per_event_record_cost_bound_ns": TRACE_INSTRUMENTATION_CONTRACT[
                "per_event_record_cost_bound_ns"
            ],
            "five_extra_event_differential_bound_per_segment_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "five_extra_event_differential_bound_per_segment_ns"
                ]
            ),
            "required_before_stage_b_worker_zero": True,
        },
        "independent_recount_external_review_status": (
            INDEPENDENT_RECOUNT_REVIEW_STATUS
        ),
        "every_figure_caption_must_state_includes_evidence_overhead": True,
        **paper_outcome,
        "data_admission_sha256": admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "target_runtime_admission_sha256": (
            target_runtime_admission["admission_sha256"]),
        "target_runtime_admission_file_sha256": (
            target_runtime_admission_file_sha256),
        "resource_admission_sha256": resource_admission["admission_sha256"],
        "resource_admission_file_sha256": resource_admission_file_sha256,
        "raw_authority_manifest_sha256": authority_manifest["manifest_sha256"],
        "controller_elapsed_seconds": (ended - started) / 1_000_000_000.0,
        "formal_conservative_budget_seconds": runtime[
            "formal_conservative_budget_seconds"],
        "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": (
            CACHE_POLICY[
                "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control"]
        ),
        "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
            "same_host_malicious_root_race_excluded"],
        "cold_process_warm_system_definition": CACHE_POLICY["cold_definition"],
        "cold_process_warm_system_excludes": list(
            CACHE_POLICY["cold_claim_excludes"]),
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"],
        "operating_system_page_cache_scope": CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]
        ),
        "worker_cache_payloads_preserved": False,
        "worker_cache_payloads_removed_after_validation": CACHE_POLICY[
            "successful_cohort_cache_payloads_removed_after_validation_before_publication"],
        "cache_receipts_preserved": CACHE_POLICY["cache_receipts_preserved"],
        "cache_payloads_are_authoritative_evidence": CACHE_POLICY[
            "cache_payloads_are_authoritative_evidence"],
        "successful_cohort_cache_payloads_removed_after_validation_before_publication": (
            CACHE_POLICY[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"]
        ),
        "failed_terminal_staging_may_preserve_cache_payloads": CACHE_POLICY[
            "failed_terminal_staging_may_preserve_cache_payloads"],
        "worker_cache_empty_directory_shells_preserved": CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount"],
        "worker_cache_empty_directory_shell_count": CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shell_count"],
        "worker_cache_empty_directory_shells_are_authoritative_evidence": (
            CACHE_POLICY[
                "empty_cache_directory_shells_are_authoritative_evidence"]
        ),
        "worker_cache_empty_directory_shells_all_empty": True,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    result = _sealed_payload(result_payload, "result_sha256")
    _write_json_create_only(staging / "RESULT.json", result)
    os.replace(staging, output_root)
    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--preexecution-authority", type=Path, required=True)
    parser.add_argument("--formal-authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(run_controller(
        repository_root=args.repository_root,
        runtime_path=args.runtime,
        preexecution_path=args.preexecution_authority,
        formal_authority_path=args.formal_authority,
        output_root=args.output_root,
    ))


if __name__ == "__main__":
    main()

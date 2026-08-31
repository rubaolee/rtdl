"""Frozen protocol and byte-identity helpers for the Goal5805 successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "rtdl.goal5805.performance_repair_freeze.v1"
TARGET_SCHEMA = "rtdl.goal5805.target_products.v1"
AUTHORITY_SCHEMA = "rtdl.goal5805.formal_execution_authority.v1"
RUNTIME_SCHEMA = "rtdl.goal5805.target_runtime_manifest.v1"
TARGET_OBSERVATION_SCHEMA = "rtdl.goal5805.target_observation.v1"
ARMS = ("PYOPTIX", "RTDL")
TASKS = ("relation", "triangle")
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
BLOCK_COUNT = 16
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
BOOTSTRAP_DRAWS = 10_000
THRESHOLDS = {
    "DEPLOYMENT_COLD": 1.10,
    "PREPARE": 1.10,
    "STEADY_E2E": 1.05,
}
STATIC_SOURCE_PATHS = (
    "Makefile",
    "README.md",
    "VERSION",
    "pyproject.toml",
)
SOURCE_DIRECTORIES = (
    "src/rtdsl",
    "src/native",
    "experiments",
    "scripts",
    "tests",
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_record(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    payload = resolved.read_bytes()
    return {
        "path": str(resolved),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _source_record(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    value = file_record(path)
    value["path"] = relative
    return value


def source_paths(root: Path) -> tuple[str, ...]:
    root = root.resolve(strict=True)
    paths = set(STATIC_SOURCE_PATHS)
    for relative in SOURCE_DIRECTORIES:
        directory = (root / relative).resolve(strict=True)
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts \
                    and path.suffix not in {".pyc", ".pyo"}:
                paths.add(path.relative_to(root).as_posix())
    result = tuple(sorted(paths, key=lambda item: item.encode("utf-8")))
    if any(not (root / item).is_file() for item in result):
        raise RuntimeError("Goal5805 source closure contains a non-file")
    return result


def build_freeze(root: Path, *, predecessor_result_sha256: str) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if len(predecessor_result_sha256) != 64:
        raise RuntimeError("Goal5805 predecessor result SHA-256 differs")
    value: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "FROZEN_BEFORE_FORMAL_SUCCESSOR_TIMING",
        "predecessor_goal5802_result_sha256": predecessor_result_sha256,
        "predecessor_goal5802_zero_of_six_preserved": True,
        "purpose": (
            "MEASURE_POSTRESULT_IMPLEMENTATION_REPAIR_UNCONDITIONALLY__"
            "NOT_CONFIRMATORY_REPLACEMENT"),
        "arms": list(ARMS),
        "tasks": list(TASKS),
        "regimes": list(REGIMES),
        "thresholds_rtdl_over_pyoptix": dict(THRESHOLDS),
        "block_count": BLOCK_COUNT,
        "within_block_orders": ["RTDL,PYOPTIX,PYOPTIX,RTDL",
                                "PYOPTIX,RTDL,RTDL,PYOPTIX"],
        "steady_warmups": STEADY_WARMUPS,
        "steady_repetitions": STEADY_REPETITIONS,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "primary_point_estimator": "MEDIAN_OF_16_PAIRED_BLOCK_RATIOS",
        "interval": "FIXED_SEED_PERCENTILE_BOOTSTRAP_OVER_BLOCK_RATIOS",
        "gate": "POINT_AND_95_PERCENT_CI_UPPER_AT_OR_BELOW_THRESHOLD",
        "result_acceptance": "UNCONDITIONAL_INCLUDING_ZERO_OF_SIX",
        "retry_replacement_row_drop": False,
        "direct_cuda_optix_primary_arm": False,
        "direct_cuda_optix_disposition": (
            "PRESERVED_GOAL5802_CONTEXT__NEW_MATCHED_CONTEXT_AFTER_PRIMARY"),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "source_manifest": [_source_record(root, item) for item in source_paths(root)],
    }
    value["freeze_sha256"] = digest(value)
    return value


def validate_freeze(value: Mapping[str, Any], root: Path, *, rehash: bool) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("freeze_sha256", None)
    if value.get("schema") != SCHEMA or observed != digest(unsigned):
        raise RuntimeError("Goal5805 freeze seal differs")
    if (
        value.get("status") != "FROZEN_BEFORE_FORMAL_SUCCESSOR_TIMING"
        or value.get("arms") != list(ARMS)
        or value.get("tasks") != list(TASKS)
        or value.get("regimes") != list(REGIMES)
        or value.get("thresholds_rtdl_over_pyoptix") != THRESHOLDS
        or value.get("block_count") != BLOCK_COUNT
        or value.get("steady_warmups") != STEADY_WARMUPS
        or value.get("steady_repetitions") != STEADY_REPETITIONS
        or value.get("bootstrap_draws") != BOOTSTRAP_DRAWS
        or value.get("result_acceptance") != "UNCONDITIONAL_INCLUDING_ZERO_OF_SIX"
        or value.get("retry_replacement_row_drop") is not False
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
    ):
        raise RuntimeError("Goal5805 frozen protocol differs")
    rows = value.get("source_manifest")
    paths = source_paths(root)
    if not isinstance(rows, list) or [row.get("path") for row in rows] != list(paths):
        raise RuntimeError("Goal5805 source manifest differs")
    if rehash:
        expected = [_source_record(root.resolve(strict=True), item)
                    for item in paths]
        if rows != expected:
            raise RuntimeError("Goal5805 source bytes differ from freeze")


def validate_target_manifest(value: Mapping[str, Any], *, rehash: bool) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("target_manifest_sha256", None)
    if value.get("schema") != TARGET_SCHEMA or observed != digest(unsigned):
        raise RuntimeError("Goal5805 target manifest seal differs")
    required = {
        "candidate_manifest", "trust_root", "trust_head", "trust_package",
        "native_library", "matched_ptx", "relation_compaction_cubin",
        "runtime_manifest", "target_observation",
    }
    files = value.get("files")
    if value.get("registered_performance_timing_count") != 0 \
            or value.get("formal_worker_count") != 0 \
            or not isinstance(files, Mapping) or set(files) != required:
        raise RuntimeError("Goal5805 target product set differs")
    for name in sorted(required):
        row = files[name]
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
            raise RuntimeError(f"Goal5805 target record differs: {name}")
        if rehash and dict(row) != file_record(Path(str(row["path"]))):
            raise RuntimeError(f"Goal5805 target bytes differ: {name}")
    runtime = json.loads(Path(str(files["runtime_manifest"]["path"])).read_text(
        encoding="utf-8"))
    observation = json.loads(Path(str(files["target_observation"]["path"])).read_text(
        encoding="utf-8"))
    validate_target_observation(observation)
    validate_runtime_manifest(runtime, rehash=rehash)
    if runtime["target_observation"] != dict(files["target_observation"]):
        raise RuntimeError("Goal5805 runtime/target observation binding differs")
    for role in (
        "candidate_manifest", "trust_root", "trust_head", "trust_package",
        "native_library", "matched_ptx", "relation_compaction_cubin",
    ):
        if runtime["measurement_files"].get(role) != dict(files[role]):
            raise RuntimeError(f"Goal5805 runtime/target product binding differs: {role}")


def validate_target_observation(value: Mapping[str, Any]) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("target_observation_sha256", None)
    required = {
        "schema", "status", "hostname", "gpu_uuid", "gpu_name",
        "compute_capability", "driver_version", "gpu_memory_total_mib",
        "cuda_visible_devices", "nvcc_version", "python_version",
        "clock_read_count", "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "target_observation_sha256",
    }
    if set(value) != required or value.get("schema") != TARGET_OBSERVATION_SCHEMA \
            or observed != digest(unsigned):
        raise RuntimeError("Goal5805 target observation seal differs")
    if value.get("status") != "PASS__OBSERVED_BEFORE_FORMAL_WORKER_ZERO" \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")):
        raise RuntimeError("Goal5805 target observation boundary differs")
    for key in (
        "hostname", "gpu_uuid", "gpu_name", "compute_capability",
        "driver_version", "cuda_visible_devices", "nvcc_version",
        "python_version",
    ):
        if not isinstance(value.get(key), str) or not value[key]:
            raise RuntimeError(f"Goal5805 target observation field differs: {key}")
    if type(value.get("gpu_memory_total_mib")) is not int \
            or value["gpu_memory_total_mib"] <= 0:
        raise RuntimeError("Goal5805 target GPU memory differs")


def validate_runtime_manifest(value: Mapping[str, Any], *, rehash: bool) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("runtime_manifest_sha256", None)
    required = {
        "schema", "status", "target_observation", "measurement_files",
        "runtime_files", "runtime_versions", "loader_environment",
        "clock_read_count", "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "runtime_manifest_sha256",
    }
    if set(value) != required or value.get("schema") != RUNTIME_SCHEMA \
            or observed != digest(unsigned):
        raise RuntimeError("Goal5805 runtime manifest seal differs")
    if value.get("status") != "TARGET_RUNTIME_FROZEN__FORMAL_WORKER_ZERO" \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")):
        raise RuntimeError("Goal5805 runtime manifest boundary differs")
    measurement_roles = {
        "candidate_manifest", "trust_root", "trust_head", "trust_package",
        "native_library", "matched_ptx", "relation_compaction_cubin",
    }
    runtime_roles = {
        "python_executable", "numpy_module", "cupy_module",
        "pyoptix_extension", "rtdlexe_module",
    }
    for label, rows, roles in (
        ("measurement", value.get("measurement_files"), measurement_roles),
        ("runtime", value.get("runtime_files"), runtime_roles),
    ):
        if not isinstance(rows, Mapping) or set(rows) != roles:
            raise RuntimeError(f"Goal5805 {label} runtime file set differs")
        for role in sorted(roles):
            row = rows[role]
            if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
                raise RuntimeError(f"Goal5805 runtime record differs: {role}")
            if rehash and dict(row) != file_record(Path(str(row["path"]))):
                raise RuntimeError(f"Goal5805 runtime bytes differ: {role}")
    observation = value.get("target_observation")
    if not isinstance(observation, Mapping) \
            or set(observation) != {"path", "bytes", "sha256"}:
        raise RuntimeError("Goal5805 runtime target observation record differs")
    if rehash and dict(observation) != file_record(Path(str(observation["path"]))):
        raise RuntimeError("Goal5805 runtime target observation bytes differ")
    target_value = json.loads(Path(str(observation["path"])).read_text(
        encoding="utf-8"))
    validate_target_observation(target_value)
    versions = value.get("runtime_versions")
    if not isinstance(versions, Mapping) or set(versions) != {
        "python", "numpy", "cupy", "pyoptix", "optix_api",
    } or any(not isinstance(item, str) or not item for item in versions.values()):
        raise RuntimeError("Goal5805 runtime version set differs")
    loader = value.get("loader_environment")
    if not isinstance(loader, Mapping) or set(loader) != {
        "cuda_home", "cuda_visible_devices", "ld_library_path",
    } or any(value is not None and not isinstance(value, str)
             for value in loader.values()):
        raise RuntimeError("Goal5805 loader environment differs")


def validate_authority(value: Mapping[str, Any], *, freeze_file_sha256: str,
                       target_manifest_file_sha256: str) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("authority_sha256", None)
    if value.get("schema") != AUTHORITY_SCHEMA or observed != digest(unsigned):
        raise RuntimeError("Goal5805 execution authority seal differs")
    if (
        value.get("freeze_file_sha256") != freeze_file_sha256
        or value.get("target_manifest_file_sha256")
        != target_manifest_file_sha256
        or value.get("owner_execution_authorized") is not True
        or value.get("formal_worker_zero_authorized") is not True
        or value.get("pod_gpu_timing_authorized") is not True
        or value.get("unconditional_result_acceptance") is not True
        or value.get("retry_replacement_row_drop") is not False
    ):
        raise RuntimeError("Goal5805 execution authority is incomplete")

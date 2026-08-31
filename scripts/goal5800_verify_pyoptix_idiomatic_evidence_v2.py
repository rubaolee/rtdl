#!/usr/bin/env python3
"""Fail-closed, repository-independent Goal5800 PyOptiX v2 evidence verifier.

Version 2 deliberately rejects the earlier evidence schema.  It binds the
native ``optix._optix`` extension that was actually imported, records the
Python/CUDA/OptiX runtime identities, and checks an execution-emitted operation
ledger rather than accepting aggregate counters supplied by the arm.
"""

from __future__ import annotations

import argparse
import ast
import base64
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Any
import zipfile


MANIFEST_SCHEMA = "rtdl.goal5800.pyoptix_idiomatic_evidence_manifest.v2"
ENVIRONMENT_SCHEMA = "rtdl.goal5800.pyoptix_idiomatic_environment.v2"
RESULT_SCHEMA = "rtdl.goal5800.pyoptix_idiomatic_arm.result.v2"
ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API__IDIOMATIC_BULK"
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
OPERATION_LEDGER_SCOPE = (
    "TASK_OWNER_CONSTRUCTION_AND_EXECUTE__SOURCE_OBSERVABLE_WRAPPERS__"
    "EXCLUDES_CONTEXT_PIPELINE_SBT_AND_DRIVER_INTERNALS"
)
OPERATION_COUNT_KEYS = (
    "prepare_device_allocation_call_count",
    "prepare_h2d_call_count",
    "prepare_pinned_host_allocation_call_count",
    "prepare_stream_creation_count",
    "execute_device_allocation_call_count",
    "execute_pinned_host_allocation_call_count",
    "execute_async_h2d_call_count",
    "execute_async_d2h_call_count",
    "execute_blocking_d2h_call_count",
    "execute_device_zero_fill_call_count",
    "execute_explicit_stream_sync_call_count",
    "execute_launch_call_count",
    "execute_stream_creation_call_count",
    "execute_stream_destroy_call_count",
)
REQUIRED_DISTRIBUTION_IMPORTS = ("optix", "cupy", "numpy", "cuda")
REQUIRED_PROCESS_MAP_ROLES = (
    "cupy_core",
    "cuda_driver",
    "cuda_runtime",
    "nvrtc",
    "optix_driver",
)
REQUIRED_EXECUTED_SOURCE_PATHS = (
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
)
EXTENSION_RE = re.compile(
    r"(?:^|/)optix/_optix(?:\.[^/]*)?\.(?:so|pyd|dll|dylib)$",
    re.IGNORECASE,
)
HEX64_RE = re.compile(r"[0-9a-f]{64}")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(value: bytes, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(
            value.decode("utf-8"), object_pairs_hook=_object_no_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite number: {token}")),
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid {label} JSON: {exc}") from exc
    if type(parsed) is not dict:
        raise RuntimeError(f"{label} must be a JSON object")
    return parsed


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise RuntimeError(
            f"{label} keys mismatch: missing={sorted(expected - set(value))}, "
            f"extra={sorted(set(value) - expected)}")


def exact_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise RuntimeError(f"{label} must be an integer >= {minimum}")
    return value


def exact_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise RuntimeError(f"{label} must be a boolean")
    return value


def exact_string(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise RuntimeError(f"{label} must be a non-empty string")
    return value


def digest_row(path: str, value: bytes) -> dict[str, Any]:
    return {"path": path, "bytes": len(value), "sha256": sha256(value)}


def _verify_digest(value: Any, label: str) -> str:
    text = exact_string(value, label)
    if HEX64_RE.fullmatch(text) is None:
        raise RuntimeError(f"{label} must be lowercase SHA-256")
    return text


def read_archive(path: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            member_path = PurePosixPath(member.name)
            if (member_path.is_absolute() or ".." in member_path.parts
                    or member.issym() or member.islnk()):
                raise RuntimeError(f"unsafe archive member: {member.name}")
            if not member.isfile():
                continue
            if member.name in files:
                raise RuntimeError(f"duplicate archive member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            files[member.name] = stream.read()
    required = {"MANIFEST.json", "idiomatic_pyoptix_untimed.json", "environment.json"}
    if not required.issubset(files):
        raise RuntimeError(f"missing top-level payloads: {sorted(required - set(files))}")
    allowed_prefixes = (
        "installed_distribution/", "executed_source/", "runtime_identity/",
        "provenance/",
    )
    unexpected = sorted(
        name for name in files
        if name not in required and not name.startswith(allowed_prefixes))
    if unexpected:
        raise RuntimeError(f"unexpected archive payloads: {unexpected}")
    return files


def rows_for_prefix(files: dict[str, bytes], prefix: str) -> list[dict[str, Any]]:
    rows = [
        digest_row(name.removeprefix(prefix), value)
        for name, value in sorted(files.items()) if name.startswith(prefix)
    ]
    if not rows:
        raise RuntimeError(f"empty archive payload family: {prefix}")
    return rows


def verify_manifest(
    files: dict[str, bytes], manifest: dict[str, Any],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]],
]:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("legacy or unknown evidence manifest schema")
    exact_keys(manifest, {
        "schema", "result", "environment",
        "installed_distribution_file_count", "installed_distribution_files_sha256",
        "executed_source_file_count", "executed_source_files_sha256",
        "runtime_identity_file_count", "runtime_identity_files_sha256",
        "provenance_file_count", "provenance_files_sha256",
        "registered_performance_timing_count",
    }, "manifest")
    if exact_int(manifest["registered_performance_timing_count"], "manifest timing count") != 0:
        raise RuntimeError("registered timing is forbidden")
    for key, filename in (
        ("result", "idiomatic_pyoptix_untimed.json"),
        ("environment", "environment.json"),
    ):
        row = manifest[key]
        if type(row) is not dict:
            raise RuntimeError(f"manifest {key} must be an object")
        exact_keys(row, {"bytes", "sha256"}, f"manifest {key}")
        if (exact_int(row["bytes"], f"manifest {key} bytes") != len(files[filename])
                or _verify_digest(row["sha256"], f"manifest {key} SHA")
                != sha256(files[filename])):
            raise RuntimeError(f"manifest {key} identity mismatch")
    families: list[list[dict[str, Any]]] = []
    for prefix, count_key, digest_key in (
        ("installed_distribution/", "installed_distribution_file_count",
         "installed_distribution_files_sha256"),
        ("executed_source/", "executed_source_file_count", "executed_source_files_sha256"),
        ("runtime_identity/", "runtime_identity_file_count", "runtime_identity_files_sha256"),
        ("provenance/", "provenance_file_count", "provenance_files_sha256"),
    ):
        rows = rows_for_prefix(files, prefix)
        if exact_int(manifest[count_key], count_key) != len(rows):
            raise RuntimeError(f"{prefix} file-count mismatch")
        if _verify_digest(manifest[digest_key], digest_key) != sha256(canonical(rows)):
            raise RuntimeError(f"{prefix} aggregate digest mismatch")
        families.append(rows)
    return families[0], families[1], families[2], families[3]


def verify_runtime_identities(
    files: dict[str, bytes], environment: dict[str, Any],
    installed_rows: list[dict[str, Any]], executed_rows: list[dict[str, Any]],
    runtime_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    exact_keys(environment, {
        "schema", "python_runtime", "python_distributions", "toolchain",
        "dynamic_dependencies", "executed_sources", "runtime_identity_files",
        "identity_ceiling", "gpu", "pyoptix_build_projections",
    }, "environment")
    if environment["schema"] != ENVIRONMENT_SCHEMA:
        raise RuntimeError("legacy or unknown environment schema")
    if environment["executed_sources"] != executed_rows:
        raise RuntimeError("executed-source payload mismatch")
    identity_rows = environment["runtime_identity_files"]
    if type(identity_rows) is not list or not identity_rows:
        raise RuntimeError("runtime_identity_files must be a non-empty list")
    role_map: dict[str, dict[str, Any]] = {}
    projected_rows: list[dict[str, Any]] = []
    for index, row in enumerate(identity_rows):
        if type(row) is not dict:
            raise RuntimeError(f"runtime identity row {index} must be an object")
        exact_keys(row, {"role", "archive_path", "source_path", "bytes", "sha256"},
                   f"runtime identity row {index}")
        role = exact_string(row["role"], f"runtime identity role {index}")
        archive_path = exact_string(row["archive_path"], f"runtime archive path {index}")
        if role in role_map:
            raise RuntimeError(f"duplicate runtime identity role: {role}")
        if not archive_path.startswith("runtime_identity/"):
            raise RuntimeError("runtime identity archive path escaped its payload family")
        payload = files.get(archive_path)
        if payload is None:
            raise RuntimeError(f"missing runtime identity payload: {archive_path}")
        if (exact_int(row["bytes"], f"runtime identity bytes {role}") != len(payload)
                or _verify_digest(row["sha256"], f"runtime identity SHA {role}")
                != sha256(payload)):
            raise RuntimeError(f"runtime identity mismatch: {role}")
        role_map[role] = row
        projected_rows.append(digest_row(archive_path.removeprefix("runtime_identity/"), payload))
    if projected_rows != runtime_rows:
        raise RuntimeError("runtime identity rows are not canonical or complete")

    python_runtime = environment["python_runtime"]
    if type(python_runtime) is not dict:
        raise RuntimeError("python_runtime must be an object")
    exact_keys(python_runtime, {"implementation", "version", "executable_identity_role"},
               "python_runtime")
    if python_runtime["implementation"] != "CPython":
        raise RuntimeError("Python implementation is not CPython")
    exact_string(python_runtime["version"], "Python version")
    if python_runtime["executable_identity_role"] not in role_map:
        raise RuntimeError("Python executable identity is not payload-bound")

    gpu = environment["gpu"]
    exact_keys(gpu, {
        "name", "compute_capability", "driver_version", "query_identity_role",
        "nvidia_smi_identity_role",
    }, "GPU identity")
    for key in ("name", "driver_version"):
        exact_string(gpu[key], f"GPU {key}")
    if re.fullmatch(r"[0-9]+\.[0-9]+", exact_string(
            gpu["compute_capability"], "GPU compute capability")) is None:
        raise RuntimeError("GPU compute capability format mismatch")
    for key in ("query_identity_role", "nvidia_smi_identity_role"):
        if gpu[key] not in role_map:
            raise RuntimeError(f"GPU {key} is not payload-bound")
    query_bytes = files[role_map[gpu["query_identity_role"]]["archive_path"]]
    expected_query = f"{gpu['name']}, {gpu['compute_capability']}, {gpu['driver_version']}"
    if query_bytes.decode("utf-8").strip() != expected_query:
        raise RuntimeError("GPU identity differs from archived nvidia-smi query")
    if PurePosixPath(role_map[gpu["nvidia_smi_identity_role"]]["source_path"]).name \
            != "nvidia-smi":
        raise RuntimeError("nvidia-smi executable identity is not exact")

    distributions = environment["python_distributions"]
    if type(distributions) is not list:
        raise RuntimeError("python_distributions must be a list")
    if [row.get("import_name") for row in distributions if type(row) is dict] \
            != list(REQUIRED_DISTRIBUTION_IMPORTS):
        raise RuntimeError("Python distribution imports/order mismatch")
    detected_names: dict[str, set[str]] = {}
    for index, row in enumerate(distributions):
        exact_keys(row, {"import_name", "detection", "distribution_names", "distributions"},
                   f"Python distribution row {index}")
        if row["detection"] != "importlib.metadata.packages_distributions":
            raise RuntimeError("distribution mapping was not detected through package metadata")
        names = row["distribution_names"]
        details = row["distributions"]
        if (type(names) is not list or not all(type(name) is str for name in names)
                or names != sorted(set(names), key=str.casefold)):
            raise RuntimeError("distribution_names must be a canonical set")
        if not names and row["import_name"] != "optix":
            raise RuntimeError(
                "only the optix import may use the exact RECORD-ownership fallback")
        if type(details) is not list or len(details) != len(names):
            raise RuntimeError("distribution metadata rows do not match detected names")
        normalized_names = {name.casefold().replace("_", "-") for name in names}
        detected_names[row["import_name"]] = normalized_names
        if {detail.get("name") for detail in details if type(detail) is dict} != set(names):
            raise RuntimeError("distribution detail names differ from detected names")
        for detail in details:
            exact_keys(detail, {"name", "version", "metadata_identity_role", "record_identity_role"},
                       f"distribution detail {detail.get('name')}")
            exact_string(detail["version"], f"distribution version {detail['name']}")
            for role_key, expected_leaf in (
                ("metadata_identity_role", "METADATA"), ("record_identity_role", "RECORD"),
            ):
                role = detail[role_key]
                if role not in role_map or PurePosixPath(role_map[role]["source_path"]).name != expected_leaf:
                    raise RuntimeError(f"distribution {role_key} is not exact payload evidence")
    if detected_names["optix"]:
        if "pyoptix" not in detected_names["optix"]:
            raise RuntimeError("optix import is not bound to the pyoptix distribution")
    else:
        verify_pyoptix_record_ownership(files, installed_rows)
    if not any(name.startswith("cupy-") or name == "cupy" for name in detected_names["cupy"]):
        raise RuntimeError("cupy import lacks a CuPy distribution identity")
    if "numpy" not in detected_names["numpy"]:
        raise RuntimeError("numpy import lacks NumPy distribution identity")
    if not ({"cuda-python", "cuda-bindings"} & detected_names["cuda"]):
        raise RuntimeError("cuda import lacks cuda-python/cuda-bindings identity")

    toolchain = environment["toolchain"]
    exact_keys(toolchain, {"nvrtc", "cuda_driver", "optix_sdk"}, "toolchain")
    for name in ("nvrtc", "cuda_driver"):
        row = toolchain[name]
        exact_keys(row, {"version", "library_identity_role"}, f"toolchain {name}")
        exact_string(row["version"], f"toolchain {name} version")
        if row["library_identity_role"] not in role_map:
            raise RuntimeError(f"toolchain {name} library is not payload-bound")
    if toolchain["cuda_driver"]["version"] != gpu["driver_version"]:
        raise RuntimeError("GPU and CUDA-driver version observations differ")
    sdk = toolchain["optix_sdk"]
    exact_keys(sdk, {"version", "header_identity_roles"}, "OptiX SDK")
    exact_string(sdk["version"], "OptiX SDK version")
    if type(sdk["header_identity_roles"]) is not list or not sdk["header_identity_roles"]:
        raise RuntimeError("OptiX SDK has no captured header identities")
    for role in sdk["header_identity_roles"]:
        if role not in role_map or not role_map[role]["source_path"].endswith(".h"):
            raise RuntimeError("OptiX SDK header role is not payload-bound")

    ceiling = environment["identity_ceiling"]
    exact_keys(ceiling, {"self_contained_for", "not_self_contained_for",
                         "system_dependency_bytes_embedded"}, "identity ceiling")
    if ceiling["self_contained_for"] != (
            "ACTUALLY_LOADED_OPTIX_EXTENSION_AND_CAPTURED_NON_SYSTEM_RUNTIME_BYTES"):
        raise RuntimeError("identity self-contained ceiling mismatch")
    if ceiling["not_self_contained_for"] != (
            "SYSTEM_LIBC_LIBSTDCXX_AND_KERNEL_DRIVER_REEXECUTION"):
        raise RuntimeError("identity non-self-contained ceiling mismatch")
    if exact_bool(ceiling["system_dependency_bytes_embedded"],
                  "system_dependency_bytes_embedded"):
        raise RuntimeError("system dependency bytes must not be overstated as embedded")
    _verify_dynamic_dependencies(environment["dynamic_dependencies"], role_map)
    return role_map


def verify_pyoptix_record_ownership(
    files: dict[str, bytes], installed_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prove ``optix`` ownership when packages_distributions has no mapping.

    Some standards-compliant wheels omit ``top_level.txt`` and therefore leave
    ``importlib.metadata.packages_distributions()["optix"]`` empty.  That is an
    observation, not permission to guess a distribution.  The fallback accepts
    only one complete installed projection whose METADATA names PyOptiX and
    whose exact RECORD owns every archived path, including the initializer and
    the one loaded native extension.
    """
    relative_paths = [row.get("path") for row in installed_rows]
    if (not relative_paths or not all(type(path) is str for path in relative_paths)
            or relative_paths != sorted(set(relative_paths))):
        raise RuntimeError("installed distribution paths are not canonical")
    metadata_paths = [
        path for path in relative_paths
        if re.fullmatch(r"pyoptix-[^/]+\.dist-info/METADATA", path)
    ]
    record_paths = [
        path for path in relative_paths
        if re.fullmatch(r"pyoptix-[^/]+\.dist-info/RECORD", path)
    ]
    if len(metadata_paths) != 1 or len(record_paths) != 1:
        raise RuntimeError("PyOptiX METADATA/RECORD ownership authority is not unique")
    metadata = files.get(f"installed_distribution/{metadata_paths[0]}")
    record = files.get(f"installed_distribution/{record_paths[0]}")
    if metadata is None or record is None:
        raise RuntimeError("PyOptiX METADATA/RECORD payload is absent")
    metadata_text = metadata.decode("utf-8", errors="strict")
    if (re.search(r"(?m)^Name: pyoptix\s*$", metadata_text) is None
            or re.search(r"(?m)^Version: 9\.1\.0\s*$", metadata_text) is None):
        raise RuntimeError("installed METADATA is not exact PyOptiX 9.1.0")
    rows = list(csv.reader(io.StringIO(record.decode("utf-8", errors="strict"))))
    if (not rows or any(len(row) != 3 or not row[0] for row in rows)
            or any(path.startswith(("/", "./")) or ".." in path.split("/")
                   for path, _, _ in rows)):
        raise RuntimeError("PyOptiX RECORD is malformed or unsafe")
    owned_paths = [row[0] for row in rows]
    if owned_paths != relative_paths:
        raise RuntimeError("PyOptiX RECORD does not own the complete installed projection")
    extension_paths = [path for path in owned_paths if EXTENSION_RE.search(path)]
    if ("optix/__init__.py" not in owned_paths or len(extension_paths) != 1
            or not extension_paths[0].startswith("optix/")):
        raise RuntimeError("PyOptiX RECORD does not uniquely own optix._optix")
    return {
        "method": "EXACT_INSTALLED_METADATA_AND_RECORD_OWNERSHIP_FALLBACK",
        "distribution": "pyoptix",
        "version": "9.1.0",
        "record_path": record_paths[0],
        "owned_file_count": len(owned_paths),
        "native_extension_path": extension_paths[0],
    }


def _verify_dynamic_dependencies(
    dynamic: Any, role_map: dict[str, dict[str, Any]],
) -> None:
    if type(dynamic) is not dict:
        raise RuntimeError("dynamic_dependencies must be an object")
    exact_keys(dynamic, {
        "subject_sha256", "raw_ldd_identity_role", "normalized_process_maps_identity_role",
        "rows", "required_process_map_roles",
    }, "dynamic_dependencies")
    subject_sha = _verify_digest(dynamic["subject_sha256"], "dynamic dependency subject SHA")
    for key in ("raw_ldd_identity_role", "normalized_process_maps_identity_role"):
        if dynamic[key] not in role_map:
            raise RuntimeError(f"missing payload-bound dynamic capture: {key}")
    rows = dynamic["rows"]
    if type(rows) is not list or not rows:
        raise RuntimeError("dynamic dependency rows must be non-empty")
    canonical_key: list[tuple[str, str, str]] = []
    process_map_by_role: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if type(row) is not dict:
            raise RuntimeError("dynamic dependency row must be an object")
        exact_keys(row, {
            "observation", "logical_role", "soname", "classification", "resolved_path",
            "bytes", "sha256", "identity_role",
        }, f"dynamic dependency row {index}")
        observation = row["observation"]
        if observation not in {"LDD", "PROCESS_MAP"}:
            raise RuntimeError("unknown dynamic dependency observation")
        logical_role = row["logical_role"]
        if logical_role is not None and type(logical_role) is not str:
            raise RuntimeError("dynamic dependency logical_role must be string or null")
        soname = exact_string(row["soname"], "dynamic dependency soname")
        classification = row["classification"]
        resolved = row["resolved_path"]
        identity_role = row["identity_role"]
        if classification == "VIRTUAL":
            if not soname.startswith("linux-vdso") or any(
                    value is not None for value in
                    (resolved, row["bytes"], row["sha256"], identity_role)):
                raise RuntimeError("invalid virtual dynamic dependency")
        elif classification == "CAPTURED_NON_SYSTEM_OR_CUDA_OPTIX":
            if (type(resolved) is not str or not resolved.startswith("/")
                    or type(identity_role) is not str or identity_role not in role_map):
                raise RuntimeError("captured dynamic dependency lacks exact payload")
            identity = role_map[identity_role]
            if (identity["source_path"] != resolved
                    or exact_int(row["bytes"], "dynamic bytes") != identity["bytes"]
                    or _verify_digest(row["sha256"], "dynamic SHA") != identity["sha256"]):
                raise RuntimeError("captured dynamic dependency identity mismatch")
        elif classification == "RESOLVED_SYSTEM_IDENTITY_ONLY":
            if (type(resolved) is not str or not resolved.startswith("/")
                    or type(identity_role) is not type(None)
                    or exact_int(row["bytes"], "system dependency bytes", minimum=1) < 1):
                raise RuntimeError("invalid system-only dynamic dependency identity")
            _verify_digest(row["sha256"], "system dependency SHA")
        else:
            raise RuntimeError("unknown dynamic dependency classification")
        canonical_key.append((observation, soname, resolved or ""))
        if observation == "PROCESS_MAP" and logical_role is not None:
            if logical_role in process_map_by_role:
                raise RuntimeError(f"duplicate process-map logical role: {logical_role}")
            process_map_by_role[logical_role] = row
    if canonical_key != sorted(set(canonical_key)):
        raise RuntimeError("dynamic dependency rows are not canonical and unique")
    required = dynamic["required_process_map_roles"]
    if required != list(REQUIRED_PROCESS_MAP_ROLES):
        raise RuntimeError("required process-map role set/order mismatch")
    for role in REQUIRED_PROCESS_MAP_ROLES:
        row = process_map_by_role.get(role)
        if row is None or row["classification"] != "CAPTURED_NON_SYSTEM_OR_CUDA_OPTIX":
            raise RuntimeError(f"required loaded runtime was not captured: {role}")
    if process_map_by_role["nvrtc"]["sha256"] != role_map[
            role_map_key_for_toolchain(role_map, "nvrtc")]["sha256"]:
        raise RuntimeError("NVRTC toolchain and process-map identities diverge")
    if process_map_by_role["cuda_driver"]["sha256"] != role_map[
            role_map_key_for_toolchain(role_map, "cuda_driver")]["sha256"]:
        raise RuntimeError("CUDA driver toolchain and process-map identities diverge")
    if subject_sha not in {row["sha256"] for row in process_map_by_role.values()}:
        raise RuntimeError("loaded extension is absent from the process-map identity set")


def role_map_key_for_toolchain(
    role_map: dict[str, dict[str, Any]], needle: str,
) -> str:
    matches = [role for role in role_map if role == f"toolchain.{needle}.library"]
    if matches != [f"toolchain.{needle}.library"]:
        raise RuntimeError(f"missing canonical toolchain runtime role: {needle}")
    return matches[0]


def verify_loaded_extension(
    result: dict[str, Any], files: dict[str, bytes],
    installed_rows: list[dict[str, Any]], environment: dict[str, Any],
) -> None:
    extension = result["loaded_optix_extension"]
    if type(extension) is not dict:
        raise RuntimeError("loaded_optix_extension must be an object")
    exact_keys(extension, {"module", "source_path", "distribution_path", "bytes", "sha256"},
               "loaded_optix_extension")
    if extension["module"] != "optix._optix":
        raise RuntimeError("identity is not the actually loaded optix._optix extension")
    distribution_path = exact_string(extension["source_path"],
                                     "loaded extension distribution-relative path")
    if EXTENSION_RE.search(distribution_path) is None or distribution_path.endswith("/__init__.py"):
        raise RuntimeError("loaded extension path is not a native optix._optix binary")
    payload_name = f"installed_distribution/{distribution_path}"
    payload = files.get(payload_name)
    if payload is None:
        raise RuntimeError("loaded extension bytes are absent from installed distribution payload")
    if (exact_int(extension["bytes"], "loaded extension bytes", minimum=1) != len(payload)
            or _verify_digest(extension["sha256"], "loaded extension SHA") != sha256(payload)
            or digest_row(distribution_path, payload) not in installed_rows):
        raise RuntimeError("loaded extension identity does not match archived bytes")
    dynamic = environment["dynamic_dependencies"]
    if dynamic["subject_sha256"] != extension["sha256"]:
        raise RuntimeError("ldd/process-map subject is not the loaded extension")
    source_path = exact_string(extension["distribution_path"], "loaded extension absolute path")
    if not source_path.startswith("/"):
        raise RuntimeError("loaded extension absolute path is not absolute")
    process_matches = [
        row for row in dynamic["rows"]
        if row["observation"] == "PROCESS_MAP" and row["resolved_path"] == source_path
        and row["sha256"] == extension["sha256"]
    ]
    if len(process_matches) != 1:
        raise RuntimeError("loaded extension lacks one exact post-launch process-map observation")


def verify_execution_authority(
    result: dict[str, Any], files: dict[str, bytes], environment: dict[str, Any],
) -> None:
    record = result["executed_source_authority"]
    if type(record) is not dict:
        raise RuntimeError("executed_source_authority must be an object")
    exact_keys(record, {"file", "document", "launch_pin"},
               "executed source authority record")
    _, authority_bytes = _one_payload_by_identity(
        files, "provenance/", record["file"], "executed source authority")
    document = load_json(authority_bytes, "executed source authority")
    if document != record["document"]:
        raise RuntimeError("executed source authority document/bytes mismatch")
    launch_pin_record = record["launch_pin"]
    exact_keys(launch_pin_record, {"file", "document"}, "execution launch pin record")
    _, launch_pin_bytes = _one_payload_by_identity(
        files, "provenance/", launch_pin_record["file"], "execution launch pin")
    launch_pin = load_json(launch_pin_bytes, "execution launch pin")
    if launch_pin != launch_pin_record["document"]:
        raise RuntimeError("execution launch pin document/bytes mismatch")
    exact_keys(document, {
        "schema", "status", "capture_phase", "file_count", "files",
        "files_sha256", "origin_repository_commit", "origin_repository_tree",
        "git_membership_proof", "registered_performance_timing_count",
    }, "executed source authority")
    if (document["schema"] != "rtdl.goal5800.pyoptix_execution_authority.v2"
            or document["status"] != "FROZEN__PREEXECUTION_SOURCE_AUTHORITY"
            or document["capture_phase"]
            != "BEFORE_PYOPTIX_CUPY_IMPORT_OR_CUDA_OPTIX_INITIALIZATION"
            or type(document["registered_performance_timing_count"]) is not int
            or document["registered_performance_timing_count"] != 0):
        raise RuntimeError("executed source authority schema/phase/timing mismatch")
    for key in ("origin_repository_commit", "origin_repository_tree"):
        identity = exact_string(document[key], f"executed source {key}")
        if re.fullmatch(r"[0-9a-f]{40}", identity) is None:
            raise RuntimeError(f"executed source {key} must be a full lowercase Git SHA-1")
    rows = document["files"]
    if type(rows) is not list \
            or exact_int(document["file_count"], "executed source file count") != len(rows):
        raise RuntimeError("executed source authority file-count mismatch")
    for index, row in enumerate(rows):
        exact_keys(row, {"path", "git_mode", "git_blob_sha1", "bytes", "sha256"},
                   f"executed source row {index}")
        exact_string(row["path"], f"executed source path {index}")
        if row["git_mode"] != "100644" or re.fullmatch(
                r"[0-9a-f]{40}", exact_string(
                    row["git_blob_sha1"], f"executed source blob {index}")) is None:
            raise RuntimeError("executed source Git blob identity is malformed")
        exact_int(row["bytes"], f"executed source bytes {index}", minimum=1)
        _verify_digest(row["sha256"], f"executed source SHA {index}")
    if [row["path"] for row in rows] != list(REQUIRED_EXECUTED_SOURCE_PATHS):
        raise RuntimeError("executed source authority path set/order mismatch")
    if _verify_digest(document["files_sha256"], "executed source aggregate SHA") \
            != sha256(canonical(rows)):
        raise RuntimeError("executed source authority aggregate mismatch")
    exact_keys(launch_pin, {
        "schema", "status", "capture_phase", "authority", "authority_schema",
        "origin_repository_commit", "origin_repository_tree",
        "executed_source_file_count", "all_required_files_exact_origin_blobs",
        "changed_expected_allowed", "registered_performance_timing_count",
    }, "execution launch pin")
    authority_identity = launch_pin["authority"]
    exact_keys(authority_identity, {"path", "bytes", "sha256"},
               "execution launch pin authority")
    if (launch_pin["schema"] != "rtdl.goal5800.pyoptix_execution_launch_pin.v1"
            or launch_pin["status"] != "FROZEN__SEPARATE_PREEXECUTION_TRUST_ANCHOR"
            or launch_pin["capture_phase"]
            != "AFTER_AUTHORITY_FREEZE__BEFORE_PYOPTIX_CUPY_IMPORT_OR_GPU_EXECUTION"
            or launch_pin["authority_schema"] != document["schema"]
            or launch_pin["origin_repository_commit"] != document["origin_repository_commit"]
            or launch_pin["origin_repository_tree"] != document["origin_repository_tree"]
            or exact_int(launch_pin["executed_source_file_count"],
                         "launch pin source file count") != len(rows)
            or launch_pin["all_required_files_exact_origin_blobs"] is not True
            or launch_pin["changed_expected_allowed"] is not False
            or exact_int(launch_pin["registered_performance_timing_count"],
                         "launch pin timing count") != 0
            or exact_int(authority_identity["bytes"], "launch pin authority bytes")
            != len(authority_bytes)
            or _verify_digest(authority_identity["sha256"],
                              "launch pin authority SHA") != sha256(authority_bytes)):
        raise RuntimeError("execution launch pin does not bind the exact v2 authority")
    archived_rows = rows_for_prefix(files, "executed_source/")
    digest_only_rows = [
        {"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in rows
    ]
    if (digest_only_rows != archived_rows
            or digest_only_rows != environment["executed_sources"]):
        raise RuntimeError("preexecution authority differs from archived/environment sources")
    verify_git_membership_proof(document, files, rows)


def _git_object_id(kind: str, value: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(value)}\0".encode("ascii") + value).hexdigest()


def _decode_git_object(row: Any, *, kind: str, label: str) -> bytes:
    exact_keys(row, {"object_id", "bytes", "base64"}, f"{label} Git object")
    object_id = exact_string(row["object_id"], f"{label} Git object id")
    if re.fullmatch(r"[0-9a-f]{40}", object_id) is None:
        raise RuntimeError(f"{label} Git object id malformed")
    encoded = exact_string(row["base64"], f"{label} Git object base64")
    if len(encoded) > 8_000_000:
        raise RuntimeError(f"{label} Git object proof is oversized")
    try:
        value = base64.b64decode(encoded, validate=True)
    except Exception as error:
        raise RuntimeError(f"{label} Git object base64 invalid") from error
    if base64.b64encode(value).decode("ascii") != encoded:
        raise RuntimeError(f"{label} Git object base64 is noncanonical")
    if exact_int(row["bytes"], f"{label} Git object bytes") != len(value) \
            or _git_object_id(kind, value) != object_id:
        raise RuntimeError(f"{label} Git object identity mismatch")
    return value


def _parse_raw_git_tree(value: bytes) -> list[dict[str, str]]:
    rows = []
    cursor = 0
    while cursor < len(value):
        space = value.find(b" ", cursor)
        nul = value.find(b"\0", space + 1)
        if space <= cursor or nul < 0 or nul + 21 > len(value):
            raise RuntimeError("malformed raw Git tree object")
        mode = value[cursor:space].decode("ascii", errors="strict")
        name = value[space + 1:nul].decode("utf-8", errors="strict")
        object_id = value[nul + 1:nul + 21].hex()
        if (not name or name in {".", ".."} or "/" in name or "\\" in name
                or mode not in {"40000", "100644"}):
            raise RuntimeError("unsafe or unsupported Git tree entry")
        rows.append({"mode": mode, "name": name, "object_id": object_id})
        cursor = nul + 21
    if len({row["name"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate raw Git tree entry")
    return rows


def _required_git_directories() -> list[str]:
    directories = {""}
    for relative in REQUIRED_EXECUTED_SOURCE_PATHS:
        parts = relative.split("/")
        for count in range(1, len(parts)):
            directories.add("/".join(parts[:count]))
    return sorted(
        directories, key=lambda value: (value.count("/") + bool(value), value))


def verify_git_membership_proof(
    document: dict[str, Any], files: dict[str, bytes], rows: list[dict[str, Any]],
) -> None:
    proof = document["git_membership_proof"]
    exact_keys(proof, {
        "object_format", "commit_object", "tree_nodes",
        "all_required_files_exact_origin_blobs",
    }, "Git membership proof")
    if proof["object_format"] != "sha1" \
            or proof["all_required_files_exact_origin_blobs"] is not True:
        raise RuntimeError("Git membership proof envelope mismatch")
    commit_body = _decode_git_object(
        proof["commit_object"], kind="commit", label="origin commit")
    if proof["commit_object"]["object_id"] != document["origin_repository_commit"]:
        raise RuntimeError("Git commit proof differs from declared origin commit")
    header = commit_body.split(b"\n\n", 1)[0].splitlines()
    trees = [line[5:].decode("ascii", errors="strict")
             for line in header if line.startswith(b"tree ")]
    if trees != [document["origin_repository_tree"]]:
        raise RuntimeError("Git commit does not uniquely bind the declared root tree")
    nodes = proof["tree_nodes"]
    expected_directories = _required_git_directories()
    if type(nodes) is not list or [node.get("path") for node in nodes
                                   if type(node) is dict] != expected_directories:
        raise RuntimeError("Git tree proof is incomplete, noncanonical, or has unused nodes")
    entries_by_path: dict[str, list[dict[str, str]]] = {}
    object_by_path: dict[str, str] = {}
    for node in nodes:
        exact_keys(node, {"path", "object_id", "bytes", "base64"}, "Git tree node")
        path = node["path"]
        if type(path) is not str:
            raise RuntimeError("Git tree node path must be a string")
        value = _decode_git_object(
            {key: node[key] for key in ("object_id", "bytes", "base64")},
            kind="tree", label=f"tree {path!r}")
        entries_by_path[path] = _parse_raw_git_tree(value)
        object_by_path[path] = node["object_id"]
    if object_by_path[""] != document["origin_repository_tree"]:
        raise RuntimeError("Git root proof differs from origin tree")
    for directory in expected_directories[1:]:
        parent, _, leaf = directory.rpartition("/")
        matches = [entry for entry in entries_by_path[parent]
                   if entry["name"] == leaf and entry["mode"] == "40000"]
        if len(matches) != 1 or matches[0]["object_id"] != object_by_path[directory]:
            raise RuntimeError(f"Git directory membership mismatch: {directory}")
    for row in rows:
        value = files.get(f"executed_source/{row['path']}")
        if value is None or _git_object_id("blob", value) != row["git_blob_sha1"]:
            raise RuntimeError(f"executed source/blob identity mismatch: {row['path']}")
        parent, _, leaf = row["path"].rpartition("/")
        matches = [entry for entry in entries_by_path[parent]
                   if entry["name"] == leaf and entry["mode"] == "100644"]
        if len(matches) != 1 or matches[0]["object_id"] != row["git_blob_sha1"]:
            raise RuntimeError(f"executed source lacks origin-tree membership: {row['path']}")


def source_payloads(files: dict[str, bytes]) -> dict[str, bytes]:
    return {
        name.removeprefix("executed_source/"): value
        for name, value in files.items() if name.startswith("executed_source/")
    }


def exact_counts(**nonzero: int) -> dict[str, int]:
    counts = {key: 0 for key in OPERATION_COUNT_KEYS}
    if set(nonzero) - set(counts):
        raise AssertionError("internal unknown counter")
    counts.update(nonzero)
    return counts


def _attribute_path(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def derive_execute_source_boundary(arm: bytes) -> dict[str, Any]:
    tree = ast.parse(arm)
    classes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    expected = {
        "RelationPrepared": {
            "zero_on_stream": 1, "enqueue": 1, "enqueue_d2h": 2,
            "synchronize": 2,
        },
        "TrianglePrepared": {
            "zero_on_stream": 1, "enqueue": 1, "enqueue_d2h": 3,
            "synchronize": 2,
        },
    }
    complete_call_shapes = {
        "RelationPrepared": {
            "<dynamic>.reshape": 1, "<dynamic>.tolist": 1,
            "DeviceStatusFailure": 1, "RuntimeError": 3,
            "b.operation_count_delta": 2, "dict": 2, "enumerate": 1,
            "exact_counts": 1, "int": 8, "len": 1, "list": 3,
            "map": 1, "require_execution_contract": 1,
            "self.launcher.enqueue": 1, "self.launcher.enqueue_d2h": 2,
            "self.launcher.synchronize": 2,
            "self.launcher.zero_on_stream": 1, "set": 1, "sorted": 1,
        },
        "TrianglePrepared": {
            "RuntimeError": 3, "b.operation_count_delta": 1, "dict": 2,
            "exact_counts": 1, "int": 8, "len": 1, "list": 1,
            "require_execution_contract": 1, "self.h_per_ray.tolist": 1,
            "self.launcher.enqueue": 1, "self.launcher.enqueue_d2h": 3,
            "self.launcher.synchronize": 2,
            "self.launcher.zero_on_stream": 1,
        },
    }
    receipts = []
    for class_name, expected_calls in expected.items():
        class_node = classes.get(class_name)
        functions = [] if class_node is None else [
            node for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_execute_observed"
        ]
        if len(functions) != 1:
            raise RuntimeError(f"executed source boundary absent: {class_name}")
        function = functions[0]
        launcher_calls: dict[str, int] = {}
        all_calls: dict[str, int] = {}
        forbidden = []
        for node in ast.walk(function):
            if isinstance(node, ast.Attribute):
                path = _attribute_path(node)
                if path == "self.launcher.stream" or (
                        path is not None and path.startswith("self.launcher.stream.")):
                    forbidden.append(path)
            if not isinstance(node, ast.Call):
                continue
            path = _attribute_path(node.func)
            if path is None and isinstance(node.func, ast.Attribute):
                call_key = f"<dynamic>.{node.func.attr}"
            else:
                call_key = path if path is not None else "<dynamic>"
            all_calls[call_key] = all_calls.get(call_key, 0) + 1
            if isinstance(node.func, ast.Name) and node.func.id in {
                    "eval", "exec", "getattr", "setattr", "__import__"}:
                forbidden.append(node.func.id)
            if path is None:
                continue
            if path.startswith(("b.cp.", "b.optix.", "cp.", "cuda.", "optix.", "self.d_")):
                forbidden.append(path)
            if path.startswith("self.launcher."):
                method = path.removeprefix("self.launcher.")
                launcher_calls[method] = launcher_calls.get(method, 0) + 1
        if (forbidden or launcher_calls != expected_calls
                or all_calls != complete_call_shapes[class_name]):
            raise RuntimeError(f"executed source boundary mismatch: {class_name}")
        receipts.append({
            "class": class_name,
            "method": "_execute_observed",
            "ast_sha256": sha256(
                ast.dump(function, include_attributes=False).encode("utf-8")),
            "wrapper_call_shape": launcher_calls,
            "complete_call_shape": all_calls,
        })
    return {
        "schema": "rtdl.goal5800.pyoptix_execute_source_boundary.v1",
        "source_sha256": sha256(arm),
        "checked_methods": receipts,
        "direct_gpu_calls_allowed": False,
        "dynamic_call_escape_allowed": False,
        "complete_driver_operation_observation_claimed": False,
    }


def verify_static_operation_sources(files: dict[str, bytes]) -> None:
    sources = source_payloads(files)
    arm_paths = [path for path in sources if path.endswith("pyoptix_idiomatic_arm.py")]
    baseline_paths = [path for path in sources if path.endswith("pyoptix_baseline.py")]
    if len(arm_paths) != 1 or len(baseline_paths) != 1:
        raise RuntimeError("cannot identify exact idiomatic-arm/baseline executed sources")
    arm = sources[arm_paths[0]]
    baseline = sources[baseline_paths[0]]
    if b"cp.asnumpy(" in arm:
        raise RuntimeError("blocking cp.asnumpy remains in executed idiomatic arm")
    source_text = arm.decode("utf-8").replace("\r\n", "\n")
    if "\r" in source_text:
        raise RuntimeError("idiomatic-arm source contains unsupported bare CR bytes")
    for class_name in ("RelationPrepared", "TrianglePrepared"):
        start = source_text.find(f"class {class_name}:")
        execute = source_text.find("    def execute(", start)
        close = source_text.find("    def close(", execute)
        if min(start, execute, close) < 0:
            raise RuntimeError(f"cannot locate {class_name}.execute source")
        body = source_text[execute:close]
        forbidden = (
            "cp.asnumpy(", "cp.cuda.alloc(", "cp.cuda.alloc_pinned_memory(",
            "cp.cuda.Stream(", "cp.zeros(", "cp.empty(", "cp.asarray(",
        )
        hits = [literal for literal in forbidden if literal in body]
        if hits:
            raise RuntimeError(f"per-execute allocation/blocking source in {class_name}: {hits}")
    baseline_text = baseline.decode("utf-8").replace("\r\n", "\n")
    if "\r" in baseline_text:
        raise RuntimeError("baseline source contains unsupported bare CR bytes")
    if baseline_text.count(
            "self.stream.synchronize(authorization=self._sync_authority)") != 1 \
            or baseline_text.count("return self._stream.synchronize()") != 1:
        raise RuntimeError("PreparedLaunch authorized explicit-sync implementation drift")
    if "copy_from_async(" not in baseline_text or "copy_to_host_async(" not in baseline_text:
        raise RuntimeError("prepared launch no longer uses explicit asynchronous transfers")
    sections = {
        "to_device": ("def to_device(", "\n\nclass Logger"),
        "launcher_init": ("    def __init__(\n", "    def _require_open(",),
        "zero": ("    def zero_on_stream(", "    def pinned_array("),
        "pinned": ("    def pinned_array(", "    def begin_execution("),
        "enqueue": ("    def enqueue(\n", "    def enqueue_d2h("),
        "d2h": ("    def enqueue_d2h(", "    def synchronize("),
        "sync": ("    def synchronize(", "    def close("),
    }
    required_literals = {
        "to_device": (
            "cp.cuda.alloc(", ".copy_from(",
            '"prepare_device_allocation_call_count"', '"prepare_h2d_call_count"',
        ),
        "launcher_init": (
            "cp.cuda.Stream(non_blocking=True)", "cp.cuda.alloc(PARAM_DTYPE.itemsize)",
            '"prepare_stream_creation_count"', '"prepare_device_allocation_call_count"',
        ),
        "zero": ("cp.cuda.runtime.memsetAsync(",
                 '"execute_device_zero_fill_call_count"'),
        "pinned": ("cp.cuda.alloc_pinned_memory(",
                   '"prepare_pinned_host_allocation_call_count"'),
        "enqueue": ("copy_from_async(", '"execute_async_h2d_call_count"',
                    "optix.launch(", '"execute_launch_call_count"'),
        "d2h": ("copy_to_host_async(", '"execute_async_d2h_call_count"'),
        "sync": ("self.stream.synchronize(authorization=self._sync_authority)",
                 '"execute_explicit_stream_sync_call_count"'),
    }
    search_from = baseline_text.find("class PreparedLaunch:")
    for name, (start_literal, end_literal) in sections.items():
        start = baseline_text.find(start_literal, search_from if name != "to_device" else 0)
        end = baseline_text.find(end_literal, start + len(start_literal))
        if start < 0 or end < 0:
            raise RuntimeError(f"cannot locate operation instrumentation section: {name}")
        section = baseline_text[start:end]
        missing = [literal for literal in required_literals[name] if literal not in section]
        if missing:
            raise RuntimeError(f"operation instrumentation is incomplete in {name}: {missing}")


def verify_count_map(value: Any, expected: dict[str, int], label: str) -> None:
    if type(value) is not dict or set(value) != set(OPERATION_COUNT_KEYS):
        raise RuntimeError(f"{label} counter vocabulary mismatch")
    for key, count in value.items():
        exact_int(count, f"{label}.{key}")
    if value != expected:
        raise RuntimeError(f"{label} exact operation counts mismatch")


def execution_projection(
    execution: dict[str, Any], byte_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "execute_operation_counts": execution["execute_operation_counts"],
        "operation_order": execution["operation_order"],
        "independent_execute_guard": execution["independent_execute_guard"],
        "total_host_blocking_count": execution["total_host_blocking_count"],
        "bytes": {key: execution[key] for key in byte_fields},
    }


def verify_task_execution(
    task: str, execution: Any, *, expected_prepare: dict[str, int],
    expected_execute: dict[str, int], expected_order: list[str],
    byte_fields: tuple[str, ...], expected_bytes: dict[str, int],
) -> None:
    if type(execution) is not dict:
        raise RuntimeError(f"{task} execution must be an object")
    common = {
        "device_status", "launch_count", "required_sync_count",
        "total_host_blocking_count", "operation_order", "prepare_operation_counts",
        "operation_ledger_scope", "execute_operation_counts",
        "independent_execute_guard",
    }
    task_keys = ({"output", "raw_event_count", "device_overflow"}
                 if task == "relation" else {"per_ray", "weighted_sum"})
    exact_keys(execution, common | task_keys | set(byte_fields), f"{task} execution")
    if execution["operation_ledger_scope"] != OPERATION_LEDGER_SCOPE:
        raise RuntimeError(f"{task} operation-ledger scope mismatch")
    expected_guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    if execution["independent_execute_guard"] != expected_guard:
        raise RuntimeError(f"{task} independent execute guard mismatch")
    verify_count_map(execution["prepare_operation_counts"], expected_prepare,
                     f"{task} prepare")
    verify_count_map(execution["execute_operation_counts"], expected_execute,
                     f"{task} execute")
    if execution["operation_order"] != expected_order:
        raise RuntimeError(f"{task} exact operation order mismatch")
    if exact_int(execution["total_host_blocking_count"],
                 f"{task} host-blocking count") != 2:
        raise RuntimeError(f"{task} must have exactly two host-blocking boundaries")
    if exact_int(execution["required_sync_count"], f"{task} sync count") != 2:
        raise RuntimeError(f"{task} must declare exactly two required syncs")
    expected_launches = 2 if task == "relation" else 1
    if exact_int(execution["launch_count"], f"{task} launch count") != expected_launches:
        raise RuntimeError(f"{task} launch count mismatch")
    if exact_int(execution["device_status"], f"{task} device status") != 0:
        raise RuntimeError(f"{task} device status is not success")
    for key, value in expected_bytes.items():
        if exact_int(execution[key], f"{task}.{key}") != value:
            raise RuntimeError(f"{task} byte projection mismatch: {key}")
    if task == "relation":
        if exact_int(execution["device_overflow"], "relation overflow") != 0:
            raise RuntimeError("relation overflow is nonzero")
        raw_count = exact_int(execution["raw_event_count"], "relation raw-event count")
        if execution["output_d2h_bytes"] != raw_count * 8:
            raise RuntimeError("relation output D2H bytes do not match raw rows")
        output = execution["output"]
        if (type(output) is not list or len(output) != 4096
                or any(type(row) is not list or len(row) != 2
                       or any(type(value) is not int or value < 0 for value in row)
                       for row in output)):
            raise RuntimeError("relation output shape/type mismatch")
    else:
        per_ray = execution["per_ray"]
        if type(per_ray) is not list or len(per_ray) != 16384 \
                or any(type(value) is not int or value < 0 for value in per_ray):
            raise RuntimeError("triangle per-ray output shape/type mismatch")
        if execution["per_ray_d2h_bytes"] != len(per_ray) * 8:
            raise RuntimeError("triangle per-ray D2H bytes do not match output")
        if exact_int(execution["weighted_sum"], "triangle weighted sum") != 65530:
            raise RuntimeError("triangle weighted sum mismatch")


def verify_operation_ledger(
    result: dict[str, Any], files: dict[str, bytes],
) -> int:
    verify_static_operation_sources(files)
    relation_prepare = exact_counts(
        prepare_device_allocation_call_count=11,
        prepare_pinned_host_allocation_call_count=4,
        prepare_h2d_call_count=4,
        prepare_stream_creation_count=1,
    )
    triangle_prepare = exact_counts(
        prepare_device_allocation_call_count=9,
        prepare_pinned_host_allocation_call_count=4,
        prepare_h2d_call_count=3,
        prepare_stream_creation_count=1,
    )
    relation_execute = exact_counts(
        execute_async_h2d_call_count=2, execute_async_d2h_call_count=2,
        execute_device_zero_fill_call_count=2,
        execute_explicit_stream_sync_call_count=2, execute_launch_call_count=2,
    )
    triangle_execute = exact_counts(
        execute_async_h2d_call_count=1, execute_async_d2h_call_count=3,
        execute_device_zero_fill_call_count=3,
        execute_explicit_stream_sync_call_count=2, execute_launch_call_count=1,
    )
    relation_order = [
        "rows_reset", "control_reset", "params0_h2d", "launch0",
        "params1_h2d", "launch1", "control_d2h", "status_ready_sync",
        "rows_d2h", "output_ready_sync",
    ]
    triangle_order = [
        "per_ray_reset", "weighted_reset", "status_reset", "params_h2d",
        "launch", "control_d2h", "status_ready_sync", "per_ray_d2h",
        "weighted_d2h", "output_ready_sync",
    ]
    failure_witness = result["device_failure_status_before_output_witness"]
    verify_failure_witness(failure_witness)
    relation_bytes = {
        "rows_reset_bytes": 8194 * 2 * 4,
        "control_reset_bytes": 3 * 4,
        "control_d2h_bytes": 3 * 4,
        "output_d2h_bytes": 8192 * 8,
    }
    triangle_bytes = {
        "per_ray_reset_bytes": 16384 * 8,
        "weighted_reset_bytes": 8,
        "status_reset_bytes": 4,
        "status_d2h_bytes": 4,
        "per_ray_d2h_bytes": 16384 * 8,
        "weighted_d2h_bytes": 8,
    }
    relation_fields = tuple(relation_bytes)
    triangle_fields = tuple(triangle_bytes)
    for execution in (
        result["relation"]["initial_execution"],
        result["relation"]["repeat_execution"],
    ):
        verify_task_execution(
            "relation", execution, expected_prepare=relation_prepare,
            expected_execute=relation_execute, expected_order=relation_order,
            byte_fields=relation_fields, expected_bytes=relation_bytes,
        )
    for execution in (
        result["triangle"]["initial_execution"],
        result["triangle"]["repeat_execution"],
    ):
        verify_task_execution(
            "triangle", execution, expected_prepare=triangle_prepare,
            expected_execute=triangle_execute, expected_order=triangle_order,
            byte_fields=triangle_fields, expected_bytes=triangle_bytes,
        )
    if result["relation"]["initial_execution"] != result["relation"]["repeat_execution"]:
        raise RuntimeError("relation same-owner initial/repeat is not exact")
    if result["triangle"]["initial_execution"] != result["triangle"]["repeat_execution"]:
        raise RuntimeError("triangle same-owner initial/repeat is not exact")
    sources = source_payloads(files)
    arm_paths = [path for path in sources if path.endswith("pyoptix_idiomatic_arm.py")]
    if len(arm_paths) != 1:
        raise RuntimeError("cannot identify source-boundary arm source")
    source_boundary = derive_execute_source_boundary(sources[arm_paths[0]])
    if result["execute_source_boundary"] != source_boundary:
        raise RuntimeError("top-level execute source boundary is not independently reproducible")
    expected_ledger = {
        "schema": "rtdl.goal5800.pyoptix_operation_ledger.v3",
        "scope": OPERATION_LEDGER_SCOPE,
        "source_observable_wrapper_counter_keys": list(OPERATION_COUNT_KEYS),
        "execute_source_boundary": source_boundary,
        "complete_driver_operation_observation_claimed": False,
        "relation": {
            "prepare_operation_counts": relation_prepare,
            "initial": execution_projection(
                result["relation"]["initial_execution"], relation_fields),
            "repeat": execution_projection(
                result["relation"]["repeat_execution"], relation_fields),
            "initial_repeat_exact": True,
        },
        "triangle": {
            "prepare_operation_counts": triangle_prepare,
            "initial": execution_projection(
                result["triangle"]["initial_execution"], triangle_fields),
            "repeat": execution_projection(
                result["triangle"]["repeat_execution"], triangle_fields),
            "initial_repeat_exact": True,
        },
        "context_module_pipeline_sbt_prepare_counted": False,
        "owner_close_operation_counts_claimed": False,
        "device_failure_status_before_output_witness": failure_witness,
    }
    if result["operation_ledger"] != expected_ledger:
        raise RuntimeError("operation ledger is not the exact task-result projection")
    return 4


def verify_failure_witness(witness: Any) -> None:
    if type(witness) is not dict:
        raise RuntimeError("device failure witness must be an object")
    exact_keys(witness, {
        "raw_event_count", "device_overflow", "device_status", "raw_capacity",
        "application_output_exposed", "application_output_d2h_call_count",
        "operation_order", "execute_operation_counts", "independent_execute_guard",
    }, "device failure witness")
    raw_count = exact_int(witness["raw_event_count"], "failure raw-event count")
    overflow = exact_int(witness["device_overflow"], "failure overflow")
    status = exact_int(witness["device_status"], "failure device status")
    if exact_int(witness["raw_capacity"], "failure raw capacity") != 1:
        raise RuntimeError("failure witness capacity is not exactly one")
    if not (overflow or status or raw_count > 1):
        raise RuntimeError("failure witness does not contain a device failure")
    if witness["application_output_exposed"] is not False \
            or exact_int(witness["application_output_d2h_call_count"],
                         "failure output D2H count") != 0:
        raise RuntimeError("failure witness exposed or copied application output")
    expected_order = [
        "rows_reset", "control_reset", "params0_h2d", "launch0",
        "params1_h2d", "launch1", "control_d2h", "status_ready_sync",
    ]
    if witness["operation_order"] != expected_order:
        raise RuntimeError("failure witness operation order passed the status boundary")
    verify_count_map(witness["execute_operation_counts"], exact_counts(
        execute_async_h2d_call_count=2, execute_async_d2h_call_count=1,
        execute_device_zero_fill_call_count=2,
        execute_explicit_stream_sync_call_count=1, execute_launch_call_count=2,
    ), "failure witness execute")
    expected_guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    if witness["independent_execute_guard"] != expected_guard:
        raise RuntimeError("failure witness execute guard mismatch")


def _one_payload_by_identity(
    files: dict[str, bytes], prefix: str, identity: dict[str, Any], label: str,
) -> tuple[str, bytes]:
    exact_keys(identity, {"path", "bytes", "sha256"}, label)
    expected_bytes = exact_int(identity["bytes"], f"{label} bytes", minimum=1)
    expected_sha = _verify_digest(identity["sha256"], f"{label} SHA")
    matches = [
        (name, value) for name, value in files.items()
        if name.startswith(prefix) and len(value) == expected_bytes
        and sha256(value) == expected_sha
    ]
    if len(matches) != 1:
        raise RuntimeError(f"{label} has {len(matches)} archive identity matches")
    return matches[0]


def _one_provenance_suffix(
    files: dict[str, bytes], suffix: str, *, expected_bytes: int,
    expected_sha: str, label: str,
) -> tuple[str, bytes]:
    normalized = suffix.replace("\\", "/").lstrip("./")
    matches = [
        (name, value) for name, value in files.items()
        if name.startswith("provenance/") and name.endswith(f"/{normalized}")
        and len(value) == expected_bytes and sha256(value) == expected_sha
    ]
    if len(matches) != 1:
        raise RuntimeError(f"{label} has {len(matches)} exact provenance matches")
    return matches[0]


def verify_receipt_chain(
    result: dict[str, Any], files: dict[str, bytes],
) -> None:
    source = result["pyoptix_source_authority_identity"]
    exact_keys(source, {"path", "commit", "tree", "status_porcelain", "clean"},
               "PyOptiX source authority")
    if (source["commit"] != PYOPTIX_COMMIT or source["tree"] != PYOPTIX_TREE
            or source["status_porcelain"] != "" or source["clean"] is not True):
        raise RuntimeError("PyOptiX source authority is not the pinned clean checkout")
    provenance = result["pyoptix_install_provenance"]
    exact_keys(provenance, {
        "wheel_build_receipt", "clean_install_receipt",
        "built_wheel_equals_installed_wheel",
        "receipt_extensions_equal_loaded_extension",
    }, "PyOptiX install provenance")
    if provenance["built_wheel_equals_installed_wheel"] is not True \
            or provenance["receipt_extensions_equal_loaded_extension"] is not True:
        raise RuntimeError("PyOptiX receipt-chain equality claims are not true")
    build_record = provenance["wheel_build_receipt"]
    install_record = provenance["clean_install_receipt"]
    exact_keys(build_record, {
        "file", "document", "wheel_identity", "wheel_sha256", "extension_sha256",
        "optix_headers_root",
    }, "wheel-build receipt record")
    exact_keys(install_record, {
        "file", "document", "wheel_identity", "wheel_sha256",
        "extension_identity", "extension_sha256",
    }, "clean-install receipt record")
    _, build_bytes = _one_payload_by_identity(
        files, "provenance/", build_record["file"], "wheel-build receipt")
    _, install_bytes = _one_payload_by_identity(
        files, "provenance/", install_record["file"], "clean-install receipt")
    build = load_json(build_bytes, "wheel-build receipt")
    install = load_json(install_bytes, "clean-install receipt")
    if build != build_record["document"] or install != install_record["document"]:
        raise RuntimeError("embedded receipt document differs from archived receipt bytes")
    if (exact_string(build_record["optix_headers_root"], "build OptiX headers root")
            != build.get("optix_headers", {}).get("root")):
        raise RuntimeError("result/build-receipt OptiX header roots differ")

    exact_keys(build, {
        "schema", "status", "transaction_kind", "registered_performance_timing_count",
        "pyoptix_source", "optix_headers", "build", "wheel",
    }, "wheel-build receipt")
    if (build["schema"] != "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1"
            or build["status"] != "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED"
            or build["transaction_kind"] != "build_provenance_not_performance"
            or type(build["registered_performance_timing_count"]) is not int
            or build["registered_performance_timing_count"] != 0):
        raise RuntimeError("wheel-build receipt status/schema/timing mismatch")
    build_source = build["pyoptix_source"]
    exact_keys(build_source, {
        "commit", "tree", "archive_projection_file_count", "archive_projection_files",
    }, "wheel-build source")
    if build_source["commit"] != PYOPTIX_COMMIT or build_source["tree"] != PYOPTIX_TREE:
        raise RuntimeError("wheel-build source identity mismatch")
    source_rows = build_source["archive_projection_files"]
    if (type(source_rows) is not list
            or exact_int(build_source["archive_projection_file_count"],
                         "build source file count") != len(source_rows)):
        raise RuntimeError("wheel-build source projection count mismatch")
    if [row.get("path") for row in source_rows if type(row) is dict] \
            != sorted(row.get("path") for row in source_rows if type(row) is dict):
        raise RuntimeError("wheel-build source projection is not canonical")
    for index, row in enumerate(source_rows):
        exact_keys(row, {"path", "bytes", "sha256"}, f"build source row {index}")
        _one_provenance_suffix(
            files, f"source/{row['path']}",
            expected_bytes=exact_int(row["bytes"], "build source bytes"),
            expected_sha=_verify_digest(row["sha256"], "build source SHA"),
            label=f"build source {row['path']}",
        )
    headers = build["optix_headers"]
    exact_keys(headers, {"commit", "tree", "api_macro", "root"}, "build OptiX headers")
    if (headers["commit"] != "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
            or headers["tree"] != "c30f1b41cb64f6cba6290d7ad82686cc84922267"
            or exact_int(headers["api_macro"], "OptiX API macro") != 90000):
        raise RuntimeError("build OptiX header authority mismatch")
    build_details = build["build"]
    required_build_keys = {
        "python", "python_version", "cmake_args", "pip", "scikit_build_core",
        "pybind11", "ninja", "cmake", "cxx", "nvcc", "command_file",
        "stdout_file", "stderr_file", "exit_code",
    }
    exact_keys(build_details, required_build_keys, "build toolchain receipt")
    if exact_int(build_details["exit_code"], "wheel build exit") != 0:
        raise RuntimeError("wheel build did not exit zero")
    for key in ("command_file", "stdout_file", "stderr_file"):
        suffix = exact_string(build_details[key], f"build {key}")
        matches = [
            name for name in files
            if name.startswith("provenance/") and name.endswith(f"/{suffix}")
        ]
        if len(matches) != 1:
            raise RuntimeError(f"build {key} is not archived exactly once")
    wheel = build["wheel"]
    exact_keys(wheel, {
        "path", "bytes", "sha256", "extension_member", "extension_bytes",
        "extension_sha256",
    }, "built wheel")
    _, wheel_bytes = _one_provenance_suffix(
        files, exact_string(wheel["path"], "built wheel path"),
        expected_bytes=exact_int(wheel["bytes"], "built wheel bytes", minimum=1),
        expected_sha=_verify_digest(wheel["sha256"], "built wheel SHA"),
        label="clean-built wheel",
    )
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as archive:
        member = exact_string(wheel["extension_member"], "wheel extension member")
        try:
            wheel_extension = archive.read(member)
        except KeyError as exc:
            raise RuntimeError("wheel extension member is absent") from exc
    if (len(wheel_extension) != exact_int(wheel["extension_bytes"],
                                          "wheel extension bytes", minimum=1)
            or sha256(wheel_extension) != _verify_digest(
                wheel["extension_sha256"], "wheel extension SHA")):
        raise RuntimeError("wheel extension bytes do not match build receipt")

    exact_keys(install, {
        "schema", "status", "transaction_kind", "registered_performance_timing_count",
        "python", "wheel", "loaded_optix_package_initializer", "loaded_optix_extension",
        "optix_api_version", "cupy_device_name", "numpy_version", "distributions",
        "install_report", "virtualenv_bootstrap_install_report", "pip_freeze",
    }, "clean-install receipt")
    if (install["schema"] != "rtdl.goal5800.pyoptix_clean_install_receipt.v1"
            or install["status"] != "PASS__FRESH_VENV__CLEAN_BUILT_EXTENSION_LOADED__UNTIMED"
            or install["transaction_kind"] != "installation_and_import_not_performance"
            or type(install["registered_performance_timing_count"]) is not int
            or install["registered_performance_timing_count"] != 0
            or install["optix_api_version"] != "9.0.0"):
        raise RuntimeError("clean-install receipt status/schema/timing mismatch")
    install_wheel = install["wheel"]
    exact_keys(install_wheel, {"path", "bytes", "sha256"}, "installed wheel")
    if (install_wheel["bytes"] != len(wheel_bytes)
            or install_wheel["sha256"] != sha256(wheel_bytes)):
        raise RuntimeError("clean-built and installed wheel identities differ")
    install_extension = install["loaded_optix_extension"]
    exact_keys(install_extension, {"module", "path", "bytes", "sha256"},
               "clean-installed extension")
    loaded = result["loaded_optix_extension"]
    if (install_extension["module"] != "optix._optix"
            or install_extension["path"] != loaded["distribution_path"]
            or install_extension["bytes"] != loaded["bytes"]
            or install_extension["sha256"] != loaded["sha256"]
            or install_extension["sha256"] != sha256(wheel_extension)):
        raise RuntimeError("wheel/clean-install/executed extension chain diverges")
    expected_distributions = {
        "pyoptix": "9.1.0", "numpy": "2.4.4", "cupy-cuda12x": "14.0.1",
        "cuda-python": "12.9.7", "cuda-bindings": "12.9.7",
        "cuda-pathfinder": "1.6.1",
    }
    if type(install["distributions"]) is not dict \
            or set(install["distributions"]) != set(expected_distributions):
        raise RuntimeError("clean-install distribution set mismatch")
    for name, version in expected_distributions.items():
        row = install["distributions"][name]
        exact_keys(row, {"canonical_name", "version"}, f"installed {name}")
        if row["version"] != version:
            raise RuntimeError(f"installed distribution version mismatch: {name}")
    for key in ("install_report", "virtualenv_bootstrap_install_report", "pip_freeze"):
        row = install[key]
        exact_keys(row, {"path", "bytes", "sha256"}, f"clean install {key}")
        _one_provenance_suffix(
            files, row["path"], expected_bytes=exact_int(row["bytes"], f"{key} bytes"),
            expected_sha=_verify_digest(row["sha256"], f"{key} SHA"), label=key,
        )
    if (build_record["wheel_sha256"] != sha256(wheel_bytes)
            or install_record["wheel_sha256"] != sha256(wheel_bytes)
            or build_record["extension_sha256"] != sha256(wheel_extension)
            or install_record["extension_sha256"] != sha256(wheel_extension)):
        raise RuntimeError("result receipt projection does not match raw receipt chain")
    for label, row in (
        ("build wheel identity", build_record["wheel_identity"]),
        ("install wheel identity", install_record["wheel_identity"]),
    ):
        exact_keys(row, {"path", "bytes", "sha256"}, label)
        if row["bytes"] != len(wheel_bytes) or row["sha256"] != sha256(wheel_bytes):
            raise RuntimeError(f"{label} differs from archived clean-built wheel")
    installed_identity = install_record["extension_identity"]
    exact_keys(installed_identity, {"path", "bytes", "sha256"},
               "installed extension identity")
    if (installed_identity["path"] != install_extension["path"]
            or installed_identity["bytes"] != len(wheel_extension)
            or installed_identity["sha256"] != sha256(wheel_extension)):
        raise RuntimeError("installed extension projection differs from wheel/receipt")


def verify_build_projections(
    result: dict[str, Any], environment: dict[str, Any], files: dict[str, bytes],
    installed_rows: list[dict[str, Any]],
) -> None:
    build = result["pyoptix_install_provenance"]["wheel_build_receipt"]["document"]
    source_rows = build["pyoptix_source"]["archive_projection_files"]
    if type(source_rows) is not list:
        raise RuntimeError("postbuild source-tree projection must be a list")
    source_paths = []
    for index, row in enumerate(source_rows):
        exact_keys(row, {"path", "bytes", "sha256"},
                   f"postbuild source-tree row {index}")
        source_paths.append(exact_string(row["path"],
                                         f"postbuild source-tree path {index}"))
        exact_int(row["bytes"], f"postbuild source-tree bytes {index}")
        _verify_digest(row["sha256"], f"postbuild source-tree SHA {index}")
    if source_paths != sorted(set(source_paths)):
        raise RuntimeError("postbuild source-tree projection is not canonical and unique")

    projection = environment["pyoptix_build_projections"]
    if type(projection) is not dict:
        raise RuntimeError("PyOptiX build projections must be an object")
    exact_keys(projection, {
        "upstream_prebuild_source", "postbuild_generated_source_tree_files",
        "postbuild_complete_source_tree", "wheel_postbuild",
        "clean_installed_distribution", "projections_are_not_interchangeable",
    }, "PyOptiX build projections")
    prebuild = projection["upstream_prebuild_source"]
    exact_keys(prebuild, {
        "projection_kind", "file_count", "files_sha256", "files",
        "payload_bytes_embedded",
    }, "upstream prebuild source projection")
    prebuild_rows = prebuild["files"]
    if type(prebuild_rows) is not list:
        raise RuntimeError("upstream prebuild source rows must be a list")
    prebuild_paths = []
    for index, row in enumerate(prebuild_rows):
        exact_keys(row, {"path", "bytes", "sha256"},
                   f"upstream prebuild source row {index}")
        prebuild_paths.append(exact_string(
            row["path"], f"upstream prebuild source path {index}"))
        exact_int(row["bytes"], f"upstream prebuild source bytes {index}")
        _verify_digest(row["sha256"], f"upstream prebuild source SHA {index}")
    if prebuild_paths != sorted(set(prebuild_paths)) or len(prebuild_rows) != 42:
        raise RuntimeError("upstream prebuild source is not the exact 42-file Git projection")
    source_by_path = {row["path"]: row for row in source_rows}
    if any(source_by_path.get(row["path"]) != row for row in prebuild_rows):
        raise RuntimeError("postbuild source tree changed an upstream prebuild file")
    prebuild_path_set = set(prebuild_paths)
    generated_rows = [
        row for row in source_rows if row["path"] not in prebuild_path_set
    ]
    if len(prebuild_rows) + len(generated_rows) != len(source_rows):
        raise RuntimeError("prebuild/generated rows do not partition postbuild source tree")

    wheel = build["wheel"]
    _, wheel_bytes = _one_provenance_suffix(
        files, wheel["path"], expected_bytes=wheel["bytes"],
        expected_sha=wheel["sha256"], label="clean-built wheel projection",
    )
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as archive:
        wheel_rows = []
        for name in sorted(archive.namelist()):
            if name.endswith("/"):
                continue
            value = archive.read(name)
            wheel_rows.append(digest_row(name, value))
    if len(wheel_rows) != 7:
        raise RuntimeError("clean-built wheel is not the exact seven-member projection")
    if len(installed_rows) != 11:
        raise RuntimeError("clean-installed distribution is not the exact 11-file projection")
    expected = {
        "upstream_prebuild_source": {
            "projection_kind": "COMPLETE_PINNED_GIT_TREE",
            "file_count": len(prebuild_rows),
            "files_sha256": sha256(canonical(prebuild_rows)),
            "files": prebuild_rows,
            "payload_bytes_embedded": True,
        },
        "postbuild_generated_source_tree_files": {
            "projection_kind": (
                "SET_DIFFERENCE_POSTBUILD_RECEIPT_MINUS_PINNED_GIT_TREE"),
            "file_count": len(generated_rows),
            "files_sha256": sha256(canonical(generated_rows)),
            "files": generated_rows,
            "payload_bytes_embedded": True,
        },
        "postbuild_complete_source_tree": {
            "projection_kind": (
                "COMPLETE_BUILD_RECEIPT_SOURCE_TREE_AFTER_WHEEL_BUILD"),
            "file_count": len(source_rows),
            "files_sha256": sha256(canonical(source_rows)),
            "payload_bytes_embedded": True,
        },
        "wheel_postbuild": {
            "projection_kind": "COMPLETE_CLEAN_BUILT_WHEEL_REGULAR_MEMBERS",
            "file_count": len(wheel_rows),
            "files_sha256": sha256(canonical(wheel_rows)),
            "wheel_bytes_embedded": True,
        },
        "clean_installed_distribution": {
            "projection_kind": "COMPLETE_IMPORTLIB_METADATA_DISTRIBUTION_FILES",
            "file_count": len(installed_rows),
            "files_sha256": sha256(canonical(installed_rows)),
            "payload_bytes_embedded": True,
        },
        "projections_are_not_interchangeable": True,
    }
    if projection != expected:
        raise RuntimeError("PyOptiX build projections are absent, conflated, or overstated")


def verify_result(
    result: dict[str, Any], environment: dict[str, Any], files: dict[str, bytes],
    installed_rows: list[dict[str, Any]],
) -> int:
    exact_keys(result, {
        "schema", "status", "arm", "pyoptix_commit", "pyoptix_tree",
        "executed_source_authority",
        "pyoptix_source_authority_identity", "pyoptix_install_provenance",
        "pyoptix_distribution_version", "pyoptix_loaded_distribution_manifest",
        "loaded_optix_module_file", "loaded_optix_module_sha256",
        "loaded_optix_initializer_identity", "loaded_optix_extension",
        "loaded_shared_library_manifest", "operation_ledger", "execute_source_boundary",
        "device_failure_status_before_output_witness",
        "optix_api_version",
        "device_source_sha256", "ptx_sha256", "relation", "triangle",
        "prepared_owners_closed_after_repeat", "operation_ledger_scope",
        "registered_performance_timing_count", "performance_claimed",
        "optix_validation", "optix_validation_error_message_count",
    }, "result")
    expected = {
        "schema": RESULT_SCHEMA,
        "status": "PASS__UNTIMED_FUNCTIONAL",
        "arm": ARM,
        "pyoptix_commit": PYOPTIX_COMMIT,
        "pyoptix_tree": PYOPTIX_TREE,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "optix_validation": "PASS",
        "optix_validation_error_message_count": 0,
    }
    for key, value in expected.items():
        if type(result[key]) is not type(value) or result[key] != value:
            raise RuntimeError(f"result claim mismatch: {key}")
    if result["operation_ledger_scope"] != OPERATION_LEDGER_SCOPE:
        raise RuntimeError("top-level operation-ledger scope mismatch")
    if result["prepared_owners_closed_after_repeat"] is not True:
        raise RuntimeError("prepared owners were not closed after repeat")
    if result["optix_api_version"] != "9.0.0" \
            or result["pyoptix_distribution_version"] != "9.1.0":
        raise RuntimeError("PyOptiX/OptiX API version mismatch")
    _verify_digest(result["device_source_sha256"], "device source SHA")
    _verify_digest(result["ptx_sha256"], "PTX SHA")
    if result["pyoptix_loaded_distribution_manifest"]["files"] != installed_rows:
        raise RuntimeError("result installed-distribution manifest differs from archive")
    distribution_manifest = result["pyoptix_loaded_distribution_manifest"]
    exact_keys(distribution_manifest, {
        "distribution", "version", "file_count", "files_sha256", "files",
    }, "PyOptiX distribution manifest")
    if (distribution_manifest["distribution"] != "pyoptix"
            or distribution_manifest["version"] != "9.1.0"
            or exact_int(distribution_manifest["file_count"], "distribution file count")
            != len(installed_rows)
            or distribution_manifest["files_sha256"] != sha256(canonical(installed_rows))):
        raise RuntimeError("PyOptiX distribution manifest identity mismatch")
    initializer = result["loaded_optix_initializer_identity"]
    exact_keys(initializer, {"path", "bytes", "sha256"}, "OptiX initializer")
    init_payloads = [
        value for name, value in files.items()
        if name == "installed_distribution/optix/__init__.py"
    ]
    if (len(init_payloads) != 1
            or initializer["path"] != result["loaded_optix_module_file"]
            or initializer["sha256"] != result["loaded_optix_module_sha256"]
            or initializer["bytes"] != len(init_payloads[0])
            or initializer["sha256"] != sha256(init_payloads[0])):
        raise RuntimeError("OptiX initializer identity mismatch")
    relation = result["relation"]
    triangle = result["triangle"]
    if type(relation) is not dict or type(triangle) is not dict:
        raise RuntimeError("task result must be an object")
    relation_execution_keys = {
        "output", "raw_event_count", "device_status", "device_overflow", "launch_count",
        "required_sync_count", "control_d2h_bytes", "output_d2h_bytes",
        "rows_reset_bytes", "control_reset_bytes", "total_host_blocking_count",
        "operation_order", "prepare_operation_counts", "operation_ledger_scope",
        "execute_operation_counts", "independent_execute_guard",
    }
    triangle_execution_keys = {
        "per_ray", "weighted_sum", "device_status", "launch_count", "required_sync_count",
        "status_d2h_bytes", "per_ray_d2h_bytes", "weighted_d2h_bytes",
        "per_ray_reset_bytes", "weighted_reset_bytes", "status_reset_bytes",
        "total_host_blocking_count", "operation_order", "prepare_operation_counts",
        "operation_ledger_scope", "execute_operation_counts", "independent_execute_guard",
    }
    exact_keys(relation, relation_execution_keys | {
        "output_sha256", "same_prepared_owner_reused", "initial_repeat_exact",
        "initial_execution", "repeat_execution",
    }, "relation result")
    exact_keys(triangle, triangle_execution_keys | {
        "per_ray_sha256", "same_prepared_owner_reused", "initial_repeat_exact",
        "initial_execution", "repeat_execution",
    }, "triangle result")
    for task, row, execution_keys, digest_key, output_key in (
        ("relation", relation, relation_execution_keys, "output_sha256", "output"),
        ("triangle", triangle, triangle_execution_keys, "per_ray_sha256", "per_ray"),
    ):
        if row["same_prepared_owner_reused"] is not True \
                or row["initial_repeat_exact"] is not True:
            raise RuntimeError(f"{task} same-owner repeat claim mismatch")
        if {key: row[key] for key in execution_keys} != row["initial_execution"]:
            raise RuntimeError(f"{task} top-level execution is not its initial execution")
        if _verify_digest(row[digest_key], f"{task} output SHA") \
                != sha256(canonical(row[output_key])):
            raise RuntimeError(f"{task} output digest mismatch")
    shared = result["loaded_shared_library_manifest"]
    exact_keys(shared, {
        "source", "address_fields_recorded", "shared_object_count",
        "rows_sha256", "rows",
    }, "loaded shared-library manifest")
    if shared["source"] != "/proc/self/maps" \
            or shared["address_fields_recorded"] is not False \
            or exact_int(shared["shared_object_count"], "loaded SO count", minimum=1) \
            != len(shared["rows"]) \
            or _verify_digest(shared["rows_sha256"], "loaded SO rows SHA") \
            != sha256(canonical(shared["rows"])):
        raise RuntimeError("loaded shared-library manifest mismatch")
    process_projection = sorted(
        ({"path": row["resolved_path"], "bytes": row["bytes"], "sha256": row["sha256"]}
         for row in environment["dynamic_dependencies"]["rows"]
         if row["observation"] == "PROCESS_MAP" and row["resolved_path"] is not None),
        key=lambda row: row["path"],
    )
    if shared["rows"] != process_projection:
        raise RuntimeError("result process-map manifest differs from frozen environment")
    verify_loaded_extension(result, files, installed_rows, environment)
    verify_execution_authority(result, files, environment)
    verify_receipt_chain(result, files)
    verify_build_projections(result, environment, files, installed_rows)
    install_document = result["pyoptix_install_provenance"][
        "clean_install_receipt"]["document"]
    python_role = environment["python_runtime"]["executable_identity_role"]
    python_rows = [
        row for row in environment["runtime_identity_files"] if row["role"] == python_role
    ]
    if (len(python_rows) != 1
            or python_rows[0]["source_path"] != install_document["python"]["executable"]
            or environment["python_runtime"]["version"]
            != install_document["python"]["version"]):
        raise RuntimeError("executed sys.executable differs from clean-install identity")
    if environment["gpu"]["name"] != install_document["cupy_device_name"]:
        raise RuntimeError("CuPy and nvidia-smi GPU identities differ")
    return verify_operation_ledger(result, files)


def verify(path: Path) -> dict[str, Any]:
    files = read_archive(path)
    manifest = load_json(files["MANIFEST.json"], "manifest")
    installed_rows, executed_rows, runtime_rows, provenance_rows = verify_manifest(files, manifest)
    environment = load_json(files["environment.json"], "environment")
    verify_runtime_identities(files, environment, installed_rows, executed_rows, runtime_rows)
    result = load_json(files["idiomatic_pyoptix_untimed.json"], "result")
    execution_projection_count = verify_result(result, environment, files, installed_rows)
    system_rows = [
        row for row in environment["dynamic_dependencies"]["rows"]
        if row["classification"] == "RESOLVED_SYSTEM_IDENTITY_ONLY"
    ]
    return {
        "status": "PASS",
        "archive_sha256": sha256(path.read_bytes()),
        "loaded_optix_extension_sha256": result["loaded_optix_extension"]["sha256"],
        "distribution_file_count": len(installed_rows),
        "executed_source_file_count": len(executed_rows),
        "runtime_identity_file_count": len(runtime_rows),
        "operation_execution_projection_count": execution_projection_count,
        "provenance_file_count": len(provenance_rows),
        "system_dependency_identity_only_count": len(system_rows),
        "system_dependency_bytes_embedded": False,
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive), sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Freeze Goal5800 PyOptiX v2 identity and untimed operation evidence."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
from typing import Any
import zipfile


MANIFEST_SCHEMA = "rtdl.goal5800.pyoptix_idiomatic_evidence_manifest.v2"
ENVIRONMENT_SCHEMA = "rtdl.goal5800.pyoptix_idiomatic_environment.v2"
REQUIRED_IMPORTS = ("optix", "cupy", "numpy", "cuda")
REQUIRED_MAP_ROLES = (
    "cupy_core", "cuda_driver", "cuda_runtime", "nvrtc", "optix_driver",
)
REQUIRED_EXECUTED_SOURCE_PATHS = (
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def json_bytes(value: object) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if type(value) is not dict:
        raise RuntimeError(f"JSON object required: {path}")
    return value


def digest_row(path: str, value: bytes) -> dict[str, Any]:
    return {"path": path, "bytes": len(value), "sha256": sha256(value)}


def run(*arguments: str) -> bytes:
    completed = subprocess.run(
        list(arguments), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return completed.stdout


def add_bytes(
    archive: tarfile.TarFile, name: str, value: bytes, mode: int = 0o644,
) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(value))


def safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (not normalized or normalized.startswith(("/", "./"))
            or ".." in parts or "" in parts):
        raise RuntimeError(f"unsafe evidence-relative path: {value}")
    return normalized


def copy_tree_projection(
    payloads: dict[str, bytes], root: Path, archive_prefix: str,
    *, exclude_caches: bool = False,
) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if exclude_caches and ("__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}):
            continue
        relative = path.relative_to(root).as_posix()
        value = path.read_bytes()
        name = f"{archive_prefix}/{relative}"
        if name in payloads:
            raise RuntimeError(f"duplicate evidence payload: {name}")
        payloads[name] = value
        rows.append(digest_row(relative, value))
    if not rows:
        raise RuntimeError(f"empty source projection: {root}")
    return rows


def distribution_probe(clean_python: Path) -> dict[str, Any]:
    program = r'''
import importlib.metadata as m
import json
from pathlib import Path
mapping = m.packages_distributions()
result = {}
for imported in ("optix", "cupy", "numpy", "cuda"):
    names = sorted(set(mapping.get(imported, ())), key=str.casefold)
    details = []
    for name in names:
        distribution = m.distribution(name)
        root = Path(distribution._path)
        details.append({
            "name": name,
            "version": distribution.version,
            "metadata_path": str((root / "METADATA").resolve(strict=True)),
            "record_path": str((root / "RECORD").resolve(strict=True)),
        })
    result[imported] = {"names": names, "details": details}
print(json.dumps(result, sort_keys=True))
'''
    value = json.loads(run(str(clean_python), "-c", program))
    if type(value) is not dict or set(value) != set(REQUIRED_IMPORTS):
        raise RuntimeError("clean-environment package/distribution probe failed")
    return value


def system_library(path: Path) -> bool:
    text = str(path)
    return text.startswith(("/lib/", "/lib64/", "/usr/lib/", "/usr/lib64/"))


def classify_loaded_role(path: Path, extension: Path) -> str | None:
    text = str(path)
    name = path.name
    if path == extension:
        return "optix_extension"
    if "/cupy/_core/" in text and name.startswith("core.") and name.endswith(".so"):
        return "cupy_core"
    if re.match(r"libcuda\.so(?:\.|$)", name):
        return "cuda_driver"
    if name.startswith("libcudart.so"):
        return "cuda_runtime"
    if re.match(r"libnvrtc\.so(?:\.|$)", name):
        return "nvrtc"
    if name.startswith("libnvoptix.so"):
        return "optix_driver"
    return None


def parse_ldd(raw: bytes) -> list[Path]:
    paths: set[Path] = set()
    for line in raw.decode("utf-8", errors="strict").splitlines():
        match = re.search(r"(?:=>\s+)?(/[^\s]+)", line)
        if match is None:
            continue
        path = Path(match.group(1)).resolve(strict=True)
        if path.is_file():
            paths.add(path)
    return sorted(paths, key=str)


def build(args: argparse.Namespace) -> bytes:
    result_bytes = args.result.resolve(strict=True).read_bytes()
    result = json.loads(result_bytes)
    if (type(result) is not dict
            or result.get("schema") != "rtdl.goal5800.pyoptix_idiomatic_arm.result.v2"
            or result.get("status") != "PASS__UNTIMED_FUNCTIONAL"
            or type(result.get("registered_performance_timing_count")) is not int
            or result["registered_performance_timing_count"] != 0):
        raise RuntimeError("v2 untimed PyOptiX result is not closeable")
    payloads: dict[str, bytes] = {}

    execution_authority_path = args.execution_authority.resolve(strict=True)
    execution_authority_bytes = execution_authority_path.read_bytes()
    execution_authority = json.loads(execution_authority_bytes)
    if (execution_authority != result["executed_source_authority"]["document"]
            or len(execution_authority_bytes)
            != result["executed_source_authority"]["file"]["bytes"]
            or sha256(execution_authority_bytes)
            != result["executed_source_authority"]["file"]["sha256"]):
        raise RuntimeError("result/preexecution source authority mismatch")
    if (execution_authority.get("schema")
            != "rtdl.goal5800.pyoptix_execution_authority.v2"
            or execution_authority.get("status")
            != "FROZEN__PREEXECUTION_SOURCE_AUTHORITY"
            or execution_authority.get("capture_phase")
            != "BEFORE_PYOPTIX_CUPY_IMPORT_OR_CUDA_OPTIX_INITIALIZATION"
            or execution_authority.get("registered_performance_timing_count") != 0
            or set(execution_authority) != {
                "schema", "status", "capture_phase", "origin_repository_commit",
                "origin_repository_tree", "git_membership_proof",
                "file_count", "files", "files_sha256",
                "registered_performance_timing_count",
            }
            or any(type(execution_authority.get(key)) is not str
                   or re.fullmatch(r"[0-9a-f]{40}", execution_authority[key]) is None
                   for key in ("origin_repository_commit", "origin_repository_tree"))
            or [row.get("path") for row in execution_authority.get("files", [])]
            != list(REQUIRED_EXECUTED_SOURCE_PATHS)
            or execution_authority.get("files_sha256")
            != sha256(canonical(execution_authority.get("files", [])))):
        raise RuntimeError("preexecution source authority is invalid")
    executed_rows = execution_authority["files"]
    executed_payload_rows = [
        {"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in executed_rows
    ]
    source_root = args.source_root.resolve(strict=True)
    for row in executed_rows:
        relative = safe_relative(row["path"])
        value = (source_root / relative).resolve(strict=True).read_bytes()
        if len(value) != row["bytes"] or sha256(value) != row["sha256"]:
            raise RuntimeError(f"executed source drift after authority freeze: {relative}")
        payloads[f"executed_source/{relative}"] = value
    payloads["provenance/execution_authority.json"] = execution_authority_bytes
    execution_pin_path = args.execution_pin.resolve(strict=True)
    execution_pin_bytes = execution_pin_path.read_bytes()
    execution_pin = json.loads(execution_pin_bytes)
    result_pin = result["executed_source_authority"].get("launch_pin")
    if (type(result_pin) is not dict
            or execution_pin != result_pin.get("document")
            or len(execution_pin_bytes) != result_pin.get("file", {}).get("bytes")
            or sha256(execution_pin_bytes) != result_pin.get("file", {}).get("sha256")
            or execution_pin.get("schema")
            != "rtdl.goal5800.pyoptix_execution_launch_pin.v1"
            or execution_pin.get("authority", {}).get("bytes")
            != len(execution_authority_bytes)
            or execution_pin.get("authority", {}).get("sha256")
            != sha256(execution_authority_bytes)
            or execution_pin.get("origin_repository_commit")
            != execution_authority["origin_repository_commit"]
            or execution_pin.get("origin_repository_tree")
            != execution_authority["origin_repository_tree"]
            or execution_pin.get("changed_expected_allowed") is not False
            or execution_pin.get("registered_performance_timing_count") != 0):
        raise RuntimeError("result/separate execution launch pin mismatch")
    payloads["provenance/execution_launch_pin.json"] = execution_pin_bytes
    build_root = args.clean_build_root.resolve(strict=True)
    install_root = args.clean_install_root.resolve(strict=True)
    build_receipt_path = build_root / "build_receipt.json"
    install_receipt_path = install_root / "clean_install_receipt.json"
    build_receipt = load_json(build_receipt_path)
    install_receipt = load_json(install_receipt_path)
    if Path(build_receipt["optix_headers"]["root"]).resolve(strict=True) \
            != args.optix_header_root.resolve(strict=True):
        raise RuntimeError("clean-build receipt used a different OptiX header root")
    result_provenance = result["pyoptix_install_provenance"]
    if (build_receipt != result_provenance["wheel_build_receipt"]["document"]
            or install_receipt != result_provenance["clean_install_receipt"]["document"]):
        raise RuntimeError("result provenance documents differ from clean roots")

    # Carry the exact clean build source, wheel, logs, and receipt.
    source_rows = build_receipt["pyoptix_source"]["archive_projection_files"]
    if len({row["path"] for row in source_rows}) != len(source_rows):
        raise RuntimeError("clean-build source projection contains duplicate paths")
    for row in source_rows:
        relative = safe_relative(row["path"])
        path = build_root / "source" / relative
        value = path.resolve(strict=True).read_bytes()
        if len(value) != row["bytes"] or sha256(value) != row["sha256"]:
            raise RuntimeError(f"clean-build source drift: {relative}")
        payloads[f"provenance/clean_build/source/{relative}"] = value
    pyoptix_root = args.pyoptix_source_root.resolve(strict=True)
    prebuild_paths = run(
        "git", "-C", str(pyoptix_root), "ls-tree", "-r", "--name-only", "HEAD",
    ).decode("utf-8").splitlines()
    if prebuild_paths != sorted(set(prebuild_paths)) or len(prebuild_paths) != 42:
        raise RuntimeError("pinned PyOptiX Git tree is not the exact 42-file projection")
    source_by_path = {row["path"]: row for row in source_rows}
    prebuild_rows = []
    for relative in prebuild_paths:
        value = run("git", "-C", str(pyoptix_root), "show", f"HEAD:{relative}")
        row = digest_row(relative, value)
        if source_by_path.get(relative) != row:
            raise RuntimeError(
                f"postbuild source tree changed a pinned prebuild file: {relative}")
        prebuild_rows.append(row)
    generated_rows = [
        row for row in source_rows if row["path"] not in set(prebuild_paths)
    ]
    if len(prebuild_rows) + len(generated_rows) != len(source_rows):
        raise RuntimeError("prebuild/generated source projections do not partition receipt")
    for key in ("command_file", "stdout_file", "stderr_file"):
        relative = safe_relative(build_receipt["build"][key])
        payloads[f"provenance/clean_build/{relative}"] = (
            build_root / relative).resolve(strict=True).read_bytes()
    wheel_relative = safe_relative(build_receipt["wheel"]["path"])
    wheel_bytes = (build_root / wheel_relative).resolve(strict=True).read_bytes()
    if (len(wheel_bytes) != build_receipt["wheel"]["bytes"]
            or sha256(wheel_bytes) != build_receipt["wheel"]["sha256"]):
        raise RuntimeError("clean-built wheel drift")
    payloads[f"provenance/clean_build/{wheel_relative}"] = wheel_bytes
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as wheel_archive:
        wheel_rows = []
        for name in sorted(wheel_archive.namelist()):
            if name.endswith("/"):
                continue
            value = wheel_archive.read(name)
            wheel_rows.append(digest_row(name, value))
    if len(wheel_rows) != 7:
        raise RuntimeError("clean-built wheel no longer has the exact seven regular members")
    payloads["provenance/clean_build/build_receipt.json"] = build_receipt_path.read_bytes()
    for key in ("install_report", "virtualenv_bootstrap_install_report", "pip_freeze"):
        relative = safe_relative(install_receipt[key]["path"])
        value = (install_root / relative).resolve(strict=True).read_bytes()
        if len(value) != install_receipt[key]["bytes"] \
                or sha256(value) != install_receipt[key]["sha256"]:
            raise RuntimeError(f"clean-install provenance drift: {key}")
        payloads[f"provenance/clean_install/{relative}"] = value
    payloads["provenance/clean_install/clean_install_receipt.json"] = (
        install_receipt_path.read_bytes())

    extension = result["loaded_optix_extension"]
    extension_path = Path(extension["distribution_path"]).resolve(strict=True)
    extension_relative = safe_relative(extension["source_path"])
    site_packages = extension_path
    for _ in extension_relative.split("/"):
        site_packages = site_packages.parent
    installed_rows = result["pyoptix_loaded_distribution_manifest"]["files"]
    if len(installed_rows) != 11:
        raise RuntimeError("expected 11-file clean-installed PyOptiX projection")
    for row in installed_rows:
        relative = safe_relative(row["path"])
        value = (site_packages / relative).resolve(strict=True).read_bytes()
        if len(value) != row["bytes"] or sha256(value) != row["sha256"]:
            raise RuntimeError(f"installed PyOptiX distribution drift: {relative}")
        payloads[f"installed_distribution/{relative}"] = value

    runtime_rows_by_role: dict[str, dict[str, Any]] = {}
    runtime_role_by_identity: dict[tuple[str, str], str] = {}

    def add_identity(
        role: str, path: Path, *, value: bytes | None = None,
        source_label: str | None = None,
    ) -> str:
        resolved = path.resolve(strict=True)
        body = resolved.read_bytes() if value is None else value
        existing = runtime_rows_by_role.get(role)
        if existing is not None:
            if existing["sha256"] != sha256(body):
                raise RuntimeError(f"runtime identity role drift: {role}")
            return role
        safe_role = re.sub(r"[^A-Za-z0-9_.-]+", "_", role)
        leaf = re.sub(r"[^A-Za-z0-9_.-]+", "_", resolved.name or "payload")
        archive_path = f"runtime_identity/{safe_role}/{leaf}"
        if archive_path in payloads:
            raise RuntimeError(f"runtime payload collision: {archive_path}")
        payloads[archive_path] = body
        row = {
            "role": role,
            "archive_path": archive_path,
            "source_path": source_label or str(resolved),
            "bytes": len(body),
            "sha256": sha256(body),
        }
        runtime_rows_by_role[role] = row
        if source_label is None:
            runtime_role_by_identity[(str(resolved), row["sha256"])] = role
        return role

    clean_python = Path(install_receipt["python"]["executable"]).resolve(strict=True)
    add_identity("python.executable", clean_python)
    distribution_data = distribution_probe(clean_python)
    environment_distributions = []
    for imported in REQUIRED_IMPORTS:
        probed = distribution_data[imported]
        details = []
        for detail in probed["details"]:
            normalized = detail["name"].casefold().replace("_", "-")
            metadata_role = add_identity(
                f"distribution.{normalized}.metadata", Path(detail["metadata_path"]))
            record_role = add_identity(
                f"distribution.{normalized}.record", Path(detail["record_path"]))
            details.append({
                "name": detail["name"], "version": detail["version"],
                "metadata_identity_role": metadata_role,
                "record_identity_role": record_role,
            })
        environment_distributions.append({
            "import_name": imported,
            "detection": "importlib.metadata.packages_distributions",
            "distribution_names": probed["names"],
            "distributions": details,
        })

    header_root = args.optix_header_root.resolve(strict=True)
    header_roles = [
        add_identity("optix_sdk.header.optix", header_root / "include" / "optix.h"),
        add_identity(
            "optix_sdk.header.optix_device", header_root / "include" / "optix_device.h"),
    ]
    shared_rows = result["loaded_shared_library_manifest"]["rows"]
    shared_paths = [Path(row["path"]).resolve(strict=True) for row in shared_rows]
    if [str(path) for path in shared_paths] != [row["path"] for row in shared_rows]:
        raise RuntimeError("result shared-library paths are not already resolved")
    role_paths: dict[str, Path] = {}
    for path in shared_paths:
        role = classify_loaded_role(path, extension_path)
        if role is not None:
            if role in role_paths:
                raise RuntimeError(f"multiple loaded libraries match required role: {role}")
            role_paths[role] = path
    missing_roles = set(REQUIRED_MAP_ROLES) - set(role_paths)
    if missing_roles:
        raise RuntimeError(f"required post-launch mappings absent: {sorted(missing_roles)}")
    canonical_roles = {
        "cuda_driver": "toolchain.cuda_driver.library",
        "nvrtc": "toolchain.nvrtc.library",
    }
    for role, path in role_paths.items():
        add_identity(canonical_roles.get(role, f"runtime.{role}"), path)

    ldd_raw = run("ldd", str(extension_path))
    ldd_role = add_identity(
        "dynamic.ldd.raw", extension_path, value=ldd_raw,
        source_label=f"ldd {extension_path}",
    )
    normalized_maps = json_bytes({
        "schema": "rtdl.goal5800.normalized_process_maps_projection.v1",
        "source": "/proc/self/maps",
        "address_fields_recorded": False,
        "rows": shared_rows,
    })
    maps_role = add_identity(
        "dynamic.process_maps.normalized_projection", extension_path,
        value=normalized_maps,
        source_label="/proc/self/maps__ADDRESS_FREE_NORMALIZED_PROJECTION",
    )
    dynamic_rows = []

    def dependency_row(observation: str, path: Path) -> dict[str, Any]:
        logical_role = classify_loaded_role(path, extension_path)
        body = path.read_bytes()
        key = (str(path), sha256(body))
        must_capture = logical_role is not None or not system_library(path)
        identity_role = runtime_role_by_identity.get(key)
        if must_capture and identity_role is None:
            identity_role = add_identity(
                f"dynamic.loaded.{sha256(body)[:16]}", path, value=body)
        return {
            "observation": observation,
            "logical_role": logical_role,
            "soname": path.name,
            "classification": (
                "CAPTURED_NON_SYSTEM_OR_CUDA_OPTIX" if must_capture
                else "RESOLVED_SYSTEM_IDENTITY_ONLY"),
            "resolved_path": str(path),
            "bytes": len(body),
            "sha256": sha256(body),
            "identity_role": identity_role if must_capture else None,
        }

    dynamic_rows.extend(dependency_row("LDD", path) for path in parse_ldd(ldd_raw))
    dynamic_rows.extend(dependency_row("PROCESS_MAP", path) for path in shared_paths)
    dynamic_rows.sort(key=lambda row: (
        row["observation"], row["soname"], row["resolved_path"] or ""))
    if len({(row["observation"], row["soname"], row["resolved_path"])
            for row in dynamic_rows}) != len(dynamic_rows):
        raise RuntimeError("duplicate dynamic dependency observations")

    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        raise RuntimeError("nvidia-smi is unavailable")
    gpu_query = run(
        nvidia_smi, "--query-gpu=name,compute_cap,driver_version",
        "--format=csv,noheader",
    )
    gpu_lines = gpu_query.decode("utf-8").strip().splitlines()
    if len(gpu_lines) != 1 or len(gpu_lines[0].split(", ")) != 3:
        raise RuntimeError("exactly one GPU identity row is required")
    gpu_name, compute_capability, driver_version = gpu_lines[0].split(", ")
    gpu_query_role = add_identity(
        "environment.gpu_query.raw", Path(nvidia_smi), value=gpu_query,
        source_label=(
            "nvidia-smi --query-gpu=name,compute_cap,driver_version "
            "--format=csv,noheader"),
    )
    nvidia_smi_role = add_identity(
        "environment.nvidia_smi.executable", Path(nvidia_smi))
    nvrtc_version = run(
        str(clean_python), "-c",
        "import cupy as c; print('.'.join(map(str,c.cuda.nvrtc.getVersion())))",
    ).decode("utf-8").strip()
    environment = {
        "schema": ENVIRONMENT_SCHEMA,
        "python_runtime": {
            "implementation": "CPython",
            "version": install_receipt["python"]["version"],
            "executable_identity_role": "python.executable",
        },
        "python_distributions": environment_distributions,
        "gpu": {
            "name": gpu_name,
            "compute_capability": compute_capability,
            "driver_version": driver_version,
            "query_identity_role": gpu_query_role,
            "nvidia_smi_identity_role": nvidia_smi_role,
        },
        "toolchain": {
            "nvrtc": {
                "version": nvrtc_version,
                "library_identity_role": "toolchain.nvrtc.library",
            },
            "cuda_driver": {
                "version": driver_version,
                "library_identity_role": "toolchain.cuda_driver.library",
            },
            "optix_sdk": {
                "version": "9.0.0", "header_identity_roles": header_roles,
            },
        },
        "dynamic_dependencies": {
            "subject_sha256": extension["sha256"],
            "raw_ldd_identity_role": ldd_role,
            "normalized_process_maps_identity_role": maps_role,
            "rows": dynamic_rows,
            "required_process_map_roles": list(REQUIRED_MAP_ROLES),
        },
        "executed_sources": executed_payload_rows,
        "pyoptix_build_projections": {
            "upstream_prebuild_source": {
                "projection_kind": "COMPLETE_PINNED_GIT_TREE",
                "file_count": len(prebuild_rows),
                "files_sha256": sha256(canonical(prebuild_rows)),
                "files": prebuild_rows,
                "payload_bytes_embedded": True,
            },
            "postbuild_generated_source_tree_files": {
                "projection_kind": "SET_DIFFERENCE_POSTBUILD_RECEIPT_MINUS_PINNED_GIT_TREE",
                "file_count": len(generated_rows),
                "files_sha256": sha256(canonical(generated_rows)),
                "files": generated_rows,
                "payload_bytes_embedded": True,
            },
            "postbuild_complete_source_tree": {
                "projection_kind": "COMPLETE_BUILD_RECEIPT_SOURCE_TREE_AFTER_WHEEL_BUILD",
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
        },
        "runtime_identity_files": sorted(
            runtime_rows_by_role.values(), key=lambda row: row["archive_path"]),
        "identity_ceiling": {
            "self_contained_for": (
                "ACTUALLY_LOADED_OPTIX_EXTENSION_AND_CAPTURED_NON_SYSTEM_RUNTIME_BYTES"),
            "not_self_contained_for": (
                "SYSTEM_LIBC_LIBSTDCXX_AND_KERNEL_DRIVER_REEXECUTION"),
            "system_dependency_bytes_embedded": False,
        },
    }
    environment_bytes = json_bytes(environment)
    payloads["idiomatic_pyoptix_untimed.json"] = result_bytes
    payloads["environment.json"] = environment_bytes

    def family_rows(prefix: str) -> list[dict[str, Any]]:
        return [
            digest_row(name.removeprefix(prefix), value)
            for name, value in sorted(payloads.items()) if name.startswith(prefix)
        ]

    installed_archive_rows = family_rows("installed_distribution/")
    executed_archive_rows = family_rows("executed_source/")
    runtime_archive_rows = family_rows("runtime_identity/")
    provenance_archive_rows = family_rows("provenance/")
    if (installed_archive_rows != installed_rows
            or executed_archive_rows != executed_payload_rows):
        raise RuntimeError("archive source/distribution projection mismatch")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "result": {"bytes": len(result_bytes), "sha256": sha256(result_bytes)},
        "environment": {
            "bytes": len(environment_bytes), "sha256": sha256(environment_bytes),
        },
        "installed_distribution_file_count": len(installed_archive_rows),
        "installed_distribution_files_sha256": sha256(canonical(installed_archive_rows)),
        "executed_source_file_count": len(executed_archive_rows),
        "executed_source_files_sha256": sha256(canonical(executed_archive_rows)),
        "runtime_identity_file_count": len(runtime_archive_rows),
        "runtime_identity_files_sha256": sha256(canonical(runtime_archive_rows)),
        "provenance_file_count": len(provenance_archive_rows),
        "provenance_files_sha256": sha256(canonical(provenance_archive_rows)),
        "registered_performance_timing_count": 0,
    }
    payloads["MANIFEST.json"] = json_bytes(manifest)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, value in sorted(payloads.items()):
            add_bytes(archive, name, value)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    return compressed.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--pyoptix-source-root", type=Path, required=True)
    parser.add_argument("--optix-header-root", type=Path, required=True)
    parser.add_argument("--clean-build-root", type=Path, required=True)
    parser.add_argument("--clean-install-root", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--execution-pin", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    pyoptix_root = args.pyoptix_source_root.resolve(strict=True)
    commit = run("git", "-C", str(pyoptix_root), "rev-parse", "HEAD").decode().strip()
    tree = run("git", "-C", str(pyoptix_root), "rev-parse", "HEAD^{tree}").decode().strip()
    status = run(
        "git", "-C", str(pyoptix_root), "status", "--porcelain=v1",
        "--untracked-files=all",
    ).decode()
    if (commit != "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
            or tree != "0bf0ec24efb4a43f129aee25dd265aa8149374e3" or status):
        raise RuntimeError("PyOptiX source root is not the pinned clean authority")
    header_root = args.optix_header_root.resolve(strict=True)
    header_commit = run(
        "git", "-C", str(header_root), "rev-parse", "HEAD").decode().strip()
    header_tree = run(
        "git", "-C", str(header_root), "rev-parse", "HEAD^{tree}").decode().strip()
    header_status = run(
        "git", "-C", str(header_root), "status", "--porcelain=v1",
        "--untracked-files=all",
    ).decode()
    if (header_commit != "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
            or header_tree != "c30f1b41cb64f6cba6290d7ad82686cc84922267"
            or header_status):
        raise RuntimeError("OptiX header root is not the pinned clean authority")
    if "#define OPTIX_VERSION 90000" not in (
            header_root / "include" / "optix.h").read_text(encoding="utf-8"):
        raise RuntimeError("OptiX header root does not declare API 9.0.0")
    value = build(args)
    args.output.write_bytes(value)
    print(json.dumps({
        "status": "PASS__V2_EVIDENCE_FROZEN__UNTIMED",
        "output": str(args.output), "bytes": len(value), "sha256": sha256(value),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

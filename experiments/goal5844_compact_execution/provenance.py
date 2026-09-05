"""Portable provenance and archive checks for Goal5844 engineering evidence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tarfile
import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from experiments.goal5798_premeasurement.compatibility import (
    PYOPTIX_COMMIT,
    PYOPTIX_REPOSITORY,
    PYOPTIX_TREE,
    frozen_registry,
)

PYOPTIX_BUILD_SCHEMA = "rtdl.goal5844.pyoptix_clean_build_install.v1"
PYOPTIX_BUILD_STATUS = "PASS__CLEAN_SOURCE_WHEEL_AND_LOADED_EXTENSION_BOUND"
EVIDENCE_MANIFEST_SCHEMA = "rtdl.goal5844.engineering_evidence_manifest.v1"
EVIDENCE_MANIFEST_NAME = "EVIDENCE_MANIFEST.json"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
REQUIRED_DEPENDENCIES = {
    "cmake": "3.31.6",
    "cuda-bindings": "12.9.7",
    "cuda-pathfinder": "1.6.1",
    "cuda-python": "12.9.7",
    "cupy-cuda12x": "14.0.1",
    "llvmlite": "0.47.0",
    "ninja": "1.13.0",
    "numba": "0.65.1",
    "numpy": "2.4.4",
    "nvidia-ml-py": "13.580.82",
    "packaging": "26.3",
    "pathspec": "1.1.1",
    "pillow": "10.2.0",
    "pybind11": "3.1.0",
    "scikit-build-core": "1.0.3",
    "wheel": "0.45.1",
}
REQUIRED_RUNTIME_DEPENDENCIES = {
    **REQUIRED_DEPENDENCIES,
    "pip": "26.2.1",
}


class Goal5844EvidenceError(RuntimeError):
    """Raised when Goal5844 evidence is incomplete, unsafe, or inconsistent."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def write_json_create(path: Path, value: Mapping[str, object]) -> None:
    destination = path.absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        payload = (
            json.dumps(
                value,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
            + b"\n"
        )
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise Goal5844EvidenceError(f"{label} is absent or symbolic")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise Goal5844EvidenceError(f"{label} is not readable JSON") from error
    if not isinstance(value, dict):
        raise Goal5844EvidenceError(f"{label} must be a JSON object")
    return value


def _safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise Goal5844EvidenceError(f"{label} path is absent")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise Goal5844EvidenceError(f"{label} path is unsafe")
    return path


def file_record(path: Path, root: Path) -> dict[str, object]:
    resolved_root = root.resolve(strict=True)
    resolved = path.resolve(strict=True)
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as error:
        raise Goal5844EvidenceError("evidence payload lies outside its root") from error
    if path.is_symlink() or not stat.S_ISREG(resolved.stat().st_mode):
        raise Goal5844EvidenceError(f"evidence payload is not a regular file: {path}")
    return {
        "path": relative.as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def validate_file_record(
    root: Path, value: object, label: str
) -> tuple[Path, dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise Goal5844EvidenceError(f"{label} file record differs")
    relative = _safe_relative(value.get("path"), label)
    path = root / relative
    resolved_root = root.resolve(strict=True)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as error:
        raise Goal5844EvidenceError(
            f"{label} payload escapes its evidence root"
        ) from error
    cursor = path
    while cursor != root:
        if cursor.is_symlink():
            raise Goal5844EvidenceError(f"{label} payload uses a symbolic path")
        cursor = cursor.parent
    if not resolved.is_file():
        raise Goal5844EvidenceError(f"{label} payload is absent or symbolic")
    if (
        type(value.get("bytes")) is not int
        or value["bytes"] < 0
        or resolved.stat().st_size != value["bytes"]
        or not isinstance(value.get("sha256"), str)
        or HEX64.fullmatch(str(value["sha256"])) is None
        or sha256_file(resolved) != value["sha256"]
    ):
        raise Goal5844EvidenceError(f"{label} payload identity differs")
    return resolved, value


def _api_macro(api: str) -> int:
    try:
        major, minor, patch = (int(part) for part in api.split("."))
    except (TypeError, ValueError) as error:
        raise Goal5844EvidenceError("OptiX API version is malformed") from error
    return major * 10_000 + minor * 100 + patch


def _selected_stack(api: str) -> dict[str, Any]:
    rows = [row for row in frozen_registry() if row["optix_api_version"] == api]
    if len(rows) != 1:
        raise Goal5844EvidenceError(
            "OptiX API is outside the frozen compatibility registry"
        )
    return rows[0]


def _validate_git_archive(
    path: Path,
    *,
    expected_commit: str,
    label: str,
    required_members: tuple[str, ...] = (),
) -> dict[str, bytes]:
    try:
        with tarfile.open(path, "r:") as archive:
            if archive.pax_headers.get("comment") != expected_commit:
                raise Goal5844EvidenceError(f"{label} Git commit annotation differs")
            members: dict[str, tarfile.TarInfo] = {}
            for member in archive.getmembers():
                candidate = Path(member.name)
                canonical = candidate.as_posix().rstrip("/")
                if (
                    candidate.is_absolute()
                    or ".." in candidate.parts
                    or not canonical
                    or canonical == "."
                    or canonical != member.name.rstrip("/")
                    or member.issym()
                    or member.islnk()
                    or not (member.isfile() or member.isdir())
                    or canonical in members
                ):
                    raise Goal5844EvidenceError(f"{label} contains an unsafe member")
                members[canonical] = member
            payloads: dict[str, bytes] = {}
            for member_name in required_members:
                member = members.get(member_name)
                if member is None or not member.isfile():
                    raise Goal5844EvidenceError(
                        f"{label} required member is absent: {member_name}"
                    )
                stream = archive.extractfile(member)
                if stream is None:
                    raise Goal5844EvidenceError(
                        f"{label} required member is unreadable: {member_name}"
                    )
                payloads[member_name] = stream.read()
            return payloads
    except (OSError, tarfile.TarError) as error:
        raise Goal5844EvidenceError(f"{label} is not a readable Git archive") from error


def validate_pyoptix_build_receipt(path: Path) -> dict[str, Any]:
    receipt_path = path.resolve(strict=True)
    root = receipt_path.parent
    value = _load_json(receipt_path, "Goal5844 PyOptiX build receipt")
    required = {
        "schema",
        "status",
        "transaction_kind",
        "registered_performance_timing_count",
        "builder",
        "pyoptix_source",
        "optix_headers",
        "build",
        "wheel",
        "installed",
        "claim_boundary",
        "receipt_sha256",
    }
    if set(value) != required:
        raise Goal5844EvidenceError("Goal5844 PyOptiX receipt envelope differs")
    observed = value["receipt_sha256"]
    body = dict(value)
    body.pop("receipt_sha256")
    if (
        value["schema"] != PYOPTIX_BUILD_SCHEMA
        or value["status"] != PYOPTIX_BUILD_STATUS
        or value["transaction_kind"] != "build_install_provenance_not_performance"
        or value["registered_performance_timing_count"] != 0
        or not isinstance(observed, str)
        or observed != digest(body)
    ):
        raise Goal5844EvidenceError("Goal5844 PyOptiX receipt header or seal differs")
    validate_file_record(root, value["builder"], "Goal5844 builder")

    source = value["pyoptix_source"]
    if (
        not isinstance(source, dict)
        or set(source)
        != {"repository_url", "checkout_path", "commit", "tree", "clean", "archive"}
        or source["repository_url"] != PYOPTIX_REPOSITORY
        or source["commit"] != PYOPTIX_COMMIT
        or source["tree"] != PYOPTIX_TREE
        or source["clean"] is not True
        or not isinstance(source["checkout_path"], str)
    ):
        raise Goal5844EvidenceError("Goal5844 PyOptiX source binding differs")
    source_archive, _ = validate_file_record(
        root, source["archive"], "Goal5844 PyOptiX source archive"
    )
    _validate_git_archive(
        source_archive,
        expected_commit=PYOPTIX_COMMIT,
        label="Goal5844 PyOptiX source archive",
    )

    headers = value["optix_headers"]
    if not isinstance(headers, dict) or set(headers) != {
        "repository_url",
        "checkout_path",
        "commit",
        "tree",
        "clean",
        "api_version",
        "api_macro",
        "archive",
        "key_header_sha256",
    }:
        raise Goal5844EvidenceError("Goal5844 OptiX header binding differs")
    stack = _selected_stack(str(headers.get("api_version")))
    key_headers = headers.get("key_header_sha256")
    if (
        headers["repository_url"] != "https://github.com/NVIDIA/optix-dev.git"
        or headers["commit"] != stack["optix_header_commit"]
        or not isinstance(headers["tree"], str)
        or HEX40.fullmatch(headers["tree"]) is None
        or headers["clean"] is not True
        or headers["api_macro"] != _api_macro(headers["api_version"])
        or not isinstance(headers["checkout_path"], str)
        or not isinstance(key_headers, dict)
        or set(key_headers) != {"optix.h", "optix_device.h"}
        or any(
            not isinstance(item, str) or HEX64.fullmatch(item) is None
            for item in key_headers.values()
        )
    ):
        raise Goal5844EvidenceError("Goal5844 OptiX header identity differs")
    header_archive, _ = validate_file_record(
        root, headers["archive"], "Goal5844 OptiX header archive"
    )
    archived_headers = _validate_git_archive(
        header_archive,
        expected_commit=headers["commit"],
        label="Goal5844 OptiX header archive",
        required_members=("include/optix.h", "include/optix_device.h"),
    )
    if any(
        hashlib.sha256(archived_headers[f"include/{name}"]).hexdigest()
        != key_headers[name]
        for name in key_headers
    ):
        raise Goal5844EvidenceError("Goal5844 archived OptiX key headers differ")
    try:
        optix_header_text = archived_headers["include/optix.h"].decode("utf-8")
    except UnicodeDecodeError as error:
        raise Goal5844EvidenceError("Goal5844 archived optix.h is not UTF-8") from error
    macro = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+(\d+)\s*$",
        optix_header_text,
        re.MULTILINE,
    )
    if macro is None or int(macro.group(1)) != headers["api_macro"]:
        raise Goal5844EvidenceError("Goal5844 archived OptiX API macro differs")

    build = value["build"]
    if (
        not isinstance(build, dict)
        or set(build)
        != {
            "python_executable",
            "python_sha256",
            "python_version",
            "platform",
            "cmake_args",
            "build_environment",
            "tools",
            "wheel_command",
            "install_command",
            "build_stdout",
            "build_stderr",
            "install_stdout",
            "install_stderr",
            "dependency_install_report",
            "installed_dependencies",
            "pip_freeze",
        }
        or not all(
            isinstance(build[key], str) and build[key]
            for key in (
                "python_executable",
                "python_sha256",
                "python_version",
                "platform",
                "cmake_args",
            )
        )
        or HEX64.fullmatch(build["python_sha256"]) is None
        or not isinstance(build["build_environment"], dict)
        or not isinstance(build["tools"], dict)
        or not isinstance(build["wheel_command"], list)
        or not isinstance(build["install_command"], list)
        or build["installed_dependencies"] != REQUIRED_RUNTIME_DEPENDENCIES
    ):
        raise Goal5844EvidenceError("Goal5844 PyOptiX build metadata differs")
    wheel_command = build["wheel_command"]
    install_command = build["install_command"]
    expected_environment = {
        "CMAKE_ARGS": build["cmake_args"],
        "PYOPTIX_CMAKE_ARGS": build["cmake_args"],
        "CXX": build["tools"].get("cxx", {}).get("path"),
        "CUDACXX": build["tools"].get("nvcc", {}).get("path"),
        "CUDA_VISIBLE_DEVICES": "0",
    }
    expected_tools = {"cmake", "cxx", "ninja", "nvcc"}
    if set(build["tools"]) != expected_tools:
        raise Goal5844EvidenceError("Goal5844 PyOptiX tool set differs")
    for name, tool in build["tools"].items():
        if (
            not isinstance(tool, dict)
            or set(tool) != {"path", "bytes", "sha256", "version"}
            or not isinstance(tool["path"], str)
            or type(tool["bytes"]) is not int
            or tool["bytes"] <= 0
            or not isinstance(tool["sha256"], str)
            or HEX64.fullmatch(tool["sha256"]) is None
            or not isinstance(tool["version"], str)
            or not tool["version"]
        ):
            raise Goal5844EvidenceError(f"Goal5844 PyOptiX tool differs: {name}")
    if (
        wheel_command[:4] != [build["python_executable"], "-m", "pip", "wheel"]
        or "--no-build-isolation" not in wheel_command
        or "--no-deps" not in wheel_command
        or install_command[:4] != [build["python_executable"], "-m", "pip", "install"]
        or "--force-reinstall" not in install_command
        or "--no-deps" not in install_command
        or build["cmake_args"]
        != "-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=" + headers["checkout_path"]
        or build["build_environment"] != expected_environment
    ):
        raise Goal5844EvidenceError("Goal5844 PyOptiX build command boundary differs")
    build_records = {}
    for key in (
        "build_stdout",
        "build_stderr",
        "install_stdout",
        "install_stderr",
        "dependency_install_report",
        "pip_freeze",
    ):
        build_records[key] = validate_file_record(root, build[key], f"Goal5844 {key}")[
            0
        ]
    try:
        dependency_report = json.loads(
            build_records["dependency_install_report"].read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise Goal5844EvidenceError(
            "Goal5844 dependency install report is unreadable"
        ) from error
    installs = (
        dependency_report.get("install")
        if isinstance(dependency_report, dict)
        else None
    )
    if (
        not isinstance(dependency_report, dict)
        or dependency_report.get("version") != "1"
        or dependency_report.get("pip_version") != REQUIRED_RUNTIME_DEPENDENCIES["pip"]
        or not isinstance(installs, list)
    ):
        raise Goal5844EvidenceError("Goal5844 dependency install report differs")
    installed_versions: dict[str, str] = {}
    for row in installs:
        metadata = row.get("metadata") if isinstance(row, dict) else None
        download = row.get("download_info") if isinstance(row, dict) else None
        archive = download.get("archive_info") if isinstance(download, dict) else None
        hashes = archive.get("hashes") if isinstance(archive, dict) else None
        if (
            not isinstance(metadata, dict)
            or not isinstance(metadata.get("name"), str)
            or not isinstance(metadata.get("version"), str)
            or not isinstance(hashes, dict)
            or not isinstance(hashes.get("sha256"), str)
            or HEX64.fullmatch(hashes["sha256"]) is None
        ):
            raise Goal5844EvidenceError("Goal5844 dependency report row differs")
        name = re.sub(r"[-_.]+", "-", metadata["name"].lower())
        if name in installed_versions:
            raise Goal5844EvidenceError(
                "Goal5844 dependency report contains a duplicate distribution"
            )
        installed_versions[name] = metadata["version"]
    if installed_versions != REQUIRED_DEPENDENCIES:
        raise Goal5844EvidenceError("Goal5844 dependency versions differ")

    wheel = value["wheel"]
    if not isinstance(wheel, dict) or set(wheel) != {
        "file",
        "extension_member",
        "extension_bytes",
        "extension_sha256",
    }:
        raise Goal5844EvidenceError("Goal5844 wheel metadata differs")
    wheel_path, _ = validate_file_record(root, wheel["file"], "Goal5844 wheel")
    if (
        not isinstance(wheel["extension_member"], str)
        or type(wheel["extension_bytes"]) is not int
        or wheel["extension_bytes"] <= 0
        or not isinstance(wheel["extension_sha256"], str)
        or HEX64.fullmatch(wheel["extension_sha256"]) is None
    ):
        raise Goal5844EvidenceError("Goal5844 wheel extension metadata differs")
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            members = [
                name
                for name in archive.namelist()
                if name.startswith("optix/_optix.") and name.endswith(".so")
            ]
            if members != [wheel["extension_member"]]:
                raise Goal5844EvidenceError("Goal5844 wheel extension member differs")
            extension_payload = archive.read(members[0])
    except (OSError, zipfile.BadZipFile, KeyError) as error:
        raise Goal5844EvidenceError("Goal5844 wheel is unreadable") from error
    if (
        len(extension_payload) != wheel["extension_bytes"]
        or hashlib.sha256(extension_payload).hexdigest() != wheel["extension_sha256"]
    ):
        raise Goal5844EvidenceError("Goal5844 wheel extension payload differs")

    installed = value["installed"]
    if not isinstance(installed, dict) or set(installed) != {
        "distribution_name",
        "distribution_version",
        "optix_api_version",
        "package_initializer",
        "loaded_extension",
        "loaded_extension_source_path",
        "installed_distributions",
    }:
        raise Goal5844EvidenceError("Goal5844 installed PyOptiX metadata differs")
    _, loaded = validate_file_record(
        root, installed["loaded_extension"], "Goal5844 loaded extension copy"
    )
    validate_file_record(
        root, installed["package_initializer"], "Goal5844 package initializer copy"
    )
    if (
        installed["distribution_name"] != "pyoptix"
        or installed["distribution_version"] != stack["pyoptix_distribution_version"]
        or installed["optix_api_version"] != headers["api_version"]
        or not isinstance(installed["loaded_extension_source_path"], str)
        or loaded["bytes"] != wheel["extension_bytes"]
        or loaded["sha256"] != wheel["extension_sha256"]
        or installed["installed_distributions"]
        != {
            **REQUIRED_RUNTIME_DEPENDENCIES,
            "pyoptix": stack["pyoptix_distribution_version"],
        }
    ):
        raise Goal5844EvidenceError("loaded PyOptiX extension is not the wheel member")
    if value["claim_boundary"] != {
        "clean_source_build_bound": True,
        "loaded_extension_bound_to_wheel_member": True,
        "performance_measurement_in_receipt": False,
        "public_or_manuscript_claim_authorized": False,
    }:
        raise Goal5844EvidenceError("Goal5844 PyOptiX receipt claim boundary differs")
    return value


def evidence_rows(root: Path) -> list[dict[str, object]]:
    resolved = root.resolve(strict=True)
    rows = []
    for path in sorted(resolved.rglob("*")):
        if path == resolved / EVIDENCE_MANIFEST_NAME:
            continue
        if path.is_symlink():
            raise Goal5844EvidenceError(f"symbolic evidence path forbidden: {path}")
        if path.is_file():
            rows.append(file_record(path, resolved))
    return rows


def build_evidence_manifest(root: Path) -> dict[str, object]:
    rows = evidence_rows(root)
    body: dict[str, object] = {
        "schema": EVIDENCE_MANIFEST_SCHEMA,
        "status": "PASS__ALL_ENGINEERING_EVIDENCE_PAYLOADS_HASHED",
        "manifest_is_non_self_referential": True,
        "file_count_excluding_manifest": len(rows),
        "bytes_excluding_manifest": sum(int(row["bytes"]) for row in rows),
        "files": rows,
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    return {**body, "manifest_sha256": digest(body)}


def write_evidence_manifest(root: Path) -> dict[str, object]:
    path = root / EVIDENCE_MANIFEST_NAME
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    value = build_evidence_manifest(root)
    write_json_create(path, value)
    return value


def validate_evidence_manifest(root: Path) -> dict[str, Any]:
    resolved = root.resolve(strict=True)
    value = _load_json(resolved / EVIDENCE_MANIFEST_NAME, "Goal5844 evidence manifest")
    required = {
        "schema",
        "status",
        "manifest_is_non_self_referential",
        "file_count_excluding_manifest",
        "bytes_excluding_manifest",
        "files",
        "claim_boundary",
        "manifest_sha256",
    }
    observed = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if (
        set(value) != required
        or value.get("schema") != EVIDENCE_MANIFEST_SCHEMA
        or value.get("status") != "PASS__ALL_ENGINEERING_EVIDENCE_PAYLOADS_HASHED"
        or value.get("manifest_is_non_self_referential") is not True
        or observed != digest(body)
        or value.get("claim_boundary")
        != {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
        }
    ):
        raise Goal5844EvidenceError("Goal5844 evidence manifest envelope differs")
    actual = evidence_rows(resolved)
    if (
        value.get("files") != actual
        or value.get("file_count_excluding_manifest") != len(actual)
        or value.get("bytes_excluding_manifest")
        != sum(int(row["bytes"]) for row in actual)
    ):
        raise Goal5844EvidenceError(
            "Goal5844 evidence manifest payload inventory differs"
        )
    return value


__all__ = [
    "EVIDENCE_MANIFEST_NAME",
    "PYOPTIX_BUILD_SCHEMA",
    "PYOPTIX_BUILD_STATUS",
    "REQUIRED_DEPENDENCIES",
    "REQUIRED_RUNTIME_DEPENDENCIES",
    "Goal5844EvidenceError",
    "build_evidence_manifest",
    "digest",
    "file_record",
    "sha256_file",
    "validate_evidence_manifest",
    "validate_file_record",
    "validate_pyoptix_build_receipt",
    "write_evidence_manifest",
    "write_json_create",
]

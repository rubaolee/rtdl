#!/usr/bin/env python3
"""Build pinned PyOptiX and bind the installed extension to its wheel bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

from experiments.goal5798_premeasurement.compatibility import (
    PYOPTIX_COMMIT,
    PYOPTIX_REPOSITORY,
    PYOPTIX_TREE,
    frozen_registry,
)
from experiments.goal5844_compact_execution.provenance import (
    PYOPTIX_BUILD_SCHEMA,
    PYOPTIX_BUILD_STATUS,
    REQUIRED_RUNTIME_DEPENDENCIES,
    digest,
    file_record,
    sha256_file,
    validate_pyoptix_build_receipt,
    write_json_create,
)

ROOT = Path(__file__).resolve().parents[1]
OPTIX_REPOSITORY = "https://github.com/NVIDIA/optix-dev.git"
KEY_HEADERS = ("optix.h", "optix_device.h")


def _git(path: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _git_identity(path: Path) -> dict[str, object]:
    checkout = path.resolve(strict=True)
    return {
        "checkout_path": str(checkout),
        "commit": _git(checkout, "rev-parse", "HEAD"),
        "tree": _git(checkout, "rev-parse", "HEAD^{tree}"),
        "clean": _git(checkout, "status", "--porcelain=v1", "--untracked-files=all")
        == "",
    }


def _stack(api: str) -> dict[str, object]:
    rows = [row for row in frozen_registry() if row["optix_api_version"] == api]
    if len(rows) != 1:
        raise RuntimeError(f"unsupported frozen OptiX API: {api}")
    return rows[0]


def _run(
    command: list[str], *, cwd: Path, environment: dict[str, str]
) -> tuple[str, str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed.stdout, completed.stderr


def _write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _archive(repository: Path, output: Path) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "archive",
            "--format=tar",
            "-o",
            str(output),
            "HEAD",
        ],
        check=True,
    )


def _extract_archive(archive_path: Path, destination: Path) -> None:
    with tarfile.open(archive_path, "r:") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            member_path = Path(member.name)
            canonical = member_path.as_posix().rstrip("/")
            if (
                member_path.is_absolute()
                or ".." in member_path.parts
                or not canonical
                or canonical == "."
                or canonical != member.name.rstrip("/")
                or member.issym()
                or member.islnk()
                or not (member.isfile() or member.isdir())
                or canonical in seen
            ):
                raise RuntimeError("unsafe member in generated Git archive")
            seen.add(canonical)
        destination.mkdir(parents=True, exist_ok=False)
        if "filter" in tarfile.TarFile.extractall.__code__.co_varnames:
            archive.extractall(destination, filter="data")
        else:  # pragma: no cover - Python 3.11 compatibility.
            archive.extractall(destination)


def _optix_macro(path: Path) -> int:
    match = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+(\d+)\s*$",
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("OptiX header has no parseable OPTIX_VERSION")
    return int(match.group(1))


def _expected_macro(api: str) -> int:
    major, minor, patch = (int(part) for part in api.split("."))
    return major * 10_000 + minor * 100 + patch


def _probe_install(python: Path) -> dict[str, object]:
    code = """
import importlib.metadata
import json
from pathlib import Path
import sys
import optix
import re
module = sys.modules.get('optix._optix')
if module is None or not getattr(module, '__file__', None):
    raise RuntimeError('optix._optix was not loaded')
installed = {}
for distribution in importlib.metadata.distributions():
    name = re.sub(r'[-_.]+', '-', distribution.metadata['Name'].lower())
    if name in installed:
        raise RuntimeError(f'duplicate installed distribution: {name}')
    installed[name] = distribution.version
print(json.dumps({
    'distribution_name': importlib.metadata.distribution('pyoptix').metadata['Name'],
    'distribution_version': importlib.metadata.version('pyoptix'),
    'optix_api_version': '.'.join(str(item) for item in optix.version()),
    'package_initializer_path': str(Path(optix.__file__).resolve(strict=True)),
    'loaded_extension_path': str(Path(module.__file__).resolve(strict=True)),
    'installed_distributions': installed,
}, sort_keys=True))
"""
    completed = subprocess.run(
        [str(python), "-I", "-B", "-c", code],
        check=True,
        text=True,
        capture_output=True,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("PyOptiX import probe emitted unexpected stdout")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise TypeError("PyOptiX import probe did not return an object")
    return value


def _probe_dependency_versions(python: Path) -> dict[str, str]:
    code = """
import importlib.metadata
import json
import re
installed = {}
for distribution in importlib.metadata.distributions():
    name = re.sub(r'[-_.]+', '-', distribution.metadata['Name'].lower())
    if name in installed:
        raise RuntimeError(f'duplicate installed distribution: {name}')
    installed[name] = distribution.version
print(json.dumps(installed, sort_keys=True))
"""
    completed = subprocess.run(
        [str(python), "-I", "-B", "-c", code],
        check=True,
        text=True,
        capture_output=True,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("dependency metadata probe emitted unexpected stdout")
    value = json.loads(lines[0])
    if value != REQUIRED_RUNTIME_DEPENDENCIES:
        raise RuntimeError("installed Goal5844 dependency versions differ")
    return value


def _tool_identity(name: str, *version_arguments: str) -> dict[str, object]:
    requested = os.environ.get("CXX") if name == "cxx" else None
    executable_name = requested or ("g++" if name == "cxx" else name)
    discovered = shutil.which(executable_name)
    if discovered is None:
        raise RuntimeError(f"required PyOptiX build tool is absent: {name}")
    path = Path(discovered).resolve(strict=True)
    completed = subprocess.run(
        [str(path), *version_arguments],
        check=True,
        text=True,
        capture_output=True,
    )
    version = (completed.stdout + completed.stderr).strip()
    if not version:
        raise RuntimeError(f"PyOptiX build tool returned no version: {name}")
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "version": version,
    }


def build(args: argparse.Namespace) -> dict[str, object]:
    output = args.output_root.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "0":
        raise RuntimeError("Goal5844 PyOptiX build requires CUDA_VISIBLE_DEVICES=0")
    resolved_output = output.parent.resolve(strict=True) / output.name
    try:
        resolved_output.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        pass
    else:
        raise RuntimeError(
            "Goal5844 PyOptiX build evidence must be outside the Git tree"
        )
    python = args.python.expanduser().resolve(strict=True)
    if python != Path(sys.executable).resolve(strict=True) or sys.version_info[
        :2
    ] not in {(3, 11), (3, 12)}:
        raise RuntimeError(
            "Goal5844 builder must run under its declared Python 3.11/3.12"
        )
    installed_dependencies = _probe_dependency_versions(python)
    source_path = args.pyoptix_source.expanduser().resolve(strict=True)
    header_path = args.optix_headers.expanduser().resolve(strict=True)
    source = _git_identity(source_path)
    headers = _git_identity(header_path)
    selected = _stack(args.expected_optix_api)
    if (
        source["commit"] != PYOPTIX_COMMIT
        or source["tree"] != PYOPTIX_TREE
        or source["clean"] is not True
        or _git(source_path, "remote", "get-url", "origin") != PYOPTIX_REPOSITORY
    ):
        raise RuntimeError("pinned PyOptiX source identity differs")
    if (
        headers["commit"] != selected["optix_header_commit"]
        or headers["clean"] is not True
        or _git(header_path, "remote", "get-url", "origin") != OPTIX_REPOSITORY
    ):
        raise RuntimeError("selected OptiX header source identity differs")
    api_macro = _optix_macro(header_path / "include" / "optix.h")
    if api_macro != _expected_macro(args.expected_optix_api):
        raise RuntimeError("selected OptiX header API differs")

    inputs = output / "inputs"
    wheelhouse = output / "wheelhouse"
    logs = output / "logs"
    installed = output / "installed"
    for directory in (inputs, wheelhouse, logs, installed):
        directory.mkdir(parents=True, exist_ok=True)
    builder_copy = inputs / Path(__file__).name
    shutil.copy2(Path(__file__).resolve(strict=True), builder_copy)
    dependency_report = logs / "dependency_install_report.json"
    shutil.copy2(
        args.dependency_install_report.expanduser().resolve(strict=True),
        dependency_report,
    )
    source_archive = inputs / "otk-pyoptix.tar"
    header_archive = inputs / "optix-dev.tar"
    _archive(source_path, source_archive)
    _archive(header_path, header_archive)
    build_source = output / "build_source"
    _extract_archive(source_archive, build_source)

    environment = dict(os.environ)
    cmake_args = f"-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS={header_path}"
    environment["CMAKE_ARGS"] = cmake_args
    environment["PYOPTIX_CMAKE_ARGS"] = cmake_args
    environment["PYTHONNOUSERSITE"] = "1"
    tools = {
        "cmake": _tool_identity("cmake", "--version"),
        "cxx": _tool_identity("cxx", "--version"),
        "ninja": _tool_identity("ninja", "--version"),
        "nvcc": _tool_identity("nvcc", "--version"),
    }
    environment["CXX"] = str(tools["cxx"]["path"])
    environment["CUDACXX"] = str(tools["nvcc"]["path"])
    wheel_command = [
        str(python),
        "-m",
        "pip",
        "wheel",
        "--no-build-isolation",
        "--no-deps",
        "--wheel-dir",
        str(wheelhouse),
        str(build_source),
    ]
    try:
        stdout, stderr = _run(wheel_command, cwd=ROOT, environment=environment)
        _write(logs / "build_stdout.txt", stdout)
        _write(logs / "build_stderr.txt", stderr)
        wheels = sorted(wheelhouse.glob("pyoptix-*.whl"))
        if len(wheels) != 1:
            raise RuntimeError(f"expected one PyOptiX wheel, found {wheels}")
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            extension_names = sorted(
                name
                for name in archive.namelist()
                if name.startswith("optix/_optix.") and name.endswith(".so")
            )
            if len(extension_names) != 1:
                raise RuntimeError(f"expected one PyOptiX extension: {extension_names}")
            extension_payload = archive.read(extension_names[0])

        install_command = [
            str(python),
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            str(wheel),
        ]
        stdout, stderr = _run(install_command, cwd=ROOT, environment=environment)
        _write(logs / "install_stdout.txt", stdout)
        _write(logs / "install_stderr.txt", stderr)
        probe = _probe_install(python)
        expected_installed = {
            **REQUIRED_RUNTIME_DEPENDENCIES,
            "pyoptix": selected["pyoptix_distribution_version"],
        }
        if (
            str(probe.get("distribution_name", "")).lower() != "pyoptix"
            or probe.get("distribution_version")
            != selected["pyoptix_distribution_version"]
            or probe.get("optix_api_version") != args.expected_optix_api
            or probe.get("installed_distributions") != expected_installed
        ):
            raise RuntimeError("installed PyOptiX identity or API differs")
        initializer_source = Path(str(probe["package_initializer_path"]))
        extension_source = Path(str(probe["loaded_extension_path"]))
        initializer_copy = installed / "optix___init__.py"
        extension_copy = installed / extension_source.name
        shutil.copy2(initializer_source, initializer_copy)
        shutil.copy2(extension_source, extension_copy)
        extension_sha = hashlib.sha256(extension_payload).hexdigest()
        if (
            extension_copy.stat().st_size != len(extension_payload)
            or sha256_file(extension_copy) != extension_sha
        ):
            raise RuntimeError("installed extension differs from built wheel member")
        freeze_stdout, freeze_stderr = _run(
            [str(python), "-m", "pip", "freeze", "--all"],
            cwd=ROOT,
            environment=environment,
        )
        if freeze_stderr:
            raise RuntimeError("pip freeze emitted stderr")
        _write(logs / "pip_freeze.txt", freeze_stdout)
    finally:
        shutil.rmtree(build_source, ignore_errors=True)

    receipt: dict[str, object] = {
        "schema": PYOPTIX_BUILD_SCHEMA,
        "status": PYOPTIX_BUILD_STATUS,
        "transaction_kind": "build_install_provenance_not_performance",
        "registered_performance_timing_count": 0,
        "builder": file_record(builder_copy, output),
        "pyoptix_source": {
            "repository_url": PYOPTIX_REPOSITORY,
            **source,
            "archive": file_record(source_archive, output),
        },
        "optix_headers": {
            "repository_url": OPTIX_REPOSITORY,
            **headers,
            "api_version": args.expected_optix_api,
            "api_macro": api_macro,
            "archive": file_record(header_archive, output),
            "key_header_sha256": {
                name: sha256_file(header_path / "include" / name)
                for name in KEY_HEADERS
            },
        },
        "build": {
            "python_executable": str(python),
            "python_sha256": sha256_file(python),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cmake_args": cmake_args,
            "build_environment": {
                name: environment[name]
                for name in (
                    "CMAKE_ARGS",
                    "PYOPTIX_CMAKE_ARGS",
                    "CXX",
                    "CUDACXX",
                    "CUDA_VISIBLE_DEVICES",
                )
            },
            "tools": tools,
            "wheel_command": wheel_command,
            "install_command": install_command,
            "build_stdout": file_record(logs / "build_stdout.txt", output),
            "build_stderr": file_record(logs / "build_stderr.txt", output),
            "install_stdout": file_record(logs / "install_stdout.txt", output),
            "install_stderr": file_record(logs / "install_stderr.txt", output),
            "dependency_install_report": file_record(dependency_report, output),
            "installed_dependencies": installed_dependencies,
            "pip_freeze": file_record(logs / "pip_freeze.txt", output),
        },
        "wheel": {
            "file": file_record(wheel, output),
            "extension_member": extension_names[0],
            "extension_bytes": len(extension_payload),
            "extension_sha256": extension_sha,
        },
        "installed": {
            "distribution_name": "pyoptix",
            "distribution_version": str(probe["distribution_version"]),
            "optix_api_version": str(probe["optix_api_version"]),
            "package_initializer": file_record(initializer_copy, output),
            "loaded_extension": file_record(extension_copy, output),
            "loaded_extension_source_path": str(extension_source.resolve(strict=True)),
            "installed_distributions": probe["installed_distributions"],
        },
        "claim_boundary": {
            "clean_source_build_bound": True,
            "loaded_extension_bound_to_wheel_member": True,
            "performance_measurement_in_receipt": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    receipt["receipt_sha256"] = digest(receipt)
    receipt_path = output / "build_receipt.json"
    write_json_create(receipt_path, receipt)
    validate_pyoptix_build_receipt(receipt_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--optix-headers", type=Path, required=True)
    parser.add_argument("--expected-optix-api", required=True)
    parser.add_argument("--dependency-install-report", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    result = build(parser.parse_args())
    print(
        json.dumps(
            {
                "status": result["status"],
                "receipt_sha256": result["receipt_sha256"],
                "wheel_sha256": result["wheel"]["file"]["sha256"],
                "extension_sha256": result["wheel"]["extension_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

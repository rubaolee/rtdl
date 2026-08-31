#!/usr/bin/env python3
"""Create-only fresh-venv runner for the Goal5801 A3 public API probe.

This orchestration is untimed.  It installs one already frozen local wheel
with pip's isolated/no-index mode, executes the public probe with ``-I`` from
outside the source tree, and preserves every command, exit code and stream.
It does not build or mutate the wheel and it never authorizes an artifact.
"""

from __future__ import annotations

import argparse
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
import sys
from typing import NoReturn
import zipfile


SCHEMA = "rtdl.goal5801.a3.clean_install_run.v3"


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _tree_rows(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"virtualenv bootstrap contains a symlink: {path}")
        if not path.is_file():
            continue
        payload = path.read_bytes()
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": len(payload), "sha256": _sha(payload),
        })
    rows.sort(key=lambda row: str(row["path"]))
    if not rows or not (root / "virtualenv/__main__.py").is_file():
        _fail("virtualenv bootstrap tree is incomplete")
    return rows


def _write(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _copy_input(role: str, source: Path, destination: Path, packet_root: Path,
                rows: list[dict[str, object]]) -> Path:
    supplied = source.expanduser()
    if supplied.is_symlink():
        _fail(f"clean-install input must not be a symlink: {supplied}")
    source = supplied.resolve(strict=True)
    if not source.is_file():
        _fail(f"clean-install input is not a regular file: {source}")
    payload = source.read_bytes()
    _write(destination, payload)
    rows.append({
        "role": role,
        "source_path": str(source),
        "saved_path": destination.relative_to(packet_root).as_posix(),
        "bytes": len(payload),
        "sha256": _sha(payload),
    })
    return destination


def _generated_input(role: str, source_label: str, destination: Path,
                     packet_root: Path,
                     payload: bytes, rows: list[dict[str, object]]) -> Path:
    _write(destination, payload)
    rows.append({
        "role": role,
        "source_path": source_label,
        "saved_path": destination.relative_to(packet_root).as_posix(),
        "bytes": len(payload),
        "sha256": _sha(payload),
    })
    return destination


def _validate_wheel(path: Path, frozen_source: Path) -> None:
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or any(info.is_dir() for info in infos):
            _fail("wheel contains duplicate or directory members")
        allowed_dist = {
            f"{dist}/METADATA", f"{dist}/WHEEL",
            f"{dist}/top_level.txt", f"{dist}/RECORD",
        }
        for name in names:
            posix = PurePosixPath(name)
            if posix.is_absolute() or ".." in posix.parts or "." in posix.parts \
                    or name != posix.as_posix() or name.endswith(".pth") \
                    or any(part.endswith(".data") for part in posix.parts) \
                    or not (name.startswith("rtdsl/") or name in allowed_dist):
                _fail(f"wheel member is outside the frozen package boundary: {name}")
        if {name for name in names if name.startswith(f"{dist}/")} != allowed_dist:
            _fail("wheel dist-info member set differs")
        record_name = f"{dist}/RECORD"
        record_rows = list(csv.reader(io.StringIO(
            archive.read(record_name).decode("utf-8"), newline="")))
        if any(len(row) != 3 for row in record_rows) \
                or len({row[0] for row in record_rows}) != len(record_rows) \
                or {row[0] for row in record_rows} != set(names):
            _fail("wheel RECORD coverage/shape differs")
        for member, encoded_hash, encoded_size in record_rows:
            payload = archive.read(member)
            if member == record_name:
                if encoded_hash or encoded_size:
                    _fail("wheel RECORD self-row must have empty hash and size")
                continue
            expected_hash = base64.urlsafe_b64encode(
                hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
            if encoded_hash != f"sha256={expected_hash}" \
                    or encoded_size != str(len(payload)):
                _fail(f"wheel RECORD identity differs: {member}")
        metadata = BytesParser().parsebytes(archive.read(f"{dist}/METADATA"))
        dependencies = metadata.get_all("Requires-Dist", [])
        if metadata.get("Name") != "rtdl-source-tree" \
                or metadata.get("Version") != "4.0.0rc1" \
                or metadata.get("Requires-Python") != ">=3.10" \
                or [value.replace(" ", "") for value in dependencies] != [
                    "numpy>=1.26"]:
            _fail("wheel METADATA identity differs from frozen pyproject")
        wheel_package = {
            name.removeprefix("rtdsl/"): archive.read(name)
            for name in names if name.startswith("rtdsl/")
        }
    source_package = {
        item.relative_to(frozen_source).as_posix(): item.read_bytes()
        for item in frozen_source.rglob("*") if item.is_file()
    }
    if wheel_package != source_package:
        _fail("wheel rtdsl package differs from frozen source projection")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _virtualenv_command(base: Path, bootstrap_root: Path, venv: Path) -> list[str]:
    app_data = venv.parent / "virtualenv_app_data"
    bootstrap_code = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path.insert(0,{bootstrap_root.as_posix()!r});"
        "sys.argv=['virtualenv','--no-download','--copies','--app-data',"
        f"{app_data.as_posix()!r},{venv.as_posix()!r}];"
        "runpy.run_module('virtualenv',run_name='__main__')"
    )
    return [str(base), "-I", "-c", bootstrap_code]


def _run(label: str, command: list[str], *, cwd: Path,
         environment: dict[str, str], receipts: Path) -> int:
    completed = subprocess.run(
        command, cwd=cwd, env=environment, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _write(receipts / f"{label}.command.json", _canonical(command) + b"\n")
    _write(receipts / f"{label}.stdout", completed.stdout)
    _write(receipts / f"{label}.stderr", completed.stderr)
    _write(receipts / f"{label}.exit_code", f"{completed.returncode}\n".encode("ascii"))
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--base-python", type=Path, required=True)
    parser.add_argument("--virtualenv-bootstrap-root", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-predecessor-package", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--host-cc", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--nvrtc-library", type=Path, required=True)
    parser.add_argument("--nvrtc-trap-source", type=Path, required=True)
    parser.add_argument("--nvrtc-kat-source", type=Path, required=True)
    args = parser.parse_args()

    output = args.output_directory.resolve()
    if args.source_root.expanduser().is_symlink():
        _fail("source root must not be a symlink")
    source = args.source_root.expanduser().resolve(strict=True)
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if _inside(output, source):
        _fail("clean-install output/venv must be outside the source tree")
    required = (
        args.base_python, args.probe, args.wheel, args.candidate_manifest,
        args.trust_root, args.trust_head, args.trust_predecessor_package,
        args.trust_package, args.native,
        args.host_cc, args.nvrtc_library,
        args.nvrtc_trap_source, args.nvrtc_kat_source,
    )
    for path in required:
        supplied = path.expanduser()
        if supplied.is_symlink() or not supplied.resolve(strict=True).is_file():
            _fail(f"clean-install input is not a regular file: {path}")
    if args.virtualenv_bootstrap_root.expanduser().is_symlink():
        _fail("virtualenv bootstrap root must not be a symlink")
    bootstrap_root = args.virtualenv_bootstrap_root.expanduser().resolve(strict=True)
    if not bootstrap_root.is_dir():
        _fail("virtualenv bootstrap root must be a real directory")
    if args.cuda_include.expanduser().is_symlink():
        _fail("CUDA include root must not be a symlink")
    cuda_include = args.cuda_include.expanduser().resolve(strict=True)
    nvrtc_header_source = cuda_include / "nvrtc.h"
    if not cuda_include.is_dir() or nvrtc_header_source.is_symlink() \
            or not nvrtc_header_source.is_file():
        _fail("CUDA include root has no regular nvrtc.h")
    bootstrap_rows = _tree_rows(bootstrap_root)
    output.mkdir(parents=True)
    inputs = output / "inputs"
    input_rows: list[dict[str, object]] = []
    for bootstrap_row in bootstrap_rows:
        relative = Path(str(bootstrap_row["path"]))
        _copy_input(
            f"virtualenv_bootstrap/{relative.as_posix()}",
            bootstrap_root / relative,
            inputs / "virtualenv_bootstrap" / relative,
            output, input_rows)
    manifest_copy = _copy_input(
        "candidate_manifest", args.candidate_manifest, inputs / "candidate_manifest.json",
        output, input_rows)
    manifest = json.loads(manifest_copy.read_text(encoding="utf-8"))
    candidates = manifest.get("candidates") if isinstance(manifest, dict) else None
    if not isinstance(candidates, dict) or set(candidates) != {"relation", "triangle"}:
        _fail("candidate manifest must contain exactly relation and triangle")
    descriptor_paths: dict[str, Path] = {}
    for family in ("relation", "triangle"):
        row = candidates[family]
        if not isinstance(row, dict) or not {
                "deployment_id", "artifact_path", "artifact_sha256",
                "authority_path", "authority_sha256"} <= set(row):
            _fail(f"candidate manifest {family} row is incomplete")
        artifact_supplied = Path(str(row["artifact_path"])).expanduser()
        authority_supplied = Path(str(row["authority_path"])).expanduser()
        if artifact_supplied.is_symlink() or authority_supplied.is_symlink():
            _fail(f"candidate manifest {family} input must not be a symlink")
        artifact_source = artifact_supplied.resolve(strict=True)
        authority_source = authority_supplied.resolve(strict=True)
        artifact_payload = artifact_source.read_bytes()
        authority_payload = authority_source.read_bytes()
        if _sha(artifact_payload) != row["artifact_sha256"] \
                or _sha(authority_payload) != row["authority_sha256"]:
            _fail(f"candidate manifest {family} input identity differs")
        artifact = _copy_input(
            f"{family}_artifact", artifact_source,
            inputs / "artifacts" / f"{row['artifact_sha256']}.rtdlexe",
            output, input_rows)
        authority = _copy_input(
            f"{family}_authority", authority_source,
            inputs / f"{family}.authority.json", output, input_rows)
        descriptor = {
            "artifact_path": artifact.relative_to(output).as_posix(),
            "authority_path": authority.relative_to(output).as_posix(),
            "deployment_id": row["deployment_id"],
        }
        descriptor_paths[family] = _generated_input(
            f"{family}_descriptor",
            f"{args.candidate_manifest.resolve()}#/candidates/{family}",
            inputs / f"{family}.descriptor.json", output,
            _canonical(descriptor) + b"\n", input_rows)

    trust_root = _copy_input(
        "trust_root", args.trust_root, inputs / "trust_root.json", output, input_rows)
    trust_head = _copy_input(
        "trust_head", args.trust_head, inputs / "trust_head.json", output, input_rows)
    _copy_input(
        "trust_predecessor_package", args.trust_predecessor_package,
        inputs / "trust_predecessor_package.json", output, input_rows)
    trust_package = _copy_input(
        "trust_package", args.trust_package, inputs / "trust_package.json",
        output, input_rows)
    native = _copy_input(
        "native", args.native, inputs / "native" / "librtdl_optix.so",
        output, input_rows)
    wheel = _copy_input(
        "wheel", args.wheel, inputs / "wheel" / args.wheel.name,
        output, input_rows)
    probe = _copy_input(
        "probe_source", args.probe, inputs / "probe" / args.probe.name,
        output, input_rows)
    _copy_input(
        "runner_source", Path(__file__), inputs / "runner" / Path(__file__).name,
        output, input_rows)
    host_cc = _copy_input(
        "host_cc", args.host_cc, inputs / "tools" / args.host_cc.name,
        output, input_rows)
    base_python_copy = _copy_input(
        "base_python", args.base_python,
        inputs / "tools" / args.base_python.resolve().name, output, input_rows)
    nvrtc_header = _copy_input(
        "nvrtc_header", nvrtc_header_source,
        inputs / "toolchain" / "nvrtc.h", output, input_rows)
    nvrtc_library = _copy_input(
        "nvrtc_library", args.nvrtc_library,
        inputs / "toolchain" / args.nvrtc_library.resolve().name,
        output, input_rows)
    trap_source = _copy_input(
        "nvrtc_trap_source", args.nvrtc_trap_source,
        inputs / "trap" / args.nvrtc_trap_source.name, output, input_rows)
    kat_source = _copy_input(
        "nvrtc_kat_source", args.nvrtc_kat_source,
        inputs / "trap" / args.nvrtc_kat_source.name, output, input_rows)
    source_package = source / "src" / "rtdsl"
    if not source_package.is_dir() or source_package.is_symlink():
        _fail("source root has no regular src/rtdsl package directory")
    for path in sorted(source_package.rglob("*")):
        if path.is_symlink():
            _fail(f"source package contains symlink: {path}")
        if path.is_file():
            relative = path.relative_to(source_package)
            _copy_input(
                f"source_package/{relative.as_posix()}", path,
                inputs / "source" / "src" / "rtdsl" / relative,
                output, input_rows)
    _copy_input(
        "source_pyproject", source / "pyproject.toml",
        inputs / "source" / "pyproject.toml", output, input_rows)
    _copy_input(
        "source_readme", source / "README.md",
        inputs / "source" / "README.md", output, input_rows)
    _validate_wheel(wheel, inputs / "source" / "src" / "rtdsl")

    receipts = output / "receipts"
    receipts.mkdir()
    build_environment = {
        key: value for key, value in os.environ.items()
        if key in {
            "PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP",
            "TEMP", "LD_LIBRARY_PATH",
        }
    }
    build_environment.update({
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    build_environment.pop("PYTHONPATH", None)
    build = output / "build"
    build.mkdir()
    _write(receipts / "build_environment.json",
           _canonical(build_environment) + b"\n")
    trap_library_path = build / "goal5801_nvrtc_forbidden_preload.so"
    trap_build = [
        str(args.host_cc.resolve()), "-shared", "-fPIC",
        "-I", str(nvrtc_header.parent), str(trap_source),
        "-o", str(trap_library_path),
    ]
    if _run("trap_build", trap_build, cwd=output,
            environment=build_environment, receipts=receipts) != 0 \
            or not trap_library_path.is_file():
        _fail(f"NVRTC trap build failed; receipts preserved at {output}")
    kat_binary_path = build / "goal5801_nvrtc_positive_kat"
    kat_build = [
        str(args.host_cc.resolve()), "-I", str(nvrtc_header.parent),
        str(kat_source), str(nvrtc_library),
        "-o", str(kat_binary_path),
    ]
    if _run("kat_build", kat_build, cwd=output,
            environment=build_environment, receipts=receipts) != 0 \
            or not kat_binary_path.is_file():
        _fail(f"NVRTC KAT build failed; receipts preserved at {output}")
    _generated_input(
        "nvrtc_trap_library", "GENERATED_BY:receipts/trap_build.command.json",
        inputs / "trap" / trap_library_path.name, output,
        trap_library_path.read_bytes(), input_rows)
    _generated_input(
        "nvrtc_kat_binary", "GENERATED_BY:receipts/kat_build.command.json",
        inputs / "trap" / kat_binary_path.name, output,
        kat_binary_path.read_bytes(), input_rows)
    trap_library = str(trap_library_path)
    kat_log_path = build / "nvrtc_kat.log"
    _write(kat_log_path, b"")
    kat_environment = dict(build_environment)
    kat_environment["LD_PRELOAD"] = trap_library
    kat_environment["RTDL_GOAL5801_NVRTC_TRAP_LOG"] = str(kat_log_path)
    _write(receipts / "kat_environment.json",
           _canonical(kat_environment) + b"\n")
    kat_exit = _run(
        "kat", [str(kat_binary_path)], cwd=output,
        environment=kat_environment, receipts=receipts)
    if kat_exit != 97 or kat_log_path.read_bytes() != b"nvrtcCreateProgram\n":
        _fail(f"NVRTC trap positive KAT failed; receipts preserved at {output}")

    lifecycle_log_path = build / "nvrtc_lifecycle.log"
    _write(lifecycle_log_path, b"")
    environment = dict(build_environment)
    environment["LD_PRELOAD"] = trap_library
    environment["RTDL_GOAL5801_NVRTC_TRAP_LOG"] = str(lifecycle_log_path)
    _write(receipts / "environment.json", _canonical(environment) + b"\n")

    venv = output / "venv"
    venv_command = _virtualenv_command(
        args.base_python.resolve(), bootstrap_root, venv)
    if _run("venv", venv_command, cwd=output, environment=environment,
            receipts=receipts) != 0:
        _fail(f"fresh venv creation failed; receipts preserved at {output}")
    for path in venv.rglob("*"):
        if path.is_symlink():
            _fail(
                "fresh venv contains a symlink despite --copies: "
                f"{path}")
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    install_command = [
        str(python), "-I", "-m", "pip", "install", "--isolated", "--no-index",
        "--no-deps", "--no-cache-dir", "--no-compile", str(wheel),
    ]
    if _run("install", install_command, cwd=output, environment=environment,
            receipts=receipts) != 0:
        _fail(f"isolated local-wheel install failed; receipts preserved at {output}")

    result = output / "result.json"
    probe_command = [
        str(python), "-I", "-B", str(probe),
        "--relation", str(descriptor_paths["relation"]),
        "--triangle", str(descriptor_paths["triangle"]),
        "--candidate-manifest", str(manifest_copy),
        "--trust-root", str(trust_root),
        "--trust-head", str(trust_head),
        "--trust-package", str(trust_package),
        "--native", str(native),
        "--wheel", str(wheel),
        "--forbid-source-root", str(source),
        "--nvrtc-trap-library", str(trap_library_path),
        "--nvrtc-trap-log", str(lifecycle_log_path),
        "--output", str(result),
    ]
    probe_exit = _run(
        "probe", probe_command, cwd=output, environment=environment,
        receipts=receipts)
    if probe_exit != 0 or not result.is_file():
        _fail(f"public API probe failed; receipts preserved at {output}")
    if lifecycle_log_path.read_bytes() != b"":
        _fail(f"NVRTC lifecycle trap fired; receipts preserved at {output}")
    for row in input_rows:
        source_path = str(row["source_path"])
        if source_path.startswith("GENERATED_BY:") or "#/candidates/" in source_path:
            continue
        source_file = Path(source_path)
        saved_file = output / str(row["saved_path"])
        if not source_file.is_file() or source_file.is_symlink() \
                or source_file.read_bytes() != saved_file.read_bytes():
            _fail(f"clean-install source input changed during execution: {row['role']}")
    for built, saved_role in (
            (trap_library_path, "nvrtc_trap_library"),
            (kat_binary_path, "nvrtc_kat_binary")):
        saved_row = next(row for row in input_rows if row["role"] == saved_role)
        if built.read_bytes() != (output / str(saved_row["saved_path"])).read_bytes():
            _fail(f"generated input changed during execution: {saved_role}")

    payloads = {
        path.relative_to(output).as_posix(): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
        and path.relative_to(output).parts[:1] != ("venv",)
    }
    rows = [{"path": name, "bytes": len(payload), "sha256": _sha(payload)}
            for name, payload in sorted(payloads.items())]
    record = {
        "schema": SCHEMA,
        "status": "PASS__FRESH_VENV__ISOLATED_LOCAL_WHEEL__PUBLIC_API",
        "registered_performance_timing_count": 0,
        "base_python_sha256": _sha(base_python_copy.read_bytes()),
        "virtualenv_bootstrap_file_count": len(bootstrap_rows),
        "virtualenv_bootstrap_files": bootstrap_rows,
        "virtualenv_creation_uses_network": False,
        "wheel_sha256": _sha(wheel.read_bytes()),
        "native_sha256": _sha(native.read_bytes()),
        "result_sha256": _sha(result.read_bytes()),
        "input_identities": sorted(input_rows, key=lambda row: str(row["role"])),
        "nvrtc_trap_library_sha256": _sha(trap_library_path.read_bytes()),
        "nvrtc_positive_kat_log_sha256": _sha(kat_log_path.read_bytes()),
        "nvrtc_positive_kat_exit_code": 97,
        "nvrtc_lifecycle_log_bytes": 0,
        "receipt_file_count": len(rows),
        "receipts": rows,
        "claim_boundary": "install_and_execution_receipt__not_performance",
    }
    _write(output / "run.json", _canonical(record) + b"\n")
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

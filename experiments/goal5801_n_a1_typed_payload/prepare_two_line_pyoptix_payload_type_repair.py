#!/usr/bin/env python3
"""Create and build the two-line PyOptiX FFI repair for Goal5801-N-A1.

The pinned NVIDIA binding exposes ModuleCompileOptions.payloadTypes but its
``sync()`` returns before copying Python payload types into the native
``OptixModuleCompileOptions``.  Its ``PayloadType`` wrapper also remains
unsynchronized when passed explicitly to ``ProgramGroupOptions``.  This
create-only helper verifies the pristine upstream repository, copies it,
removes exactly that return statement, adds exactly one constructor sync,
builds
a wheel without network or build isolation, and installs it into an isolated
target directory.  It does not create an OptiX context or execute GPU work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
import zipfile


UPSTREAM_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
UPSTREAM_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
UPSTREAM_MAIN_SHA256 = "a6626e2c78dbf561a9cb3297b0bed3e04128360443cacb14d552cd1e1ebcafdb"
PATCH_OLD = b"""    void sync()
    {
        return;
#if OPTIX_VERSION >= 70200
        boundValues.clear();
"""
PATCH_NEW = b"""    void sync()
    {
#if OPTIX_VERSION >= 70200
        boundValues.clear();
"""
CONSTRUCTOR_OLD = b"""    PayloadType( const py::list&  payload_semantics )
    {
        setPayloadSemantics( payload_semantics );
    }
"""
CONSTRUCTOR_NEW = b"""    PayloadType( const py::list&  payload_semantics )
    {
        setPayloadSemantics( payload_semantics );
        sync();
    }
"""


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def identity(path: Path) -> dict[str, object]:
    value = path.read_bytes()
    return {"path": str(path), "bytes": len(value), "sha256": sha_bytes(value)}


def run(argv: list[str], *, cwd: Path | None = None,
        env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, check=False)


def git_text(repo: Path, *argv: str) -> str:
    completed = run(["git", "-C", str(repo), *argv])
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout.decode("utf-8", errors="strict").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--optix-headers", type=Path, required=True)
    parser.add_argument("--stage-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.stage_root.exists() or args.output.exists():
        raise FileExistsError("Goal5801-N-A1 binding stage is create-only")
    source_repo = args.source_repo.resolve(strict=True)
    headers = args.optix_headers.resolve(strict=True)
    if git_text(source_repo, "rev-parse", "HEAD") != UPSTREAM_COMMIT:
        raise RuntimeError("PyOptiX upstream commit drift")
    if git_text(source_repo, "rev-parse", "HEAD^{tree}") != UPSTREAM_TREE:
        raise RuntimeError("PyOptiX upstream tree drift")
    if git_text(source_repo, "status", "--porcelain"):
        raise RuntimeError("PyOptiX upstream source is dirty")
    upstream_main = source_repo / "src/main.cpp"
    upstream_bytes = upstream_main.read_bytes()
    if sha_bytes(upstream_bytes) != UPSTREAM_MAIN_SHA256:
        raise RuntimeError("PyOptiX main.cpp identity drift")
    if upstream_bytes.count(PATCH_OLD) != 1:
        raise RuntimeError("PyOptiX inert sync anchor is not unique")
    if upstream_bytes.count(CONSTRUCTOR_OLD) != 1:
        raise RuntimeError("PyOptiX PayloadType constructor anchor is not unique")

    args.stage_root.mkdir(parents=True)
    copied = args.stage_root / "otk-pyoptix-two-line-payload-type-repair"
    shutil.copytree(source_repo, copied, ignore=shutil.ignore_patterns(".git"))
    copied_main = copied / "src/main.cpp"
    copied_before = copied_main.read_bytes()
    patched = copied_before.replace(PATCH_OLD, PATCH_NEW, 1)
    patched = patched.replace(CONSTRUCTOR_OLD, CONSTRUCTOR_NEW, 1)
    copied_main.write_bytes(patched)
    expected_delta = len(b"        sync();\n") - len(b"        return;\n")
    if len(patched) - len(copied_before) != expected_delta:
        raise RuntimeError("repair changed more than the two frozen lines")
    if patched.count(PATCH_NEW) != 1 or patched.count(CONSTRUCTOR_NEW) != 1:
        raise RuntimeError("repair postcondition failed")

    wheel_dir = args.stage_root / "wheel"
    site_dir = args.stage_root / "site"
    wheel_dir.mkdir()
    site_dir.mkdir()
    build_stdout = args.stage_root / "wheel_build_stdout.bin"
    build_stderr = args.stage_root / "wheel_build_stderr.bin"
    install_stdout = args.stage_root / "target_install_stdout.bin"
    install_stderr = args.stage_root / "target_install_stderr.bin"
    env = dict(os.environ)
    cmake_args = f"-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS={headers}"
    env["CMAKE_ARGS"] = cmake_args
    env["PYOPTIX_CMAKE_ARGS"] = cmake_args
    build_argv = [
        sys.executable, "-m", "pip", "wheel", "--no-cache-dir",
        "--no-build-isolation", "--no-deps", str(copied), "-w", str(wheel_dir),
    ]
    built = run(build_argv, env=env)
    build_stdout.write_bytes(built.stdout)
    build_stderr.write_bytes(built.stderr)
    if built.returncode != 0:
        raise RuntimeError(
            "two-line PyOptiX wheel build failed; raw logs preserved")
    wheels = sorted(wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one repaired wheel, found {wheels}")
    wheel = wheels[0]
    install_argv = [
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "--no-deps", "--target", str(site_dir), str(wheel),
    ]
    installed = run(install_argv, env=env)
    install_stdout.write_bytes(installed.stdout)
    install_stderr.write_bytes(installed.stderr)
    if installed.returncode != 0:
        raise RuntimeError(
            "two-line PyOptiX target install failed; raw logs preserved")
    extensions = sorted((site_dir / "optix").glob("_optix*.so"))
    if len(extensions) != 1:
        raise RuntimeError(f"expected one installed OptiX extension: {extensions}")
    extension = extensions[0]
    with zipfile.ZipFile(wheel) as archive:
        extension_members = [
            name for name in archive.namelist()
            if name.startswith("optix/_optix") and name.endswith(".so")]
        if len(extension_members) != 1:
            raise RuntimeError("wheel extension member is not unique")
        wheel_extension = archive.read(extension_members[0])
    if sha_bytes(wheel_extension) != sha_bytes(extension.read_bytes()):
        raise RuntimeError("installed extension differs from wheel member")

    receipt = {
        "schema": "rtdl.goal5801_n_a1.pyoptix_two_line_payload_type_repair.v1",
        "status": "PASS__TWO_LINE_FFI_PAYLOAD_TYPE_REPAIR__UNTIMED",
        "scope": {
            "gpu_context_created": False,
            "gpu_launch_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "pod_count": 0,
            "network_required": False,
            "stock_or_unmodified_pyoptix_claimed": False,
        },
        "upstream": {
            "repository": "https://github.com/NVIDIA/otk-pyoptix",
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
            "source_clean": True,
            "main_cpp": identity(upstream_main),
        },
        "observed_binding_defect": {
            "property_exposed": "ModuleCompileOptions.payloadTypes",
            "native_sync_short_circuited_by_unconditional_return": True,
            "payload_type_constructor_does_not_sync_native_struct": True,
            "anchor_occurrence_count_each": 1,
            "meaning": "unmodified binding neither transmits module payloadTypes nor populates an explicitly bound ProgramGroupOptions payload type",
        },
        "repair": {
            "edited_file_count": 1,
            "source_edit_site_count": 2,
            "deleted_line_count": 1,
            "added_line_count": 1,
            "deleted_exact_line": "        return;",
            "added_exact_line": "        sync();",
            "scientific_device_or_host_harness_changed": False,
            "patched_main_cpp": identity(copied_main),
        },
        "build": {
            "python": sys.executable,
            "cmake_args": cmake_args,
            "argv": build_argv,
            "returncode": built.returncode,
            "stdout": identity(build_stdout),
            "stderr": identity(build_stderr),
        },
        "install": {
            "argv": install_argv,
            "returncode": installed.returncode,
            "stdout": identity(install_stdout),
            "stderr": identity(install_stderr),
            "site_root": str(site_dir),
        },
        "wheel": identity(wheel),
        "wheel_extension_member": {
            "path": extension_members[0],
            "bytes": len(wheel_extension),
            "sha256": sha_bytes(wheel_extension),
        },
        "installed_extension": identity(extension),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": receipt["status"],
        "patched_main_cpp_sha256": receipt["repair"]["patched_main_cpp"]["sha256"],
        "wheel_sha256": receipt["wheel"]["sha256"],
        "installed_extension_sha256": receipt["installed_extension"]["sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Clean, CPU-only usability validation for the Goal5767 V4 RC."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    seen: set[str] = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe archive member: {member.name}")
            name = "/".join(parts)
            if name in seen:
                raise RuntimeError(f"duplicate archive member: {name}")
            seen.add(name)
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise RuntimeError(f"unsupported archive member: {member.name}")
        for member in members:
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            target = destination.joinpath(*parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            target.write_bytes(handle.read())


def _tree_sha(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    files = 0
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(data).digest())
        files += 1
    return digest.hexdigest(), files


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--packaging-python", default=sys.executable)
    args = parser.parse_args()

    bundle_root = Path(args.bundle_root).resolve()
    work_root = Path(args.work_root).resolve()
    output = Path(args.output).resolve()
    packaging_python = str(Path(args.packaging_python).resolve())
    if work_root.exists():
        raise FileExistsError(work_root)
    if output.exists():
        raise FileExistsError(output)
    manifest = json.loads((bundle_root / "PORTABLE_MANIFEST.json").read_text(encoding="utf-8"))
    source_archive = bundle_root / "SOURCE.tar.gz"
    if _sha(source_archive) != manifest["source_archive_sha256"]:
        raise RuntimeError("source archive digest mismatch")
    source_root = work_root / "source"
    _safe_extract(source_archive, source_root)
    before_sha, source_file_count = _tree_sha(source_root)

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(source_root / "src"), str(source_root)))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    tests = sorted((source_root / "tests").glob("goal57*_v4_*test.py"))
    if len(tests) != 20:
        raise RuntimeError(f"expected 20 V4 test modules, found {len(tests)}")
    test_output = _run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "goal57*_v4_*test.py"],
        cwd=source_root, env=env,
    )
    if "Ran 186 tests" not in test_output or "OK" not in test_output:
        raise RuntimeError(f"unexpected unit-test output:\n{test_output}")
    quickstart = json.loads(_run(
        [sys.executable, "examples/current/v4_restricted_callback_quickstart.py"],
        cwd=source_root, env=env,
    ))
    audit_text = _run(
        [sys.executable, "scripts/goal5767_release_audit.py"],
        cwd=source_root, env=env,
    )
    audit = json.loads(audit_text)

    # Prove the documented installation surface without mutating the sealed
    # source: build from a disposable copy, install the wheel to an isolated
    # target directory, then run the shipped quickstart against that target.
    packaging_source = work_root / "packaging_source"
    shutil.copytree(source_root, packaging_source)
    wheel_root = work_root / "wheel"
    wheel_root.mkdir()
    packaging_env = dict(os.environ)
    packaging_env.pop("PYTHONHOME", None)
    packaging_env["PYTHONDONTWRITEBYTECODE"] = "1"
    _run([
        packaging_python, "-m", "pip", "wheel", ".", "--no-deps",
        "--no-build-isolation", "--wheel-dir", str(wheel_root),
    ], cwd=packaging_source, env=packaging_env)
    wheels = list(wheel_root.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel, found {wheels}")
    install_root = work_root / "installed"
    _run([
        packaging_python, "-m", "pip", "install", str(wheels[0]),
        "--no-deps", "--target", str(install_root),
    ], cwd=work_root, env=packaging_env)
    installed_env = dict(os.environ)
    installed_env.pop("PYTHONHOME", None)
    installed_env["PYTHONPATH"] = str(install_root)
    installed_env["PYTHONDONTWRITEBYTECODE"] = "1"
    installed_version = _run([
        packaging_python, "-c",
        "import rtdsl, rtdsl.v4; print(rtdsl.__version__); print(rtdsl.v4.V4_API_VERSION)",
    ], cwd=work_root, env=installed_env).strip().splitlines()
    if installed_version != ["4.0.0rc1", "4.0.0rc1"]:
        raise RuntimeError(f"installed version mismatch: {installed_version}")
    installed_quickstart = json.loads(_run([
        packaging_python,
        str(source_root / "examples/current/v4_restricted_callback_quickstart.py"),
    ], cwd=work_root, env=installed_env))
    if installed_quickstart != quickstart:
        raise RuntimeError("installed-package quickstart differs from source quickstart")
    after_sha, after_count = _tree_sha(source_root)
    if before_sha != after_sha or source_file_count != after_count:
        raise RuntimeError("clean validation modified extracted source")

    result = {
        "schema": "rtdl.goal5767.clean_usability_result.v1",
        "goal": 5767,
        "source_archive_sha256": manifest["source_archive_sha256"],
        "source_tree_sha256": before_sha,
        "source_file_count": source_file_count,
        "source_pre_post_match": True,
        "v4_test_module_count": len(tests),
        "unit_tests": "186/186 PASS",
        "quickstart": quickstart,
        "wheel_sha256": _sha(wheels[0]),
        "wheel_install_without_network_or_dependencies": True,
        "installed_package_version": installed_version[0],
        "packaging_python": packaging_python,
        "installed_quickstart_matches_source": True,
        "release_audit_output_sha256": hashlib.sha256(audit_text.encode()).hexdigest(),
        "release_audit_canonical_sha256": hashlib.sha256(
            (json.dumps(audit, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ).hexdigest(),
        "documentation_file_count": len(audit["documentation"]),
        "v4_product_module_dispatch_hits": sum(
            row["dispatch_hits"] for row in audit["v4_module_dispatch_audit"]
        ),
        "performance_timing_registered": False,
        "gpu_or_pod_used": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

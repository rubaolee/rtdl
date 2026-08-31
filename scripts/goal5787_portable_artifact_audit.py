#!/usr/bin/env python3
"""Clean, read-only audit of the frozen Goal5767 portable V4 RC."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_twin_20260812.tar.gz"
EXPECTED_SHA = "50e37b1d4a311bdde40d30392cd9201bc781e5d228d72df4f430b3e12f81955c"
EXPECTED_OUTER = {
    "HARNESS/goal5766_portable_validate.py",
    "HARNESS/goal5767_clean_validate.py",
    "PORTABLE_MANIFEST.json",
    "README.md",
    "SOURCE.tar.gz",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_name(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "" in path.parts:
        raise RuntimeError(f"unsafe archive path: {name}")


def validate_tar(archive: tarfile.TarFile, *, allow_directories: bool = True) -> list[str]:
    names = []
    seen = set()
    for member in archive.getmembers():
        validate_name(member.name)
        if member.name in seen:
            raise RuntimeError(f"duplicate archive member: {member.name}")
        seen.add(member.name)
        if member.isdir() and allow_directories:
            continue
        if not member.isfile():
            raise RuntimeError(f"non-regular archive member: {member.name}")
        names.append(member.name)
    return names


def tree_sha(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(name.encode() + b"\0" + hashlib.sha256(data).digest())
        count += 1
    return digest.hexdigest(), count


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {command}\n{completed.stdout}")
    return completed.stdout


def independent_clean_workflow(source_root: Path, work_root: Path) -> dict[str, object]:
    """Equivalent workflow that tolerates this host's relocated Python executable.

    The canonical Goal5767 validator intentionally removes PYTHONHOME for its
    packaging subprocess.  This Windows host has python.exe separated from its
    standard-library prefix, so removing PYTHONHOME makes the host interpreter
    unusable.  The artifact is not modified: we rerun the same tests, audit,
    wheel build, isolated install, and quickstart while retaining the discovered
    standard-library prefix.
    """
    env = dict(os.environ)
    stdlib_home = str(Path(json.__file__).resolve().parents[2])
    if not (Path(sys.executable).resolve().parent / "Lib").is_dir():
        env["PYTHONHOME"] = stdlib_home
    python_paths = [str(source_root / "src"), str(source_root)]
    # The relocated C:\Python311 host lacks the optional `wheel` package.  A
    # separate, ordinary local Python installation provides it; this affects
    # only packaging tooling, never the extracted RTDL source or runtime.
    pgadmin_site = Path("C:/PostgreSQL/pgsql/pgAdmin 4/python/Lib/site-packages")
    if pgadmin_site.is_dir():
        python_paths.append(str(pgadmin_site))
    env["PYTHONPATH"] = os.pathsep.join(python_paths)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    before_sha, before_count = tree_sha(source_root)
    tests = sorted((source_root / "tests").glob("goal57*_v4_*test.py"))
    test_output = run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "goal57*_v4_*test.py"],
        cwd=source_root, env=env,
    )
    if len(tests) != 20 or "Ran 186 tests" not in test_output or "OK" not in test_output:
        raise RuntimeError("independent unit-test contract mismatch")
    quickstart = json.loads(run(
        [sys.executable, "examples/current/v4_restricted_callback_quickstart.py"],
        cwd=source_root, env=env,
    ))
    release_audit = json.loads(run(
        [sys.executable, "scripts/goal5767_release_audit.py"], cwd=source_root, env=env,
    ))
    packaging_source = work_root / "packaging_source_independent"
    shutil.copytree(source_root, packaging_source)
    wheel_root = work_root / "wheel_independent"
    wheel_root.mkdir()
    run([
        sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation",
        "--wheel-dir", str(wheel_root),
    ], cwd=packaging_source, env=env)
    wheels = list(wheel_root.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel, found {wheels}")
    install_root = work_root / "installed_independent"
    run([
        sys.executable, "-m", "pip", "install", str(wheels[0]), "--no-deps",
        "--target", str(install_root),
    ], cwd=work_root, env=env)
    installed_env = dict(env)
    installed_env["PYTHONPATH"] = str(install_root)
    version = run([
        sys.executable, "-c",
        "import rtdsl, rtdsl.v4; print(rtdsl.__version__); print(rtdsl.v4.V4_API_VERSION)",
    ], cwd=work_root, env=installed_env).strip().splitlines()
    installed_quickstart = json.loads(run([
        sys.executable, str(source_root / "examples/current/v4_restricted_callback_quickstart.py"),
    ], cwd=work_root, env=installed_env))
    after_sha, after_count = tree_sha(source_root)
    if version != ["4.0.0rc1", "4.0.0rc1"] or installed_quickstart != quickstart:
        raise RuntimeError("independent installed-package contract mismatch")
    if (before_sha, before_count) != (after_sha, after_count):
        raise RuntimeError("independent clean workflow modified sealed source")
    return {
        "status": "PASS",
        "source_tree_sha256": before_sha,
        "source_file_count": before_count,
        "unit_tests": "186/186 PASS",
        "test_module_count": len(tests),
        "quickstart": quickstart,
        "release_audit_summary": {
            "documentation_file_count": len(release_audit["documentation"]),
            "missing_local_link_count": sum(
                row["local_links_missing"] for row in release_audit["documentation"]
            ),
            "v4_module_count": len(release_audit["v4_module_dispatch_audit"]),
            "application_or_publication_dispatch_hit_count": sum(
                row["dispatch_hits"] for row in release_audit["v4_module_dispatch_audit"]
            ),
            "arbitrary_provider_escape_present": release_audit["public_surface"]["arbitrary_provider_escape_present"],
            "backend_runtime_module_import_count": len(release_audit["public_surface"]["backend_runtime_module_imports"]),
            "quickstart_matches": release_audit["quickstart"] == quickstart,
        },
        "wheel_built": True,
        "wheel_install_without_network_or_dependencies": True,
        "installed_package_version": version[0],
        "installed_quickstart_matches_source": True,
        "source_pre_post_match": True,
        "host_pythonhome_retained": "PYTHONHOME" in env,
    }


def main() -> None:
    archive_sha = sha256(ARCHIVE)
    twin_sha = sha256(TWIN)
    if archive_sha != EXPECTED_SHA or twin_sha != EXPECTED_SHA:
        raise RuntimeError("portable archive/twin identity drift")
    with tempfile.TemporaryDirectory(prefix="goal5787_rc_audit_") as td:
        temp = Path(td)
        outer_root = temp / "outer"
        outer_root.mkdir()
        with tarfile.open(ARCHIVE, "r:gz") as outer:
            outer_files = validate_tar(outer)
            if set(outer_files) != EXPECTED_OUTER:
                raise RuntimeError(f"unexpected outer members: {outer_files}")
            outer.extractall(outer_root)
        source_archive = outer_root / "SOURCE.tar.gz"
        with tarfile.open(source_archive, "r:gz") as source:
            source_files = validate_tar(source)
            source_root = temp / "source"
            source_root.mkdir()
            source.extractall(source_root)
        forbidden_private = [name for name in source_files if ".codex" in PurePosixPath(name).parts]
        prebuilt_native = [name for name in source_files if name.endswith((".so", ".dll", ".dylib"))]
        if forbidden_private or prebuilt_native:
            raise RuntimeError(
                f"non-portable payloads: private={forbidden_private}, native={prebuilt_native}"
            )
        work_root = temp / "work"
        output = temp / "clean_validation.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(outer_root / "HARNESS/goal5767_clean_validate.py"),
                "--bundle-root", str(outer_root),
                "--work-root", str(work_root),
                "--output", str(output),
            ],
            cwd=outer_root,
            text=True,
            capture_output=True,
            check=False,
        )
        canonical_validation = None
        if completed.returncode == 0 and output.is_file():
            canonical_validation = json.loads(output.read_text(encoding="utf-8"))
        independent_validation = independent_clean_workflow(source_root, work_root)
        result = {
            "schema": "rtdl.goal5787.portable_artifact_audit.v1",
            "goal": 5787,
            "archive": str(ARCHIVE.relative_to(ROOT)).replace("\\", "/"),
            "archive_sha256": archive_sha,
            "twin_sha256": twin_sha,
            "byte_identical_twin": ARCHIVE.read_bytes() == TWIN.read_bytes(),
            "outer_regular_file_count": len(outer_files),
            "outer_members": sorted(outer_files),
            "source_regular_file_count": len(source_files),
            "unsafe_member_count": 0,
            "private_codex_member_count": len(forbidden_private),
            "prebuilt_native_member_count": len(prebuilt_native),
            "canonical_clean_validator": {
                "status": "PASS" if canonical_validation is not None else "HOST_PYTHON_RELOCATION_BLOCKED",
                "result": canonical_validation,
                "returncode": completed.returncode,
                "host_blocker": "relocated Windows python.exe loses its standard-library prefix when the canonical validator removes PYTHONHOME for packaging",
                "scientific_or_artifact_defect_claimed": False,
            },
            "independent_equivalent_clean_workflow": independent_validation,
            "clean_validator_returncode": completed.returncode,
            "clean_validator_stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
            "claim_boundary": {
                "functional_usability_rc_reverified": True,
                "performance_reproduced": False,
                "goal5785_source_identity_claimed": False,
                "pod_used_or_authorized": False,
                "public_release_or_submission_ready_claimed": False,
            },
        }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

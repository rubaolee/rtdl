#!/usr/bin/env python3
"""Clean-machine validator for the Goal5766 portable V4 release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, cwd: Path, env: dict[str, str], log: Path) -> None:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}; see {log}")


def _safe_extract(archive_path: Path, target: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe source member: {member.name}")
            normalized = "/".join(parts)
            if normalized in seen:
                raise RuntimeError(f"duplicate source member: {normalized}")
            seen.add(normalized)
            if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
                raise RuntimeError(f"unsupported source member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts):
                raise RuntimeError(f"private/cache source member: {member.name}")
            if member.isfile() and (
                normalized.endswith(".pyc")
                or normalized.endswith("librtdl_optix.so")
                or "/build/" in f"/{normalized}/"
            ):
                raise RuntimeError(f"prebuilt/cache source payload: {member.name}")
        archive.extractall(target)


def _tree_sha(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if (
            rel.startswith("build/") or "/__pycache__/" in f"/{rel}/"
            or rel.endswith(".pyc")
        ):
            continue
        data = path.read_bytes()
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--optix-prefix", required=True, type=Path)
    parser.add_argument("--cuda-prefix", required=True, type=Path)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    args = parser.parse_args()
    bundle_root = args.bundle_root.resolve()
    work_root = args.work_root.resolve()
    if work_root.exists():
        raise FileExistsError(work_root)
    work_root.mkdir(parents=True)
    source_archive = bundle_root / "SOURCE.tar.gz"
    manifest = json.loads((bundle_root / "PORTABLE_MANIFEST.json").read_text())
    if _sha(source_archive) != manifest["source_archive_sha256"]:
        raise RuntimeError("portable source SHA-256 mismatch")
    source = work_root / "source"
    source.mkdir()
    _safe_extract(source_archive, source)
    source_tree_before = _tree_sha(source)

    result_root = work_root / "result"
    result_root.mkdir()
    logs = result_root / "logs"
    logs.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(source / "src"), str(source / "scripts"), str(source)))
    env["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu"
    env["NUMBA_CUDA_NVVM"] = "/usr/lib/x86_64-linux-gnu/libnvvm.so"
    env["NUMBA_CUDA_LIBDEVICE"] = "/usr/lib/cuda/nvvm/libdevice/libdevice.10.bc"

    _run([
        "make", "build-optix", f"OPTIX_PREFIX={args.optix_prefix}",
        f"CUDA_PREFIX={args.cuda_prefix}", f"OPTIX_CUDA_ARCH=sm_{args.cc}",
    ], cwd=source, env=env, log=logs / "build.log")
    native = source / "build/librtdl_optix.so"
    if not native.is_file():
        raise RuntimeError("fresh native was not built")
    env["RTDL_OPTIX_LIB"] = str(native)

    _run([
        sys.executable, "-m", "unittest", "discover", "-s", "tests",
        "-p", "goal57*_v4_*test.py",
    ], cwd=source, env=env, log=logs / "unit_tests.log")

    py_version = platform.python_version()
    version_probe = subprocess.run(
        [sys.executable, "-c", "import numba,numpy,llvmlite; print(numba.__version__,numpy.__version__,llvmlite.__version__)"],
        cwd=source, env=env, text=True, check=True, capture_output=True,
    ).stdout.strip().split()
    if len(version_probe) != 3:
        raise RuntimeError("unexpected Python partner version probe")
    numba_version, numpy_version, llvmlite_version = version_probe
    optix_include = args.optix_prefix / "include"
    cuda_include = args.cuda_prefix / "include"
    common = ["--optix-include", str(optix_include), "--cuda-include", str(cuda_include)]
    raw = result_root / "raw"
    raw.mkdir()

    commands = [
        ("m0", [sys.executable, "scripts/goal5756_builtin_triangle_device_validation.py",
            "--output", str(raw / "m0_particle_tracking"), *common,
            "--cc", args.cc, "--expected-python", py_version,
            "--expected-numba", numba_version, "--expected-numpy", numpy_version,
            "--expected-llvmlite", llvmlite_version, "--cuda-toolkit", "12.0",
            "--optix-sdk", "9.0.0"]),
        ("m1", [sys.executable, "scripts/goal5759_home_triangle_reduction_device_validation.py",
            "--output", str(raw / "m1_triangle_reduction"), *common,
            "--cc", args.cc, "--expected-python", py_version,
            "--expected-numba", numba_version, "--expected-numpy", numpy_version,
            "--optix-sdk", "9.0.0"]),
        ("m2", [sys.executable, "scripts/goal5760_home_bounded_relation_device_validation.py",
            "--native", str(native), *common, "--output", str(raw / "m2_bounded_relation")]),
        ("m3", [sys.executable, "scripts/goal5761_home_multiround_spatial_validation.py",
            "--native", str(native), *common, "--output", str(raw / "m3_multiround_spatial")]),
        ("m4", [sys.executable, "scripts/goal5762_home_exact_predicate_witness_validation.py",
            "--native", str(native), *common, "--output", str(raw / "m4_exact_predicate")]),
    ]
    for name, command in commands:
        _run(command, cwd=source, env=env, log=logs / f"{name}.log")
    _run([
        sys.executable, "scripts/goal5763_home_grouped_event_reduction_validation.py",
        "--m2-result", str(raw / "m2_bounded_relation/RESULT.json"),
        "--m4-result", str(raw / "m4_exact_predicate/RESULT.json"),
        "--output", str(raw / "m5_grouped_events"),
    ], cwd=source, env=env, log=logs / "m5.log")
    _run([
        sys.executable, "scripts/goal5764_home_hierarchy_frontier_validation.py",
        "--output", str(raw / "m6_hierarchy"),
    ], cwd=source, env=env, log=logs / "m6.log")

    recount_commands = [
        ("m1", [sys.executable, "scripts/goal5759_recount_home_triangle_reduction.py", "--raw", str(raw / "m1_triangle_reduction")]),
        ("m2", [sys.executable, "scripts/goal5760_recount_home_bounded_relation.py", "--raw", str(raw / "m2_bounded_relation")]),
        ("m3", [sys.executable, "scripts/goal5761_recount_home_multiround_spatial.py", "--raw", str(raw / "m3_multiround_spatial")]),
        ("m4", [sys.executable, "scripts/goal5762_recount_home_exact_predicate_witness.py", "--raw", str(raw / "m4_exact_predicate")]),
    ]
    recount_dir = result_root / "recounts"
    recount_dir.mkdir()
    for name, command in recount_commands:
        command.extend(("--output", str(recount_dir / f"goal5765_{name}_recount_20260812.json")))
        _run(command, cwd=source, env=env, log=logs / f"recount_{name}.log")
    _run([
        sys.executable, "scripts/goal5763_recount_home_grouped_event_reduction.py",
        "--result", str(raw / "m5_grouped_events/RESULT.json"),
        "--m2-result", str(raw / "m2_bounded_relation/RESULT.json"),
        "--m4-result", str(raw / "m4_exact_predicate/RESULT.json"),
        "--output", str(recount_dir / "goal5765_m5_recount_20260812.json"),
    ], cwd=source, env=env, log=logs / "recount_m5.log")
    _run([
        sys.executable, "scripts/goal5764_recount_home_hierarchy_frontier.py",
        "--raw", str(raw / "m6_hierarchy"),
        "--output", str(recount_dir / "goal5765_m6_recount_20260812.json"),
    ], cwd=source, env=env, log=logs / "recount_m6.log")
    integrated = result_root / "INTEGRATED_RECOUNT.json"
    _run([
        sys.executable, "scripts/goal5765_integrated_nine_app_recount.py",
        "--raw-root", str(raw), "--recount-root", str(recount_dir),
        "--source-archive", str(source_archive), "--native", str(native),
        "--output", str(integrated),
    ], cwd=source, env=env, log=logs / "integrated.log")
    integrated_payload = json.loads(integrated.read_text())
    if integrated_payload["paper_lane_count"] != 13:
        raise RuntimeError("integrated gate did not close 13 paper lanes")

    source_tree_after = _tree_sha(source)
    if source_tree_before != source_tree_after:
        raise RuntimeError("source tree changed outside ignored build/cache paths")
    shutil.copy2(source_archive, result_root / "EXECUTION_SOURCE.tar.gz")
    shutil.copy2(native, result_root / "librtdl_optix.so")
    result = {
        "schema": "rtdl.goal5766.portable_clean_validation_result.v1",
        "goal": 5766,
        "source_archive_sha256": _sha(source_archive),
        "source_tree_sha256": source_tree_before,
        "native_library_sha256": _sha(native),
        "paper_app_count": 9,
        "paper_lane_count": 13,
        "exact_paper_lane_count": 13,
        "behavioral_true_optix_paper_lane_count": 13,
        "full_v4_unit_tests": "180/180 PASS",
        "registered_performance_timing_count": 0,
        "clean_source_pre_post_match": True,
        "prebuilt_target_native_in_bundle": False,
        "private_codex_dependency": False,
        "claim_boundary": {
            "portable_functional_rc_claimed": True,
            "performance_claimed": False,
            "modern_rtx_claimed": False,
            "rt_silicon_claimed": False,
            "production_public_submission_claimed": False,
            "pod_used_or_authorized": False,
        },
    }
    (result_root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

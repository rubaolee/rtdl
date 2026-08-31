#!/usr/bin/env python3
"""Create-only target preparation for Goal5774 V2-direct versus V4."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _archive_members(archive_path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe bundle member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported bundle member: {member.name}")
            name = "/".join(parts)
            if name in result:
                raise RuntimeError(f"duplicate bundle member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable bundle member: {name}")
            result[name] = handle.read()
    manifest = json.loads(result["PORTABLE_MANIFEST.json"])
    expected = {row["path"] for row in manifest["payloads"]}
    if set(result) != expected | {"PORTABLE_MANIFEST.json"}:
        raise RuntimeError("bundle membership differs from manifest")
    for row in manifest["payloads"]:
        data = result[row["path"]]
        if _sha_bytes(data) != row["sha256"] or len(data) != row["size_bytes"]:
            raise RuntimeError(f"bundle payload mismatch: {row['path']}")
    return result


def _safe_extract_bytes(data: bytes, target: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or path.is_absolute() or ".." in parts or name in seen:
                raise RuntimeError(f"unsafe/duplicate source member: {member.name}")
            seen.add(name)
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported source member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts):
                raise RuntimeError(f"private/cache source member: {name}")
            if name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"prebuilt/cache source member: {name}")
        archive.extractall(target)


def _run(command: list[str], *, cwd: Path, env: dict[str, str], log: Path) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(
            f"create-only prepare command failed: {command!r}; see {log}")
    return completed.stdout


def _validate_authority(
    authority: dict[str, object], *, bundle_sha256: str, source_sha256: str,
    gpu: tuple[str, str, str, str], cc: str,
    cuda_toolkit: str, optix_sdk: str,
) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("prepare authority digest mismatch")
    expected_keys = {
        "schema", "bundle_sha256", "source_archive_sha256",
        "required_gpu_name", "required_gpu_uuid", "required_driver_version",
        "required_compute_capability", "required_cuda_toolkit",
        "required_optix_sdk", "owner_authorized_create_only_prepare",
        "formal_worker_allowed", "registered_formal_timing_allowed",
        "authority_sha256",
    }
    if set(authority) != expected_keys:
        raise PermissionError("prepare authority fields are not exact")
    expected = {
        "schema": "rtdl.goal5774.owner_create_only_prepare_authority.v1",
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "required_gpu_name": gpu[0],
        "required_gpu_uuid": gpu[1],
        "required_driver_version": gpu[2],
        "required_compute_capability": cc,
        "required_cuda_toolkit": cuda_toolkit,
        "required_optix_sdk": optix_sdk,
        "owner_authorized_create_only_prepare": True,
        "formal_worker_allowed": False,
        "registered_formal_timing_allowed": False,
    }
    for key, value in expected.items():
        if authority.get(key) != value:
            raise PermissionError(f"prepare authority mismatch: {key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    parser.add_argument("--optix-root", type=Path, required=True)
    parser.add_argument("--cuda-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()

    bundle = args.bundle.resolve()
    work_root = args.work_root.resolve()
    if work_root.exists():
        raise FileExistsError(work_root)
    outer = _archive_members(bundle)
    manifest = json.loads(outer["PORTABLE_MANIFEST.json"])
    if (
        manifest["schema"] != "rtdl.goal5774.v2_v4_pre_pod_manifest.v1"
        or manifest["formal_worker_count"] != 208
        or manifest["independent_comparison_row_count"] != 26
        or manifest["v3_required_or_executed"] is not False
    ):
        raise RuntimeError("unexpected Goal5774 bundle manifest")
    bundle_sha256 = _sha(bundle)
    source_sha256 = _sha_bytes(outer["SOURCE.tar.gz"])

    nvidia = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader"], text=True, capture_output=True, check=True)
    gpu_lines = [line.strip() for line in nvidia.stdout.splitlines() if line.strip()]
    if len(gpu_lines) != 1:
        raise RuntimeError("prepare requires exactly one visible NVIDIA GPU")
    gpu = tuple(part.strip() for part in gpu_lines[0].split(","))
    if len(gpu) != 4 or gpu[3].replace(".", "") != args.cc:
        raise RuntimeError("target GPU compute capability mismatch")
    authority = json.loads(args.authority.read_text(encoding="utf-8"))
    _validate_authority(
        authority, bundle_sha256=bundle_sha256, source_sha256=source_sha256,
        gpu=gpu, cc=args.cc, cuda_toolkit="12.8", optix_sdk="9.0.0")

    source = work_root / "source"
    logs = work_root / "logs"
    result_root = work_root / "result"
    source.mkdir(parents=True)
    logs.mkdir()
    result_root.mkdir()
    _safe_extract_bytes(outer["SOURCE.tar.gz"], source)

    python = args.python.resolve()
    optix_root = args.optix_root.resolve()
    cuda_root = args.cuda_root.resolve()
    cuda_include = (
        cuda_root / "targets/x86_64-linux/include"
        if (cuda_root / "targets/x86_64-linux/include/cuda.h").is_file()
        else cuda_root / "include"
    )
    if not python.is_file() or not (optix_root / "include/optix.h").is_file() \
            or not (cuda_include / "cuda.h").is_file() \
            or not (cuda_root / "bin/nvcc").is_file():
        raise RuntimeError("prepare toolchain paths are incomplete")
    nvcc_version = subprocess.run(
        [str(cuda_root / "bin/nvcc"), "--version"], text=True,
        capture_output=True, check=True).stdout
    if "release 12.8" not in nvcc_version:
        raise RuntimeError("prepare CUDA toolkit is not exact 12.8")
    optix_header = (optix_root / "include/optix.h").read_text(
        encoding="utf-8", errors="replace")
    if re.search(r"#\s*define\s+OPTIX_VERSION\s+90000\b", optix_header) is None:
        raise RuntimeError("prepare OptiX SDK is not exact 9.0")
    env = dict(os.environ)
    env.update({
        "PYTHONPATH": f"{source / 'src'}:{source / 'scripts'}:{source}",
        "RTDL_V4_OPTIX_PREFIX": str(optix_root),
        "RTDL_V4_CUDA_PREFIX": str(cuda_root),
        # Home Ubuntu uses GCC 13 with CUDA 12.2.  This flag is a compiler
        # admission override only; target compilation and all runtime tests
        # still fail closed on any actual incompatibility.
        "NVCC_PREPEND_FLAGS": "-allow-unsupported-compiler",
    })
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix_root}",
        f"CUDA_PREFIX={cuda_root}", f"OPTIX_CUDA_ARCH=sm_{args.cc}",
    ], cwd=source, env=env, log=logs / "build.log")
    native = (source / "build/librtdl_optix.so").resolve()
    if not native.is_file():
        raise RuntimeError("fresh target native missing")
    native_sha256 = _sha(native)
    env["RTDL_OPTIX_LIB"] = str(native)
    env["RTDL_OPTIX_LIBRARY"] = str(native)

    tests = _run([
        str(python), "-m", "unittest", "discover", "-s", "tests",
        "-p", "goal5774*test.py",
    ], cwd=source, env=env, log=logs / "goal5774_tests.log")
    match = re.search(r"Ran (\d+) tests?", tests)
    if match is None or int(match.group(1)) != 13 or "OK" not in tests:
        raise RuntimeError("Goal5774 focused test cardinality/status mismatch")

    evidence = result_root / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    execution_source = result_root / "EXECUTION_SOURCE.tar.gz"
    rematerialization = result_root / "REMATERIALIZATION.json"
    _run([
        str(python), "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "--source-root", str(source), "--native", str(native),
        "--evidence-output", str(evidence),
        "--execution-source-output", str(execution_source),
        "--result-output", str(rematerialization),
    ], cwd=source, env=env, log=logs / "rematerialization.log")
    remat = json.loads(rematerialization.read_text(encoding="utf-8"))
    if remat.get("case_count") != 17 or remat.get("all_cases_exact") is not True \
            or remat.get("native_sha256") != native_sha256:
        raise RuntimeError("fixed-radius rematerialization failed")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(evidence)

    functional = result_root / "TARGET_FUNCTIONAL_RESULT.json"
    _run([
        str(python), "scripts/goal5774_home_v2_v4_prepared_validation.py",
        "--native", str(native), "--optix-include", str(optix_root / "include"),
        "--cuda-include", str(cuda_include), "--output", str(functional),
    ], cwd=source, env=env, log=logs / "target_functional.log")
    functional_payload = json.loads(functional.read_text(encoding="utf-8"))
    if (
        functional_payload.get("correct_activation_call_count") != 26
        or functional_payload.get("correct_call_count") != 52
        or functional_payload.get("behavioral_true_optix_activation_call_count") != 26
        or functional_payload.get("behavioral_true_optix_call_count") != 52
        or functional_payload.get("native_library_sha256") != native_sha256
    ):
        raise RuntimeError("target functional gate failed")
    recount = result_root / "TARGET_FUNCTIONAL_RECOUNT.json"
    _run([
        str(python), "scripts/goal5774_recount_home_v2_v4_prepared.py",
        "--result", str(functional), "--output", str(recount),
    ], cwd=source, env=env, log=logs / "target_recount.log")

    versions_text = _run([
        str(python), "-c",
        "import json,platform,numba,numpy; print(json.dumps({"
        "'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__},sort_keys=True))",
    ], cwd=source, env=env, log=logs / "versions.log").strip()
    versions = json.loads(versions_text)
    target_identity = _digest({
        "gpu": gpu, "cc": args.cc, "python": versions,
        "python_executable_sha256": _sha(python),
        "native_sha256": native_sha256,
    })
    prepared_identity = _digest({
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "execution_source_sha256": _sha(execution_source),
        "execution_tree_sha256": remat["execution_tree_sha256"],
        "native_sha256": native_sha256,
        "target_identity_sha256": target_identity,
        "functional_result_sha256": _sha(functional),
        "functional_recount_sha256": _sha(recount),
    })
    formal_sources = {
        name: _sha(source / "scripts" / name)
        for name in (
            "goal5774_prepared_three_way_frontdoors.py",
            "goal5774_prepared_v2_v4_worker.py",
            "goal5774_prepared_v2_v4_controller.py",
            "goal5774_evaluate_prepared_v2_v4.py",
            "goal5774_recount_prepared_v2_v4_raw.py",
        )
    }
    formal_identity = _digest({
        "prepared_identity_sha256": prepared_identity,
        "formal_sources": formal_sources,
        "worker_count": 208, "row_count": 26,
        "methods": [
            "v2_direct_true_optix_backport",
            "v4_restricted_callback_true_optix"],
    })
    runtime = {
        "schema": "rtdl.goal5774.prepared_v2_v4_runtime.v1",
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "execution_source_sha256": _sha(execution_source),
        "execution_tree_sha256": remat["execution_tree_sha256"],
        "native_library_path": str(native),
        "native_library_sha256": native_sha256,
        "target": {
            "provider": "optix", "optix_sdk": "9.0.0",
            "compute_capability": f"{args.cc[0]}.{args.cc[1]}",
            "native_sha256": native_sha256,
            "supports_custom_aabb": True, "supports_builtin_triangle": True,
        },
        "compute_capability": [int(args.cc[0]), int(args.cc[1])],
        "optix_include": str(optix_root / "include"),
        "cuda_include": str(cuda_include),
        "expected_python_version": versions["python"],
        "expected_numba_version": versions["numba"],
        "expected_numpy_version": versions["numpy"],
        "python_executable_sha256": _sha(python),
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "formal_worker_environment": {
            name: env.get(name) for name in (
                "PYTHONPATH", "PATH", "LD_LIBRARY_PATH",
                "RTDL_V4_OPTIX_PREFIX", "RTDL_V4_CUDA_PREFIX",
                "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
                "RTDL_OPTIX_LIB", "RTDL_OPTIX_LIBRARY")
        },
    }
    runtime_path = result_root / "RUNTIME.json"
    runtime_path.write_text(
        json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = {
        "schema": "rtdl.goal5774.prepared_v2_v4_plan.v1",
        "bundle_sha256": bundle_sha256,
        "prepared_identity_sha256": prepared_identity,
        "target_identity_sha256": target_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_sha256": _sha(runtime_path),
        "formal_sources": formal_sources,
        "paper_app_count": 9, "lane_count": 13,
        "method_count": 2, "formal_worker_count": 208,
        "independent_row_count": 26,
        "activation_per_worker": 1, "registered_calls_per_worker": 2,
        "v3_required_or_executed": False,
        "formal_worker_executed": False,
        "registered_formal_timing_created": False,
        "formal_requires_second_exact_owner_authority": True,
    }
    plan_path = result_root / "PLAN.json"
    plan_path.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(native, result_root / "librtdl_optix.so")
    receipt = {
        "schema": "rtdl.goal5774.create_only_target_prepare_result.v1",
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "execution_source_sha256": _sha(execution_source),
        "native_library_sha256": native_sha256,
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "functional_result_sha256": _sha(functional),
        "functional_recount_sha256": _sha(recount),
        "all_78_functional_calls_correct_and_behavioral_true_optix": True,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "v3_required_or_executed": False,
        "formal_requires_second_exact_owner_authority": True,
    }
    receipt_path = result_root / "PREPARED.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create-only modern-RTX preparation for Goal5776 real-scale V2/V4."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _members(path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in result:
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            result[name] = handle.read()
    return result


def _extract_source(data: bytes, target: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in seen:
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


def _extract_data(path: Path, target: Path) -> dict[str, object]:
    observed: dict[str, dict[str, object]] = {}
    manifest_bytes = None
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in observed:
                raise RuntimeError(f"unsafe/duplicate data member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported data member: {member.name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable data member: {member.name}")
            if name == "DATA_MANIFEST.json":
                manifest_bytes = handle.read()
                observed[name] = {
                    "size_bytes": len(manifest_bytes),
                    "sha256": _sha_bytes(manifest_bytes),
                }
                continue
            if not name.startswith("DATA/"):
                raise RuntimeError(f"data payload outside DATA/: {name}")
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            size = 0
            with destination.open("xb") as stream:
                for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
                    size += len(chunk)
                    stream.write(chunk)
            observed[name] = {"size_bytes": size, "sha256": digest.hexdigest()}
    if manifest_bytes is None:
        raise RuntimeError("Goal5776 data archive lacks DATA_MANIFEST.json")
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "rtdl.goal5776.real_scale_data_manifest.v1":
        raise RuntimeError("unexpected Goal5776 data manifest")
    expected = {str(row["path"]): row for row in manifest["files"]}
    actual_names = set(observed) - {"DATA_MANIFEST.json"}
    if actual_names != set(expected):
        raise RuntimeError("Goal5776 data archive membership mismatch")
    for name, row in expected.items():
        actual = observed[name]
        if actual["size_bytes"] != int(row["size_bytes"]) \
                or actual["sha256"] != row["sha256"]:
            raise RuntimeError(f"Goal5776 data payload mismatch: {name}")
    (target / "DATA_MANIFEST.json").write_bytes(manifest_bytes)
    return manifest


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str], log: Path,
    timeout_seconds: int,
) -> str:
    try:
        completed = subprocess.run(
            command, cwd=cwd, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout if isinstance(exc.stdout, str) else ""
        log.write_text(partial, encoding="utf-8")
        raise RuntimeError(
            f"prepare command exceeded {timeout_seconds} seconds terminally: "
            f"{command!r}; see {log}"
        ) from exc
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"prepare command failed: {command!r}; see {log}")
    return completed.stdout


def _seal_read_only(root: Path) -> None:
    paths = [root, *root.rglob("*")]
    for path in sorted(paths, key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            raise RuntimeError(f"cannot seal symlink: {path}")
        path.chmod(path.stat().st_mode & ~0o222)


def _validate_authority(
    authority: dict[str, object], *, bundle_sha: str, source_sha: str,
    data_sha: str, expected_value_statement_sha: str,
    gpu: tuple[str, str, str, str], cc: str,
    python_identity: dict[str, str],
) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("Goal5776 prepare authority digest mismatch")
    expected = {
        "schema": "rtdl.goal5776.owner_create_only_prepare_authority.v2",
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "data_archive_sha256": data_sha,
        "expected_value_statement_sha256": expected_value_statement_sha,
        "required_gpu_name": gpu[0],
        "required_gpu_uuid": gpu[1],
        "required_driver_version": gpu[2],
        "required_compute_capability": cc,
        "required_cuda_toolkit": "12.8",
        "required_optix_sdk": "9.0.0",
        "required_python_executable_sha256": python_identity[
            "python_executable_sha256"],
        "required_python_version": python_identity["python"],
        "required_numba_version": python_identity["numba"],
        "required_numpy_version": python_identity["numpy"],
        "required_cupy_version": python_identity["cupy"],
        "required_scipy_version": python_identity["scipy"],
        "owner_authorized_create_only_prepare": True,
        "formal_worker_allowed": False,
        "registered_formal_timing_allowed": False,
    }
    if set(authority) != set(expected) | {"authority_sha256"}:
        raise PermissionError("Goal5776 prepare authority fields are not exact")
    for key, value in expected.items():
        if authority.get(key) != value:
            raise PermissionError(f"Goal5776 prepare authority mismatch: {key}")


def main() -> None:
    # This process imports the frozen formal-contract helpers after sealing the
    # source tree.  Prevent those imports from materializing writable pyc files
    # inside the already-sealed tree.
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    parser.add_argument("--optix-root", type=Path, required=True)
    parser.add_argument("--cuda-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    data_bundle = args.data_bundle.resolve()
    root = args.work_root.resolve()
    if root.exists():
        raise FileExistsError(root)
    outer = _members(bundle)
    manifest = json.loads(outer["PORTABLE_MANIFEST.json"])
    if (
        manifest.get("schema") != "rtdl.goal5776.real_scale_pre_pod_manifest.v1"
        or manifest.get("bundle_version") != 9
        or manifest.get("formal_worker_count") != 464
        or manifest.get("independent_comparison_row_count") != 34
        or manifest.get("v3_required_or_executed") is not False
    ):
        raise RuntimeError("unexpected Goal5776 source bundle")
    expected_outer = {row["path"]: row for row in manifest["payloads"]}
    if set(outer) != set(expected_outer) | {"PORTABLE_MANIFEST.json"}:
        raise RuntimeError("Goal5776 source bundle membership mismatch")
    for name, row in expected_outer.items():
        data = outer[name]
        if len(data) != row["size_bytes"] or _sha_bytes(data) != row["sha256"]:
            raise RuntimeError(f"Goal5776 source payload mismatch: {name}")
    budget_bytes = outer.get("RUNTIME_BUDGET.json")
    if budget_bytes is None:
        raise RuntimeError("Goal5776 source bundle lacks runtime budget")
    budget = json.loads(budget_bytes)
    budget_seconds = float(budget.get("conservative_budget_seconds", 0.0))
    if (
        budget.get("schema")
        != "rtdl.goal5776.home_derived_formal_runtime_budget.v1"
        or budget.get("not_a_performance_result") is not True
        or budget.get("worker_count") != 464
        or budget.get("formal_method_lifecycle_units") != 58
        or budget.get("owner_must_confirm_budget_before_worker_zero") is not True
        or _sha_bytes(budget_bytes) != manifest.get("runtime_budget_sha256")
        or budget_seconds != float(manifest.get("conservative_budget_seconds", 0.0))
        or not math.isfinite(budget_seconds) or budget_seconds <= 0.0
    ):
        raise RuntimeError("Goal5776 runtime budget payload is ineligible")
    expectation_bytes = outer.get("EXPECTED_VALUE_STATEMENT.md")
    if expectation_bytes is None or (
        _sha_bytes(expectation_bytes)
        != manifest.get("expected_value_statement_sha256")
    ):
        raise RuntimeError("Goal5776 expected-value statement is absent")
    bundle_sha = _sha(bundle)
    source_sha = _sha_bytes(outer["SOURCE.tar.gz"])
    data_sha = _sha(data_bundle)
    if data_sha != manifest["data_archive_sha256"]:
        raise RuntimeError("Goal5776 data bundle differs from source manifest")

    nvidia = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader"], text=True, capture_output=True, check=True,
        timeout=30)
    lines = [line.strip() for line in nvidia.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("Goal5776 prepare requires exactly one visible GPU")
    gpu = tuple(part.strip() for part in lines[0].split(","))
    if len(gpu) != 4 or gpu[3].replace(".", "") != args.cc:
        raise RuntimeError("Goal5776 target GPU mismatch")
    # Preserve the virtual-environment launcher spelling.  Resolving this
    # symlink on Linux selects the system interpreter and loses venv packages.
    python = Path(os.path.abspath(args.python))
    if not python.is_file():
        raise RuntimeError("Goal5776 target Python executable is missing")
    version_probe = subprocess.run([
        str(python), "-c",
        "import json,platform,numba,numpy,cupy,scipy; print(json.dumps({"
        "'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__,'cupy':cupy.__version__,"
        "'scipy':scipy.__version__},sort_keys=True))",
    ], text=True, capture_output=True, check=True, timeout=60)
    python_identity = {
        **json.loads(version_probe.stdout),
        "python_executable_sha256": _sha(python),
    }
    authority = json.loads(args.authority.read_text(encoding="utf-8"))
    _validate_authority(
        authority, bundle_sha=bundle_sha, source_sha=source_sha,
        data_sha=data_sha,
        expected_value_statement_sha=_sha_bytes(expectation_bytes),
        gpu=gpu, cc=args.cc,
        python_identity=python_identity)

    source = root / "source"
    logs = root / "logs"
    result = root / "result"
    data_extract = root / "data"
    for path in (source, logs, result, data_extract):
        path.mkdir(parents=True)
    runtime_budget = result / "RUNTIME_BUDGET.json"
    runtime_budget.write_bytes(budget_bytes)
    expected_value_statement = result / "EXPECTED_VALUE_STATEMENT.md"
    expected_value_statement.write_bytes(expectation_bytes)
    _extract_source(outer["SOURCE.tar.gz"], source)
    _run([
        str(python), "scripts/goal5776_verify_source_file_manifest.py",
        "--source-root", str(source),
        "--manifest", str(
            source / "history/internal_docs/goal5776_source_file_manifest.json"),
    ], cwd=source, env=dict(os.environ), log=logs / "source_manifest_check.log",
       timeout_seconds=300)
    data_manifest = _extract_data(data_bundle, data_extract)

    optix = args.optix_root.resolve()
    cuda = args.cuda_root.resolve()
    cuda_include = (
        cuda / "targets/x86_64-linux/include"
        if (cuda / "targets/x86_64-linux/include/cuda.h").is_file()
        else cuda / "include")
    if not python.is_file() or not (optix / "include/optix.h").is_file() \
            or not (cuda_include / "cuda.h").is_file() \
            or not (cuda / "bin/nvcc").is_file():
        raise RuntimeError("Goal5776 target toolchain paths are incomplete")
    nvcc = subprocess.run(
        [str(cuda / "bin/nvcc"), "--version"], text=True,
        capture_output=True, check=True, timeout=30).stdout
    if "release 12.8" not in nvcc:
        raise RuntimeError("Goal5776 target CUDA is not 12.8")
    optix_header = (optix / "include/optix.h").read_text(
        encoding="utf-8", errors="replace")
    if re.search(r"#\s*define\s+OPTIX_VERSION\s+90000\b", optix_header) is None:
        raise RuntimeError("Goal5776 target OptiX SDK is not 9.0")
    env = dict(os.environ)
    runtime_cache = result / "RUNTIME_CACHE"
    runtime_cache.mkdir()
    numba_cache = runtime_cache / "numba"
    cupy_cache = runtime_cache / "cupy"
    numba_cache.mkdir()
    cupy_cache.mkdir()
    env.update({
        "PYTHONPATH": f"{source / 'src'}:{source / 'scripts'}:{source}",
        "RTDL_V4_OPTIX_PREFIX": str(optix),
        "RTDL_V4_CUDA_PREFIX": str(cuda),
        "NVCC_PREPEND_FLAGS": "-allow-unsupported-compiler",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NUMBA_CACHE_DIR": str(numba_cache),
        "CUPY_CACHE_DIR": str(cupy_cache),
    })
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix}",
        f"CUDA_PREFIX={cuda}", f"OPTIX_CUDA_ARCH=sm_{args.cc}",
    ], cwd=source, env=env, log=logs / "build.log", timeout_seconds=1_800)
    native = (source / "build/librtdl_optix.so").resolve()
    if not native.is_file():
        raise RuntimeError("Goal5776 fresh native missing")
    native_sha = _sha(native)
    env["RTDL_OPTIX_LIB"] = str(native)
    env["RTDL_OPTIX_LIBRARY"] = str(native)
    tests = _run([
        str(python), "-m", "unittest", "discover", "-s", "tests",
        "-p", "goal5776*test.py",
    ], cwd=source, env=env, log=logs / "goal5776_tests.log",
       timeout_seconds=1_800)
    match = re.search(r"Ran (\d+) tests?", tests)
    if match is None or int(match.group(1)) != manifest["focused_test_count"] \
            or "OK" not in tests:
        raise RuntimeError("Goal5776 focused test cardinality/status mismatch")

    evidence = result / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    execution_source = result / "EXECUTION_SOURCE.tar.gz"
    rematerialization = result / "REMATERIALIZATION.json"
    _run([
        str(python), "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "--source-root", str(source), "--native", str(native),
        "--evidence-output", str(evidence),
        "--execution-source-output", str(execution_source),
        "--result-output", str(rematerialization),
    ], cwd=source, env=env, log=logs / "rematerialization.log",
       timeout_seconds=1_800)
    remat = json.loads(rematerialization.read_text(encoding="utf-8"))
    if remat.get("case_count") != 17 or remat.get("all_cases_exact") is not True \
            or remat.get("native_sha256") != native_sha:
        raise RuntimeError("Goal5776 fixed-radius rematerialization failed")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(evidence)

    cache = result / "FORMAL_NUMBA_LEAF_CACHE"
    cache_manifest = result / "FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json"
    functional_root = result / "TARGET_FUNCTIONAL"
    _run([
        str(python), "scripts/goal5776_target_real_scale_functional_prepare.py",
        "--source-root", str(source), "--native", str(native),
        "--optix-include", str(optix / "include"),
        "--cuda-include", str(cuda_include),
        "--compute-capability", args.cc,
        "--data-root", str(data_extract / "DATA"),
        "--rtdbscan-evidence", str(evidence),
        "--cache-root", str(cache),
        "--cache-manifest", str(cache_manifest),
        "--output-root", str(functional_root),
    ], cwd=source, env=env, log=logs / "target_functional.log",
       timeout_seconds=7_200)
    functional = json.loads(
        (functional_root / "SUMMARY.json").read_text(encoding="utf-8"))
    if (
        functional.get("functional_trial_count") != 126
        or functional.get("all_correct_and_behaviorally_true_optix") is not True
        or functional.get("formal_worker_count") != 0
        or functional.get("registered_formal_timing_count") != 0
        or int(functional.get("cache_population_observation_count", 0)) <= 0
        or functional.get("cache_population_cost_is_free") is not False
        or functional.get("cache_population_observation_is_not_formal_performance")
            is not True
    ):
        raise RuntimeError("Goal5776 target functional gate failed")

    sys.path.insert(0, str(source / "scripts"))
    from goal5769_rematerialize_fixed_radius_evidence import _tree_digest
    if _tree_digest(source) != remat["execution_tree_sha256"]:
        raise RuntimeError("Goal5776 product source drifted during target functional gate")

    # Formal workers consume exact prepared bytes.  Product source and input
    # data are sealed after the complete functional/cache-population gate;
    # only explicitly separated runtime caches and raw-result roots stay writable.
    _seal_read_only(source)
    _seal_read_only(data_extract)
    _seal_read_only(cache)
    _seal_read_only(functional_root)
    cache_manifest.chmod(cache_manifest.stat().st_mode & ~0o222)
    evidence.chmod(evidence.stat().st_mode & ~0o222)
    execution_source.chmod(execution_source.stat().st_mode & ~0o222)
    runtime_budget.chmod(runtime_budget.stat().st_mode & ~0o222)
    expected_value_statement.chmod(
        expected_value_statement.stat().st_mode & ~0o222)

    (logs / "versions.log").write_text(
        json.dumps(python_identity, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    versions = python_identity
    python_sha = python_identity["python_executable_sha256"]
    target_identity = _digest({
        "gpu": gpu, "cc": args.cc, "python": versions,
        "python_executable_sha256": python_sha, "native_sha256": native_sha,
    })
    from goal5776_real_scale_formal_contract import contract_sha256
    from goal5776_real_scale_runtime_inputs import build_real_scale_inputs
    inputs = build_real_scale_inputs(
        data_extract / "DATA", refinement_evidence_path=evidence)
    formal_names = (
        "goal5776_real_scale_formal_contract.py",
        "goal5776_real_scale_runtime_inputs.py",
        "goal5776_real_scale_frontdoors.py",
        "goal5776_real_scale_formal_worker.py",
        "goal5776_real_scale_formal_controller.py",
        "goal5776_evaluate_real_scale_v2_v4.py",
        "goal5776_recount_real_scale_v2_v4_raw.py",
    )
    formal_sources = {name: _sha(source / "scripts" / name) for name in formal_names}
    prepared_identity = _digest({
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "execution_source_sha256": _sha(execution_source),
        "execution_tree_sha256": remat["execution_tree_sha256"],
        "data_archive_sha256": data_sha,
        "data_archive_path": str(data_bundle),
        "data_root": str(data_extract / "DATA"),
        "data_manifest_path": str(data_extract / "DATA_MANIFEST.json"),
        "data_manifest_sha256": _sha(data_extract / "DATA_MANIFEST.json"),
        "source_root": str(source),
        "execution_source_path": str(execution_source),
        "rtdbscan_evidence_path": str(evidence),
        "rtdbscan_evidence_sha256": _sha(evidence),
        "runtime_budget_path": str(runtime_budget),
        "runtime_budget_sha256": _sha(runtime_budget),
        "expected_value_statement_sha256": _sha(expected_value_statement),
        "conservative_budget_seconds": budget_seconds,
        "native_sha256": native_sha,
        "target_identity_sha256": target_identity,
        "functional_summary_sha256": _sha(functional_root / "SUMMARY.json"),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
    })
    formal_identity = _digest({
        "prepared_identity_sha256": prepared_identity,
        "formal_sources": formal_sources,
        "formal_contract_sha256": contract_sha256(),
        "worker_count": 464, "row_count": 34,
    })
    runtime = {
        "schema": "rtdl.goal5776.real_scale_runtime.v1",
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "execution_source_sha256": _sha(execution_source),
        "source_tree_sha256": remat["execution_tree_sha256"],
        "source_root": str(source),
        "execution_source_path": str(execution_source),
        "data_archive_path": str(data_bundle),
        "data_archive_sha256": data_sha,
        "data_root": str(data_extract / "DATA"),
        "data_manifest_path": str(data_extract / "DATA_MANIFEST.json"),
        "data_manifest_sha256": _sha(data_extract / "DATA_MANIFEST.json"),
        "rtdbscan_evidence_path": str(evidence),
        "rtdbscan_evidence_sha256": _sha(evidence),
        "native_library_path": str(native),
        "native_library_sha256": native_sha,
        "target": {
            "provider": "optix", "optix_sdk": "9.0.0",
            "compute_capability": f"{args.cc[0]}.{args.cc[1]}",
            "native_sha256": native_sha,
            "supports_custom_aabb": True, "supports_builtin_triangle": True,
        },
        "compute_capability": [int(args.cc[0]), int(args.cc[1])],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(optix / "include"),
        "cuda_include": str(cuda_include),
        "python_executable": str(python),
        "python_executable_sha256": python_sha,
        "python_version": versions["python"],
        "numba_version": versions["numba"],
        "numpy_version": versions["numpy"],
        "cupy_version": versions["cupy"],
        "scipy_version": versions["scipy"],
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_budget_path": str(runtime_budget),
        "runtime_budget_sha256": _sha(runtime_budget),
        "expected_value_statement_path": str(expected_value_statement),
        "expected_value_statement_sha256": _sha(expected_value_statement),
        "conservative_budget_seconds": budget_seconds,
        "plan_sha256": "pending_until_plan_materialization",
        "formal_contract_sha256": contract_sha256(),
        "leaf_cache_root": str(cache),
        "leaf_cache_manifest_path": str(cache_manifest),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
        "target_functional_root": str(functional_root),
        "target_functional_summary_sha256": _sha(functional_root / "SUMMARY.json"),
        "inputs": inputs,
        "formal_worker_environment": {
            name: env.get(name) for name in (
                "PYTHONPATH", "PATH", "LD_LIBRARY_PATH",
                "PYTHONDONTWRITEBYTECODE", "NUMBA_CACHE_DIR", "CUPY_CACHE_DIR",
                "RTDL_V4_OPTIX_PREFIX", "RTDL_V4_CUDA_PREFIX",
                "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
                "RTDL_OPTIX_LIB", "RTDL_OPTIX_LIBRARY")
        },
    }
    plan = {
        "schema": "rtdl.goal5776.real_scale_plan.v1",
        "bundle_sha256": bundle_sha,
        "data_archive_sha256": data_sha,
        "prepared_identity_sha256": prepared_identity,
        "target_identity_sha256": target_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_budget_sha256": _sha(runtime_budget),
        "expected_value_statement_sha256": _sha(expected_value_statement),
        "conservative_budget_seconds": budget_seconds,
        "formal_sources": formal_sources,
        "paper_app_count": 9, "functional_execution_unit_count": 32,
        "formal_execution_unit_count": 15,
        "formal_worker_count": 464, "independent_row_count": 34,
        "v3_required_or_executed": False,
        "formal_worker_executed": False,
        "registered_formal_timing_created": False,
        "formal_requires_second_exact_owner_authority": True,
    }
    plan_path = result / "PLAN.json"
    plan_path.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    runtime["plan_sha256"] = _sha(plan_path)
    runtime_path = result / "RUNTIME.json"
    runtime_path.write_text(
        json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(native, result / "librtdl_optix.so")
    receipt = {
        "schema": "rtdl.goal5776.create_only_target_prepare_result.v1",
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "data_archive_sha256": data_sha,
        "rtdbscan_evidence_sha256": _sha(evidence),
        "execution_source_sha256": _sha(execution_source),
        "native_library_sha256": native_sha,
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_budget_sha256": _sha(runtime_budget),
        "expected_value_statement_sha256": _sha(expected_value_statement),
        "conservative_budget_seconds": budget_seconds,
        "plan_sha256": _sha(plan_path),
        "runtime_sha256": _sha(runtime_path),
        "python_environment": dict(python_identity),
        "target_functional_summary_sha256": _sha(functional_root / "SUMMARY.json"),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
        "all_126_functional_trials_correct_and_behavioral_true_optix": True,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "formal_requires_second_exact_owner_authority": True,
    }
    (result / "PREPARED.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

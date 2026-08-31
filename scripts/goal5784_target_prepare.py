#!/usr/bin/env python3
"""Create-only modern-RTX preparation for exact Goal5784 targeted cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

from goal5776_target_prepare import (
    _digest, _extract_data, _extract_source, _members, _run,
    _seal_read_only, _sha, _sha_bytes,
)


def _validate_authority(authority: dict[str, object], *, bundle_sha: str,
                        source_sha: str, data_sha: str, prereg_sha: str,
                        budget_sha: str, expectation_sha: str,
                        gpu: tuple[str, str, str, str], cc: str,
                        python_identity: dict[str, str]) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("Goal5784 prepare authority digest mismatch")
    expected = {
        "schema": "rtdl.goal5784.owner_create_only_prepare_authority.v1",
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "data_archive_sha256": data_sha,
        "preregistration_sha256": prereg_sha,
        "runtime_budget_sha256": budget_sha,
        "expected_value_statement_sha256": expectation_sha,
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
        raise PermissionError("Goal5784 prepare authority fields are not exact")
    for key, value in expected.items():
        if authority.get(key) != value:
            raise PermissionError(f"Goal5784 prepare authority mismatch: {key}")


def main() -> None:
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--cc", choices=("89",), required=True)
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
        manifest.get("schema") != "rtdl.goal5784.targeted_pre_pod_manifest.v1"
        or manifest.get("bundle_version") != 5
        or manifest.get("formal_worker_count") != 128
        or manifest.get("independent_comparison_row_count") != 8
        or manifest.get("v3_required_or_executed") is not False
    ):
        raise RuntimeError("unexpected Goal5784 bundle")
    expected_outer = {row["path"]: row for row in manifest["payloads"]}
    if set(outer) != set(expected_outer) | {"PORTABLE_MANIFEST.json"}:
        raise RuntimeError("Goal5784 bundle membership mismatch")
    for name, row in expected_outer.items():
        data = outer[name]
        if len(data) != row["size_bytes"] or _sha_bytes(data) != row["sha256"]:
            raise RuntimeError(f"Goal5784 bundle payload mismatch: {name}")
    bundle_sha = _sha(bundle)
    source_sha = _sha_bytes(outer["SOURCE.tar.gz"])
    data_sha = _sha(data_bundle)
    if source_sha != manifest["source_archive_sha256"] \
            or data_sha != manifest["data_archive_sha256"]:
        raise RuntimeError("Goal5784 source/data identity mismatch")
    prereg_bytes = outer["PREREGISTRATION.json"]
    budget_bytes = outer["RUNTIME_BUDGET.json"]
    expectation_bytes = outer["EXPECTED_VALUE_STATEMENT.md"]
    budget = json.loads(budget_bytes)
    if (
        budget.get("schema") != "rtdl.goal5784.targeted_formal_runtime_budget.v1"
        or budget.get("worker_count") != 128
        or budget.get("not_a_performance_result") is not True
        or budget.get("owner_must_confirm_budget_before_worker_zero") is not True
        or not math.isfinite(float(budget.get(
            "total_transaction_conservative_budget_seconds", 0.0)))
        or float(budget["total_transaction_conservative_budget_seconds"]) <= 0.0
    ):
        raise RuntimeError("Goal5784 runtime budget is ineligible")
    nvidia = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader"], text=True, capture_output=True, check=True,
        timeout=30)
    gpu_lines = [line.strip() for line in nvidia.stdout.splitlines() if line.strip()]
    if len(gpu_lines) != 1:
        raise RuntimeError("Goal5784 requires exactly one visible GPU")
    gpu = tuple(part.strip() for part in gpu_lines[0].split(","))
    if len(gpu) != 4 or gpu[3].replace(".", "") != args.cc:
        raise RuntimeError("Goal5784 target GPU mismatch")
    python = args.python.resolve()
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
        data_sha=data_sha, prereg_sha=_sha_bytes(prereg_bytes),
        budget_sha=_sha_bytes(budget_bytes),
        expectation_sha=_sha_bytes(expectation_bytes), gpu=gpu, cc=args.cc,
        python_identity=python_identity)

    source = root / "source"
    harness = root / "harness"
    logs = root / "logs"
    result = root / "result"
    data_extract = root / "data"
    for path in (source, harness, logs, result, data_extract):
        path.mkdir(parents=True)
    _extract_source(outer["SOURCE.tar.gz"], source)
    for name, data in outer.items():
        if name.startswith("HARNESS/"):
            destination = harness / name.removeprefix("HARNESS/")
            if "/" in name.removeprefix("HARNESS/"):
                destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    data_manifest = _extract_data(data_bundle, data_extract)
    prereg = result / "PREREGISTRATION.json"
    runtime_budget = result / "RUNTIME_BUDGET.json"
    expectation = result / "EXPECTED_VALUE_STATEMENT.md"
    prereg.write_bytes(prereg_bytes)
    runtime_budget.write_bytes(budget_bytes)
    expectation.write_bytes(expectation_bytes)

    optix = args.optix_root.resolve()
    cuda = args.cuda_root.resolve()
    cuda_include = (cuda / "targets/x86_64-linux/include"
                    if (cuda / "targets/x86_64-linux/include/cuda.h").is_file()
                    else cuda / "include")
    if not (optix / "include/optix.h").is_file() \
            or not (cuda_include / "cuda.h").is_file() \
            or not (cuda / "bin/nvcc").is_file():
        raise RuntimeError("Goal5784 target toolchain is incomplete")
    nvcc = subprocess.run([str(cuda / "bin/nvcc"), "--version"], text=True,
                          capture_output=True, check=True, timeout=30).stdout
    if "release 12.8" not in nvcc:
        raise RuntimeError("Goal5784 target CUDA is not 12.8")
    optix_header = (optix / "include/optix.h").read_text(
        encoding="utf-8", errors="replace")
    if re.search(r"#\s*define\s+OPTIX_VERSION\s+90000\b", optix_header) is None:
        raise RuntimeError("Goal5784 target OptiX SDK is not 9.0")
    runtime_cache = result / "RUNTIME_CACHE"
    numba_cache = runtime_cache / "numba"
    cupy_cache = runtime_cache / "cupy"
    numba_cache.mkdir(parents=True)
    cupy_cache.mkdir()
    env = dict(os.environ)
    env.update({
        "PYTHONPATH": f"{harness}:{source / 'src'}:{source / 'scripts'}:{source}",
        "RTDL_V4_OPTIX_PREFIX": str(optix),
        "RTDL_V4_CUDA_PREFIX": str(cuda),
        "NVCC_PREPEND_FLAGS": "-allow-unsupported-compiler",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NUMBA_CACHE_DIR": str(numba_cache),
        "CUPY_CACHE_DIR": str(cupy_cache),
        "RTDL_GOAL5784_PREREGISTRATION_PATH": str(prereg),
        "RTDL_GOAL5784_RUNTIME_BUDGET_PATH": str(runtime_budget),
        "RTDL_GOAL5784_EXPECTED_VALUE_STATEMENT_PATH": str(expectation),
        "RTDL_GOAL5784_HARNESS_ROOT": str(harness),
    })
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix}",
        f"CUDA_PREFIX={cuda}", "OPTIX_CUDA_ARCH=sm_89",
    ], cwd=source, env=env, log=logs / "build.log", timeout_seconds=1_800)
    native = (source / "build/librtdl_optix.so").resolve()
    if not native.is_file():
        raise RuntimeError("Goal5784 fresh native missing")
    native_sha = _sha(native)
    env["RTDL_OPTIX_LIB"] = str(native)
    env["RTDL_OPTIX_LIBRARY"] = str(native)
    tests = _run([
        str(python), "-m", "unittest",
        "tests.goal5778_v4_checked_u64_device_reduction_test",
        "tests.goal5782_canonical_packed_hierarchy_binding_test",
        "goal5784_targeted_pre_pod_test",
    ], cwd=source, env=env, log=logs / "focused_tests.log",
       timeout_seconds=1_800)
    match = re.search(r"Ran (\d+) tests?", tests)
    if match is None or int(match.group(1)) != manifest["focused_test_count"] \
            or "OK" not in tests:
        raise RuntimeError("Goal5784 focused test gate failed")

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
        raise RuntimeError("Goal5784 fixed-radius rematerialization failed")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(evidence)

    cache = result / "FORMAL_NUMBA_LEAF_CACHE"
    cache_manifest = result / "FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json"
    functional_root = result / "TARGET_FUNCTIONAL"
    _run([
        str(python), str(harness / "goal5784_target_functional_prepare.py"),
        "--source-root", str(source), "--native", str(native),
        "--optix-include", str(optix / "include"),
        "--cuda-include", str(cuda_include), "--compute-capability", "89",
        "--data-root", str(data_extract / "DATA"),
        "--cache-root", str(cache), "--cache-manifest", str(cache_manifest),
        "--output-root", str(functional_root),
        "--execution-source-sha256", _sha(execution_source),
    ], cwd=source, env=env, log=logs / "target_functional.log",
       timeout_seconds=7_200)
    functional = json.loads(
        (functional_root / "SUMMARY.json").read_text(encoding="utf-8"))
    if functional.get("functional_trial_count") != 16 \
            or functional.get("all_correct_and_behaviorally_true_optix") is not True \
            or functional.get("triangle_v4_mechanism_bound_trial_count") != 6 \
            or functional.get("triangle_v4_mechanism_binding_complete") is not True \
            or functional.get("formal_worker_count") != 0 \
            or functional.get("registered_formal_timing_count") != 0:
        raise RuntimeError("Goal5784 target functional gate failed")

    _seal_read_only(source)
    _seal_read_only(harness)
    _seal_read_only(data_extract)
    _seal_read_only(cache)
    _seal_read_only(functional_root)
    for path in (cache_manifest, evidence, execution_source, prereg,
                 runtime_budget, expectation):
        path.chmod(path.stat().st_mode & ~0o222)
    sys.path.insert(0, str(harness))
    sys.path.insert(1, str(source / "scripts"))
    from goal5784_targeted_formal_contract import (
        contract_sha256, schedule, statistical_rows)
    from goal5784_targeted_runtime_inputs import build_targeted_inputs
    inputs = build_targeted_inputs(data_extract / "DATA")
    target_identity = _digest({
        "gpu": gpu, "cc": args.cc, "python": python_identity,
        "native_sha256": native_sha,
    })
    formal_names = (
        "goal5784_mechanism_binding.py",
        "goal5784_targeted_formal_contract.py",
        "goal5784_targeted_runtime_inputs.py",
        "goal5784_targeted_worker.py",
        "goal5784_targeted_controller.py",
        "goal5784_targeted_evaluate.py",
        "goal5784_targeted_recount.py",
    )
    formal_sources = {name: {
        "path": str(harness / name), "sha256": _sha(harness / name),
    } for name in formal_names}
    for name in (
        "goal5776_real_scale_frontdoors.py",
        "goal5776_real_scale_formal_worker.py",
        "goal5776_evaluate_real_scale_v2_v4.py",
        "goal5776_symmetric_endpoint.py",
    ):
        formal_sources[f"base::{name}"] = {
            "path": str(source / "scripts" / name),
            "sha256": _sha(source / "scripts" / name),
        }
    prepared_identity = _digest({
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "execution_source_sha256": _sha(execution_source),
        "source_tree_sha256": remat["execution_tree_sha256"],
        "data_archive_sha256": data_sha,
        "native_sha256": native_sha,
        "target_identity_sha256": target_identity,
        "functional_summary_sha256": _sha(functional_root / "SUMMARY.json"),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
        "preregistration_sha256": _sha(prereg),
    })
    formal_identity = _digest({
        "prepared_identity_sha256": prepared_identity,
        "formal_sources": formal_sources,
        "formal_contract_sha256": contract_sha256(),
        "worker_count": len(schedule()),
        "row_count": len(statistical_rows()),
    })
    plan = {
        "schema": "rtdl.goal5784.targeted_plan.v1",
        "bundle_sha256": bundle_sha,
        "data_archive_sha256": data_sha,
        "prepared_identity_sha256": prepared_identity,
        "target_identity_sha256": target_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_budget_sha256": _sha(runtime_budget),
        "expected_value_statement_sha256": _sha(expectation),
        "preregistration_sha256": _sha(prereg),
        "formal_contract_sha256": contract_sha256(),
        "formal_sources": formal_sources,
        "formal_worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "v3_required_or_executed": False,
        "formal_worker_executed": False,
        "registered_formal_timing_created": False,
        "formal_requires_second_exact_owner_authority": True,
    }
    plan_path = result / "PLAN.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8", newline="\n")
    runtime = {
        "schema": "rtdl.goal5776.real_scale_runtime.v1",
        "run_goal_id": 5784,
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "execution_source_sha256": _sha(execution_source),
        "source_tree_sha256": remat["execution_tree_sha256"],
        "source_root": str(source), "harness_root": str(harness),
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
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "runtime_budget_path": str(runtime_budget),
        "runtime_budget_sha256": _sha(runtime_budget),
        "formal_conservative_budget_seconds": float(
            budget["formal_conservative_budget_seconds"]),
        "expected_value_statement_path": str(expectation),
        "expected_value_statement_sha256": _sha(expectation),
        "preregistration_path": str(prereg),
        "preregistration_sha256": _sha(prereg),
        "plan_sha256": _sha(plan_path),
        "formal_contract_sha256": contract_sha256(),
        "leaf_cache_root": str(cache),
        "leaf_cache_manifest_path": str(cache_manifest),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
        "target_functional_root": str(functional_root),
        "target_functional_summary_sha256": _sha(functional_root / "SUMMARY.json"),
        "python_executable": str(python),
        "python_executable_sha256": python_identity["python_executable_sha256"],
        "python_version": python_identity["python"],
        "numba_version": python_identity["numba"],
        "numpy_version": python_identity["numpy"],
        "cupy_version": python_identity["cupy"],
        "scipy_version": python_identity["scipy"],
        # These four fields are consumed by every V4 formal front door.  They
        # must be carried by the sealed formal runtime just as they are by the
        # functional runtime; otherwise V2 worker 0 can succeed while V4
        # worker 1 fails before entering the endpoint.
        "compute_capability": [8, 9],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(optix / "include"),
        "cuda_include": str(cuda_include),
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
    runtime_path = result / "RUNTIME.json"
    runtime_path.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8", newline="\n")
    shutil.copy2(native, result / "librtdl_optix.so")
    receipt = {
        "schema": "rtdl.goal5784.create_only_target_prepare_result.v1",
        "bundle_sha256": bundle_sha,
        "source_archive_sha256": source_sha,
        "data_archive_sha256": data_sha,
        "execution_source_sha256": _sha(execution_source),
        "native_library_sha256": native_sha,
        "target_identity_sha256": target_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
        "plan_sha256": _sha(plan_path),
        "runtime_sha256": _sha(runtime_path),
        "formal_contract_sha256": contract_sha256(),
        "leaf_cache_manifest_sha256": _sha(cache_manifest),
        "all_16_functional_trials_correct_and_behavioral_true_optix": True,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "formal_requires_second_exact_owner_authority": True,
    }
    (result / "PREPARED.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

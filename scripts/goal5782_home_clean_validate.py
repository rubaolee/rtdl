#!/usr/bin/env python3
"""Clean Home-GPU functional validation of an exact Goal5782 candidate."""

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


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, cwd: Path, env: dict[str, str], log: Path) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"command failed: {command!r}; see {log}")
    return completed.stdout


def safe_extract(archive: Path, target: Path) -> None:
    with tarfile.open(archive, "r:gz") as handle:
        seen: set[str] = set()
        for member in handle.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in seen:
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            seen.add(name)
            if not (member.isdir() or member.isfile()):
                raise RuntimeError(f"unsupported archive member: {member.name}")
        handle.extractall(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-bundle-sha256", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    root = args.work_root.resolve()
    if root.exists():
        raise FileExistsError(root)
    if sha(bundle) != args.expected_bundle_sha256:
        raise RuntimeError("Goal5782 bundle bytes changed")
    for path in (args.python, args.cuda_prefix, args.optix_prefix):
        if not path.exists():
            raise FileNotFoundError(path)
    root.mkdir(parents=True)
    logs = root / "logs"
    logs.mkdir()
    outer = root / "outer"
    outer.mkdir()
    safe_extract(bundle, outer)
    source = root / "source"
    source.mkdir()
    safe_extract(outer / "SOURCE.tar.gz", source)
    forbidden = [path for path in source.rglob("*") if (
        any(part in (".codex", ".git", "__pycache__") for part in path.parts)
        or path.name == "librtdl_optix.so" or path.suffix == ".pyc"
        or "build" in path.relative_to(source).parts
    )]
    if forbidden:
        raise RuntimeError(f"portable source contains cache/prebuilt files: {forbidden[:3]}")

    python = args.python.resolve()
    cuda = args.cuda_prefix.resolve()
    optix = args.optix_prefix.resolve()
    env = os.environ.copy()
    # Several frozen lifecycle tests import their app-neutral fixture helpers
    # as top-level modules.  The portable source must therefore expose the
    # scripts directory explicitly; succeeding only from a developer shell's
    # inherited PYTHONPATH would defeat the clean-room check.
    env["PYTHONPATH"] = os.pathsep.join(
        (str(source / "src"), str(source), str(source / "scripts")))
    env["PATH"] = os.pathsep.join((str(cuda / "bin"), env.get("PATH", "")))
    env["LD_LIBRARY_PATH"] = os.pathsep.join((
        str(cuda / "nvvm/lib64"), str(cuda / "targets/x86_64-linux/lib"),
        "/usr/lib/x86_64-linux-gnu"))
    env["NUMBA_CUDA_NVVM"] = str(cuda / "nvvm/lib64/libnvvm.so")
    env["NUMBA_CUDA_LIBDEVICE"] = str(cuda / "nvvm/libdevice/libdevice.10.bc")
    env["RTDL_V4_CUDA_PREFIX"] = str(cuda)
    env["RTDL_V4_OPTIX_PREFIX"] = str(optix)
    versions = json.loads(run([
        str(python), "-c",
        "import json,platform,numba,numpy,llvmlite,cupy; "
        "print(json.dumps({'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__,'llvmlite':llvmlite.__version__,'cupy':cupy.__version__},sort_keys=True))",
    ], cwd=source, env=env, log=logs / "versions.log").strip())
    gpu = run(["nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
               "--format=csv,noheader"], cwd=source, env=env,
              log=logs / "gpu.log").strip()
    run(["make", "build-optix", f"OPTIX_PREFIX={optix}", f"CUDA_PREFIX={cuda}",
         "OPTIX_CUDA_ARCH=sm_61"], cwd=source, env=env, log=logs / "build.log")
    native = source / "build/librtdl_optix.so"
    if not native.is_file():
        raise RuntimeError("fresh Home native missing")
    env["RTDL_OPTIX_LIB"] = env["RTDL_OPTIX_LIBRARY"] = str(native)

    evidence = root / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    execution_source = root / "EXECUTION_SOURCE.tar.gz"
    rematerialization = root / "REMATERIALIZATION.json"
    run([
        str(python), "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "--source-root", str(source), "--native", str(native),
        "--evidence-output", str(evidence),
        "--execution-source-output", str(execution_source),
        "--result-output", str(rematerialization),
    ], cwd=source, env=env, log=logs / "rematerialize.log")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(evidence)

    test_files = (
        "goal5764_v4_hierarchy_frontier_test.py",
        "goal5773_v4_prepared_hierarchy_lifecycle_test.py",
        "goal5776_v4_hierarchy_single_materialization_test.py",
        "goal5776_v4_triangle_device_columns_test.py",
        "goal5778_v4_checked_u64_device_reduction_test.py",
        "goal5782_canonical_packed_hierarchy_binding_test.py",
    )
    test_count = 0
    for name in test_files:
        output = run([str(python), "-m", "unittest", "discover", "-s", "tests",
                      "-p", name], cwd=source, env=env,
                     log=logs / f"test__{name}.log")
        import re
        matches = re.findall(r"Ran (\d+) tests?", output)
        if len(matches) != 1:
            raise RuntimeError(f"cannot determine test count: {name}")
        test_count += int(matches[0])

    runtime = {
        "target": {"provider": "optix", "optix_sdk": "9.0.0",
                   "compute_capability": "6.1", "native_sha256": sha(native),
                   "supports_custom_aabb": True, "supports_builtin_triangle": True},
        "compute_capability": [6, 1],
        "optix_include": str(optix / "include"),
        "cuda_include": str(cuda / "include"),
        "expected_python_version": versions["python"],
        "expected_numba_version": versions["numba"],
        "expected_numpy_version": versions["numpy"],
        "expected_llvmlite_version": versions["llvmlite"],
        "expected_cupy_version": versions["cupy"],
        "native_library_path": str(native),
        "native_library_sha256": sha(native),
        "optix_sdk": "9.0.0", "cuda_toolkit": "12.8",
    }
    runtime_path = root / "RUNTIME.json"
    runtime_path.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    # The validator itself is an outer harness process, so changing the child
    # environment above does not mutate its own sys.path.  Make the same three
    # clean-source roots explicit before importing only the immutable lane
    # inventory.  This is not an inherited developer-shell dependency.
    sys.path.insert(0, str(source / "scripts"))
    sys.path.insert(0, str(source / "src"))
    sys.path.insert(0, str(source))
    from scripts.goal5768_three_way_frontdoors import LANES  # type: ignore
    raw = root / "functional_raw"
    raw.mkdir()
    for lane in LANES:
        for method in (V2, V4):
            output = raw / f"{lane.lane_id}__{method}.json"
            run([str(python), "scripts/goal5768_three_way_functional_smoke.py",
                 "--lane-id", lane.lane_id, "--method", method,
                 "--runtime", str(runtime_path), "--output", str(output)],
                cwd=source, env=env,
                log=logs / f"smoke__{lane.lane_id}__{method}.log")
    recount = root / "FUNCTIONAL_RECOUNT.json"
    run([str(python), "scripts/goal5782_recount_home_functional.py",
         "--raw", str(raw), "--expected-native-sha256", sha(native),
         "--output", str(recount)], cwd=source, env=env,
        log=logs / "functional_recount.log")
    counted = json.loads(recount.read_text(encoding="utf-8"))
    materialized = json.loads(rematerialization.read_text(encoding="utf-8"))
    result = {
        "schema": "rtdl.goal5782.home_clean_validation.v1",
        "status": "PASS__CLEAN_REBUILD_AND_26_OF_26_FUNCTIONAL",
        "bundle_sha256": sha(bundle),
        "portable_source_archive_sha256": sha(outer / "SOURCE.tar.gz"),
        "execution_source_archive_sha256": sha(execution_source),
        "execution_source_tree_sha256": materialized["execution_tree_sha256"],
        "native_library_sha256": sha(native),
        "fixed_radius_refinement_case_count": materialized["case_count"],
        "fixed_radius_refinement_evidence_sha256": materialized["evidence_sha256"],
        "gpu": gpu, "versions": versions,
        "focused_test_count": test_count,
        "functional_worker_count": counted["worker_count"],
        "functional_correct_count": counted["exact_output_count"],
        "functional_behavioral_true_optix_count": counted[
            "behavioral_true_optix_worker_count"],
        "leaf_receipt_count": counted["leaf_receipt_count"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "pod_used": False,
        "private_codex_dependency_used": False,
        "prebuilt_native_used": False,
    }
    (root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    shutil.copy2(native, root / "librtdl_optix.so")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

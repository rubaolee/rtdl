#!/usr/bin/env python3
"""Create-only Home Linux validation of an exact Goal5769 bundle.

This is a local functional validator, not an execution authority and not a
performance worker.  It deliberately cannot launch the formal controller.
"""

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
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or path.is_absolute() or ".." in parts or name in seen:
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            seen.add(name)
            if not (member.isfile() or member.isdir()):
                raise RuntimeError(f"unsupported archive member: {member.name}")
        handle.extractall(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-bundle-sha256", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    root = args.work_root.resolve()
    if root.exists():
        raise FileExistsError(root)
    if sha(bundle) != args.expected_bundle_sha256:
        raise RuntimeError("Home bundle bytes differ from exact candidate")
    root.mkdir(parents=True)
    logs = root / "logs"
    logs.mkdir()
    outer = root / "outer"
    outer.mkdir()
    safe_extract(bundle, outer)
    sys.path.insert(0, str(outer / "HARNESS"))
    from goal5768_target_prepare import (  # type: ignore
        _read_outer_bundle, _safe_extract, _sha, _validate_receipt)
    from goal5769_pre_pod_admission import (  # type: ignore
        expected_test_count, parse_unittest_count,
        validate_exact_test_manifest, validate_toolchain_policy)
    payloads = _read_outer_bundle(bundle)
    policy = json.loads(payloads["TOOLCHAIN/TOOLCHAIN_POLICY.json"])
    tests = json.loads(payloads["POLICY/EXACT_TEST_MANIFEST.json"])
    validate_toolchain_policy(policy, payloads=payloads)
    source = root / "source"
    source.mkdir()
    _safe_extract(outer / "SOURCE.tar.gz", source)
    validate_exact_test_manifest(source, tests)

    python = Path(policy["python_executable"])
    if not python.is_file() or platform.python_version() != policy["versions"]["python"]:
        raise RuntimeError("Home Python differs from Goal5769 policy")
    toolchain = root / "toolchain"
    toolchain.mkdir()
    for package in sorted((outer / "TOOLCHAIN/cuda_debs").glob("*.deb")):
        run(["dpkg-deb", "-x", str(package), str(toolchain)],
            cwd=source, env=os.environ.copy(), log=logs / f"extract__{package.name}.log")
    cuda = toolchain / "usr/local/cuda-12.8"
    optix = root / "optix"
    optix.mkdir()
    _safe_extract(outer / "TOOLCHAIN/optix9_include.tar.gz", optix)
    site = root / "python_site"
    site.mkdir()
    wheels = sorted((outer / "TOOLCHAIN/wheelhouse").glob("*.whl"))
    run([str(python), "-m", "pip", "install", "--no-index", "--no-deps",
         "--target", str(site), *(str(path) for path in wheels)],
        cwd=source, env=os.environ.copy(), log=logs / "pip_install.log")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(source / "src"), str(source), str(site)))
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
    if any(versions[name] != policy["versions"][name]
           for name in ("python", "numba", "numpy", "llvmlite", "cupy")):
        raise RuntimeError("Home installed Python partners differ from policy")
    for pattern, name in (("goal57*_v4_*test.py", "focused"),
                          ("goal5768_*test.py", "goal5768")):
        output = run([str(python), "-m", "unittest", "discover", "-s", "tests",
                      "-p", pattern], cwd=source, env=env,
                     log=logs / f"{name}_tests.log")
        if parse_unittest_count(output) != expected_test_count(tests, pattern):
            raise RuntimeError(f"Home test cardinality mismatch: {pattern}")

    gpu = run(["nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
               "--format=csv,noheader"], cwd=source, env=env,
              log=logs / "nvidia_smi.log").strip()
    columns = tuple(part.strip() for part in gpu.split(","))
    if len(columns) != 4 or columns[0] != "NVIDIA GeForce GTX 1070" \
            or columns[2] != "580.126.09" or columns[3] != "6.1":
        raise RuntimeError("Home GPU identity changed")
    if "V12.8.93" not in run([str(cuda / "bin/nvcc"), "--version"],
                              cwd=source, env=env, log=logs / "nvcc.log"):
        raise RuntimeError("bundled NVCC version changed")
    run(["make", "build-optix", f"OPTIX_PREFIX={optix}", f"CUDA_PREFIX={cuda}",
         "OPTIX_CUDA_ARCH=sm_61"], cwd=source, env=env, log=logs / "build.log")
    native = source / "build/librtdl_optix.so"
    if not native.is_file():
        raise RuntimeError("Home fresh native missing")
    env["RTDL_OPTIX_LIB"] = str(native)
    env["RTDL_OPTIX_LIBRARY"] = str(native)
    evidence = root / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    execution_source = root / "EXECUTION_SOURCE.tar.gz"
    rematerialization = root / "FIXED_RADIUS_REMATERIALIZATION.json"
    run([
        str(python), "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "--source-root", str(source), "--native", str(native),
        "--evidence-output", str(evidence),
        "--execution-source-output", str(execution_source),
        "--result-output", str(rematerialization),
    ], cwd=source, env=env, log=logs / "fixed_radius_rematerialization.log")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(evidence)
    materialized = json.loads(rematerialization.read_text(encoding="utf-8"))
    runtime = {
        "target": {"provider": "optix", "optix_sdk": "9.0.0",
                   "compute_capability": "6.1", "native_sha256": _sha(native),
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
        "native_library_sha256": _sha(native),
        "optix_sdk": "9.0.0", "cuda_toolkit": "12.8",
    }
    runtime_path = root / "RUNTIME.json"
    runtime_path.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    sys.path.insert(0, str(site))
    sys.path.insert(0, str(source / "src"))
    sys.path.insert(0, str(source))
    from scripts.goal5768_three_way_frontdoors import LANES, METHODS  # type: ignore
    raw = root / "functional_raw"
    raw.mkdir()
    records = []
    for lane in LANES:
        for method in METHODS:
            output = raw / f"{lane.lane_id}__{method}.json"
            run([str(python), "scripts/goal5768_three_way_functional_smoke.py",
                 "--lane-id", lane.lane_id, "--method", method,
                 "--runtime", str(runtime_path), "--output", str(output)],
                cwd=source, env=env, log=logs / f"smoke__{lane.lane_id}__{method}.log")
            record = json.loads(output.read_text())
            _validate_receipt(record["endpoint"], _sha(native))
            records.append(record)
    if len(records) != 39 or len({row["parent_pid"] for row in records}) != 39:
        raise RuntimeError("Home functional cohort is not 39 fresh processes")
    for lane in LANES:
        cohort = [row for row in records if row["lane_id"] == lane.lane_id]
        if len({row["endpoint"]["input_sha256"] for row in cohort}) != 1 \
                or len({row["endpoint"]["output_sha256"] for row in cohort}) != 1:
            raise RuntimeError(f"Home three-way identity mismatch: {lane.lane_id}")
    result = {
        "schema": "rtdl.goal5769.home_clean_validation.v1",
        "bundle_sha256": sha(bundle),
        "portable_source_archive_sha256": sha(outer / "SOURCE.tar.gz"),
        "source_archive_sha256": sha(execution_source),
        "source_tree_sha256": materialized["execution_tree_sha256"],
        "native_sha256": _sha(native), "gpu": gpu, "versions": versions,
        "fixed_radius_refinement_evidence_sha256": materialized["evidence_sha256"],
        "fixed_radius_refinement_case_count": materialized["case_count"],
        "focused_test_count": expected_test_count(tests, "goal57*_v4_*test.py"),
        "goal5768_test_count": expected_test_count(tests, "goal5768_*test.py"),
        "functional_count": 39, "functional_correct_count": 39,
        "functional_behavioral_true_optix_count": 39,
        "formal_worker_count": 0, "registered_performance_timing_count": 0,
        "performance_claimed": False, "execution_authority_created": False,
    }
    (root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    shutil.copy2(native, root / "librtdl_optix.so")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

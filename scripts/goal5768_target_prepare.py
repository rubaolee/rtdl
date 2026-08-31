#!/usr/bin/env python3
"""Create-only target preparation for the 13-lane V2/V3/V4 cohort.

This transaction builds a fresh native and executes 39 functional admissions.
It cannot execute the 312-worker formal matrix.  Formal execution requires a
second exact owner authority consumed by goal5768_formal_controller.py.
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
import time

try:
    from scripts.goal5769_pre_pod_admission import (
        expected_test_count,
        parse_unittest_count,
        sha256_bytes,
        validate_exact_test_manifest,
        validate_prepare_authority_files,
        validate_toolchain_policy,
    )
except ModuleNotFoundError:  # Standalone outer-bundle harness directory.
    from goal5769_pre_pod_admission import (  # type: ignore
        expected_test_count,
        parse_unittest_count,
        sha256_bytes,
        validate_exact_test_manifest,
        validate_prepare_authority_files,
        validate_toolchain_policy,
    )


METHODS = (
    "v2_direct_true_optix_backport",
    "v3_compiler_true_optix",
    "v4_restricted_callback_true_optix",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _run(command: list[str], *, cwd: Path, env: dict[str, str], log: Path) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(
            f"prepare command failed ({completed.returncode}): {command!r}; see {log}")
    return completed.stdout


def _safe_extract(archive_path: Path, target: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            normalized = "/".join(parts)
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe source member: {member.name}")
            if normalized in seen:
                raise RuntimeError(f"duplicate source member: {normalized}")
            seen.add(normalized)
            if not member.isfile():
                if member.isdir():
                    continue
                raise RuntimeError(f"unsupported source member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts):
                raise RuntimeError(f"private/cache source member: {member.name}")
            if normalized.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{normalized}/":
                raise RuntimeError(f"prebuilt/cache source member: {member.name}")
        archive.extractall(target)


def _read_outer_bundle(archive_path: Path) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe outer member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported outer member: {member.name}")
            name = "/".join(parts)
            if name in payloads:
                raise RuntimeError(f"duplicate outer member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable outer member: {name}")
            payloads[name] = handle.read()
    manifest_name = "PORTABLE_MANIFEST.json"
    if manifest_name not in payloads:
        raise RuntimeError("outer bundle lacks manifest")
    manifest = json.loads(payloads[manifest_name])
    expected = {row["path"] for row in manifest["payloads"]}
    if set(payloads) != expected | {manifest_name}:
        raise RuntimeError("outer bundle membership differs from manifest")
    for row in manifest["payloads"]:
        data = payloads[row["path"]]
        if hashlib.sha256(data).hexdigest() != row["sha256"] \
                or len(data) != row["size_bytes"]:
            raise RuntimeError(f"outer payload mismatch: {row['path']}")
    return payloads


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("build/") or "/__pycache__/" in f"/{rel}/" \
                or rel.endswith(".pyc"):
            continue
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha(path)))
    return digest.hexdigest()


def _validate_prepare_authority(
    authority: dict[str, object], *, bundle_sha256: str, source_sha256: str,
    toolchain_policy_sha256: str, test_manifest_sha256: str,
    owner_review_path: Path, review_absorption_path: Path,
    cc: str, optix_sdk: str, cuda_toolkit: str,
) -> dict[str, object]:
    return validate_prepare_authority_files(
        authority, owner_review_path=owner_review_path,
        review_absorption_path=review_absorption_path,
        bundle_sha256=bundle_sha256, source_sha256=source_sha256,
        toolchain_policy_sha256=toolchain_policy_sha256,
        test_manifest_sha256=test_manifest_sha256, cc=cc,
        optix_sdk=optix_sdk, cuda_toolkit=cuda_toolkit)


def _validate_receipt(endpoint: dict[str, object], native_sha256: str) -> None:
    if endpoint.get("matched") is not True \
            or endpoint.get("native_library_sha256") != native_sha256:
        raise RuntimeError("functional endpoint correctness/native binding failed")
    receipt = endpoint.get("traversal_receipt")
    if not isinstance(receipt, dict):
        raise RuntimeError("functional endpoint lacks traversal receipt")
    body = dict(receipt)
    claimed = body.pop("receipt_sha256", None)
    if claimed != _digest(body):
        raise RuntimeError("functional traversal receipt digest mismatch")
    snapshot = receipt.get("native_snapshot")
    if receipt.get("physical_executor_classification") \
            != "optix_traversal_observed" or not isinstance(snapshot, dict):
        raise RuntimeError("functional endpoint is not behaviorally true-OptiX")
    attempted = snapshot.get("attempted_launch_count")
    launches = snapshot.get("successful_launch_count")
    complete = snapshot.get("complete_context_launch_count")
    context_binds = snapshot.get("context_bind_count")
    if type(attempted) is not int or attempted <= 0 \
            or attempted != launches or launches != complete \
            or complete != context_binds:
        raise RuntimeError("functional traversal launch binding incomplete")
    if any(snapshot.get(name) != 0 for name in (
        "failed_launch_count", "incomplete_context_launch_count",
        "incomplete_callsite_record_count", "pending_context_at_finish",
        "session_error",
    )):
        raise RuntimeError("functional traversal receipt contains failure")
    if any(snapshot.get(name) in (None, 0) for name in (
        "first_traversable", "last_traversable",
        "first_program_bundle_id", "last_program_bundle_id",
    )):
        raise RuntimeError("functional traversal receipt lacks edge binding")
    raygen = snapshot.get("raygen_invocation_count")
    if type(raygen) is not int or raygen <= 0:
        raise RuntimeError("functional traversal receipt lacks raygen work")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-archive", type=Path, required=True)
    parser.add_argument("--prepare-authority", type=Path, required=True)
    parser.add_argument("--owner-review", type=Path, required=True)
    parser.add_argument("--review-absorption", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--cuda-toolkit", default="12.8")
    parser.add_argument("--minimum-free-gib", type=float, default=12.0)
    args = parser.parse_args()

    bundle_archive = args.bundle_archive.resolve()
    work_root = args.work_root.resolve()
    if work_root.exists():
        raise FileExistsError(work_root)
    bundle_sha256 = _sha(bundle_archive)
    outer = _read_outer_bundle(bundle_archive)
    manifest = json.loads(outer["PORTABLE_MANIFEST.json"])
    source_sha256 = hashlib.sha256(outer["SOURCE.tar.gz"]).hexdigest()
    if source_sha256 != manifest["source_archive_sha256"]:
        raise RuntimeError("bundle source identity mismatch")
    policy_bytes = outer.get("TOOLCHAIN/TOOLCHAIN_POLICY.json")
    test_manifest_bytes = outer.get("POLICY/EXACT_TEST_MANIFEST.json")
    if policy_bytes is None or test_manifest_bytes is None:
        raise RuntimeError("bundle lacks Goal5769 policy payloads")
    toolchain_policy = json.loads(policy_bytes)
    test_manifest = json.loads(test_manifest_bytes)
    validate_toolchain_policy(toolchain_policy, payloads=outer)
    toolchain_policy_sha256 = sha256_bytes(policy_bytes)
    test_manifest_sha256 = sha256_bytes(test_manifest_bytes)
    authority = json.loads(args.prepare_authority.read_text(encoding="utf-8"))
    _validate_prepare_authority(
        authority, bundle_sha256=bundle_sha256, source_sha256=source_sha256,
        toolchain_policy_sha256=toolchain_policy_sha256,
        test_manifest_sha256=test_manifest_sha256,
        owner_review_path=args.owner_review.resolve(),
        review_absorption_path=args.review_absorption.resolve(),
        cc=args.cc, optix_sdk=args.optix_sdk, cuda_toolkit=args.cuda_toolkit)
    if shutil.disk_usage(work_root.parent).free < args.minimum_free_gib * 1024**3:
        raise RuntimeError("target lacks predeclared free-disk budget")
    work_root.mkdir(parents=True)
    bundle_root = work_root / "bundle"
    bundle_root.mkdir()
    for name, data in outer.items():
        path = bundle_root / Path(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    source_archive = bundle_root / "SOURCE.tar.gz"
    source = work_root / "source"
    source.mkdir()
    _safe_extract(source_archive, source)
    portable_source_tree = _tree_digest(source)
    result_root = work_root / "result"
    result_root.mkdir()
    logs = result_root / "logs"
    logs.mkdir()

    validate_exact_test_manifest(source, test_manifest)
    python_executable = Path(toolchain_policy["python_executable"])
    if not python_executable.is_file() \
            or _sha(python_executable) != authority["required_python_executable_sha256"]:
        raise RuntimeError("target Python executable differs from owner authority")
    toolchain_root = work_root / "toolchain"
    toolchain_root.mkdir()
    for package in sorted((bundle_root / "TOOLCHAIN/cuda_debs").glob("*.deb")):
        _run(["dpkg-deb", "-x", str(package), str(toolchain_root)],
             cwd=source, env=os.environ.copy(),
             log=logs / f"extract__{package.name}.log")
    cuda_root = toolchain_root / "usr/local/cuda-12.8"
    optix_root = work_root / "optix"
    optix_root.mkdir()
    _safe_extract(bundle_root / "TOOLCHAIN/optix9_include.tar.gz", optix_root)
    optix_include = optix_root / "include"
    cuda_include = cuda_root / "include"
    for required in (
        optix_include / "optix.h", cuda_include / "cuda.h",
        cuda_root / "bin/nvcc", cuda_root / "nvvm/lib64/libnvvm.so",
        cuda_root / "nvvm/libdevice/libdevice.10.bc",
    ):
        if not required.is_file():
            raise RuntimeError(f"bundled SDK payload absent: {required}")
    python_site = work_root / "python_site"
    python_site.mkdir()
    wheels = sorted((bundle_root / "TOOLCHAIN/wheelhouse").glob("*.whl"))
    _run([
        str(python_executable), "-m", "pip", "install", "--no-index",
        "--no-deps", "--target", str(python_site), *(str(path) for path in wheels),
    ], cwd=source, env=os.environ.copy(), log=logs / "pip_install.log")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        (str(source / "src"), str(source), str(python_site)))
    env["PATH"] = os.pathsep.join((str(cuda_root / "bin"), env.get("PATH", "")))
    env["LD_LIBRARY_PATH"] = os.pathsep.join((
        str(cuda_root / "nvvm/lib64"),
        str(cuda_root / "targets/x86_64-linux/lib"),
        "/usr/lib/x86_64-linux-gnu",
    ))
    env["NUMBA_CUDA_NVVM"] = str(cuda_root / "nvvm/lib64/libnvvm.so")
    env["NUMBA_CUDA_LIBDEVICE"] = str(
        cuda_root / "nvvm/libdevice/libdevice.10.bc")
    env["RTDL_V4_CUDA_PREFIX"] = str(cuda_root)
    env["RTDL_V4_OPTIX_PREFIX"] = str(optix_root)

    nvidia_smi = _run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], cwd=source, env=env, log=logs / "nvidia_smi.log").strip()
    if len(nvidia_smi.splitlines()) != 1:
        raise RuntimeError("prepare requires exactly one visible NVIDIA GPU")
    gpu_columns = tuple(part.strip() for part in nvidia_smi.split(","))
    if len(gpu_columns) != 4 \
            or authority["required_gpu_name"] != gpu_columns[0] \
            or authority["required_gpu_uuid"] != gpu_columns[1] \
            or authority["required_driver_version"] != gpu_columns[2] \
            or gpu_columns[3].replace(".", "") != args.cc:
        raise RuntimeError("target GPU differs from owner-authorized model/CC")
    nvcc_version = _run([
        str(cuda_root / "bin/nvcc"), "--version",
    ], cwd=source, env=env, log=logs / "nvcc_version.log")
    if "V12.8.93" not in nvcc_version:
        raise RuntimeError("bundled NVCC version differs from policy")
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix_root}",
        f"CUDA_PREFIX={cuda_root}",
        f"OPTIX_CUDA_ARCH=sm_{args.cc}",
    ], cwd=source, env=env, log=logs / "build.log")
    native = (source / "build/librtdl_optix.so").resolve()
    if not native.is_file():
        raise RuntimeError("fresh target native was not produced")
    native_sha256 = _sha(native)
    env["RTDL_OPTIX_LIB"] = str(native)
    env["RTDL_OPTIX_LIBRARY"] = str(native)

    refinement_evidence = result_root / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    execution_source_archive = result_root / "EXECUTION_SOURCE.tar.gz"
    rematerialization_path = result_root / "FIXED_RADIUS_REMATERIALIZATION.json"
    _run([
        str(python_executable),
        "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "--source-root", str(source),
        "--native", str(native),
        "--evidence-output", str(refinement_evidence),
        "--execution-source-output", str(execution_source_archive),
        "--result-output", str(rematerialization_path),
    ], cwd=source, env=env, log=logs / "fixed_radius_rematerialization.log")
    rematerialization = json.loads(
        rematerialization_path.read_text(encoding="utf-8"))
    if rematerialization.get("case_count") != 17 \
            or rematerialization.get("all_cases_exact") is not True \
            or rematerialization.get("native_sha256") != native_sha256:
        raise RuntimeError("fixed-radius target rematerialization failed closed")
    env["RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"] = str(
        refinement_evidence)
    execution_source_sha256 = _sha(execution_source_archive)
    execution_tree_sha256 = str(rematerialization["execution_tree_sha256"])

    for pattern, log_name in (
        ("goal57*_v4_*test.py", "focused_tests.log"),
        ("goal5768_*test.py", "goal5768_tests.log"),
        ("goal5769_*test.py", "goal5769_admission_tests.log"),
    ):
        output = _run([
            str(python_executable), "-m", "unittest", "discover", "-s", "tests",
            "-p", pattern,
        ], cwd=source, env=env, log=logs / log_name)
        if parse_unittest_count(output) != expected_test_count(test_manifest, pattern):
            raise RuntimeError(f"test cardinality differs from manifest: {pattern}")
    version_output = _run([
        str(python_executable), "-c",
        "import json,platform,numba,numpy,llvmlite,cupy; "
        "print(json.dumps({'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__,'llvmlite':llvmlite.__version__,'cupy':cupy.__version__},sort_keys=True))",
    ], cwd=source, env=env, log=logs / "versions.log").strip()
    versions = json.loads(version_output)
    if versions != {
        key: toolchain_policy["versions"][key]
        for key in ("python", "numba", "numpy", "llvmlite", "cupy")
    }:
        raise RuntimeError("installed partner versions differ from policy")
    numba_version = versions["numba"]
    numpy_version = versions["numpy"]
    llvmlite_version = versions["llvmlite"]
    cupy_version = versions["cupy"]
    target = {
        "provider": "optix",
        "optix_sdk": args.optix_sdk,
        "compute_capability": f"{args.cc[0]}.{args.cc[1]}",
        "native_sha256": native_sha256,
        "supports_custom_aabb": True,
        "supports_builtin_triangle": True,
    }
    runtime = {
        "target": target,
        "compute_capability": [int(args.cc[0]), int(args.cc[1])],
        "optix_include": str(optix_include),
        "cuda_include": str(cuda_include),
        "expected_python_version": versions["python"],
        "expected_numba_version": numba_version,
        "expected_numpy_version": numpy_version,
        "expected_llvmlite_version": llvmlite_version,
        "native_library_path": str(native),
        "native_library_sha256": native_sha256,
        "optix_sdk": args.optix_sdk,
        "expected_cupy_version": cupy_version,
        "cuda_toolkit": args.cuda_toolkit,
        "toolchain_policy_sha256": toolchain_policy_sha256,
        "test_manifest_sha256": test_manifest_sha256,
        # Stage A executes its fresh-process smoke children with this exact
        # environment.  Preserve the same partner/compiler environment in the
        # scientific plan so Stage B cannot silently fall back to an ambient
        # Python installation that lacks Numba/CuPy or the frozen CUDA SDK.
        "formal_worker_environment": {
            name: env.get(name)
            for name in (
                "PYTHONPATH",
                "PATH",
                "LD_LIBRARY_PATH",
                "NUMBA_CUDA_NVVM",
                "NUMBA_CUDA_LIBDEVICE",
                "RTDL_V4_CUDA_PREFIX",
                "RTDL_V4_OPTIX_PREFIX",
                "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
                "CUDA_VISIBLE_DEVICES",
                "NVIDIA_VISIBLE_DEVICES",
            )
        },
    }
    runtime_path = result_root / "RUNTIME.json"
    runtime_path.write_text(
        json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sys.path.insert(0, str(python_site))
    sys.path.insert(0, str(source))
    # This import is executed by the outer Stage-A process itself, not by a
    # child using ``env`` above.  Bind it to the freshly extracted source tree
    # instead of relying on an ambient/install-time rtdsl package.
    sys.path.insert(0, str(source / "src"))
    from scripts.goal5768_three_way_frontdoors import LANES
    raw = result_root / "functional_raw"
    raw.mkdir()
    observed = []
    for lane in LANES:
        for method in METHODS:
            output = raw / f"{lane.lane_id}__{method}.json"
            _run([
                str(python_executable),
                "scripts/goal5768_three_way_functional_smoke.py",
                "--lane-id", lane.lane_id,
                "--method", method,
                "--runtime", str(runtime_path),
                "--output", str(output),
            ], cwd=source, env=env,
                log=logs / f"smoke__{lane.lane_id}__{method}.log")
            record = json.loads(output.read_text(encoding="utf-8"))
            if record.get("formal_worker") is not False \
                    or record.get("performance_interpretation_allowed") is not False:
                raise RuntimeError("functional smoke was relabelled as formal/performance")
            _validate_receipt(record["endpoint"], native_sha256)
            observed.append(record)
    if len(observed) != 39 or len({row["parent_pid"] for row in observed}) != 39:
        raise RuntimeError("functional admission lacks 39 fresh processes")
    for lane in LANES:
        cohort = [row for row in observed if row["lane_id"] == lane.lane_id]
        if len({row["endpoint"]["input_sha256"] for row in cohort}) != 1 \
                or len({row["endpoint"]["output_sha256"] for row in cohort}) != 1:
            raise RuntimeError(f"three-way functional identity mismatch: {lane.lane_id}")
    lane_contracts = {}
    for lane in LANES:
        cohort = [row for row in observed if row["lane_id"] == lane.lane_id]
        exemplar = cohort[0]["endpoint"]
        lane_contracts[lane.lane_id] = {
            "input_sha256": exemplar["input_sha256"],
            "output_sha256": exemplar["output_sha256"],
            "expected_sha256": exemplar["expected_sha256"],
        }

    target_identity = {
        "nvidia_smi": nvidia_smi,
        "cc": args.cc,
        "optix_sdk": args.optix_sdk,
        "cuda_toolkit": args.cuda_toolkit,
        "optix_h_sha256": _sha(optix_include / "optix.h"),
        "cuda_h_sha256": _sha(cuda_include / "cuda.h"),
        "python_executable": str(python_executable),
        "python_executable_sha256": _sha(python_executable),
        "python_version": versions["python"],
        "numba_version": numba_version,
        "numpy_version": numpy_version,
        "llvmlite_version": llvmlite_version,
        "cupy_version": cupy_version,
        "native_library_sha256": native_sha256,
    }
    target_identity_sha256 = _digest(target_identity)
    smoke_hashes = sorted(_sha(path) for path in raw.glob("*.json"))
    prepared_identity = {
        "bundle_sha256": bundle_sha256,
        "portable_source_archive_sha256": source_sha256,
        "portable_source_tree_sha256": portable_source_tree,
        "source_archive_sha256": execution_source_sha256,
        "source_tree_sha256": execution_tree_sha256,
        "native_library_sha256": native_sha256,
        "fixed_radius_refinement_evidence_sha256": (
            rematerialization["evidence_sha256"]),
        "target_identity_sha256": target_identity_sha256,
        "functional_smoke_payload_sha256s": smoke_hashes,
        "functional_smoke_count": 39,
    }
    prepared_identity_sha256 = _digest(prepared_identity)

    from scripts.goal5768_formal_controller import (
        _formal_worker_environment,
        build_prepared_plan,
    )
    plan = build_prepared_plan(
        bundle_sha256=bundle_sha256,
        execution_source_sha256=execution_source_sha256,
        execution_tree_sha256=execution_tree_sha256,
        native_library_sha256=native_sha256,
        prepared_identity_sha256=prepared_identity_sha256,
        target_identity_sha256=target_identity_sha256,
        python_executable=str(python_executable),
        python_version=versions["python"],
        runtime=runtime,
        lane_contracts=lane_contracts,
    )
    # Exercise the exact environment that the formal controller will pass to
    # every worker.  Stage A previously proved the application routes using
    # ``env`` above, while Stage B accidentally inherited only ambient Python
    # paths.  This zero-application preflight makes that mismatch impossible:
    # it imports every required partner and performs the same compiler-owned
    # target/memory probe used by the Triangle V3 route.
    formal_environment = _formal_worker_environment(plan)
    formal_environment_probe_text = _run([
        str(python_executable), "-c",
        "import json,platform,numba,numpy,llvmlite,cupy; "
        "from rtdsl.action_ray_triangle_scalar_summary import "
        "detect_ray_triangle_scalar_summary_target; "
        "t=detect_ray_triangle_scalar_summary_target(); "
        "print(json.dumps({'python':platform.python_version(),"
        "'numba':numba.__version__,'numpy':numpy.__version__,"
        "'llvmlite':llvmlite.__version__,'cupy':cupy.__version__,"
        "'optix_available':t.optix_available,"
        "'device_memory_limit_bytes':t.device_memory_limit_bytes},"
        "sort_keys=True))",
    ], cwd=source, env=formal_environment,
        log=logs / "formal_worker_environment_preflight.log").strip()
    formal_environment_probe = json.loads(formal_environment_probe_text)
    expected_formal_probe_fields = {
        "python": versions["python"],
        "numba": numba_version,
        "numpy": numpy_version,
        "llvmlite": llvmlite_version,
        "cupy": cupy_version,
        "optix_available": True,
    }
    if any(
        formal_environment_probe.get(name) != value
        for name, value in expected_formal_probe_fields.items()
    ) or set(formal_environment_probe) != {
        *expected_formal_probe_fields,
        "device_memory_limit_bytes",
    } or type(formal_environment_probe["device_memory_limit_bytes"]) is not int \
            or formal_environment_probe["device_memory_limit_bytes"] <= 0:
        raise RuntimeError(
            "formal worker environment cannot reproduce the Stage-A partner/target probe")
    (result_root / "FORMAL_WORKER_ENVIRONMENT_PREFLIGHT.json").write_text(
        json.dumps(formal_environment_probe, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (result_root / "PREPARED_FORMAL_PLAN.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (result_root / "TARGET_IDENTITY.json").write_text(
        json.dumps(target_identity, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (result_root / "PREPARED_IDENTITY.json").write_text(
        json.dumps(prepared_identity, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    smoke_seconds = sum(
        float(row["endpoint"]["registered_complete_seconds"])
        for row in observed)
    estimated_formal_seconds = smoke_seconds * 8.0
    cost_gate = {
        "functional_smoke_complete_seconds_sum": smoke_seconds,
        "estimated_312_worker_serial_seconds_from_same_endpoint_samples": (
            estimated_formal_seconds),
        "owner_runtime_budget_required_seconds": max(
            3600.0, estimated_formal_seconds * 1.5),
        "estimate_is_admission_budget_not_performance_result": True,
        "largest_lane_measurements": sorted(({
            "lane_id": row["lane_id"],
            "method": row["method"],
            "seconds": row["endpoint"]["registered_complete_seconds"],
        } for row in observed), key=lambda item: item["seconds"], reverse=True)[:6],
    }
    (result_root / "COST_GATE.json").write_text(
        json.dumps(cost_gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if _tree_digest(source) != execution_tree_sha256:
        raise RuntimeError("prepare mutated materialized source outside build/cache")
    shutil.copy2(native, result_root / "librtdl_optix.so")
    shutil.copy2(bundle_archive, result_root / "EXECUTION_BUNDLE.tar.gz")
    authorization_kind = (
        "owner_direct_after_strict_internal_review__not_external_review"
        if authority.get("external_preexecution_review_claimed") is False
        else "owner_returned_exact_byte_external_review"
    )
    result = {
        "schema": "rtdl.goal5768.three_way_target_prepare.v1",
        "bundle_sha256": bundle_sha256,
        "portable_source_archive_sha256": source_sha256,
        "portable_source_tree_sha256": portable_source_tree,
        "source_archive_sha256": execution_source_sha256,
        "source_tree_sha256": execution_tree_sha256,
        "native_library_sha256": native_sha256,
        "fixed_radius_refinement_evidence_sha256": (
            rematerialization["evidence_sha256"]),
        "fixed_radius_refinement_case_count": 17,
        "target_identity_sha256": target_identity_sha256,
        "prepared_identity_sha256": prepared_identity_sha256,
        "plan_sha256": plan["plan_sha256"],
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "toolchain_policy_sha256": toolchain_policy_sha256,
        "test_manifest_sha256": test_manifest_sha256,
        "preexecution_authorization_kind": authorization_kind,
        "preexecution_authorization_artifact_sha256": _sha(
            args.owner_review.resolve()),
        "preexecution_review_artifact_sha256": _sha(
            args.review_absorption.resolve()),
        "external_preexecution_review_claimed": (
            authorization_kind == "owner_returned_exact_byte_external_review"),
        "functional_smoke_count": 39,
        "functional_smoke_unique_parent_pid_count": 39,
        "functional_correct_count": 39,
        "functional_behavioral_true_optix_count": 39,
        "formal_worker_environment_preflight_passed": True,
        "formal_worker_environment_partner_imports_exact": True,
        "formal_worker_environment_device_memory_probe_positive": True,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "performance_result_exists": False,
        "exact_execution_source_and_native_preserved_before_formal_worker_zero": True,
        "formal_execution_requires_second_exact_owner_authority": True,
        "claim_boundary": {
            "performance_claimed": False,
            "no_slower_claimed": False,
            "author_performance_claimed": False,
            "hardware_rt_core_utilization_claimed": False,
            "public_production_submission_claimed": False,
        },
    }
    (result_root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

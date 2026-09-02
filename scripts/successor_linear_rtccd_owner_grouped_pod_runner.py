#!/usr/bin/env python3
"""GPU validation runner for the successor owner-grouped RT-CCD subset."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
for import_root in (ROOT / "src", ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from case_studies.linear_rtccd_owner_grouped import (
    evaluate_owner_grouped_collision_reference,
    prepare_problem,
)
from case_studies.linear_rtccd_owner_grouped.fixtures import (
    REGISTERED_SURFACE_GAP_FLOOR,
    RegisteredLocalCase,
    deterministic_scale_case,
    registered_local_cases,
)
from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve_owner_grouped_any_hit_public import (
    V4CurveTarget,
    curve_owner_grouped_any_hit_source,
)
from scripts.build_v4_optix_native_snapshot import (
    REQUIRED_SYMBOLS,
    _build_input_id,
    _gpu_identity,
    _header_inventory,
    _optix_sdk_number,
    _source_inventory as _native_source_inventory,
)
from scripts.successor_owner_grouped_pod_preflight import (
    ensure_runtime_environment,
    resolve_cuda_runtime_files,
)

RUNNER_SOURCE_PATHS = (
    ROOT / "scripts/build_v4_optix_native_snapshot.py",
    ROOT / "scripts/successor_owner_grouped_pod_preflight.py",
    Path(__file__).resolve(),
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _capture(command: list[str], *, required: bool = True) -> str:
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    if required and completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}: {output}")
    return output


def _validate_result_paths(output: Path, artifact_root: Path) -> None:
    if output == artifact_root or output in artifact_root.parents \
            or artifact_root in output.parents:
        raise ValueError(
            "GPU output and artifact directory must be distinct and non-nested")


def _write_json_exclusive(path: Path, value: object) -> None:
    payload = json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def _execution_source_inventory() -> list[dict[str, object]]:
    paths = set(RUNNER_SOURCE_PATHS)
    for base in (
        ROOT / "src",
        ROOT / "case_studies/linear_rtccd_owner_grouped",
    ):
        paths.update(
            path for path in base.rglob("*")
            if path.is_file() and path.suffix in {".py", ".cpp", ".cu", ".h"})
    return [{
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    } for path in sorted(paths)]


def _parse_compute_capability(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([0-9]{1,2})\.([0-9]{1,2})", value)
    if match is None:
        raise ValueError(f"invalid compute capability: {value!r}")
    return int(match.group(1)), int(match.group(2))


def _validated_include_from_prefix(
    prefix: Path,
    supplied_include: Path,
    *,
    label: str,
) -> tuple[Path, Path]:
    resolved_prefix = prefix.expanduser().resolve(strict=True)
    logical_include = resolved_prefix / "include"
    resolved_include = logical_include.resolve(strict=True)
    if not resolved_prefix.is_dir() or not resolved_include.is_dir():
        raise NotADirectoryError(
            resolved_prefix if not resolved_prefix.is_dir() else logical_include)
    if supplied_include.expanduser().resolve(strict=True) != resolved_include:
        raise ValueError(
            f"--{label}-include does not belong to --{label}-prefix")
    return resolved_prefix, logical_include


def _validate_native_build_manifest(
    path: Path,
    native: Path,
    *,
    git_commit: str,
    optix_sdk: str,
    compute_capability: tuple[int, int],
    gpu_identity: str,
    optix_include: Path,
    cuda_include: Path,
    optix_prefix: Path,
    cuda_prefix: Path,
    allow_dirty: bool,
) -> dict[str, object]:
    native = native.resolve(strict=True)
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("native build manifest is unreadable") from exc
    if type(manifest) is not dict \
            or manifest.get("schema") != "rtdl.v4.optix_native_snapshot_build.v1" \
            or manifest.get("status") != \
                "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED" \
            or manifest.get("git_commit") != git_commit \
            or manifest.get("git_commit_after_build") != git_commit \
            or manifest.get("optix_version") != _optix_sdk_number(optix_sdk) \
            or manifest.get("native_sha256") != _sha(native) \
            or manifest.get("native_bytes") != native.stat().st_size \
            or Path(str(manifest.get("native_path", ""))).resolve() != native \
            or manifest.get("required_symbols") != list(REQUIRED_SYMBOLS) \
            or manifest.get("exported_symbol_match_mode") != \
                "exact_nm_dynamic_defined_name" \
            or manifest.get("all_required_symbols_exported") is not True:
        raise RuntimeError("native build manifest does not bind the selected library")
    build_input = manifest.get("build_input")
    builder_path = ROOT / "scripts/build_v4_optix_native_snapshot.py"
    cuda_prefix, cuda_include = _validated_include_from_prefix(
        cuda_prefix, cuda_include, label="cuda")
    _, optix_include = _validated_include_from_prefix(
        optix_prefix, optix_include, label="optix")
    nvcc = (cuda_prefix / "bin/nvcc").resolve(strict=True)
    nvcc_version = _capture([str(nvcc), "--version"])
    if type(build_input) is not dict \
            or build_input.get("git_commit") != git_commit \
            or build_input.get("builder_sha256") != _sha(builder_path) \
            or build_input.get("source_inventory") != _native_source_inventory() \
            or build_input.get("optix_version") != _optix_sdk_number(optix_sdk) \
            or build_input.get("expected_optix_sdk") != optix_sdk \
            or build_input.get("compute_capability") != list(compute_capability) \
            or build_input.get("gpu") != gpu_identity \
            or build_input.get("nvcc_path") != str(nvcc) \
            or build_input.get("nvcc_sha256") != _sha(nvcc) \
            or build_input.get("nvcc_version") != nvcc_version \
            or build_input.get("optix_include") != str(optix_include) \
            or build_input.get("cuda_include") != str(cuda_include) \
            or build_input.get("optix_header_inventory") != \
                _header_inventory(optix_include) \
            or build_input.get("cuda_header_inventory") != \
                _header_inventory(cuda_include):
        raise RuntimeError("native build manifest source identity differs")
    if manifest.get("build_id") != _build_input_id(build_input):
        raise RuntimeError("native build manifest build-input digest differs")
    host_compiler_value = build_input.get("host_compiler_path")
    if not isinstance(host_compiler_value, str) or not host_compiler_value:
        raise RuntimeError("native build manifest host compiler is absent")
    host_compiler = Path(host_compiler_value).resolve(strict=True)
    host_compiler_version = _capture([str(host_compiler), "--version"])
    if build_input.get("host_compiler_path") != str(host_compiler) \
            or build_input.get("host_compiler_sha256") != \
                _sha(host_compiler) \
            or build_input.get("host_compiler_version") != \
                host_compiler_version:
        raise RuntimeError("native build manifest host compiler identity differs")
    if manifest.get("nvcc_path") != str(nvcc) \
            or manifest.get("nvcc_sha256") != build_input["nvcc_sha256"] \
            or manifest.get("nvcc_version") != nvcc_version:
        raise RuntimeError("native build manifest compiler identity differs")
    if manifest.get("host_compiler_path") != str(host_compiler) \
            or manifest.get("host_compiler_sha256") != \
                build_input["host_compiler_sha256"] \
            or manifest.get("host_compiler_version") != host_compiler_version:
        raise RuntimeError("native build manifest host compiler identity differs")
    if manifest.get("gpu") != gpu_identity:
        raise RuntimeError("native build manifest GPU identity differs")
    if manifest.get("git_status_after_build") != \
            manifest.get("git_status_before_build"):
        raise RuntimeError("native build manifest records build-time source drift")
    if (manifest.get("git_status_before_build") or
            manifest.get("dirty_build_authorized")) and not allow_dirty:
        raise RuntimeError("dirty native build is not authorized for GPU evidence")
    return manifest


def _write_artifacts(root: Path, source, materialized) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=False)
    executable = materialized.executable
    bodies = {
        "wrapper.cu": executable.wrapper.source.encode("utf-8"),
        "wrapper.ptx": executable.wrapper_ptx.encode("utf-8"),
        "composed.ptx": executable.composed.ptx.encode("utf-8"),
        "nvrtc.log": materialized.compiler_log.encode("utf-8"),
    }
    for index, leaf in enumerate(executable.generated_leaves):
        bodies[f"leaf_{index}_{leaf.role.value}.py"] = \
            leaf.generated_source.encode("utf-8")
    for index, leaf in enumerate(executable.compiled_leaves):
        bodies[f"leaf_{index}_{leaf.role}.ptx"] = leaf.ptx.encode("utf-8")
    rows = []
    for name, body in sorted(bodies.items()):
        path = root / name
        path.write_bytes(body)
        rows.append({
            "path": name,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
    manifest = {
        "schema": "rtdl.successor_owner_grouped.materialized_artifacts.v1",
        "source_sha256": source.source_sha256,
        "executable_sha256": executable.executable_sha256,
        "members": rows,
    }
    payload = json.dumps(
        manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (root / "manifest.json").write_text(
        payload, encoding="utf-8", newline="\n")
    return {
        **manifest,
        "manifest_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }


def _parse_scale(value: str) -> tuple[int, int, int, int]:
    match = re.fullmatch(r"([1-9][0-9]*):([1-9][0-9]*):([1-9][0-9]*):([1-9][0-9]*)", value)
    if match is None:
        raise argparse.ArgumentTypeError(
            "scale must be OWNERS:SEGMENTS:HIT_STRIDE:DUPLICATES")
    return tuple(int(item) for item in match.groups())


def _safe_case_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _workloads(scales) -> tuple[RegisteredLocalCase, ...]:
    if len(scales) > 16:
        raise ValueError("at most 16 scale workloads are allowed per GPU run")
    rows = list(registered_local_cases())
    rows.extend(deterministic_scale_case(
        owners, segments, hit_stride=stride,
        duplicate_query_factor=duplicates,
    ) for owners, segments, stride, duplicates in scales)
    if len({row.case_id for row in rows}) != len(rows):
        raise RuntimeError("GPU workload IDs are not unique")
    if len({_safe_case_id(row.case_id) for row in rows}) != len(rows):
        raise RuntimeError("GPU workload artifact IDs are not unique")
    return tuple(rows)


def _run_workload(
    source,
    target,
    toolchain,
    case: RegisteredLocalCase,
    *,
    repeat: int,
    artifact_root: Path,
    native_build_id: str,
) -> dict[str, object]:
    static, batch = case.problem.public_inputs()
    oracle_start = time.perf_counter_ns()
    oracle = evaluate_owner_grouped_collision_reference(case.problem)
    oracle_ns = time.perf_counter_ns() - oracle_start
    if oracle.per_trajectory_collision != case.expected_bits:
        raise RuntimeError(f"independent oracle mismatch: {case.case_id}")
    if oracle.minimum_surface_gap < REGISTERED_SURFACE_GAP_FLOOR:
        raise RuntimeError(f"numeric boundary-band workload: {case.case_id}")
    print(
        f"[owner-grouped] materialize {case.case_id} "
        f"owners={static.owner_count} primitives={len(static.segment_indices)} "
        f"queries={len(batch.queries)}",
        flush=True,
    )
    materialize_start = time.perf_counter_ns()
    program = source.compile(target=target)
    materialized = program.materialize(toolchain=toolchain)
    materialize_ns = time.perf_counter_ns() - materialize_start
    safe_id = _safe_case_id(case.case_id)
    artifacts = _write_artifacts(artifact_root / safe_id, source, materialized)
    prepare_start = time.perf_counter_ns()
    prepared = prepare_problem(materialized, case.problem)
    prepare_ns = time.perf_counter_ns() - prepare_start
    executions = []
    close_ns = None
    try:
        for iteration in range(repeat):
            execute_start = time.perf_counter_ns()
            observed = prepared.execute()
            execute_ns = time.perf_counter_ns() - execute_start
            if observed.per_trajectory_collision != case.expected_bits:
                raise RuntimeError(
                    f"GPU owner bits mismatch: {case.case_id} repeat={iteration}")
            snapshot = observed.traversal_receipt["native_snapshot"]
            if observed.traversal_receipt["physical_executor_classification"] != \
                    "optix_traversal_observed" \
                    or snapshot["successful_launch_count"] != 1 \
                    or snapshot["raygen_invocation_count"] != len(batch.queries):
                raise RuntimeError(
                    f"true-OptiX receipt mismatch: {case.case_id} repeat={iteration}")
            descriptor = observed.physical_receipt["native_descriptor"]
            if descriptor["native_build_id"] != native_build_id \
                    or descriptor["execution_count"] != iteration + 1 \
                    or descriptor["last_query_count"] != len(batch.queries) \
                    or descriptor["last_status_failed"] is not False:
                raise RuntimeError(
                    f"native descriptor mismatch: {case.case_id} repeat={iteration}")
            executions.append({
                "iteration": iteration,
                "diagnostic_execute_ns": execute_ns,
                "owner_hit_bits": list(observed.per_trajectory_collision),
                "output_sha256": observed.output_sha256,
                "physical_receipt": observed.physical_receipt,
                "traversal_receipt": observed.traversal_receipt,
            })
            print(
                f"[owner-grouped] pass {case.case_id} repeat={iteration} "
                f"execute_ms={execute_ns / 1e6:.3f}",
                flush=True,
            )
        lifecycle = prepared.lifecycle_receipt
    finally:
        close_start = time.perf_counter_ns()
        prepared.close()
        close_ns = time.perf_counter_ns() - close_start
    if lifecycle["execution_count"] != repeat:
        raise RuntimeError(f"prepared reuse count mismatch: {case.case_id}")
    return {
        "case_id": case.case_id,
        "purpose": case.purpose,
        "owner_count": static.owner_count,
        "primitive_count": len(static.segment_indices),
        "query_count": len(batch.queries),
        "expected_owner_hit_bits": list(case.expected_bits),
        "independent_oracle_pair_count": oracle.intersecting_pair_count,
        "minimum_surface_gap": oracle.minimum_surface_gap,
        "surface_crossing_domain_admission":
            case.problem.surface_crossing_domain_admission(),
        "diagnostic_oracle_ns": oracle_ns,
        "diagnostic_materialize_ns": materialize_ns,
        "diagnostic_prepare_ns": prepare_ns,
        "diagnostic_close_ns": close_ns,
        "repeat_count": repeat,
        "prepared_lifecycle_receipt": lifecycle,
        "materialized_artifacts": artifacts,
        "executions": executions,
    }


def validate(args) -> dict[str, object]:
    native = args.native.resolve(strict=True)
    native_manifest_path = args.native_manifest.resolve(strict=True)
    output = args.output.resolve()
    artifact_root = args.artifact_dir.resolve()
    _validate_result_paths(output, artifact_root)
    if not native.is_file():
        raise FileNotFoundError(native)
    if output.exists() or artifact_root.exists():
        raise FileExistsError(output if output.exists() else artifact_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    cuda_prefix, cuda_include = _validated_include_from_prefix(
        args.cuda_prefix, args.cuda_include, label="cuda")
    optix_prefix, optix_include = _validated_include_from_prefix(
        args.optix_prefix, args.optix_include, label="optix")
    pre_commit = _capture(["git", "rev-parse", "HEAD"])
    pre_status = _capture(["git", "status", "--porcelain"])
    if pre_status and not args.allow_dirty:
        raise RuntimeError("GPU evidence requires a clean Git tree")
    pre_sources = _execution_source_inventory()
    native_sha_before = _sha(native)
    native_manifest_sha_before = _sha(native_manifest_path)
    runtime_environment = getattr(args, "runtime_environment_identity", None)
    if type(runtime_environment) is not dict:
        raise RuntimeError("runner CUDA environment was not configured")
    capability = _parse_compute_capability(args.compute_capability)
    gpu_identity, observed_capability = _gpu_identity()
    if capability != observed_capability:
        raise RuntimeError(
            "--compute-capability differs from the visible GPU: "
            f"requested={capability}, observed={observed_capability}")
    native_manifest = _validate_native_build_manifest(
        native_manifest_path,
        native,
        git_commit=pre_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
        gpu_identity=gpu_identity,
        optix_include=optix_include,
        cuda_include=cuda_include,
        optix_prefix=optix_prefix,
        cuda_prefix=cuda_prefix,
        allow_dirty=args.allow_dirty,
    )
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    target = V4CurveTarget.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )
    source = curve_owner_grouped_any_hit_source()
    scales = args.scale or ((8, 2, 2, 1), (32, 4, 3, 2), (64, 8, 5, 1))
    workloads = _workloads(scales)
    if len(workloads) * args.repeat > 128:
        raise ValueError("GPU validation launch budget exceeds 128 executions")
    artifact_root.mkdir(parents=True, exist_ok=False)
    incomplete = artifact_root / "RUN_INCOMPLETE.json"
    incomplete.write_text(json.dumps({
        "schema": "rtdl.successor_owner_grouped_any_hit.incomplete.v1",
        "status": "INCOMPLETE__NO_GPU_RESULT_AUTHORIZED",
        "git_commit": pre_commit,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    rows = []
    for index, case in enumerate(workloads, start=1):
        print(
            f"[owner-grouped] workload {index}/{len(workloads)}: {case.case_id}",
            flush=True,
        )
        rows.append(_run_workload(
            source,
            target,
            toolchain,
            case,
            repeat=args.repeat,
            artifact_root=artifact_root,
            native_build_id=native_manifest["build_id"],
        ))
    launch_count = sum(
        execution["traversal_receipt"]["native_snapshot"][
            "successful_launch_count"]
        for row in rows for execution in row["executions"]
    )
    post_commit = _capture(["git", "rev-parse", "HEAD"])
    post_status = _capture(["git", "status", "--porcelain"])
    post_sources = _execution_source_inventory()
    if post_commit != pre_commit or post_status != pre_status \
            or post_sources != pre_sources \
            or _sha(native) != native_sha_before \
            or _sha(native_manifest_path) != native_manifest_sha_before \
            or _gpu_identity() != (gpu_identity, observed_capability) \
            or _header_inventory(optix_include) != \
                native_manifest["build_input"]["optix_header_inventory"] \
            or _header_inventory(cuda_include) != \
                native_manifest["build_input"]["cuda_header_inventory"] \
            or any(
                _sha(Path(runtime_environment[path_key])) !=
                    runtime_environment[sha_key]
                for path_key, sha_key in (
                    ("nvrtc_library", "nvrtc_sha256"),
                    ("nvvm_library", "nvvm_sha256"),
                    ("libdevice", "libdevice_sha256"),
                )
            ):
        raise RuntimeError("source identity changed during GPU validation")
    result = {
        "schema": "rtdl.successor_owner_grouped_any_hit.pod_validation.v1",
        "status": "PASS__TRUE_OPTIX_PARITY_AND_PREPARED_REUSE",
        "scope": "bounded paper-derived linear RT-CCD owner-grouped Boolean subset",
        "git_commit": pre_commit,
        "git_status_before_run": pre_status.splitlines(),
        "git_status_after_run": post_status.splitlines(),
        "dirty_run_authorized": bool(args.allow_dirty),
        "execution_source_inventory": pre_sources,
        "native_build_manifest": {
            "path": str(native_manifest_path),
            "sha256": native_manifest_sha_before,
            "build_id": native_manifest["build_id"],
            "native_sha256": native_manifest["native_sha256"],
        },
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "gpu": gpu_identity,
            "nvcc_path": native_manifest["nvcc_path"],
            "nvcc_sha256": native_manifest["nvcc_sha256"],
            "nvcc_version": native_manifest["nvcc_version"],
            "host_compiler_path": native_manifest["host_compiler_path"],
            "host_compiler_sha256":
                native_manifest["host_compiler_sha256"],
            "host_compiler_version":
                native_manifest["host_compiler_version"],
            "runtime_environment": runtime_environment,
        },
        "target": {
            "native_path": str(native),
            "native_sha256": _sha(native),
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "optix_include": str(optix_include),
            "cuda_include": str(cuda_include),
        },
        "registered_local_workload_count": len(registered_local_cases()),
        "scale_workload_count": len(scales),
        "workload_count": len(rows),
        "repeat_count_per_workload": args.repeat,
        "true_optix_launch_count": launch_count,
        "matching_gpu_execution_count": len(rows) * args.repeat,
        "all_independent_oracles_match": True,
        "all_true_optix_receipts_valid": True,
        "all_prepared_reuse_counts_match": True,
        "diagnostic_timing_sample_count": len(rows) * args.repeat,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "author_code_executed": False,
        "full_paper_reproduction_claimed": False,
        "benchmark_app_claimed": False,
        "external_review_count": 0,
        "workloads": rows,
    }
    _write_json_exclusive(output, result)
    incomplete.unlink()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--native-manifest", required=True, type=Path)
    parser.add_argument("--optix-prefix", required=True, type=Path)
    parser.add_argument("--cuda-prefix", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--nvvm-library", type=Path)
    parser.add_argument("--libdevice", type=Path)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--scale", type=_parse_scale, action="append")
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    if args.repeat < 2 or args.repeat > 20:
        raise SystemExit("--repeat must be in [2,20] to prove prepared reuse")
    cuda_prefix, _ = _validated_include_from_prefix(
        args.cuda_prefix, args.cuda_include, label="cuda")
    optix_prefix, _ = _validated_include_from_prefix(
        args.optix_prefix, args.optix_include, label="optix")
    runtime_files = resolve_cuda_runtime_files(
        cuda_prefix,
        nvrtc_library=args.nvrtc_library,
        nvvm_library=args.nvvm_library,
        libdevice=args.libdevice,
    )
    args.runtime_environment_identity = ensure_runtime_environment(
        cuda_prefix,
        optix_prefix,
        runtime_files,
        argv=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
    )
    result = validate(args)
    print(json.dumps({
        "status": result["status"],
        "workload_count": result["workload_count"],
        "true_optix_launch_count": result["true_optix_launch_count"],
        "performance_claimed": result["performance_claimed"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

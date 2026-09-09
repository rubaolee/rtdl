#!/usr/bin/env python3
"""Freeze and run the natural-scale authored Particle A/C comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import signal
import statistics
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.v4.authored_particle.transition_ensemble_formal.v3"
PREREG_SCHEMA = f"{SCHEMA}.preregistration"
QUERY_COUNT = 160_000_000
WARMUPS = 1
SAMPLES = 3
CALIBRATION_WORKERS = 3
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 9_202_609
ORDERS = (
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
)
SOURCE_PATHS = (
    "scripts/authored_particle_transition_ensemble_formal_compare.py",
    "scripts/authored_particle_transition_ensemble_worker.py",
    "scripts/generate_authored_particle_transition_ensemble.py",
    "scripts/build_authored_particle_pyoptix_ptx.py",
    "scripts/build_v4_optix_native_snapshot.py",
    "experiments/v4_authored_particle/program.py",
    "experiments/v4_authored_particle/pyoptix_device.cu",
    "experiments/v4_paper_apps_pyoptix/inputs.py",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "experiments/goal5814_particle/public_pyoptix_owner.py",
    "src/rtdsl/v4.py",
    "src/rtdsl/v4_public_builtin_triangle.py",
    "src/rtdsl/v4_callback_cuda_inline_codegen.py",
    "src/rtdsl/v4_triangle_optix_compiler.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_prepared_runtime.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, object]:
    value = Path(path).resolve(strict=True)
    return {
        "path": str(value),
        "bytes": value.stat().st_size,
        "sha256": sha256(value),
    }


def checked_binding(value: object) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ValueError("exact file binding required")
    path = Path(value["path"]).resolve(strict=True)
    if binding(path) != value:
        raise ValueError(f"bound file changed: {path}")
    return path


def read_json(path: str | Path) -> dict[str, object]:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON value is forbidden: {value}")

    value = json.loads(
        Path(path).read_text(encoding="utf-8"), parse_constant=reject_nonfinite)
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def write_new(path: str | Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def append_ledger(path: Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False)
               + "\n").encode()
    with path.open("ab") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def gpu_identity(uuid: str) -> dict[str, str]:
    completed = subprocess.run([
        "nvidia-smi", "-i", uuid,
        "--query-gpu=uuid,name,driver_version,compute_cap",
        "--format=csv,noheader,nounits",
    ], check=True, capture_output=True, text=True)
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("formal Particle comparison requires one selected GPU")
    fields = tuple(item.strip() for item in rows[0].split(","))
    if len(fields) != 4 or fields[0] != uuid:
        raise RuntimeError("selected Particle GPU identity differs")
    return dict(zip(("uuid", "name", "driver", "compute_capability"), fields))


def worker_environment(prereg: dict[str, object]) -> dict[str, str]:
    environment = dict(os.environ)
    root = Path(prereg["source_root"])
    environment.update({
        "CUDA_VISIBLE_DEVICES": prereg["gpu"]["uuid"],
        "CUDA_HOME": prereg["cuda_home"],
        "LD_LIBRARY_PATH": prereg["ld_library_path"],
        "PYTHONPATH": os.pathsep.join((str(root / "src"), str(root))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "CUDA_CACHE_DISABLE": "1",
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "NUMBA_CUDA_USE_NVIDIA_BINDING": prereg[
            "numba_cuda_use_nvidia_binding"],
    })
    return environment


def worker_command(
    prereg: dict[str, object], arm: str, *, samples: int,
    formal_worker: bool,
) -> list[str]:
    command = [
        prereg["python"],
        str(Path(prereg["source_root"])
            / "scripts/authored_particle_transition_ensemble_worker.py"),
        "--arm", arm,
        "--base-particle-dir", prereg["base_particle_dir"],
        "--ensemble-dir", prereg["ensemble_dir"],
        "--query-count", str(QUERY_COUNT),
        "--warmups", str(WARMUPS),
        "--samples", str(samples),
    ]
    if formal_worker:
        command.append("--formal-worker")
    if arm == "rtdl":
        command.extend([
            "--native", prereg["native_library"]["path"],
            "--optix-include", prereg["optix_include"],
            "--cuda-include", prereg["cuda_include"],
            "--compute-capability", prereg["gpu"]["compute_capability"],
            "--optix-sdk", prereg["optix_sdk"],
        ])
    elif arm == "pyoptix":
        command.extend([
            "--pyoptix-ptx", prereg["pyoptix_ptx"]["path"],
        ])
    else:
        raise ValueError(f"unknown arm: {arm}")
    return command


def validate_worker(
    prereg: dict[str, object], value: dict[str, object], arm: str,
    *, samples: int, formal_worker: bool,
) -> None:
    expected_machine = {
        "hostname": prereg["hostname"],
        "python": prereg["python_version"],
        "gpu_name": prereg["gpu"]["name"],
        "gpu_uuid": prereg["gpu"]["uuid"],
        "driver": prereg["gpu"]["driver"],
        "compute_capability": prereg["gpu"]["compute_capability"],
        "cuda_visible_devices": prereg["gpu"]["uuid"],
        "numba_cuda_use_nvidia_binding": prereg[
            "numba_cuda_use_nvidia_binding"],
    }
    if value.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble_worker.v2" \
            or value.get("status") != "PASS" \
            or value.get("arm") != arm \
            or value.get("source") != {
                "commit": prereg["source_commit"],
                "tree": prereg["source_tree"],
            } \
            or value.get("machine") != expected_machine \
            or value.get("query_count") != QUERY_COUNT \
            or value.get("output_shape") != [QUERY_COUNT, 3] \
            or value.get("base_manifest_sha256") \
                != prereg["base_manifest"]["sha256"] \
            or value.get("ensemble_manifest_sha256") \
                != prereg["ensemble_manifest"]["sha256"] \
            or value.get("input_sha256") != prereg["input_sha256"] \
            or value.get("independent_oracle_sha256") \
                != prereg["independent_oracle_sha256"] \
            or value.get("output_sha256") != prereg["output_sha256"] \
            or value.get("warmup_count") != WARMUPS \
            or value.get("sample_count") != samples \
            or len(value.get("samples_ns", [])) != samples \
            or any(type(item) is not int or item <= 0
                   for item in value.get("samples_ns", [])) \
            or value.get("median_ns") \
                != statistics.median(value["samples_ns"]) \
            or any(type(value.get(key)) is not int or value[key] < 0
                   for key in ("prepare_ns", "close_ns")) \
            or value.get("claim_boundary") != {
                "diagnostic_only": True,
                "formal_worker_zero_reached": formal_worker,
                "natural_single_transition_ensemble": True,
                "temporal_particle_simulation": False,
            }:
        raise ValueError(f"formal Particle {arm} worker contract differs")
    metadata = value["metadata"]
    evidence = value["last_execution_evidence"]
    if arm == "rtdl":
        if metadata.get("path_class") \
                != "public_rtdl_provider_native_closest_prepared" \
                or metadata.get("native_library_sha256") \
                    != prereg["native_library"]["sha256"] \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or metadata.get("oracle_validation") \
                    != "canonical_u32x3_sha256" \
                or evidence.get("output_sha256") != prereg["output_sha256"] \
                or evidence.get("physical_executor_classification") \
                    != "optix_traversal_observed" \
                or evidence.get("role_counters") \
                    != [0, QUERY_COUNT, 0, 0, QUERY_COUNT, 0, QUERY_COUNT]:
            raise ValueError("formal RTDL Particle evidence differs")
    else:
        prepared = metadata.get("prepared_query_batch_operation_counts", {})
        counts = evidence.get("operation_counts", {})
        if metadata.get("path_class") \
                != "public_pyoptix_native_closest_prepared" \
                or metadata.get("pyoptix_ptx_sha256") \
                    != prereg["pyoptix_ptx"]["sha256"] \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or metadata.get("output_layout") \
                    != "aos_u32x3_c_contiguous" \
                or metadata.get("output_strides") != [12, 4] \
                or prepared.get("query_h2d_copy_call_count") != 7 \
                or prepared.get("query_h2d_bytes") != QUERY_COUNT * 7 * 4 \
                or prepared.get("pinned_host_allocation_call_count") != 0 \
                or counts.get("query_h2d_copy_call_count") != 0 \
                or counts.get("query_h2d_bytes") != 0 \
                or counts.get("optix_launch_call_count") != 1 \
                or counts.get("output_d2h_bytes") != QUERY_COUNT * 3 * 4 \
                or evidence.get("control") \
                    != [QUERY_COUNT, 0xFFFFFFFF, 0, 0]:
            raise ValueError("formal PyOptiX Particle evidence differs")


def validate_prereg(path: str | Path) -> dict[str, object]:
    prereg = read_json(path)
    root = Path(prereg.get("source_root", "")).resolve(strict=True)
    if prereg.get("schema") != PREREG_SCHEMA \
            or prereg.get("status") != "FROZEN_BEFORE_FORMAL_WORKER_ZERO" \
            or git("rev-parse", "HEAD") != prereg.get("source_commit") \
            or git("rev-parse", "HEAD^{tree}") != prereg.get("source_tree") \
            or root != ROOT \
            or git("status", "--porcelain") \
            or prereg.get("query_count") != QUERY_COUNT \
            or prereg.get("pyoptix_output_layout") \
                != "aos_u32x3_c_contiguous" \
            or prereg.get("warmups") != WARMUPS \
            or prereg.get("samples") != SAMPLES \
            or tuple(tuple(row) for row in prereg.get("orders", ())) != ORDERS \
            or type(prereg.get("worker_timeout_seconds")) is not int \
            or prereg["worker_timeout_seconds"] < 120 \
            or prereg.get("retry_count") != 0 \
            or prereg.get("discard_count") != 0 \
            or prereg.get("numba_cuda_use_nvidia_binding") != "1" \
            or prereg.get("engineering_targets") != {
                "paired_median_rtdl_over_pyoptix_at_most": 1.20,
                "every_block_rtdl_over_pyoptix_at_most": 1.35,
                "targets_are_not_sample_filters": True,
            } \
            or prereg.get("claim_boundary") != {
                "natural_single_transition_ensemble": True,
                "temporal_particle_simulation": False,
                "full_trajectory_tracking": False,
                "public_claim_authorized": False,
            }:
        raise ValueError("formal Particle preregistration identity differs")
    if len(prereg.get("source_files", ())) != len(SOURCE_PATHS):
        raise ValueError("formal Particle source closure length differs")
    for relative, row in zip(SOURCE_PATHS, prereg["source_files"], strict=True):
        if checked_binding(row) != (ROOT / relative).resolve(strict=True):
            raise ValueError(f"formal Particle source differs: {relative}")
    for name in (
        "base_manifest", "ensemble_manifest", "native_library",
        "native_build", "pyoptix_ptx", "pyoptix_build",
        "c_only_calibration",
    ):
        checked_binding(prereg[name])
    native_build = read_json(prereg["native_build"]["path"])
    pyoptix_build = read_json(prereg["pyoptix_build"]["path"])
    if native_build.get("status") \
            != "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED" \
            or native_build.get("git_commit") != prereg["source_commit"] \
            or native_build.get("native_sha256") \
                != prereg["native_library"]["sha256"]:
        raise ValueError("formal Particle native build differs")
    if pyoptix_build.get("status") \
            != "PASS__AUTHORED_PARTICLE_PUBLIC_PYOPTIX_PTX_BUILT" \
            or pyoptix_build.get("source_commit") != prereg["source_commit"] \
            or pyoptix_build.get("source_tree") != prereg["source_tree"] \
            or pyoptix_build.get("ptx") != prereg["pyoptix_ptx"]:
        raise ValueError("formal Particle PyOptiX PTX build differs")
    if gpu_identity(prereg["gpu"]["uuid"]) != prereg["gpu"]:
        raise ValueError("formal Particle GPU identity changed")
    return prereg


def run_worker(
    prereg: dict[str, object], arm: str, *, samples: int,
    directory: Path, formal_worker: bool, validate: bool = True,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    command = worker_command(
        prereg, arm, samples=samples, formal_worker=formal_worker)
    write_new(directory / "COMMAND.json", command)
    started = time.perf_counter_ns()
    process = subprocess.Popen(
        command, cwd=prereg["source_root"], env=worker_environment(prereg),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(
            timeout=prereg["worker_timeout_seconds"])
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
    process_wall_ns = time.perf_counter_ns() - started
    (directory / "STDOUT.bin").write_bytes(stdout)
    (directory / "STDERR.bin").write_bytes(stderr)
    write_new(directory / "EXIT.json", {
        "returncode": process.returncode,
        "timed_out": timed_out,
        "process_wall_ns": process_wall_ns,
    })
    record = {
        "arm": arm,
        "samples": samples,
        "timed_out": timed_out,
        "returncode": process.returncode,
        "process_wall_ns": process_wall_ns,
        "command": binding(directory / "COMMAND.json"),
        "stdout": binding(directory / "STDOUT.bin"),
        "stderr": binding(directory / "STDERR.bin"),
        "exit": binding(directory / "EXIT.json"),
    }
    if timed_out or process.returncode:
        raise RuntimeError(
            f"formal Particle worker failed: arm={arm} "
            f"timeout={timed_out} code={process.returncode}")
    result = json.loads(stdout)
    if validate:
        validate_worker(
            prereg, result, arm, samples=samples,
            formal_worker=formal_worker)
    elif result.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble_worker.v2" \
            or result.get("status") != "PASS" \
            or result.get("arm") != arm \
            or result.get("source") != {
                "commit": prereg["source_commit"],
                "tree": prereg["source_tree"],
            } \
            or result.get("query_count") != QUERY_COUNT \
            or result.get("warmup_count") != WARMUPS \
            or result.get("sample_count") != samples \
            or result.get("claim_boundary", {}).get(
                "formal_worker_zero_reached") is not formal_worker:
        raise ValueError(f"calibration Particle {arm} worker contract differs")
    record["worker_result"] = result
    return record


def bootstrap_interval(values: list[float]) -> list[float]:
    generator = random.Random(BOOTSTRAP_SEED)
    draws = sorted(statistics.median(
        generator.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS))
    return [draws[249], draws[9749]]


def command_freeze(args: argparse.Namespace) -> int:
    if git("status", "--porcelain"):
        raise RuntimeError("formal Particle freeze requires a clean source tree")
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    native_build = read_json(args.native_build)
    pyoptix_build = read_json(args.pyoptix_build)
    if native_build.get("git_commit") != commit \
            or pyoptix_build.get("source_commit") != commit \
            or pyoptix_build.get("source_tree") != tree:
        raise ValueError("formal artifacts were not built from exact source")
    ensemble = args.ensemble_dir.resolve(strict=True)
    ensemble_manifest = read_json(ensemble / "MANIFEST.json")
    if ensemble_manifest.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble.v1" \
            or ensemble_manifest.get("queries", {}).get("count") != QUERY_COUNT \
            or ensemble_manifest.get("queries", {}).get("distinct_origin_count") \
                != QUERY_COUNT:
        raise ValueError("formal Particle ensemble contract differs")
    gpu = gpu_identity(args.gpu_uuid)
    provisional: dict[str, object] = {
        "source_root": str(ROOT),
        "source_commit": commit,
        "source_tree": tree,
        "base_particle_dir": str(args.base_particle_dir.resolve(strict=True)),
        "ensemble_dir": str(ensemble),
        "base_manifest": binding(
            args.base_particle_dir.resolve(strict=True) / "MANIFEST.json"),
        "native_library": binding(args.native),
        "pyoptix_ptx": binding(args.pyoptix_ptx),
        "python": str(Path(sys.executable).resolve(strict=True)),
        "optix_sdk": args.optix_sdk,
        "optix_include": str(args.optix_include.resolve(strict=True)),
        "cuda_include": str(args.cuda_include.resolve(strict=True)),
        "cuda_home": str(args.cuda_home.resolve(strict=True)),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH", ""),
        # Keep the binding choice explicit alongside the registered CUDA_HOME
        # and NVRTC library path. The pre-worker-zero RTDL probe below rejects
        # any combination that emits incompatible leaf and wrapper PTX.
        "numba_cuda_use_nvidia_binding": "1",
        "gpu": gpu,
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "worker_timeout_seconds": args.worker_timeout_seconds,
    }
    calibration_root = args.calibration_output.resolve()
    calibration_root.mkdir(parents=True, exist_ok=False)
    target_probe = run_worker(
        provisional, "rtdl", samples=1,
        directory=calibration_root / "rtdl_target_compatibility_probe",
        formal_worker=False, validate=False)
    calibration_workers = []
    for ordinal in range(CALIBRATION_WORKERS):
        record = run_worker(
            provisional, "pyoptix", samples=1,
            directory=calibration_root / f"worker_{ordinal:02d}",
            formal_worker=False, validate=False)
        calibration_workers.append(record)
    all_probe_workers = [target_probe, *calibration_workers]
    outputs = {row["worker_result"]["output_sha256"]
               for row in all_probe_workers}
    inputs = {row["worker_result"]["input_sha256"]
              for row in all_probe_workers}
    oracles = {row["worker_result"]["independent_oracle_sha256"]
               for row in all_probe_workers}
    if len(outputs) != 1 or len(inputs) != 1 or len(oracles) != 1:
        raise RuntimeError("C-only calibration identities differ")
    provisional.update({
        "input_sha256": next(iter(inputs)),
        "independent_oracle_sha256": next(iter(oracles)),
        "output_sha256": next(iter(outputs)),
        "ensemble_manifest": binding(ensemble / "MANIFEST.json"),
    })
    for row in calibration_workers:
        validate_worker(
            provisional, row["worker_result"], "pyoptix", samples=1,
            formal_worker=False)
    validate_worker(
        provisional, target_probe["worker_result"], "rtdl", samples=1,
        formal_worker=False)
    calibration = {
        "schema": f"{SCHEMA}.c_only_calibration",
        "status": "PASS__THREE_FRESH_C_WORKERS_RETAINED",
        "purpose": (
            "confirm_previously_selected_160m_natural_scale_without_reselection"),
        "rtdl_target_compatibility_probe": target_probe,
        "workers": calibration_workers,
        "medians_ns": [row["worker_result"]["median_ns"]
                       for row in calibration_workers],
        "median_ns": statistics.median(
            row["worker_result"]["median_ns"]
            for row in calibration_workers),
        "selection_boundary": {
            "scale_changed_after_rtdl_observation": False,
            "subsecond_confirmation_triggers_reselection": False,
            "all_confirmation_rows_retained": True,
        },
    }
    write_new(calibration_root / "CALIBRATION.json", calibration)
    prereg = {
        **provisional,
        "schema": PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_FORMAL_WORKER_ZERO",
        "source_files": [binding(ROOT / path) for path in SOURCE_PATHS],
        "base_manifest": provisional["base_manifest"],
        "ensemble_manifest": provisional["ensemble_manifest"],
        "native_build": binding(args.native_build),
        "pyoptix_build": binding(args.pyoptix_build),
        "c_only_calibration": binding(calibration_root / "CALIBRATION.json"),
        "query_count": QUERY_COUNT,
        "pyoptix_output_layout": "aos_u32x3_c_contiguous",
        "input_sha256": provisional["input_sha256"],
        "independent_oracle_sha256": provisional[
            "independent_oracle_sha256"],
        "output_sha256": provisional["output_sha256"],
        "warmups": WARMUPS,
        "samples": SAMPLES,
        "orders": [list(row) for row in ORDERS],
        "retry_count": 0,
        "discard_count": 0,
        "engineering_targets": {
            "paired_median_rtdl_over_pyoptix_at_most": 1.20,
            "every_block_rtdl_over_pyoptix_at_most": 1.35,
            "targets_are_not_sample_filters": True,
        },
        "endpoint": (
            "prepared_natural_160m_transition_full_u32x3_d2h_"
            "public_validation_wall_ns"),
        "claim_boundary": {
            "natural_single_transition_ensemble": True,
            "temporal_particle_simulation": False,
            "full_trajectory_tracking": False,
            "public_claim_authorized": False,
        },
    }
    write_new(args.output, prereg)
    validate_prereg(args.output)
    print(args.output.resolve())
    return 0


def command_run(args: argparse.Namespace) -> int:
    prereg = validate_prereg(args.preregistration)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    workers_root = output / "workers"
    workers_root.mkdir()
    ledger = output / "APPEND_ONLY_LEDGER.jsonl"
    workers = []
    ordinal = 0
    try:
        for block, order in enumerate(ORDERS):
            for position, arm in enumerate(order):
                directory = workers_root / f"{ordinal:02d}_{arm}"
                try:
                    record = run_worker(
                        prereg, arm, samples=SAMPLES, directory=directory,
                        formal_worker=True)
                except BaseException as error:
                    retained_artifacts = {}
                    for name in (
                        "COMMAND.json", "STDOUT.bin", "STDERR.bin", "EXIT.json",
                    ):
                        path = directory / name
                        if path.is_file():
                            retained_artifacts[name] = binding(path)
                    failure = {
                        "ordinal": ordinal, "block": block,
                        "position": position, "arm": arm,
                        "status": "TERMINAL_FAILURE_RETAINED_NO_RETRY",
                        "error_type": type(error).__name__, "error": str(error),
                        "worker_directory": str(directory.resolve()),
                        "retained_artifacts": retained_artifacts,
                    }
                    append_ledger(ledger, failure)
                    write_new(output / "FAILURE.json", {
                        "schema": f"{SCHEMA}.failure", **failure,
                        "completed_worker_count": len(workers),
                        "retry_count": 0, "discard_count": 0,
                    })
                    raise
                record.update({
                    "ordinal": ordinal, "block": block,
                    "position": position, "status": "PASS_RETAINED",
                })
                workers.append(record)
                append_ledger(ledger, {
                    "ordinal": ordinal, "block": block,
                    "position": position, "arm": arm,
                    "status": "PASS_RETAINED",
                    "median_ns": record["worker_result"]["median_ns"],
                    "stdout_sha256": record["stdout"]["sha256"],
                })
                ordinal += 1
    except BaseException:
        raise
    block_rows = []
    for block, order in enumerate(ORDERS):
        rows = [row for row in workers if row["block"] == block]
        by_arm = {row["arm"]: row["worker_result"] for row in rows}
        ratio = by_arm["rtdl"]["median_ns"] / by_arm["pyoptix"]["median_ns"]
        block_rows.append({
            "block": block,
            "order": list(order),
            "rtdl_median_ns": by_arm["rtdl"]["median_ns"],
            "pyoptix_median_ns": by_arm["pyoptix"]["median_ns"],
            "rtdl_over_pyoptix": ratio,
            "rtdl_queries_per_second": (
                QUERY_COUNT * 1e9 / by_arm["rtdl"]["median_ns"]),
            "pyoptix_queries_per_second": (
                QUERY_COUNT * 1e9 / by_arm["pyoptix"]["median_ns"]),
        })
    ratios = [row["rtdl_over_pyoptix"] for row in block_rows]
    paired_median = statistics.median(ratios)
    worst = max(ratios)
    result = {
        "schema": f"{SCHEMA}.result",
        "status": (
            "PASS__INTERNAL_ENGINEERING_TARGETS__LEAD_RECOUNT_PENDING"
            if paired_median <= 1.20 and worst <= 1.35
            else "FAILED_ENGINEERING_TARGETS__ADVERSE_RESULT_RETAINED"),
        "preregistration": binding(args.preregistration),
        "source_commit": prereg["source_commit"],
        "source_tree": prereg["source_tree"],
        "gpu": prereg["gpu"],
        "query_count": QUERY_COUNT,
        "input_sha256": prereg["input_sha256"],
        "output_sha256": prereg["output_sha256"],
        "block_rows": block_rows,
        "paired_median_rtdl_over_pyoptix": paired_median,
        "worst_block_rtdl_over_pyoptix": worst,
        "block_bootstrap_95_percent": bootstrap_interval(ratios),
        "worker_count": len(workers),
        "timed_sample_count": len(workers) * SAMPLES,
        "warmup_count": len(workers) * WARMUPS,
        "rtdl_prepare_median_ns": statistics.median(
            row["worker_result"]["prepare_ns"]
            for row in workers if row["arm"] == "rtdl"),
        "pyoptix_prepare_median_ns": statistics.median(
            row["worker_result"]["prepare_ns"]
            for row in workers if row["arm"] == "pyoptix"),
        "retry_count": 0,
        "discard_count": 0,
        "workers": workers,
        "claim_boundary": {
            "internal_engineering_target_only": True,
            "lead_independent_recount_completed": False,
            "paper_claim_authorized": False,
            "natural_single_transition_ensemble": True,
            "temporal_particle_simulation": False,
            "scale_reselected_after_outcome": False,
        },
    }
    write_new(output / "RESULT.json", result)
    print((output / "RESULT.json").resolve())
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    commands = value.add_subparsers(dest="command", required=True)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--base-particle-dir", type=Path, required=True)
    freeze.add_argument("--ensemble-dir", type=Path, required=True)
    freeze.add_argument("--native", type=Path, required=True)
    freeze.add_argument("--native-build", type=Path, required=True)
    freeze.add_argument("--pyoptix-ptx", type=Path, required=True)
    freeze.add_argument("--pyoptix-build", type=Path, required=True)
    freeze.add_argument("--gpu-uuid", required=True)
    freeze.add_argument("--optix-sdk", default="8.0.0")
    freeze.add_argument("--optix-include", type=Path, required=True)
    freeze.add_argument("--cuda-include", type=Path, required=True)
    freeze.add_argument("--cuda-home", type=Path, required=True)
    freeze.add_argument("--worker-timeout-seconds", type=int, default=300)
    freeze.add_argument("--calibration-output", type=Path, required=True)
    freeze.add_argument("--output", type=Path, required=True)
    freeze.set_defaults(handler=command_freeze)
    run = commands.add_parser("run")
    run.add_argument("--preregistration", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=command_run)
    return value


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "worker_timeout_seconds", 300) < 120:
        raise ValueError("formal Particle worker timeout must be at least 120 seconds")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

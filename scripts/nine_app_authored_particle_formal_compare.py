#!/usr/bin/env python3
"""Fresh-process formal comparison for the public-authored Particle path."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import threading
import time


SCHEMA = "rtdl.nine_app.authored_particle.formal_compare.v1"
PREREG_SCHEMA = f"{SCHEMA}.preregistration"
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
    "scripts/nine_app_authored_particle_formal_compare.py",
    "scripts/build_authored_particle_pyoptix_ptx.py",
    "scripts/v4_authored_particle_worker.py",
    "experiments/v4_authored_particle/program.py",
    "experiments/v4_authored_particle/pyoptix_device.cu",
    "experiments/v4_paper_apps_pyoptix/inputs.py",
    "experiments/v4_paper_apps_pyoptix/particle_adapter.py",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "experiments/goal5814_particle/public_pyoptix_owner.py",
    "src/rtdsl/v4.py",
    "src/rtdsl/v4_public_builtin_triangle.py",
    "src/rtdsl/v4_triangle_optix_compiler.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_prepared_runtime.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
)
PRIMARY_WARMUPS = 1
PRIMARY_CALLS = 215
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 9_202_609


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


def read_json(path: str | Path) -> dict[str, object]:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON value is forbidden: {value}")

    value = json.loads(
        Path(path).read_text(encoding="utf-8"),
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def write_new(path: str | Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False,
    ) + "\n").encode("utf-8")
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def gpu_identity(gpu_uuid: str) -> dict[str, str]:
    completed = subprocess.run([
        "nvidia-smi", "-i", gpu_uuid,
        "--query-gpu=uuid,name,driver_version,compute_cap",
        "--format=csv,noheader,nounits",
    ], check=True, capture_output=True, text=True)
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("formal Particle comparison requires one selected GPU")
    fields = [field.strip() for field in rows[0].split(",")]
    if len(fields) != 4 or fields[0] != gpu_uuid:
        raise RuntimeError("selected Particle GPU identity differs")
    return {
        "uuid": fields[0],
        "name": fields[1],
        "driver": fields[2],
        "compute_capability": fields[3],
    }


def checked_binding(row: object) -> Path:
    if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
        raise ValueError("exact file binding required")
    path = Path(row["path"]).resolve(strict=True)
    if binding(path) != row:
        raise ValueError(f"bound file changed: {path}")
    return path


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
    })
    return environment


def worker_command(
    prereg: dict[str, object], arm: str, *, warmups: int, samples: int,
) -> list[str]:
    command = [
        prereg["python"],
        str(Path(prereg["source_root"]) / "scripts/v4_authored_particle_worker.py"),
        "--arm", arm,
        "--data-root", prereg["data_root"],
        "--optix-sdk", prereg["optix_sdk"],
        "--warmups", str(warmups),
        "--samples", str(samples),
    ]
    if arm == "rtdl":
        command.extend([
            "--native", prereg["native_library"]["path"],
            "--optix-include", prereg["optix_include"],
            "--cuda-include", prereg["cuda_include"],
            "--compute-capability", prereg["gpu"]["compute_capability"],
        ])
    elif arm == "pyoptix":
        command.extend([
            "--pyoptix-ptx", prereg["pyoptix_ptx"]["path"],
        ])
    else:
        raise ValueError(f"unknown arm: {arm}")
    return command


def validate_prereg(path: str | Path) -> dict[str, object]:
    prereg = read_json(path)
    if prereg.get("schema") != PREREG_SCHEMA:
        raise ValueError("unexpected authored Particle preregistration schema")
    root = Path(prereg["source_root"]).resolve(strict=True)
    if git(root, "rev-parse", "HEAD") != prereg["source_commit"] \
            or git(root, "rev-parse", "HEAD^{tree}") != prereg["source_tree"]:
        raise ValueError("formal Particle source identity changed")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("formal Particle tracked source is dirty")
    for relative, row in zip(
            SOURCE_PATHS, prereg["source_files"], strict=True):
        if checked_binding(row) != (root / relative).resolve(strict=True):
            raise ValueError(f"formal Particle source closure differs: {relative}")
    for key in (
        "data_manifest", "native_library", "native_build", "pyoptix_ptx",
        "pyoptix_build", "calibration",
    ):
        checked_binding(prereg[key])
    native_build = read_json(prereg["native_build"]["path"])
    if native_build.get("status") != \
            "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED" \
            or native_build.get("git_commit") != prereg["source_commit"] \
            or git(root, "rev-parse", f"{native_build['git_commit']}^{{tree}}") \
                != prereg["source_tree"] \
            or native_build.get("native_sha256") \
                != prereg["native_library"]["sha256"]:
        raise ValueError("formal Particle native build binding differs")
    pyoptix_build = read_json(prereg["pyoptix_build"]["path"])
    if pyoptix_build.get("schema") != \
            "rtdl.v4.authored_particle.public_pyoptix_ptx_build.v1" \
            or pyoptix_build.get("status") != \
                "PASS__AUTHORED_PARTICLE_PUBLIC_PYOPTIX_PTX_BUILT" \
            or pyoptix_build.get("source_commit") != prereg["source_commit"] \
            or pyoptix_build.get("source_tree") != prereg["source_tree"] \
            or pyoptix_build.get("source") != prereg["source_files"][4] \
            or pyoptix_build.get("ptx") != prereg["pyoptix_ptx"] \
            or pyoptix_build.get("compute_capability") != [
                int(value) for value in prereg["gpu"][
                    "compute_capability"].split(".")
            ]:
        raise ValueError("formal Particle public-PyOptiX PTX build differs")
    if tuple(tuple(row) for row in prereg["orders"]) != ORDERS \
            or prereg["primary_warmups"] != PRIMARY_WARMUPS \
            or prereg["primary_calls"] != PRIMARY_CALLS:
        raise ValueError("formal Particle schedule differs")
    if gpu_identity(prereg["gpu"]["uuid"]) != prereg["gpu"]:
        raise ValueError("formal Particle GPU identity changed")
    return prereg


def validate_worker(
    prereg: dict[str, object], result: dict[str, object], arm: str,
    *, warmups: int, samples: int,
) -> None:
    try:
        output_bytes = base64.b64decode(
            result.get("output_u32_le_base64", ""), validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError(
            f"formal Particle {arm} output encoding differs") from error
    output_digest = hashlib.sha256()
    output_digest.update(b"<u4")
    output_digest.update(b"(5000, 3)")
    output_digest.update(output_bytes)
    if result.get("schema") != "rtdl.v4.authored_particle_worker.v2" \
            or result.get("status") != "PASS" \
            or result.get("arm") != arm \
            or result.get("source") != {
                "commit": prereg["source_commit"],
                "tree": prereg["source_tree"],
            } \
            or result.get("input_sha256") \
                != prereg["data_manifest"]["sha256"] \
            or result.get("independent_oracle_sha256") \
                != prereg["independent_oracle_sha256"] \
            or result.get("query_count") != 5_000 \
            or result.get("output_shape") != [5_000, 3] \
            or result.get("output_sha256") != prereg["output_sha256"] \
            or len(output_bytes) != 60_000 \
            or output_digest.hexdigest() != prereg["output_sha256"] \
            or result.get("warmup_count") != warmups \
            or result.get("sample_count") != samples \
            or len(result.get("samples_ns", [])) != samples \
            or any(type(value) is not int or value <= 0
                   for value in result.get("samples_ns", [])) \
            or result.get("median_ns") \
                != statistics.median(result.get("samples_ns", [])) \
            or any(type(result.get(key)) is not int or result[key] <= 0
                   for key in ("prepare_ns", "close_ns", "lifecycle_ns")) \
            or result.get("retained_output_owned") is not True \
            or result.get("retained_output_read_only") is not True \
            or result.get("machine") != prereg["worker_machine"]:
        raise ValueError(f"formal Particle {arm} worker contract differs")
    metadata = result["metadata"]
    if arm == "rtdl":
        evidence = result["last_execution_evidence"]
        if metadata.get("native_library_sha256") \
                != prereg["native_library"]["sha256"] \
                or metadata.get("path_class") != \
                    "public_source_verify_compile_materialize_prepare_execute" \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or evidence.get("physical_executor_classification") != \
                    "optix_traversal_observed" \
                or evidence.get("role_counters") != [0, 5000, 0, 0, 5000, 0, 5000]:
            raise ValueError("formal authored RTDL execution evidence differs")
    else:
        prepared_counts = metadata.get(
            "prepared_query_batch_operation_counts", {})
        execution_counts = result["last_execution_evidence"].get(
            "operation_counts", {})
        if metadata.get("pyoptix_ptx_sha256") \
                != prereg["pyoptix_ptx"]["sha256"] \
                or metadata.get("prevalidated_execution_input_used") is not True \
                or metadata.get("prepared_query_batch_used") is not True \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or prepared_counts.get("query_h2d_copy_call_count") != 7 \
                or prepared_counts.get("query_h2d_bytes") != 140_000 \
                or execution_counts.get("query_h2d_copy_call_count") != 0 \
                or execution_counts.get("query_h2d_bytes") != 0 \
                or execution_counts.get("optix_launch_call_count") != 1 \
                or execution_counts.get("output_d2h_bytes") != 60_000 \
                or result["last_execution_evidence"].get("control") \
                    != [5000, 0xFFFFFFFF, 0, 0]:
            raise ValueError("formal public-PyOptiX execution evidence differs")


class MemorySampler:
    def __init__(self, gpu_uuid: str) -> None:
        import pynvml
        self._pynvml = pynvml
        pynvml.nvmlInit()
        self._handle = pynvml.nvmlDeviceGetHandleByUUID(gpu_uuid)
        self._stop = threading.Event()
        self._baseline = self._used()
        self._peak = self._baseline
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _used(self) -> int:
        return int(self._pynvml.nvmlDeviceGetMemoryInfo(self._handle).used)

    def _sample(self) -> None:
        while not self._stop.wait(0.005):
            self._peak = max(self._peak, self._used())

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> dict[str, int]:
        self._stop.set()
        self._thread.join()
        self._peak = max(self._peak, self._used())
        self._pynvml.nvmlShutdown()
        return {
            "baseline_used_bytes": self._baseline,
            "peak_used_bytes": self._peak,
            "sampled_peak_delta_bytes": max(0, self._peak - self._baseline),
            "sampling_period_ms": 5,
        }


def run_worker(
    prereg: dict[str, object], arm: str, *, warmups: int, samples: int,
    directory: Path,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    command = worker_command(prereg, arm, warmups=warmups, samples=samples)
    write_new(directory / "COMMAND.json", command)
    sampler = MemorySampler(prereg["gpu"]["uuid"])
    started = time.perf_counter_ns()
    sampler.start()
    try:
        completed = subprocess.run(
            command,
            cwd=prereg["source_root"],
            env=worker_environment(prereg),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
    finally:
        process_wall_ns = time.perf_counter_ns() - started
        memory = sampler.stop()
    (directory / "STDOUT.json").write_bytes(completed.stdout)
    (directory / "STDERR.bin").write_bytes(completed.stderr)
    if completed.returncode:
        raise RuntimeError(
            f"formal Particle worker failed: arm={arm} code={completed.returncode}")
    result = json.loads(completed.stdout)
    validate_worker(
        prereg, result, arm, warmups=warmups, samples=samples)
    return {
        "arm": arm,
        "warmups": warmups,
        "samples": samples,
        "worker_result": result,
        "process_wall_ns": process_wall_ns,
        "memory": memory,
        "stdout": binding(directory / "STDOUT.json"),
        "stderr": binding(directory / "STDERR.bin"),
    }


def bootstrap_interval(values: list[float]) -> list[float]:
    generator = random.Random(BOOTSTRAP_SEED)
    draws = sorted(statistics.median(
        generator.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS))
    return [draws[249], draws[9749]]


def command_freeze(args: argparse.Namespace) -> int:
    root = args.source_root.resolve(strict=True)
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("formal Particle freeze requires clean tracked source")
    commit = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    native_build = read_json(args.native_build)
    if native_build.get("git_commit") != commit \
            or git(root, "rev-parse", f"{native_build['git_commit']}^{{tree}}") \
                != tree:
        raise ValueError("native build was not produced from exact formal source")
    gpu = gpu_identity(args.gpu_uuid)
    prereg: dict[str, object] = {
        "schema": PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_FORMAL_WORKER_ZERO",
        "source_root": str(root),
        "source_commit": commit,
        "source_tree": tree,
        "source_files": [binding(root / path) for path in SOURCE_PATHS],
        "data_root": str(args.data_root.resolve(strict=True)),
        "data_manifest": binding(
            args.data_root.resolve(strict=True) / "particle/MANIFEST.json"),
        "native_library": binding(args.native),
        "native_build": binding(args.native_build),
        "pyoptix_ptx": binding(args.pyoptix_ptx),
        "pyoptix_build": binding(args.pyoptix_build),
        "python": str(Path(sys.executable).absolute()),
        "python_resolved": str(Path(sys.executable).resolve(strict=True)),
        "optix_sdk": args.optix_sdk,
        "optix_include": str(args.optix_include.resolve(strict=True)),
        "cuda_include": str(args.cuda_include.resolve(strict=True)),
        "cuda_home": str(args.cuda_home.resolve(strict=True)),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH", ""),
        "gpu": gpu,
        "worker_machine": {
            "hostname": platform.node(),
            "python": platform.python_version(),
            "gpu_name": gpu["name"],
            "gpu_uuid": gpu["uuid"],
            "driver": gpu["driver"],
            "compute_capability": gpu["compute_capability"],
            "cuda_visible_devices": gpu["uuid"],
        },
        "versions": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "numba", "cupy-cuda12x", "pyoptix")
        },
        "orders": [list(row) for row in ORDERS],
        "primary_warmups": PRIMARY_WARMUPS,
        "primary_calls": PRIMARY_CALLS,
        "lifecycle_warmups": 0,
        "lifecycle_calls": 1,
        "engineering_targets": {
            "paired_median_rtdl_over_pyoptix_at_most": 1.20,
            "every_block_rtdl_over_pyoptix_at_most": 1.35,
            "targets_are_not_sample_filters": True,
        },
        "retry_count": 0,
        "discard_count": 0,
        "primary_endpoint": (
            "prepared_complete_u32x3_d2h_sync_and_exact_oracle_ns"),
        "lifecycle_endpoint": (
            "prepare_plus_first_complete_execution_plus_close_ns"),
    }
    environment = worker_environment(prereg)
    command = worker_command(
        prereg, "pyoptix", warmups=1, samples=args.calibration_calls)
    calibration = subprocess.run(
        command, cwd=root, env=environment, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    calibration_result = json.loads(calibration.stdout)
    prereg["independent_oracle_sha256"] = calibration_result[
        "independent_oracle_sha256"]
    prereg["output_sha256"] = calibration_result["output_sha256"]
    validate_worker(
        prereg, calibration_result, "pyoptix",
        warmups=1, samples=args.calibration_calls)
    calibration_record = {
        "schema": f"{SCHEMA}.c_only_calibration",
        "status": "PASS",
        "purpose": "select_short_task_replication_before_preregistration",
        "worker": calibration_result,
        "stderr_utf8": calibration.stderr.decode("utf-8", errors="replace"),
    }
    write_new(args.calibration_output, calibration_record)
    prereg["calibration"] = binding(args.calibration_output)
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
    workers: list[dict[str, object]] = []
    try:
        ordinal = 0
        for block, order in enumerate(ORDERS):
            for position, arm in enumerate(order):
                record = run_worker(
                    prereg, arm,
                    warmups=PRIMARY_WARMUPS,
                    samples=PRIMARY_CALLS,
                    directory=workers_root / f"primary_{ordinal:02d}_{arm}",
                )
                record.update({
                    "endpoint": "primary", "block": block,
                    "position": position, "ordinal": ordinal,
                })
                workers.append(record)
                ordinal += 1
        for position, arm in enumerate(("rtdl", "pyoptix")):
            record = run_worker(
                prereg, arm, warmups=0, samples=1,
                directory=workers_root / f"lifecycle_{position:02d}_{arm}",
            )
            record.update({
                "endpoint": "lifecycle", "block": None,
                "position": position, "ordinal": ordinal,
            })
            workers.append(record)
            ordinal += 1
    except BaseException as error:
        write_new(output / "FAILURE.json", {
            "schema": f"{SCHEMA}.failure",
            "status": "TERMINAL_FAILURE_RETAINED_NO_RETRY",
            "completed_worker_count": len(workers),
            "error_type": type(error).__name__,
            "error": str(error),
            "retry_count": 0,
            "discard_count": 0,
        })
        raise

    primary = [row for row in workers if row["endpoint"] == "primary"]
    block_rows = []
    for block in range(len(ORDERS)):
        rows = [row for row in primary if row["block"] == block]
        by_arm = {row["arm"]: row["worker_result"] for row in rows}
        ratio = by_arm["rtdl"]["median_ns"] / by_arm["pyoptix"]["median_ns"]
        block_rows.append({
            "block": block,
            "order": list(ORDERS[block]),
            "rtdl_median_ns": by_arm["rtdl"]["median_ns"],
            "pyoptix_median_ns": by_arm["pyoptix"]["median_ns"],
            "rtdl_over_pyoptix": ratio,
        })
    ratios = [row["rtdl_over_pyoptix"] for row in block_rows]
    paired_median = statistics.median(ratios)
    worst_block = max(ratios)
    lifecycle = {
        row["arm"]: row for row in workers if row["endpoint"] == "lifecycle"
    }
    lifecycle_values = {
        arm: row["worker_result"]["lifecycle_ns"]
        for arm, row in lifecycle.items()
    }
    summary = {
        "schema": f"{SCHEMA}.result",
        "status": (
            "PASS__INTERNAL_ENGINEERING_TARGETS__EXTERNAL_REVIEW_PENDING"
            if paired_median <= 1.20 and worst_block <= 1.35
            else "FAILED_ENGINEERING_TARGETS__ADVERSE_RESULT_RETAINED"
        ),
        "preregistration": binding(args.preregistration),
        "source_commit": prereg["source_commit"],
        "source_tree": prereg["source_tree"],
        "gpu": prereg["gpu"],
        "input_sha256": prereg["data_manifest"]["sha256"],
        "output_sha256": prereg["output_sha256"],
        "block_rows": block_rows,
        "paired_median_rtdl_over_pyoptix": paired_median,
        "worst_block_rtdl_over_pyoptix": worst_block,
        "block_bootstrap_95_percent": bootstrap_interval(ratios),
        "primary_worker_count": len(primary),
        "primary_timed_call_count": len(primary) * PRIMARY_CALLS,
        "primary_warmup_count": len(primary) * PRIMARY_WARMUPS,
        "lifecycle_worker_count": len(lifecycle),
        "lifecycle_ns": lifecycle_values,
        "lifecycle_rtdl_over_pyoptix": (
            lifecycle_values["rtdl"] / lifecycle_values["pyoptix"]),
        "retry_count": 0,
        "discard_count": 0,
        "worker_records": workers,
        "claim_boundary": {
            "internal_engineering_target_only": True,
            "external_review_completed": False,
            "paper_claim_authorized": False,
            "single_gpu_generation": True,
            "full_50000_step_advection": False,
            "sampled_peak_memory_is_lower_bound": True,
        },
    }
    write_new(output / "RESULT.json", summary)
    print(output / "RESULT.json")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    subcommands = value.add_subparsers(dest="command", required=True)
    freeze = subcommands.add_parser("freeze")
    freeze.add_argument("--source-root", type=Path, required=True)
    freeze.add_argument("--data-root", type=Path, required=True)
    freeze.add_argument("--native", type=Path, required=True)
    freeze.add_argument("--native-build", type=Path, required=True)
    freeze.add_argument("--pyoptix-ptx", type=Path, required=True)
    freeze.add_argument("--pyoptix-build", type=Path, required=True)
    freeze.add_argument("--gpu-uuid", required=True)
    freeze.add_argument("--optix-sdk", default="8.0.0")
    freeze.add_argument("--optix-include", type=Path, required=True)
    freeze.add_argument("--cuda-include", type=Path, required=True)
    freeze.add_argument("--cuda-home", type=Path, required=True)
    freeze.add_argument("--calibration-calls", type=int, default=32)
    freeze.add_argument("--calibration-output", type=Path, required=True)
    freeze.add_argument("--output", type=Path, required=True)
    freeze.set_defaults(handler=command_freeze)
    run = subcommands.add_parser("run")
    run.add_argument("--preregistration", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=command_run)
    return value


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "calibration_calls", 1) < 1:
        raise ValueError("calibration calls must be positive")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

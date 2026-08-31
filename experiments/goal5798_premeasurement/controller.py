#!/usr/bin/env python3
"""Create-only Goal5798 controller for A/B/D matched measurement.

The controller runs all 30 non-timed memory/correctness workers before worker
zero of the 288-worker timing schedule.  It never retries, resumes, replaces,
or drops a worker.  A failure leaves the create-only output root intact and
terminates the transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

from contract_runtime import (
    MEMORY_MODE,
    digest,
    load_freeze,
)
from formal_contract_runtime import validate_final_worker_receipt
from worker_common import (
    create_json,
    finish_receipt,
    load_execution_authority,
    load_runtime_manifest,
    sha256_file,
)
from workload import digest as workload_digest, relation_workload, triangle_workload


ARM_DIRECT = "A_DIRECT_CUDA_OPTIX"
ARM_PYOPTIX = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"
ARM_RTDL = "D_RTDL_PUBLIC"
RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
SCHEMA = "rtdl.goal5798.formal_controller_result.v1"


def create_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(
        f".{path.name}.tmp.{os.getpid()}.{time.monotonic_ns()}")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def worker_command(args: argparse.Namespace, row: dict[str, Any], output: Path, barrier: Path | None) -> list[str]:
    common = [
        "--freeze", str(args.freeze.resolve()),
        "--runtime-manifest", str(args.runtime_manifest.resolve()),
        "--execution-authority", str(args.execution_authority.resolve()),
        "--worker-id", row["worker_id"], "--output", str(output.resolve()),
    ]
    if barrier is not None:
        common += ["--barrier-dir", str(barrier.resolve())]
    root = Path(__file__).resolve().parent
    if row["arm"] == ARM_PYOPTIX:
        return [args.python, str(root / "pyoptix_worker.py"), *common,
                "--device-source", str(args.device_source.resolve()),
                "--optix-include", str(args.optix_include.resolve()),
                "--cuda-include", str(args.cuda_include.resolve())]
    if row["arm"] == ARM_RTDL:
        return [args.python, str(root / "rtdl_worker.py"), *common,
                "--native", str(args.native.resolve()),
                "--optix-include", str(args.optix_include.resolve()),
                "--cuda-include", str(args.cuda_include.resolve()),
                "--optix-sdk", args.optix_sdk,
                "--compute-capability", args.compute_capability,
                "--proof", str(args.proof.resolve())]
    raise ValueError("Direct worker command is built separately")


def direct_command(
    args: argparse.Namespace, row: dict[str, Any], ticket: str, barrier: Path | None,
) -> list[str]:
    command = [
        str(args.direct_binary.resolve()),
        "--worker-id", row["worker_id"], "--task", row["task"],
        "--mode", row["mode"], "--device-source", str(args.device_source.resolve()),
        "--optix-include", str(args.optix_include.resolve()),
        "--cuda-include", str(args.cuda_include.resolve()),
        "--freeze-sha256", args.freeze_value["freeze_sha256"],
        "--controller-ticket", ticket,
    ]
    if barrier is not None:
        command += ["--barrier-dir", str(barrier.resolve())]
    return command


def read_rss_bytes(pid: int) -> tuple[int | None, int | None]:
    try:
        rows = (Path("/proc") / str(pid) / "status").read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None, None
    values: dict[str, int] = {}
    for row in rows:
        if row.startswith(("VmRSS:", "VmHWM:")):
            key, value, unit = row.split()[:3]
            if unit != "kB":
                raise RuntimeError(f"unexpected /proc memory unit: {unit}")
            values[key.rstrip(":")] = int(value) * 1024
    return values.get("VmRSS"), values.get("VmHWM")


def visible_compute_pids(gpu_uuid: str | None = None) -> list[int]:
    output = subprocess.run([
        "nvidia-smi", "--query-compute-apps=gpu_uuid,pid",
        "--format=csv,noheader,nounits",
    ], check=True, text=True, capture_output=True).stdout
    result = []
    for row in output.splitlines():
        row = row.strip()
        if not row or "No running" in row:
            continue
        row_uuid, value = (part.strip() for part in row.split(",", 1))
        if gpu_uuid is None or row_uuid == gpu_uuid:
            result.append(int(value))
    return result


def revalidate_current_host(binding: dict[str, Any]) -> None:
    rows = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap,memory.total",
        "--format=csv,noheader,nounits",
    ], check=True, text=True, capture_output=True).stdout.strip().splitlines()
    expected_ordinal = binding.get("visible_gpu_ordinal", 0)
    if type(expected_ordinal) is not int or not 0 <= expected_ordinal < len(rows):
        raise RuntimeError("bound visible GPU ordinal is unavailable")
    name, uuid, driver, capability, memory_mib = (
        value.strip() for value in rows[expected_ordinal].split(","))
    observed = {
        "hostname": platform.node(), "gpu_model": name, "gpu_uuid": uuid,
        "driver_version": driver, "compute_capability": capability,
        "vram_bytes": int(memory_mib) * 1024 * 1024,
        "kernel": platform.release(),
    }
    mismatches = [key for key, value in observed.items() if binding.get(key) != value]
    if mismatches:
        raise RuntimeError("current host differs from bound host: " + ",".join(mismatches))
    pids = visible_compute_pids(binding["gpu_uuid"])
    if pids:
        raise RuntimeError(f"foreign GPU compute process present before transaction: {pids}")


class NvmlProcessSampler:
    def __init__(self, gpu_uuid: str):
        try:
            import pynvml
        except ImportError as error:
            raise RuntimeError("memory measurement requires nvidia-ml-py/pynvml") from error
        self.api = pynvml
        pynvml.nvmlInit()
        try:
            self.handle = pynvml.nvmlDeviceGetHandleByUUID(gpu_uuid)
        except TypeError:
            self.handle = pynvml.nvmlDeviceGetHandleByUUID(gpu_uuid.encode("ascii"))

    def close(self) -> None:
        self.api.nvmlShutdown()

    def used_bytes(self, pid: int) -> int | None:
        try:
            rows = self.api.nvmlDeviceGetComputeRunningProcesses(self.handle)
        except self.api.NVMLError:
            rows = self.api.nvmlDeviceGetComputeRunningProcesses_v3(self.handle)
        for row in rows:
            if int(row.pid) == pid:
                value = int(row.usedGpuMemory)
                if value < (1 << 63):
                    return value
        return None


def validate_direct_raw(
    raw: dict[str, Any], *, row: dict[str, Any], freeze: dict[str, Any],
    runtime: dict[str, Any], authority: dict[str, Any], ticket: str,
) -> dict[str, Any]:
    if raw.get("schema") != "rtdl.goal5798.direct_raw_worker.v1" \
            or raw.get("status") != "PASS" or raw.get("worker_id") != row["worker_id"]:
        raise ValueError("Direct raw worker identity mismatch")
    if raw.get("task") != row["task"] or raw.get("mode") != row["mode"]:
        raise ValueError("Direct raw worker schedule mismatch")
    if raw.get("freeze_sha256") != freeze["freeze_sha256"] \
            or raw.get("controller_ticket") != ticket:
        raise ValueError("Direct raw worker authority mismatch")
    selected_version = authority["host_binding"]["selected_stack"]["optix_api_version"]
    major, minor, patch = (int(value) for value in selected_version.split("."))
    if raw.get("optix_header_version") != major * 10000 + minor * 100 + patch:
        raise ValueError("Direct binary was not built against the selected OptiX API")
    durations = raw.get("execute_durations_ns")
    if not isinstance(durations, list) or any(type(value) is not int or value < 0 for value in durations):
        raise ValueError("Direct duration vector invalid")
    direct = raw.get("correctness")
    if not isinstance(direct, dict) or direct.get("oracle_exact") is not True:
        raise ValueError("Direct worker lacks exact correctness")
    if row["task"] == RELATION_TASK:
        task = relation_workload()
        output = direct.pop("canonical_rows", None)
        if output != task["expected_rows"]:
            raise ValueError("Direct relation controller-oracle mismatch")
        correctness = {
            **direct,
            "oracle_exact": True,
            "canonical_row_count": len(output),
            "output_sha256": workload_digest(output),
            "expected_output_sha256": workload_digest(task["expected_rows"]),
            "raw_output_sha256": workload_digest(output),
        }
    else:
        task = triangle_workload()
        per_ray = direct.pop("per_ray", None)
        if per_ray != task["expected_per_ray"] \
                or direct.get("weighted_sum") != task["expected_weighted_sum"]:
            raise ValueError("Direct triangle controller-oracle mismatch")
        correctness = {
            **direct,
            "oracle_exact": True,
            "per_ray_count": len(per_ray),
            "per_ray_sha256": workload_digest(per_ray),
            "expected_per_ray_sha256": workload_digest(task["expected_per_ray"]),
            "expected_weighted_sum": task["expected_weighted_sum"],
            "raw_output_sha256": workload_digest({
                "per_ray": per_ray, "weighted_sum": direct["weighted_sum"]}),
        }
    phases = dict(raw["phase_durations_ns"])
    phases["close"] = None
    return finish_receipt(
        freeze=freeze, row=row, runtime_manifest=runtime, authority=authority,
        phases_ns=phases, execute_durations_ns=durations,
        correctness=correctness,
        implementation={
            "arm": ARM_DIRECT,
            "device_authoring_path": "CUDA_CPP_NVRTC_FROM_CPP_HOST",
            "optix_header_version": raw["optix_header_version"],
            "direct_binary_sha256": authority["built_artifacts"]["direct_binary_sha256"],
            "controller_validated_full_output": True,
            "host_rusage_maxrss_bytes": raw["host_rusage_maxrss_bytes"],
        },
    )


def sample_memory_worker(
    process: subprocess.Popen[str], *, barrier: Path, gpu_uuid: str,
    poll_interval_seconds: float = 0.01, timeout_seconds: float = 1800.0,
) -> dict[str, Any]:
    sampler = NvmlProcessSampler(gpu_uuid)
    peak_rss = 0
    peak_hwm = 0
    peak_gpu = 0
    samples = 0
    ready = barrier / "prepared.ready.json"
    deadline = time.monotonic() + timeout_seconds
    prepared_seen = False
    steady_values: list[int] = []
    try:
        while process.poll() is None:
            rss, hwm = read_rss_bytes(process.pid)
            gpu = sampler.used_bytes(process.pid)
            if rss is not None:
                peak_rss = max(peak_rss, rss)
            if hwm is not None:
                peak_hwm = max(peak_hwm, hwm)
            if gpu is not None:
                peak_gpu = max(peak_gpu, gpu)
            samples += 1
            if ready.is_file() and not prepared_seen:
                payload = json.loads(ready.read_text(encoding="utf-8"))
                if payload.get("pid") != process.pid:
                    raise RuntimeError("prepared barrier PID mismatch")
                # Ten 10-ms observations make the steady prepared value an
                # explicit barrier-window maximum, not a single lucky sample.
                for _ in range(10):
                    value = sampler.used_bytes(process.pid)
                    if value is not None:
                        steady_values.append(value)
                        peak_gpu = max(peak_gpu, value)
                    rss, hwm = read_rss_bytes(process.pid)
                    if rss is not None:
                        peak_rss = max(peak_rss, rss)
                    if hwm is not None:
                        peak_hwm = max(peak_hwm, hwm)
                    time.sleep(poll_interval_seconds)
                if not steady_values:
                    raise RuntimeError("NVML never observed the prepared GPU process")
                create_bytes(barrier / "controller.continue", b"CONTINUE\n")
                prepared_seen = True
            if time.monotonic() >= deadline:
                process.terminate()
                raise TimeoutError("memory worker timeout")
            time.sleep(poll_interval_seconds)
    finally:
        sampler.close()
    if not prepared_seen:
        raise RuntimeError("memory worker exited before prepared barrier")
    return {
        "poll_interval_ms": 10,
        "sample_count": samples + len(steady_values),
        "host_process_sampled_peak_rss_bytes": max(peak_rss, peak_hwm),
        "gpu_process_sampled_peak_bytes": peak_gpu,
        "gpu_process_steady_prepared_bytes": steady_values[-1],
        "gpu_process_steady_prepared_barrier_samples": steady_values,
        "sampled_peak_is_lower_bound_on_sub_10ms_transients": True,
    }


def execute_worker(
    args: argparse.Namespace, row: dict[str, Any], index: int,
    freeze: dict[str, Any], runtime: dict[str, Any], authority: dict[str, Any],
) -> dict[str, Any]:
    foreign_pids = visible_compute_pids(authority["host_binding"]["gpu_uuid"])
    if foreign_pids:
        raise RuntimeError(f"foreign GPU compute process before worker {row['worker_id']}: {foreign_pids}")
    worker_dir = args.output_root / f"{index:03d}_{row['worker_id']}"
    worker_dir.mkdir(parents=False, exist_ok=False)
    worker_receipt_path = worker_dir / "worker_receipt.json"
    barrier = worker_dir / "memory_barrier" if row["mode"] == MEMORY_MODE else None
    ticket = hashlib.sha256(
        f"{authority['authority_sha256']}:{row['worker_id']}:{os.getpid()}".encode("utf-8")
    ).hexdigest()
    environment = os.environ.copy()
    repository = Path(__file__).resolve().parents[2]
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(repository / "src"), str(repository), environment.get("PYTHONPATH", "")])
    environment["GOAL5798_FORMAL_CONTROLLER_PID"] = str(os.getpid())
    if row["arm"] == ARM_DIRECT:
        command = direct_command(args, row, ticket, barrier)
    else:
        command = worker_command(args, row, worker_receipt_path, barrier)
    create_json(worker_dir / "command.json", {
        "schema": "rtdl.goal5798.worker_command.v1", "worker_id": row["worker_id"],
        "argv": command, "controller_ticket": ticket if row["arm"] == ARM_DIRECT else None,
    })
    stdout_path = worker_dir / "stdout.txt"
    stderr_path = worker_dir / "stderr.txt"
    start = time.perf_counter_ns()
    memory = None
    with stdout_path.open("xb") as stdout_stream, stderr_path.open("xb") as stderr_stream:
        process = subprocess.Popen(
            command, cwd=repository, env=environment,
            stdout=stdout_stream, stderr=stderr_stream)
        try:
            if barrier is not None:
                memory = sample_memory_worker(
                    process, barrier=barrier,
                    gpu_uuid=authority["host_binding"]["gpu_uuid"])
            process.wait()
        except BaseException:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            raise
    process_wall_ns = time.perf_counter_ns() - start
    stdout = stdout_path.read_text(encoding="utf-8")
    stderr = stderr_path.read_text(encoding="utf-8")
    if process.returncode != 0:
        create_json(worker_dir / "failure.json", {
            "schema": "rtdl.goal5798.worker_failure.v1", "worker_id": row["worker_id"],
            "returncode": process.returncode, "process_wall_ns": process_wall_ns,
            "retry_performed": False, "replacement_performed": False,
        })
        raise RuntimeError(f"worker failed: {row['worker_id']} rc={process.returncode}")
    if row["arm"] == ARM_DIRECT:
        raw = json.loads(stdout)
        create_json(worker_dir / "direct_raw.json", raw)
        receipt = validate_direct_raw(
            raw, row=row, freeze=freeze, runtime=runtime,
            authority=authority, ticket=ticket)
        create_json(worker_receipt_path, receipt)
    else:
        receipt = json.loads(worker_receipt_path.read_text(encoding="utf-8"))
        seal = receipt.get("receipt_sha256")
        unsealed = dict(receipt)
        unsealed.pop("receipt_sha256", None)
        if digest(unsealed) != seal:
            raise ValueError("worker receipt seal mismatch")
    if memory is not None:
        host_peak = receipt.get("implementation", {}).get("host_rusage_maxrss_bytes")
        if type(host_peak) is not int or host_peak <= 0:
            raise ValueError("memory worker lacks RUSAGE_SELF maxrss")
        memory["host_peak_rss_bytes"] = host_peak
    final_receipt = dict(receipt)
    final_receipt.pop("receipt_sha256", None)
    final_receipt["schema"] = "rtdl.goal5798.formal_worker_receipt.v1"
    final_receipt["worker_payload_receipt_file_sha256"] = sha256_file(worker_receipt_path)
    final_receipt["durations_ns"] = dict(final_receipt["durations_ns"])
    final_receipt["durations_ns"]["controller_process_wall_ns"] = process_wall_ns
    final_receipt["memory"] = memory
    final_receipt["primary_sample_ns"] = (
        process_wall_ns if row["mode"] == "COLD_FRESH_PROCESS"
        else final_receipt["primary_sample_ns"])
    final_receipt["receipt_sha256"] = digest(final_receipt)
    reasons = validate_final_worker_receipt(freeze, final_receipt)
    if reasons:
        raise ValueError("final worker receipt rejected: " + ",".join(reasons))
    final_receipt_path = worker_dir / "final_receipt.json"
    create_json(final_receipt_path, final_receipt)
    if row["mode"] == "COLD_FRESH_PROCESS":
        primary = process_wall_ns
    elif row["mode"] == "PREPARED_EXECUTION":
        primary = final_receipt["primary_sample_ns"]
    else:
        primary = None
    record = {
        "schema": "rtdl.goal5798.controller_worker_record.v1",
        "sequence_index": index, "worker_id": row["worker_id"],
        "arm": row["arm"], "task": row["task"], "mode": row["mode"],
        "row_sample_index": row["row_sample_index"],
        "process_wall_ns": process_wall_ns,
        "registered_primary_sample_ns": primary,
        "timing_eligible": row["mode"] != MEMORY_MODE,
        "memory": memory,
        "worker_payload_receipt_sha256": sha256_file(worker_receipt_path),
        "final_receipt_sha256": sha256_file(final_receipt_path),
        "correctness_oracle_exact": final_receipt["correctness"]["oracle_exact"],
    }
    record["record_sha256"] = digest(record)
    create_json(worker_dir / "controller_record.json", record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--direct-binary", type=Path)
    parser.add_argument("--device-source", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--optix-sdk")
    parser.add_argument("--plan-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.freeze = args.freeze.resolve()
    args.runtime_manifest = args.runtime_manifest.resolve()
    freeze = load_freeze(args.freeze)
    runtime = load_runtime_manifest(args.runtime_manifest)
    args.freeze_value = freeze
    schedule = freeze["memory_schedule"] + freeze["performance_schedule"]
    if args.plan_only:
        if args.execution_authority is not None:
            raise ValueError("plan-only must not carry execution authority")
        plan = {
            "schema": "rtdl.goal5798.formal_controller_plan.v1",
            "status": "PLAN_ONLY__NO_GPU_EXECUTION",
            "freeze_sha256": freeze["freeze_sha256"],
            "runtime_manifest_sha256": runtime["manifest_sha256"],
            "memory_workers_before_timing": len(freeze["memory_schedule"]),
            "performance_worker_count": len(freeze["performance_schedule"]),
            "worker_ids": [row["worker_id"] for row in schedule],
        }
        plan["plan_sha256"] = digest(plan)
        create_json(args.output_root.resolve(), plan)
        print(json.dumps(plan, sort_keys=True))
        return
    required = ("execution_authority", "direct_binary", "device_source", "optix_include",
                "cuda_include", "native", "proof")
    for name in required:
        value = getattr(args, name)
        if value is None:
            raise ValueError(f"formal execution requires --{name.replace('_', '-')}")
        if name in ("execution_authority", "direct_binary", "device_source", "native", "proof") \
                and not value.resolve().is_file():
            raise FileNotFoundError(value)
        if name in ("optix_include", "cuda_include") and not value.resolve().is_dir():
            raise FileNotFoundError(value)
    if platform.system() != "Linux" or "microsoft" in platform.release().lower():
        raise RuntimeError("Goal5798 formal controller requires non-WSL Linux")
    authority = load_execution_authority(
        args.execution_authority.resolve(), freeze_path=args.freeze,
        freeze=freeze, runtime_manifest=runtime)
    revalidate_current_host(authority["host_binding"])
    selected_stack = authority["host_binding"].get("selected_stack")
    if not isinstance(selected_stack, dict):
        raise RuntimeError("portable execution authority lacks selected stack")
    args.optix_sdk = selected_stack["optix_api_version"]
    args.compute_capability = authority["host_binding"]["compute_capability"]
    if authority.get("built_artifacts", {}).get("direct_binary_sha256") \
            != sha256_file(args.direct_binary.resolve()):
        raise RuntimeError("Direct binary identity mismatch")
    if authority.get("built_artifacts", {}).get("rtdl_native_sha256") \
            != sha256_file(args.native.resolve()):
        raise RuntimeError("RTDL native identity mismatch")
    args.output_root = args.output_root.resolve()
    args.output_root.mkdir(parents=True, exist_ok=False)
    create_json(args.output_root / "transaction_start.json", {
        "schema": "rtdl.goal5798.transaction_start.v1",
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_sha256": runtime["manifest_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "memory_workers_before_timing": True,
        "retry": False, "resume": False, "replacement": False, "row_drop": False,
    })
    records = []
    for index, row in enumerate(schedule):
        try:
            records.append(execute_worker(args, row, index, freeze, runtime, authority))
        except BaseException as error:
            create_json(args.output_root / "transaction_failure.json", {
                "schema": "rtdl.goal5798.transaction_failure.v1",
                "status": "TERMINAL_FAILURE__NO_RETRY_OR_REPLACEMENT",
                "failed_sequence_index": index, "failed_worker_id": row["worker_id"],
                "exception_type": type(error).__name__, "exception": str(error),
                "completed_worker_count": len(records),
                "performance_worker_started_count": sum(
                    record["timing_eligible"] for record in records),
                "retry_count": 0, "resume_count": 0,
                "replacement_count": 0, "dropped_row_count": 0,
            })
            raise
    result = {
        "schema": SCHEMA, "status": "PASS", "worker_count": len(records),
        "memory_worker_count": len(freeze["memory_schedule"]),
        "performance_worker_count": len(freeze["performance_schedule"]),
        "all_correct": all(row["correctness_oracle_exact"] for row in records),
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_sha256": runtime["manifest_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "record_sha256s": [row["record_sha256"] for row in records],
        "retry_count": 0, "resume_count": 0, "replacement_count": 0, "dropped_row_count": 0,
    }
    result["result_sha256"] = digest(result)
    create_json(args.output_root / "controller_result.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

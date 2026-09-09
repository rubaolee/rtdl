#!/usr/bin/env python3
"""Sample process memory for the 160M Particle arms.

Sampling perturbs timing.  This tool emits descriptive memory evidence only.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import time

import pynvml


ORDERS = ("rtdl", "pyoptix", "pyoptix", "rtdl")


def rss_kib(pid: int) -> tuple[int, int]:
    current = high = 0
    try:
        rows = Path(f"/proc/{pid}/status").read_text().splitlines()
    except FileNotFoundError:
        return current, high
    for row in rows:
        if row.startswith("VmRSS:"):
            current = int(row.split()[1])
        elif row.startswith("VmHWM:"):
            high = int(row.split()[1])
    return current, high


def process_gpu_bytes(handle, pid: int) -> int:
    for process in pynvml.nvmlDeviceGetComputeRunningProcesses(handle):
        if process.pid == pid:
            used = int(process.usedGpuMemory)
            return 0 if used < 0 or used >= (1 << 63) else used
    return 0


def command(args, arm: str) -> list[str]:
    result = [
        str(args.python),
        str(args.source_root / "scripts/authored_particle_transition_ensemble_worker.py"),
        "--arm", arm,
        "--base-particle-dir", str(args.base_particle_dir),
        "--ensemble-dir", str(args.ensemble_dir),
        "--query-count", "160000000",
        "--warmups", "1",
        "--samples", "1",
    ]
    if arm == "rtdl":
        result.extend([
            "--native", str(args.native),
            "--optix-include", str(args.optix_include),
            "--cuda-include", str(args.cuda_include),
            "--compute-capability", "8.9",
            "--optix-sdk", "8.0.0",
        ])
    else:
        result.extend(["--pyoptix-ptx", str(args.pyoptix_ptx)])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--base-particle-dir", type=Path, required=True)
    parser.add_argument("--ensemble-dir", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--pyoptix-ptx", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-interval-ms", type=float, default=10.0)
    args = parser.parse_args()
    if args.sample_interval_ms <= 0:
        raise ValueError("sample interval must be positive")
    args.source_root = args.source_root.resolve(strict=True)
    if subprocess.run(
        ["git", "status", "--porcelain"], cwd=args.source_root,
        check=True, capture_output=True, text=True,
    ).stdout:
        raise RuntimeError("memory diagnostic requires a clean source checkout")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=args.source_root,
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if commit != "110dee7aa11e57e984cc2509163e021d787c692a":
        raise RuntimeError(f"unexpected source commit: {commit}")

    pynvml.nvmlInit()
    try:
        handle = pynvml.nvmlDeviceGetHandleByUUID(args.gpu_uuid)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(gpu_name, bytes):
            gpu_name = gpu_name.decode()
        environment = dict(os.environ)
        environment.update({
            "CUDA_VISIBLE_DEVICES": args.gpu_uuid,
            "PYTHONPATH": f"{args.source_root / 'src'}:{args.source_root}",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "CUDA_CACHE_DISABLE": "1",
            "OPTIX_CACHE_ENABLED": "0",
            "OPTIX_CACHE_MAXSIZE": "0",
            "NUMBA_CUDA_USE_NVIDIA_BINDING": "1",
        })
        rows = []
        for ordinal, arm in enumerate(ORDERS):
            argv = command(args, arm)
            baseline = int(pynvml.nvmlDeviceGetMemoryInfo(handle).used)
            started = time.monotonic_ns()
            process = subprocess.Popen(
                argv, cwd=args.source_root, env=environment,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True,
            )
            peak_process_gpu = 0
            peak_device_gpu = baseline
            peak_rss = 0
            peak_hwm = 0
            sample_count = 0
            while process.poll() is None:
                peak_process_gpu = max(
                    peak_process_gpu, process_gpu_bytes(handle, process.pid))
                peak_device_gpu = max(
                    peak_device_gpu,
                    int(pynvml.nvmlDeviceGetMemoryInfo(handle).used),
                )
                rss, hwm = rss_kib(process.pid)
                peak_rss = max(peak_rss, rss)
                peak_hwm = max(peak_hwm, hwm)
                sample_count += 1
                time.sleep(args.sample_interval_ms / 1000.0)
            stdout, stderr = process.communicate()
            elapsed = time.monotonic_ns() - started
            if process.returncode:
                raise RuntimeError(
                    f"{arm} memory worker failed: {stderr.decode(errors='replace')}")
            worker = json.loads(stdout)
            rows.append({
                "ordinal": ordinal,
                "arm": arm,
                "command": argv,
                "worker_pid": process.pid,
                "sample_count": sample_count,
                "sampling_interval_requested_ms": args.sample_interval_ms,
                "sampler_process_wall_ns": elapsed,
                "baseline_device_used_bytes": baseline,
                "peak_worker_gpu_bytes": peak_process_gpu,
                "peak_device_used_bytes": peak_device_gpu,
                "peak_worker_rss_kib": peak_rss,
                "peak_worker_vmhwm_kib": peak_hwm,
                "worker_result": worker,
                "stderr": stderr.decode(errors="replace"),
            })
        output_digests = {row["worker_result"]["output_sha256"] for row in rows}
        if output_digests != {
            "6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89"
        }:
            raise RuntimeError("memory diagnostic output identity differs")
        by_arm = {
            arm: [row for row in rows if row["arm"] == arm]
            for arm in ("rtdl", "pyoptix")
        }
        result = {
            "schema": "rtdl.v4.authored_particle.peak_memory_diagnostic.v1",
            "status": "PASS__DESCRIPTIVE_MEMORY_ONLY",
            "source_commit": commit,
            "gpu_name": gpu_name,
            "gpu_uuid": args.gpu_uuid,
            "query_count": 160_000_000,
            "orders": list(ORDERS),
            "rows": rows,
            "summary": {
                arm: {
                    "peak_worker_gpu_bytes": [r["peak_worker_gpu_bytes"] for r in values],
                    "median_peak_worker_gpu_bytes": statistics.median(
                        r["peak_worker_gpu_bytes"] for r in values),
                    "peak_device_used_bytes": [r["peak_device_used_bytes"] for r in values],
                    "median_peak_device_used_bytes": statistics.median(
                        r["peak_device_used_bytes"] for r in values),
                    "peak_worker_rss_kib": [r["peak_worker_rss_kib"] for r in values],
                    "median_peak_worker_rss_kib": statistics.median(
                        r["peak_worker_rss_kib"] for r in values),
                }
                for arm, values in by_arm.items()
            },
            "claim_boundary": {
                "formal_timing_evidence": False,
                "sampler_perturbs_latency": True,
                "memory_values_descriptive": True,
                "nvml_sampling_can_miss_short_lived_peak": True,
                "direct_worker_rss_excludes_child_processes": True,
                "pooled_with_formal_transaction": False,
            },
        }
        payload = (json.dumps(
            result, indent=2, sort_keys=True, allow_nan=False,
        ) + "\n").encode()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        print(args.output)
    finally:
        pynvml.nvmlShutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

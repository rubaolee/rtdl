#!/usr/bin/env python3
"""Create-only exact physical-host binding for Goal5798 (no GPU workload)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
sys.path.insert(0, str(GOAL))
from contract_runtime import digest, load_freeze, validate_host_binding
from compatibility import select_compatible_stack


def run(command: list[str]) -> str:
    return subprocess.run(
        command, check=True, text=True, capture_output=True,
    ).stdout.strip()


def git_head(path: Path) -> str:
    return run(["git", "-C", str(path.resolve()), "rev-parse", "HEAD"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--optix-header-repo", type=Path, required=True)
    parser.add_argument("--pyoptix-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    freeze = load_freeze(args.freeze.resolve())
    if platform.system() != "Linux" or "microsoft" in platform.release().lower():
        raise RuntimeError("Goal5798 requires non-WSL Linux")
    line = run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap,memory.total",
        "--format=csv,noheader,nounits",
    ]).splitlines()
    if not line:
        raise RuntimeError("Goal5798 requires an NVIDIA GPU visible to nvidia-smi")
    gpu_model, gpu_uuid, driver_version, compute_capability, memory_mib = (
        value.strip() for value in line[0].split(","))
    selected_stack = select_compatible_stack(driver_version)
    compute_rows = run([
        "nvidia-smi", "--query-compute-apps=gpu_uuid,pid",
        "--format=csv,noheader,nounits",
    ]).splitlines()
    compute_pids = []
    for row in compute_rows:
        if not row.strip() or "No running" in row:
            continue
        row_uuid, pid = (value.strip() for value in row.split(",", 1))
        if row_uuid == gpu_uuid:
            compute_pids.append(pid)
    os_release = Path("/etc/os-release").read_text(encoding="utf-8")
    import importlib.metadata
    import optix
    from cuda.bindings import nvrtc

    actual_optix_api = ".".join(str(value) for value in optix.version())
    if actual_optix_api != selected_stack["optix_api_version"]:
        raise RuntimeError(
            f"installed OptiX API {actual_optix_api} does not match selected "
            f"stack {selected_stack['optix_api_version']}")
    distribution_name = selected_stack["pyoptix_distribution_name"]
    distribution_version = importlib.metadata.version(distribution_name)
    if distribution_version != selected_stack["pyoptix_distribution_version"]:
        raise RuntimeError("installed PyOptiX distribution does not match selected stack")

    binding = {
        "schema": "rtdl.goal5798.physical_host_binding.v2",
        "hostname": platform.node(),
        "gpu_model": gpu_model,
        "gpu_uuid": gpu_uuid,
        "compute_capability": compute_capability,
        "vram_bytes": int(memory_mib) * 1024 * 1024,
        "driver_version": driver_version,
        "driver_branch": int(driver_version.split(".", 1)[0]),
        "kernel": platform.release(),
        "os_release": os_release,
        "wsl": False,
        "cuda_toolkit": run(["nvcc", "--version"]),
        "nvrtc": str(nvrtc.nvrtcVersion()[1:]),
        "python": platform.python_version(),
        "gxx": run(["g++", "--version"]).splitlines()[0],
        "optix_api_version": actual_optix_api,
        "optix_header_commit": git_head(args.optix_header_repo),
        "pyoptix_commit": git_head(args.pyoptix_repo),
        "pyoptix_distribution_name": distribution_name,
        "pyoptix_distribution_version": distribution_version,
        "selected_stack": selected_stack,
        "visible_gpu_ordinal": 0,
        "visible_gpu_count": len(line),
        "stack_selection_inputs": ["driver_version"],
        "stack_selection_before_task_materialization": True,
        "source_manifest_sha256": freeze["source_manifest_sha256"],
        "other_compute_process_count": len(compute_pids),
    }
    binding["binding_sha256"] = digest(binding)
    reasons = validate_host_binding(freeze, binding)
    if reasons:
        raise RuntimeError("host rejected: " + ",".join(reasons))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        binding, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS", "binding_sha256": binding["binding_sha256"],
        "gpu_uuid": gpu_uuid, "driver_version": driver_version,
        "pyoptix_distribution_name": distribution_name,
        "pyoptix_distribution_version": distribution_version,
        "selected_stack_id": selected_stack["stack_id"],
        "gpu_workload_executed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

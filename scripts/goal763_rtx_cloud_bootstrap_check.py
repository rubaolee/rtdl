#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _candidate_optix_prefix() -> Path:
    if os.environ.get("OPTIX_PREFIX"):
        return Path(os.environ["OPTIX_PREFIX"])
    for candidate in (
        Path.home() / "vendor" / "optix-dev",
        Path.home() / "vendor" / "optix",
        Path("/usr/local/NVIDIA-OptiX-SDK-9.0.0-linux64-x86_64"),
        Path("/usr/local/NVIDIA-OptiX-SDK"),
        Path("/opt/optix"),
    ):
        if (candidate / "include" / "optix.h").exists():
            return candidate
    return Path.home() / "vendor" / "optix-dev"


def _candidate_cuda_prefix() -> Path:
    if os.environ.get("CUDA_PREFIX"):
        return Path(os.environ["CUDA_PREFIX"])
    for candidate in (Path("/usr/local/cuda"), Path("/usr"), Path("/usr/lib/cuda")):
        if (candidate / "bin" / "nvcc").exists() or (candidate / "include" / "cuda.h").exists():
            return candidate
    return Path("/usr/local/cuda")


def _candidate_nvcc(cuda_prefix: Path) -> Path:
    if os.environ.get("NVCC"):
        return Path(os.environ["NVCC"])
    for candidate in (cuda_prefix / "bin" / "nvcc", Path("/usr/bin/nvcc")):
        if candidate.exists():
            return candidate
    return cuda_prefix / "bin" / "nvcc"


def _run(command: list[str], *, env: dict[str, str], dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "command": command,
            "status": "dry_run",
            "returncode": 0,
            "elapsed_sec": 0.0,
            "stdout_tail": "",
            "stderr_tail": "",
        }
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "status": "ok" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "elapsed_sec": time.perf_counter() - start,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def _probe(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-4000:],
        }
    except Exception as exc:
        return {"command": command, "returncode": -1, "output_tail": str(exc)}


def run_check(*, dry_run: bool, skip_build: bool, skip_tests: bool) -> dict[str, Any]:
    optix_prefix = _candidate_optix_prefix()
    cuda_prefix = _candidate_cuda_prefix()
    nvcc = _candidate_nvcc(cuda_prefix)
    optix_lib = ROOT / "build" / "librtdl_optix.so"
    env = {
        **os.environ,
        "PYTHONPATH": "src:.",
        "OPTIX_PREFIX": str(optix_prefix),
        "CUDA_PREFIX": str(cuda_prefix),
        "NVCC": str(nvcc),
        "RTDL_OPTIX_LIB": str(optix_lib),
        "RTDL_OPTIX_PTX_COMPILER": "nvcc",
        "RTDL_NVCC": str(nvcc),
    }
    preflight = {
        "optix_prefix": str(optix_prefix),
        "optix_header_exists": (optix_prefix / "include" / "optix.h").exists(),
        "cuda_prefix": str(cuda_prefix),
        "cuda_header_exists": (cuda_prefix / "include" / "cuda.h").exists(),
        "nvcc": str(nvcc),
        "nvcc_exists": nvcc.exists(),
        "nvidia_smi": _probe(["nvidia-smi"]),
        "nvcc_version": _probe([str(nvcc), "--version"]) if nvcc.exists() else None,
        "git_head": _probe(["git", "rev-parse", "HEAD"]),
        "git_status_short": _probe(["git", "status", "--short"]),
    }
    steps: list[dict[str, Any]] = []
    if not skip_build:
        steps.append(
            {
                "name": "build_optix",
                "result": _run(
                    [
                        "make",
                        "build-optix",
                        f"OPTIX_PREFIX={optix_prefix}",
                        f"CUDA_PREFIX={cuda_prefix}",
                        f"NVCC={nvcc}",
                    ],
                    env=env,
                    dry_run=dry_run,
                ),
            }
        )
    if not skip_tests:
        steps.append(
            {
                "name": "native_optix_focused_tests",
                "result": _run(
                    [
                        sys.executable,
                        "-m",
                        "unittest",
                        "-v",
                        "tests.goal671_optix_prepared_anyhit_count_test",
                        "tests.goal757_prepared_optix_fixed_radius_count_test",
                        "tests.goal760_optix_robot_pose_flags_phase_profiler_test",
                    ],
                    env=env,
                    dry_run=dry_run,
                ),
            }
        )
    failures = [
        step for step in steps
        if step["result"]["status"] not in {"ok", "dry_run"}
    ]
    preflight_blockers = []
    if not dry_run:
        if not preflight["optix_header_exists"]:
            preflight_blockers.append("missing OptiX SDK header optix.h")
        if not preflight["nvcc_exists"]:
            preflight_blockers.append("missing nvcc")
    return {
        "suite": "goal763_rtx_cloud_bootstrap_check",
        "dry_run": dry_run,
        "skip_build": skip_build,
        "skip_tests": skip_tests,
        "preflight": preflight,
        "steps": steps,
        "preflight_blockers": preflight_blockers,
        "status": "ok" if not failures and not preflight_blockers else "needs_attention",
        "boundary": (
            "This bootstrap check verifies cloud build/test readiness. It does not run performance benchmarks "
            "and does not authorize RTX speedup claims."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight, build, and focused-test the OptiX backend on an RTX cloud host.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--output-json", default="docs/reports/goal763_rtx_cloud_bootstrap_check.json")
    args = parser.parse_args(argv)
    payload = run_check(dry_run=args.dry_run, skip_build=args.skip_build, skip_tests=args.skip_tests)
    text = json.dumps(payload, indent=2, sort_keys=True)
    Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

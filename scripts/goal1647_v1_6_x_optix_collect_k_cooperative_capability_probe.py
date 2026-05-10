#!/usr/bin/env python3
"""Record whether the current CUDA device can run cooperative collect-k probes.

This is a capability/readiness probe only. It does not enable a new collect-k
path, does not measure speedup, and does not authorize public claims.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs/reports/goal1647_v1_6_x_optix_collect_k_cooperative_capability_2026-05-09.json"
DEFAULT_MD = ROOT / "docs/reports/goal1647_v1_6_x_optix_collect_k_cooperative_capability_2026-05-09.md"


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return "unavailable"
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def _git_head() -> str:
    return _run_text(["git", "rev-parse", "HEAD"])


def _gpu_summary() -> str:
    return _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader",
        ]
    )


def _claim_boundary() -> str:
    return (
        "Goal1647 records cooperative-launch readiness for a future opt-in "
        "collect-k merge-chain diagnostic. It is not performance evidence, "
        "does not change fastest-candidate behavior, and does not authorize public speedup wording, "
        "stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, release "
        "tags, or release action."
    )


def run_probe(library: Path) -> dict[str, Any]:
    lib = ctypes.CDLL(str(library))
    func = lib.rtdl_optix_collect_k_cooperative_launch_capability
    func.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    func.restype = ctypes.c_int

    cooperative_launch = ctypes.c_int()
    cooperative_multi_device_launch = ctypes.c_int()
    multiprocessor_count = ctypes.c_int()
    max_threads_per_block = ctypes.c_int()
    max_shared_memory_per_block_optin = ctypes.c_int()
    error = ctypes.create_string_buffer(4096)

    rc = func(
        ctypes.byref(cooperative_launch),
        ctypes.byref(cooperative_multi_device_launch),
        ctypes.byref(multiprocessor_count),
        ctypes.byref(max_threads_per_block),
        ctypes.byref(max_shared_memory_per_block_optin),
        error,
        ctypes.sizeof(error),
    )
    error_text = error.value.decode("utf-8", errors="replace")
    if rc != 0:
        raise RuntimeError(error_text or f"capability probe failed with rc={rc}")

    return {
        "goal": "Goal1647",
        "status": "cooperative_launch_capability_recorded",
        "library": str(library),
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "nvidia_smi": _gpu_summary(),
        "capability": {
            "cuda_device_index": 0,
            "cooperative_launch_supported": bool(cooperative_launch.value),
            "cooperative_multi_device_launch_supported": bool(cooperative_multi_device_launch.value),
            "multiprocessor_count": multiprocessor_count.value,
            "max_threads_per_block": max_threads_per_block.value,
            "max_shared_memory_per_block_optin": max_shared_memory_per_block_optin.value,
        },
        "next_probe_allowed": bool(cooperative_launch.value),
        "performance_evidence_authorized": False,
        "fastest_candidate_behavior_changed": False,
        "public_speedup_wording_authorized": False,
        "stable_collect_k_promotion_authorized": False,
        "broad_rtx_wording_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": _claim_boundary(),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    capability = payload["capability"]
    return "\n".join(
        [
            "# Goal1647 v1.6.x OptiX Collect-K Cooperative Capability Probe",
            "",
            "## Verdict",
            "",
            "`cooperative_launch_capability_recorded`",
            "",
            "## Scope",
            "",
            f"- Git commit: `{payload['git_commit']}`",
            f"- Library: `{payload['library']}`",
            f"- Host: `{payload['host']}`",
            f"- GPU summary: `{payload['nvidia_smi']}`",
            "",
            "## Capability",
            "",
            f"- CUDA device index: `{capability['cuda_device_index']}`",
            f"- Cooperative launch supported: `{capability['cooperative_launch_supported']}`",
            f"- Cooperative multi-device launch supported: `{capability['cooperative_multi_device_launch_supported']}`",
            f"- Multiprocessor count: `{capability['multiprocessor_count']}`",
            f"- Max threads per block: `{capability['max_threads_per_block']}`",
            f"- Max shared memory per block opt-in: `{capability['max_shared_memory_per_block_optin']}`",
            f"- Next cooperative merge-chain probe allowed: `{payload['next_probe_allowed']}`",
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1647 OptiX collect-k cooperative capability probe.")
    parser.add_argument("--library", type=Path, default=ROOT / "build" / "librtdl_optix.so")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_probe(args.library)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "next_probe_allowed": payload["next_probe_allowed"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run a real CUDA cooperative-launch smoke test for collect-k prep.

This probe launches a tiny cooperative kernel with grid synchronization. It is
readiness evidence only, not collect-k performance evidence.
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
DEFAULT_JSON = ROOT / "docs/reports/goal1648_v1_6_x_optix_collect_k_cooperative_launch_smoke_2026-05-10.json"
DEFAULT_MD = ROOT / "docs/reports/goal1648_v1_6_x_optix_collect_k_cooperative_launch_smoke_2026-05-10.md"


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
        "Goal1648 proves that the current CUDA/OptiX build can launch a tiny "
        "cooperative grid-sync kernel. It is readiness evidence only and does not authorize public speedup wording, "
        "stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, release tags, or release action."
    )


def run_probe(library: Path, blocks: int, threads: int) -> dict[str, Any]:
    lib = ctypes.CDLL(str(library))
    func = lib.rtdl_optix_collect_k_cooperative_launch_smoke
    func.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    func.restype = ctypes.c_int

    observed_blocks = ctypes.c_int()
    sync_observed_blocks = ctypes.c_int()
    error = ctypes.create_string_buffer(4096)
    rc = func(
        blocks,
        threads,
        ctypes.byref(observed_blocks),
        ctypes.byref(sync_observed_blocks),
        error,
        ctypes.sizeof(error),
    )
    error_text = error.value.decode("utf-8", errors="replace")
    if rc != 0:
        raise RuntimeError(error_text or f"cooperative launch smoke failed with rc={rc}")

    return {
        "goal": "Goal1648",
        "status": "cooperative_launch_smoke_passed",
        "library": str(library),
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "nvidia_smi": _gpu_summary(),
        "requested_blocks": blocks,
        "requested_threads": threads,
        "observed_blocks": observed_blocks.value,
        "sync_observed_blocks": sync_observed_blocks.value,
        "cooperative_grid_sync_smoke_passed": observed_blocks.value == blocks and sync_observed_blocks.value == blocks,
        "performance_evidence_authorized": False,
        "public_speedup_wording_authorized": False,
        "stable_collect_k_promotion_authorized": False,
        "broad_rtx_wording_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": _claim_boundary(),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal1648 v1.6.x OptiX Collect-K Cooperative Launch Smoke",
            "",
            "## Verdict",
            "",
            "`cooperative_launch_smoke_passed`",
            "",
            "## Scope",
            "",
            f"- Git commit: `{payload['git_commit']}`",
            f"- Library: `{payload['library']}`",
            f"- Host: `{payload['host']}`",
            f"- GPU summary: `{payload['nvidia_smi']}`",
            f"- Requested blocks: `{payload['requested_blocks']}`",
            f"- Requested threads: `{payload['requested_threads']}`",
            "",
            "## Result",
            "",
            f"- Observed blocks before grid sync: `{payload['observed_blocks']}`",
            f"- Observed blocks after grid sync: `{payload['sync_observed_blocks']}`",
            f"- Cooperative grid-sync smoke passed: `{payload['cooperative_grid_sync_smoke_passed']}`",
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1648 cooperative launch smoke probe.")
    parser.add_argument("--library", type=Path, default=ROOT / "build" / "librtdl_optix.so")
    parser.add_argument("--blocks", type=int, default=16)
    parser.add_argument("--threads", type=int, default=64)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_probe(args.library, args.blocks, args.threads)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "passed": payload["cooperative_grid_sync_smoke_passed"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

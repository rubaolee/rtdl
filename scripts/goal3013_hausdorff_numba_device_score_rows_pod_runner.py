from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


def _activate_numba_redirector() -> None:
    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass


def _git_lines(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], text=True).splitlines()


def _gpu_summary() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--warmup-copies", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.copies <= 0 or args.warmup_copies <= 0:
        raise ValueError("copies and warmup-copies must be positive")

    _activate_numba_redirector()
    from examples.benchmark_apps.hausdorff_xhd import (
        rtdl_hausdorff_distance_app as app,
    )

    print(f"[goal3013] warmup copies={args.warmup_copies}", flush=True)
    warm_started = time.perf_counter()
    warmup = app.run_app("partner_numba_witness_exact", copies=args.warmup_copies)
    warm_elapsed = time.perf_counter() - warm_started
    print(
        f"[goal3013] warmup matches={warmup['matches_oracle']} "
        f"wall={warm_elapsed:.6f}s",
        flush=True,
    )

    print(f"[goal3013] evidence copies={args.copies}", flush=True)
    evidence_started = time.perf_counter()
    evidence = app.run_app("partner_numba_witness_exact", copies=args.copies)
    evidence_elapsed = time.perf_counter() - evidence_started
    print(
        f"[goal3013] evidence matches={evidence['matches_oracle']} "
        f"wall={evidence_elapsed:.6f}s",
        flush=True,
    )

    artifact = {
        "goal": "Goal3013",
        "commit": _git_lines("rev-parse", "HEAD")[0],
        "source_dirty": _git_lines("status", "--short"),
        "gpu": _gpu_summary(),
        "backend": "partner_numba_witness_exact",
        "partner": "numba",
        "warmup": {
            "copies": args.warmup_copies,
            "wall_sec": warm_elapsed,
            "matches_oracle": bool(warmup["matches_oracle"]),
            "host_score_row_materialization_used": bool(
                warmup["host_score_row_materialization_used"]
            ),
            "score_rows_generated_on_partner_device": bool(
                warmup["score_rows_generated_on_partner_device"]
            ),
        },
        "evidence": evidence,
        "evidence_wall_sec": evidence_elapsed,
        "claim_boundary": evidence["claim_boundary"],
        "all_claim_flags_false": all(value is False for value in evidence["claim_boundary"].values()),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3013] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

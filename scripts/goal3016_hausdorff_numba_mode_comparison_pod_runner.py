from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any


MODES = ("partner_numba_witness_exact", "partner_numba_block_nearest_exact")


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


def _run_mode(app: Any, mode: str, copies: int) -> dict[str, Any]:
    started = time.perf_counter()
    payload = app.run_app(mode, copies=copies)
    wall = time.perf_counter() - started
    return {"mode": mode, "copies": copies, "wall_sec": wall, "payload": payload}


def _summary(row: dict[str, Any]) -> dict[str, Any]:
    payload = row["payload"]
    directed = payload["directed_a_to_b"]
    return {
        "mode": row["mode"],
        "copies": row["copies"],
        "wall_sec": row["wall_sec"],
        "point_count_a": payload["point_count_a"],
        "point_count_b": payload["point_count_b"],
        "matches_oracle": payload["matches_oracle"],
        "host_score_row_materialization_used": payload["host_score_row_materialization_used"],
        "score_rows_generated_on_partner_device": payload["score_rows_generated_on_partner_device"],
        "bounded_tile_summary_rows": payload.get("bounded_tile_summary_rows", False),
        "rt_core_accelerated": payload["rt_core_accelerated"],
        "score_operation": directed["v2_6_numba_score_row_operation"],
        "logical_pair_count": directed.get("logical_pair_count", directed.get("dense_score_row_count")),
        "materialized_summary_row_count": directed.get(
            "partial_nearest_row_count",
            directed.get("dense_score_row_count"),
        ),
        "directed_summary_sec": next(
            value
            for key, value in payload["run_phases"].items()
            if key.endswith("_directed_summary_sec")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", type=int, default=512)
    parser.add_argument("--warmup-copies", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.copies <= 0 or args.warmup_copies <= 0:
        raise ValueError("copies and warmup-copies must be positive")

    _activate_numba_redirector()
    from examples.benchmark_apps.hausdorff_xhd import (
        rtdl_hausdorff_distance_app as app,
    )

    warmups: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for mode in MODES:
        print(f"[goal3016] warmup mode={mode} copies={args.warmup_copies}", flush=True)
        row = _run_mode(app, mode, args.warmup_copies)
        print(
            f"[goal3016] warmup mode={mode} matches={row['payload']['matches_oracle']} "
            f"wall={row['wall_sec']:.6f}s",
            flush=True,
        )
        warmups.append(row)

    for mode in MODES:
        print(f"[goal3016] evidence mode={mode} copies={args.copies}", flush=True)
        row = _run_mode(app, mode, args.copies)
        print(
            f"[goal3016] evidence mode={mode} matches={row['payload']['matches_oracle']} "
            f"wall={row['wall_sec']:.6f}s",
            flush=True,
        )
        evidence.append(row)

    dense = next(row for row in evidence if row["mode"] == "partner_numba_witness_exact")
    block = next(row for row in evidence if row["mode"] == "partner_numba_block_nearest_exact")
    dense_wall = float(dense["wall_sec"])
    block_wall = float(block["wall_sec"])
    artifact = {
        "goal": "Goal3016",
        "commit": _git_lines("rev-parse", "HEAD")[0],
        "source_dirty": _git_lines("status", "--short"),
        "gpu": _gpu_summary(),
        "warmup_summaries": [_summary(row) for row in warmups],
        "evidence_summaries": [_summary(row) for row in evidence],
        "dense_device_score_wall_sec": dense_wall,
        "block_nearest_wall_sec": block_wall,
        "block_vs_dense_wall_ratio": block_wall / dense_wall if dense_wall else None,
        "all_match_oracle": all(bool(row["payload"]["matches_oracle"]) for row in evidence),
        "all_claim_flags_false": all(
            all(value is False for value in row["payload"]["claim_boundary"].values())
            for row in evidence
        ),
        "claim_boundary": {
            "v2_6_release_authorized": False,
            "public_speedup_claim_authorized": False,
            "numba_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "full_evidence": {row["mode"]: row["payload"] for row in evidence},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3016] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

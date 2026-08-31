from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()[0].strip()
    except Exception:
        return "unknown"


def _run_case(*, mode: str, copies: int) -> dict[str, object]:
    print(f"[goal3143] running mode={mode} copies={copies}", flush=True)
    started = time.perf_counter()
    if mode == "partner_exact_numba":
        payload = hausdorff.run_app("partner_exact", copies=copies, partner="numba")
    else:
        payload = hausdorff.run_app(mode, copies=copies)
    elapsed = time.perf_counter() - started
    directed = payload["directed_a_to_b"]
    return {
        "mode": mode,
        "copies": copies,
        "points_a": int(payload["point_count_a"]),
        "points_b": int(payload["point_count_b"]),
        "elapsed_sec": elapsed,
        "matches_oracle": bool(payload["matches_oracle"]),
        "hausdorff_distance": float(payload["hausdorff_distance"]),
        "numba_strategy": payload.get("numba_strategy", directed.get("numba_strategy")),
        "score_row_operation": directed.get("numba_score_row_operation")
        or directed.get("v2_6_numba_score_row_operation"),
        "score_row_count": directed.get("numba_score_row_count")
        or directed.get("partial_nearest_row_count")
        or directed.get("dense_score_row_count"),
        "logical_pair_count": directed.get("numba_logical_pair_count")
        or directed.get("logical_pair_count")
        or directed.get("dense_score_row_count"),
        "host_score_row_materialization_used": bool(payload.get("host_score_row_materialization_used", False)),
        "score_rows_generated_on_partner_device": bool(payload.get("score_rows_generated_on_partner_device", True)),
        "rt_core_accelerated": bool(payload["rt_core_accelerated"]),
        "claim_boundary": payload.get("claim_boundary", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3143 Hausdorff partner_exact+Numba pod probe")
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--copies", type=int, nargs="+", default=[256, 1024, 2048])
    parser.add_argument("--warmup-copies", type=int, default=64)
    parser.add_argument(
        "--mode",
        action="append",
        dest="modes",
        default=None,
        help="mode to run; repeatable",
    )
    args = parser.parse_args(argv)
    modes = args.modes or ["partner_exact_numba", "partner_numba_block_nearest_exact"]

    for mode in modes:
        print(f"[goal3143] warmup mode={mode} copies={args.warmup_copies}", flush=True)
        _run_case(mode=mode, copies=int(args.warmup_copies))

    rows: list[dict[str, object]] = []
    for copies in args.copies:
        for mode in modes:
            rows.append(_run_case(mode=mode, copies=int(copies)))

    payload = {
        "goal": "Goal3143",
        "commit": _git_commit(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "gpu": _gpu_name(),
        "warmup_copies": int(args.warmup_copies),
        "rows": rows,
        "all_match": all(bool(row["matches_oracle"]) for row in rows),
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "numba_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v2_8_release_authorized": False,
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3143] wrote {args.json_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

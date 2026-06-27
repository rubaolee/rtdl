#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


MODES = ("count", "sum", "min", "max", "avg_as_sum_count")


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_results_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "package_install_claim_authorized": False,
    }


def _command_output(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _run_case(
    *,
    root: Path,
    mode: str,
    copies: int,
    warmup: int,
    repeat: int,
    timeout_sec: int,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    lib = root / "build" / "librtdl_optix.so"
    env["RTDL_OPTIX_LIBRARY"] = str(lib)
    env["RTDL_OPTIX_LIB"] = str(lib)
    command = [
        sys.executable,
        "examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
        "--mode",
        mode,
        "--backend",
        "optix_partner_resident_experimental",
        "--copies",
        str(copies),
        "--warmup",
        str(warmup),
        "--repeat",
        str(repeat),
    ]
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
    wall_sec = time.perf_counter() - started
    if result.returncode != 0:
        return {
            "status": "failed",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "wall_sec": wall_sec,
        }
    payload = json.loads(result.stdout)
    timings = payload.get("metadata", {}).get("timings", {})
    return {
        "status": "ok",
        "wall_sec": wall_sec,
        "metric_sec": float(timings["query_median_sec"]),
        "query_min_sec": float(timings["query_min_sec"]),
        "query_max_sec": float(timings["query_max_sec"]),
        "matches_cpu_reference": bool(payload.get("matches_cpu_reference")),
        "reduction": payload.get("metadata", {}).get("reduction"),
        "semantic_aggregate": payload.get("metadata", {}).get("semantic_aggregate"),
        "native_launch_count": payload.get("metadata", {}).get("native_launch_count"),
        "generic_sum_count_abi_used": payload.get("metadata", {}).get("generic_sum_count_abi_used"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3572 grouped-i64 full-reduction fast-path probe.")
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--copies", type=int, default=120000)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=2000)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--timeout-sec", type=int, default=240)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for mode in MODES:
        for trial in range(1, args.trials + 1):
            for lane, root in (("baseline", args.baseline_root), ("candidate", args.candidate_root)):
                print(f"[goal3572] mode={mode} trial={trial}/{args.trials} lane={lane}", flush=True)
                row = {
                    "mode": mode,
                    "trial": trial,
                    "lane": lane,
                    "root": str(root),
                    "claim_boundary": _claim_boundary(),
                }
                row.update(
                    _run_case(
                        root=root,
                        mode=mode,
                        copies=args.copies,
                        warmup=args.warmup,
                        repeat=args.repeat,
                        timeout_sec=args.timeout_sec,
                    )
                )
                rows.append(row)

    by_mode: dict[str, Any] = {}
    speedups: list[float] = []
    for mode in MODES:
        mode_rows = [row for row in rows if row["mode"] == mode]
        baseline_values = [row["metric_sec"] for row in mode_rows if row["lane"] == "baseline" and row["status"] == "ok"]
        candidate_values = [row["metric_sec"] for row in mode_rows if row["lane"] == "candidate" and row["status"] == "ok"]
        all_ok = (
            len(baseline_values) == args.trials
            and len(candidate_values) == args.trials
            and all(bool(row.get("matches_cpu_reference")) for row in mode_rows if row["status"] == "ok")
        )
        baseline_median = statistics.median(baseline_values) if baseline_values else None
        candidate_median = statistics.median(candidate_values) if candidate_values else None
        speedup = baseline_median / candidate_median if baseline_median and candidate_median else None
        if speedup is not None:
            speedups.append(speedup)
        by_mode[mode] = {
            "all_ok": all_ok,
            "baseline_median_sec": baseline_median,
            "candidate_median_sec": candidate_median,
            "candidate_speedup_vs_baseline": speedup,
            "baseline_values_sec": baseline_values,
            "candidate_values_sec": candidate_values,
        }

    summary = {
        "mode_count": len(MODES),
        "all_modes_ok": all(info["all_ok"] for info in by_mode.values()),
        "geomean_speedup": math.exp(sum(math.log(value) for value in speedups) / len(speedups)) if speedups else None,
        "median_speedup": statistics.median(speedups) if speedups else None,
        "min_speedup": min(speedups) if speedups else None,
        "max_speedup": max(speedups) if speedups else None,
    }
    payload = {
        "schema": "rtdl.goal3572.grouped_i64_full_reduction_fastpath_probe.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline_root": str(args.baseline_root),
        "candidate_root": str(args.candidate_root),
        "baseline_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.baseline_root),
        "candidate_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.candidate_root),
        "candidate_has_uncommitted_native_change": bool(
            _command_output(["git", "status", "--short", "src/native/optix/rtdl_optix_workloads.cpp"], cwd=args.candidate_root)
        ),
        "copies": args.copies,
        "warmup": args.warmup,
        "repeat": args.repeat,
        "trials": args.trials,
        "claim_boundary": _claim_boundary(),
        "summary": summary,
        "by_mode": by_mode,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if summary["all_modes_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

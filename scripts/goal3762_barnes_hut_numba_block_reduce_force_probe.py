#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app  # noqa: E402


SCHEMA = "rtdl.goal3762.barnes_hut_numba_block_reduce_force_probe.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3762_barnes_hut_numba_block_reduce_force_a5000" / "summary.json"
SCOPED_SOURCE_PATHS = (
    "src/rtdsl/app_adapters/barnes_hut.py",
    "scripts/goal3762_barnes_hut_numba_block_reduce_force_probe.py",
    "tests/goal3762_barnes_hut_numba_block_reduce_force_probe_test.py",
)


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "hierarchical_barnes_hut_acceleration_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "native_engine_app_specific": False,
        "true_zero_copy_claim_authorized": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timing list")
    return float(statistics.median(values))


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("--body-counts must not be empty")
    if any(count <= 0 for count in counts):
        raise ValueError("--body-counts values must be positive")
    return counts


def _time_partner(*, partner: str, body_count: int, warmup: int, repeat: int) -> dict[str, Any]:
    measured: list[float] = []
    runs: list[dict[str, Any]] = []
    force_counts: list[int] = []
    last_metadata: dict[str, Any] = {}
    for iteration in range(warmup + repeat):
        start = time.perf_counter()
        payload = app.run_app(
            "partner_exact_force",
            partner=partner,
            body_count=body_count,
            output_mode="force_summary",
            skip_validation=True,
        )
        elapsed = time.perf_counter() - start
        is_warmup = iteration < warmup
        force_count = int(payload["force_row_count"])
        force_counts.append(force_count)
        last_metadata = dict(payload["partner_metadata"])
        print(
            f"[goal3762] partner={partner} body_count={body_count} "
            f"{'warmup' if is_warmup else 'repeat'} {iteration + 1}/{warmup + repeat} "
            f"elapsed={elapsed:.6f}s force_rows={force_count}",
            flush=True,
        )
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "force_row_count": force_count,
            }
        )
        if not is_warmup:
            measured.append(elapsed)
    if len(set(force_counts)) != 1:
        raise RuntimeError(f"{partner} force row count changed: {force_counts}")
    return {
        "partner": partner,
        "body_count": body_count,
        "force_row_count": force_counts[-1],
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "repeat": repeat,
        "warmup": warmup,
        "metadata": last_metadata,
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    counts = _parse_counts(args.body_counts)
    correctness = app.run_app(
        "partner_exact_force",
        partner="numba",
        body_count=int(args.correctness_body_count),
        output_mode="force_summary",
        skip_validation=False,
    )
    rows = []
    for count in counts:
        cupy = _time_partner(partner="cupy", body_count=count, warmup=args.warmup, repeat=args.repeat)
        numba = _time_partner(partner="numba", body_count=count, warmup=args.warmup, repeat=args.repeat)
        rows.append(
            {
                "body_count": count,
                "cupy": cupy,
                "numba": numba,
                "force_counts_match": int(cupy["force_row_count"]) == int(numba["force_row_count"]),
                "numba_speedup_vs_cupy": float(cupy["hot_median_sec"]) / float(numba["hot_median_sec"]),
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [float(row["numba_speedup_vs_cupy"]) for row in rows]
    return {
        "schema": SCHEMA,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "goal3762_scoped_source_paths": list(SCOPED_SOURCE_PATHS),
        "goal3762_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3762_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "body_counts": list(counts),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "correctness": {
            "body_count": int(args.correctness_body_count),
            "matches_oracle": bool(correctness.get("matches_oracle")),
            "max_relative_error": float(correctness.get("max_relative_error", 0.0)),
            "metadata": correctness.get("partner_metadata", {}),
        },
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_force_counts_match": all(bool(row["force_counts_match"]) for row in rows),
            "min_numba_speedup_vs_cupy": min(ratios) if ratios else None,
            "geomean_numba_speedup_vs_cupy": (
                __import__("math").prod(ratios) ** (1.0 / len(ratios)) if ratios else None
            ),
        },
        "interpretation": (
            "Same-contract app-layer exact all-pairs force-vector timing. The Numba path uses an "
            "adaptive no-RawKernel strategy: a block-per-source target-stride reduction for "
            "large enough partner inputs, with older kernels retained only as fallback shapes. "
            "This is not hierarchical Barnes-Hut acceleration and not an RT-core claim."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3762 Barnes-Hut Numba block-reduce exact-force probe.")
    parser.add_argument("--body-counts", default="1024,2048,4096,8192")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--correctness-body-count", type=int, default=256)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.correctness_body_count <= 0:
        raise ValueError("--correctness-body-count must be positive")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3762] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

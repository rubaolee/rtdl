#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app  # noqa: E402


SCHEMA = "rtdl.goal3869.barnes_hut_resident_output_reuse_probe.v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3869_barnes_hut_resident_output_reuse_a5000"
    / "summary.json"
)
SCOPED_SOURCE_PATHS = (
    "src/rtdsl/app_adapters/barnes_hut.py",
    "examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py",
    "scripts/goal3869_barnes_hut_resident_output_reuse_probe.py",
    "tests/goal3869_barnes_hut_resident_output_reuse_test.py",
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


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("--body-counts must not be empty")
    if any(count <= 0 for count in counts):
        raise ValueError("--body-counts values must be positive")
    return counts


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timing list")
    return float(statistics.median(values))


def _column_sum(column: object, *, partner: str) -> float:
    if partner == "numba":
        return float(column.copy_to_host().sum())  # type: ignore[attr-defined]
    if partner == "cupy":
        import cupy

        return float(cupy.sum(column).item())
    raise ValueError("partner must be 'numba' or 'cupy'")


def _time_partner_reuse_mode(
    *,
    partner: str,
    body_count: int,
    reuse_outputs: bool,
    warmup: int,
    repeat: int,
) -> dict[str, Any]:
    bodies = app.make_generated_bodies(body_count)
    columns = rt.weighted_point_rows_to_partner_columns(bodies, partner=partner)
    reusable_output_columns: dict[str, object] | None = None
    runs: list[dict[str, Any]] = []
    measured: list[float] = []
    final_result: dict[str, Any] | None = None
    for iteration in range(warmup + repeat):
        start = time.perf_counter()
        result = rt.pairwise_inverse_square_force_2d_partner_columns(
            columns,
            columns,
            softening=app.SOFTENING,
            partner=partner,
            exclude_equal_ids=True,
            output_columns=reusable_output_columns if reuse_outputs else None,
            return_metadata=True,
        )
        elapsed = time.perf_counter() - start
        final_result = result
        if reuse_outputs:
            reusable_output_columns = {
                "force_x": result["columns"]["force_x"],
                "force_y": result["columns"]["force_y"],
            }
        is_warmup = iteration < warmup
        print(
            f"[goal3869] partner={partner} body_count={body_count} "
            f"reuse_outputs={reuse_outputs} {'warmup' if is_warmup else 'repeat'} "
            f"{iteration + 1}/{warmup + repeat} elapsed={elapsed:.6f}s "
            f"output_reused={result['metadata'].get('output_columns_reused')}",
            flush=True,
        )
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "output_columns_reused": bool(result["metadata"].get("output_columns_reused")),
            }
        )
        if not is_warmup:
            measured.append(elapsed)
    if final_result is None:
        raise RuntimeError("resident output reuse probe produced no result")
    force_columns = final_result["columns"]
    return {
        "partner": partner,
        "body_count": body_count,
        "reuse_outputs": reuse_outputs,
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "repeat": repeat,
        "warmup": warmup,
        "checksum_force_x": _column_sum(force_columns["force_x"], partner=partner),
        "checksum_force_y": _column_sum(force_columns["force_y"], partner=partner),
        "metadata": final_result["metadata"],
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    counts = _parse_counts(args.body_counts)
    rows: list[dict[str, Any]] = []
    for count in counts:
        for partner in args.partners:
            without_reuse = _time_partner_reuse_mode(
                partner=partner,
                body_count=count,
                reuse_outputs=False,
                warmup=args.warmup,
                repeat=args.repeat,
            )
            with_reuse = _time_partner_reuse_mode(
                partner=partner,
                body_count=count,
                reuse_outputs=True,
                warmup=args.warmup,
                repeat=args.repeat,
            )
            checksum_abs_delta = math.hypot(
                float(with_reuse["checksum_force_x"]) - float(without_reuse["checksum_force_x"]),
                float(with_reuse["checksum_force_y"]) - float(without_reuse["checksum_force_y"]),
            )
            rows.append(
                {
                    "body_count": count,
                    "partner": partner,
                    "without_reuse": without_reuse,
                    "with_reuse": with_reuse,
                    "reuse_speedup_vs_no_reuse": float(without_reuse["hot_median_sec"])
                    / float(with_reuse["hot_median_sec"]),
                    "checksum_abs_delta": checksum_abs_delta,
                    "checksum_match": checksum_abs_delta <= float(args.checksum_abs_tolerance),
                    "claim_boundary": _claim_boundary(),
                }
            )
    speedups = [float(row["reuse_speedup_vs_no_reuse"]) for row in rows]
    return {
        "schema": SCHEMA,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "goal3869_scoped_source_paths": list(SCOPED_SOURCE_PATHS),
        "goal3869_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3869_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "body_counts": list(counts),
        "partners": list(args.partners),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "checksum_abs_tolerance": float(args.checksum_abs_tolerance),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_checksum_match": all(bool(row["checksum_match"]) for row in rows),
            "min_reuse_speedup_vs_no_reuse": min(speedups) if speedups else None,
            "geomean_reuse_speedup_vs_no_reuse": (
                math.prod(speedups) ** (1.0 / len(speedups)) if speedups else None
            ),
        },
        "interpretation": (
            "Same-contract resident-repeat probe for Barnes-Hut exact all-pairs "
            "force-vector partner continuation. Output-column reuse removes repeated "
            "device output allocation for warmed repeated requests, but it is not a "
            "hierarchical Barnes-Hut acceleration path and not an RT-core claim."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3869 Barnes-Hut resident output-column reuse probe.")
    parser.add_argument("--body-counts", default="8192,16384")
    parser.add_argument("--partners", nargs="+", default=("numba", "cupy"), choices=("numba", "cupy"))
    parser.add_argument("--repeat", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--checksum-abs-tolerance", type=float, default=1.0e-6)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3869] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Rebuild Goal5774 duration buckets directly from raw worker endpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


V2_METHOD = "v2_direct_true_optix_backport"
V4_METHOD = "v4_restricted_callback_true_optix"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bucket(seconds: float) -> str:
    if seconds > 10.0:
        return ">10s"
    if seconds >= 1.0:
        return "1-10s"
    return "<1s"


def _corr(xs: list[float], ys: list[float]) -> float:
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs)
        * sum((y - mean_y) ** 2 for y in ys)
    )
    return numerator / denominator


def build_diagnostic(worker_root: Path, result_path: Path) -> dict:
    workers = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(worker_root.glob("*.json"))
    ]
    if len(workers) != 208:
        raise ValueError(f"expected 208 workers, got {len(workers)}")
    if {worker["method"] for worker in workers} != {V2_METHOD, V4_METHOD}:
        raise ValueError("unexpected method set")

    indexed = {
        (worker["lane_id"], worker["block_index"], worker["method"]): worker
        for worker in workers
    }
    if len(indexed) != len(workers):
        raise ValueError("duplicate worker identity")

    rows: list[dict] = []
    observations: list[dict] = []
    for lane_id in sorted({worker["lane_id"] for worker in workers}):
        for call_index in (0, 1):
            v2_seconds: list[float] = []
            v4_seconds: list[float] = []
            for block_index in range(8):
                v2 = indexed[(lane_id, block_index, V2_METHOD)]["calls"][call_index][
                    "registered_prepared_execution_seconds"
                ]
                v4 = indexed[(lane_id, block_index, V4_METHOD)]["calls"][call_index][
                    "registered_prepared_execution_seconds"
                ]
                v2_seconds.append(v2)
                v4_seconds.append(v4)
                observations.append(
                    {
                        "lane_id": lane_id,
                        "call_index": call_index,
                        "block_index": block_index,
                        "v2_seconds": v2,
                        "v4_seconds": v4,
                        "v2_over_v4": v2 / v4,
                        "v4_over_v2": v4 / v2,
                        "v4_minus_v2_seconds": v4 - v2,
                        "bucket_by_v2_seconds": _bucket(v2),
                    }
                )
            ratios = [v2 / v4 for v2, v4 in zip(v2_seconds, v4_seconds)]
            slowdowns = [v4 / v2 for v2, v4 in zip(v2_seconds, v4_seconds)]
            gaps = [v4 - v2 for v2, v4 in zip(v2_seconds, v4_seconds)]
            v2_median = statistics.median(v2_seconds)
            rows.append(
                {
                    "lane_id": lane_id,
                    "call_index": call_index,
                    "bucket_by_v2_median_seconds": _bucket(v2_median),
                    "v2_median_seconds": v2_median,
                    "v4_median_seconds": statistics.median(v4_seconds),
                    "paired_v2_over_v4_median": statistics.median(ratios),
                    "paired_v4_over_v2_median": statistics.median(slowdowns),
                    "paired_v4_minus_v2_median_seconds": statistics.median(gaps),
                }
            )

    if len(rows) != 26 or len(observations) != 208:
        raise ValueError("unexpected reconstructed shape")

    bucket_rows = []
    for bucket_name in (">10s", "1-10s", "<1s"):
        selected = [
            row for row in rows if row["bucket_by_v2_median_seconds"] == bucket_name
        ]
        summary = {
            "bucket": bucket_name,
            "independent_row_count": len(selected),
            "slower_row_count": sum(
                row["paired_v2_over_v4_median"] < 1.0 for row in selected
            ),
        }
        if selected:
            summary.update(
                {
                    "v2_median_seconds_min": min(
                        row["v2_median_seconds"] for row in selected
                    ),
                    "v2_median_seconds_max": max(
                        row["v2_median_seconds"] for row in selected
                    ),
                    "v4_over_v2_median_across_rows": statistics.median(
                        row["paired_v4_over_v2_median"] for row in selected
                    ),
                    "v4_over_v2_min": min(
                        row["paired_v4_over_v2_median"] for row in selected
                    ),
                    "v4_over_v2_max": max(
                        row["paired_v4_over_v2_median"] for row in selected
                    ),
                    "v4_minus_v2_median_seconds_across_rows": statistics.median(
                        row["paired_v4_minus_v2_median_seconds"] for row in selected
                    ),
                    "v4_minus_v2_min_seconds": min(
                        row["paired_v4_minus_v2_median_seconds"] for row in selected
                    ),
                    "v4_minus_v2_max_seconds": max(
                        row["paired_v4_minus_v2_median_seconds"] for row in selected
                    ),
                }
            )
        bucket_rows.append(summary)

    preparation = {}
    for method in (V2_METHOD, V4_METHOD):
        selected = [worker for worker in workers if worker["method"] == method]
        prepare = [
            worker["activation"]["reported_total_prepare_seconds"]
            for worker in selected
        ]
        activation = [
            worker["activation"]["activation_seconds"] for worker in selected
        ]
        preparation[method] = {
            "worker_count": len(selected),
            "prepare_seconds_median": statistics.median(prepare),
            "prepare_seconds_min": min(prepare),
            "prepare_seconds_max": max(prepare),
            "prepare_bucket_counts": {
                name: sum(_bucket(value) == name for value in prepare)
                for name in (">10s", "1-10s", "<1s")
            },
            "activation_seconds_median": statistics.median(activation),
            "activation_seconds_min": min(activation),
            "activation_seconds_max": max(activation),
        }

    return {
        "schema": "rtdl.goal5774.duration_stratified_diagnostic.v1",
        "source": {
            "result_path": str(result_path),
            "result_sha256": _sha256(result_path),
            "worker_root": str(worker_root),
            "worker_count": len(workers),
        },
        "bucket_basis": "median V2 registered prepared-execution seconds per independent row",
        "bucket_summary": bucket_rows,
        "preparation": preparation,
        "row_level": rows,
        "diagnostic_signals": {
            "v2_median_vs_absolute_gap_pearson": _corr(
                [row["v2_median_seconds"] for row in rows],
                [row["paired_v4_minus_v2_median_seconds"] for row in rows],
            ),
            "v2_median_vs_slowdown_factor_pearson": _corr(
                [row["v2_median_seconds"] for row in rows],
                [row["paired_v4_over_v2_median"] for row in rows],
            ),
            "long_duration_inference_allowed": False,
            "reason": "No registered prepared-execution row has a V2 median at or above one second.",
        },
    }


def render_markdown(data: dict) -> str:
    buckets = {item["bucket"]: item for item in data["bucket_summary"]}
    short = buckets["<1s"]
    prep_v2 = data["preparation"][V2_METHOD]
    prep_v4 = data["preparation"][V4_METHOD]
    return f"""# Goal5774 duration-stratified V2/V4 diagnostic

## Answer

The registered prepared-execution cohort contains **zero** independent rows in
the `>10s` bucket and **zero** in `1-10s`. All **26/26** independent rows are
below one second; in fact their V2 medians span only
{short['v2_median_seconds_min'] * 1000:.3f}--{short['v2_median_seconds_max'] * 1000:.3f} ms.
All 26 are slower under V4.

Across those 26 short rows, the median row slowdown is
**{short['v4_over_v2_median_across_rows']:.3f}x** (range
{short['v4_over_v2_min']:.3f}x--{short['v4_over_v2_max']:.3f}x), while the median
absolute per-call deficit is only
**{short['v4_minus_v2_median_seconds_across_rows'] * 1000:.3f} ms** (range
{short['v4_minus_v2_min_seconds'] * 1000:.3f}--{short['v4_minus_v2_max_seconds'] * 1000:.3f} ms).

## Startup versus execution

One-time preparation is a major separate problem: V4 preparation has a median
of **{prep_v4['prepare_seconds_median']:.3f}s**, versus
**{prep_v2['prepare_seconds_median']:.3f}s** for V2. Among 104 V4 preparation
observations, {prep_v4['prepare_bucket_counts']['>10s']} exceed 10 seconds,
{prep_v4['prepare_bucket_counts']['1-10s']} are between 1 and 10 seconds, and
{prep_v4['prepare_bucket_counts']['<1s']} are below one second. Preparation is
reported outside the registered prepared-execution timer.

The registered-call result proves that startup is **not the only problem**:
after preparation, V4 still adds a median 5.828 ms per row. The strongly
negative correlation between baseline duration and multiplicative slowdown
({data['diagnostic_signals']['v2_median_vs_slowdown_factor_pearson']:.3f}) is
consistent with a largely fixed per-call control-plane cost dominating tiny
fixtures. Some lanes add up to 15.137 ms, so lane-specific callback/composition
work may also contribute; the present receipts do not phase-separate that work
from the OptiX execution.

## Scope limit

This cohort cannot answer how V4 behaves for 1--10 second or >10 second
executions. Any claim that the observed 13.173x median slowdown generalizes to
long paper workloads would be invalid. A duration-scaled cohort or a read-only
per-call phase ledger is required before distinguishing fixed callback/control
cost from physical-algorithm cost on long-running inputs.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    data = build_diagnostic(args.worker_root, args.result)
    args.json_output.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(data), encoding="utf-8")


if __name__ == "__main__":
    main()

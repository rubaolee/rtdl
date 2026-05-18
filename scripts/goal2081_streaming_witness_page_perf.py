#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

import rtdsl as rt
from scripts.goal1856_segment_polygon_v2_partner_perf import _build_partner_columns
from scripts.goal1856_segment_polygon_v2_partner_perf import _build_records
from scripts.goal1856_segment_polygon_v2_partner_perf import _canonical_rows


def _summary(samples: list[float]) -> dict[str, float]:
    return {
        "min_s": min(samples),
        "median_s": statistics.median(samples),
        "max_s": max(samples),
    }


def _time_call(label: str, iterations: int, fn, sync) -> tuple[list[float], object]:
    print(f"[goal2081] timing {label} iterations={iterations}", flush=True)
    samples: list[float] = []
    last = None
    for index in range(iterations):
        start = time.perf_counter()
        last = fn()
        sync()
        elapsed = time.perf_counter() - start
        samples.append(elapsed)
        print(f"[goal2081] {label} iter={index + 1} elapsed_s={elapsed:.6f}", flush=True)
    return samples, last


def _sync_for_partner(partner: str):
    if partner == "cupy":
        import cupy

        return cupy.cuda.runtime.deviceSynchronize
    if partner == "torch":
        import torch

        return torch.cuda.synchronize
    raise ValueError("partner must be 'cupy' or 'torch'")


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal2081 streaming witness-page perf probe.")
    parser.add_argument("--count", type=int, default=4096)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--partner", choices=("cupy", "torch"), default="cupy")
    parser.add_argument("--output-capacity", type=int, default=None)
    parser.add_argument("--page-limit", type=int, default=None)
    parser.add_argument("--output", default="docs/reports/goal2081_streaming_witness_page_perf.json")
    args = parser.parse_args()
    if args.count <= 0:
        raise ValueError("--count must be positive")
    if args.iterations <= 0:
        raise ValueError("--iterations must be positive")

    segments, polygons = _build_records(args.count)
    output_capacity = int(args.output_capacity) if args.output_capacity is not None else args.count * 2
    page_limit = int(args.page_limit) if args.page_limit is not None else args.count
    if output_capacity <= 0 or page_limit <= 0:
        raise ValueError("--output-capacity and --page-limit must be positive")
    expected_rows = tuple({"segment_id": segment.id, "polygon_id": polygon.id} for segment, polygon in zip(segments, polygons))
    expected_canonical = _canonical_rows(expected_rows)
    sync = _sync_for_partner(args.partner)
    print(
        f"[goal2081] setup count={args.count} output_capacity={output_capacity} "
        f"page_limit={page_limit} partner={args.partner}",
        flush=True,
    )

    v18_samples, v18_rows = _time_call(
        "v1_8_native_optix_rows",
        args.iterations,
        lambda: rt.segment_polygon_anyhit_rows_native_bounded_optix(
            segments,
            polygons,
            output_capacity=output_capacity,
        ),
        sync,
    )
    if _canonical_rows(v18_rows) != expected_canonical:
        raise RuntimeError("v1.8 native rows did not match expected rows")

    ray_columns, triangle_columns, triangle_aabbs, column_build_s = _build_partner_columns(
        segments,
        polygons,
        args.partner,
    )
    witness_output_columns = rt.allocate_segment_polygon_witness_partner_device_output_columns(
        output_capacity,
        partner=args.partner,
    )
    prepared_scene = rt.prepare_segment_polygon_anyhit_optix_partner_device_scene(
        triangle_columns,
        triangle_aabbs,
    )
    try:
        old_samples, old_rows = _time_call(
            "v2_0_partner_columns_full_python_rows",
            args.iterations,
            lambda: rt.segment_polygon_anyhit_rows_optix_partner_columns(
                ray_columns,
                triangle_columns,
                triangle_aabbs,
                partner=args.partner,
                output_capacity=output_capacity,
            ),
            sync,
        )
        if _canonical_rows(old_rows) != expected_canonical:
            raise RuntimeError("old v2 full-row path did not match expected rows")

        page_samples, page_result = _time_call(
            "v2_0_streaming_exact_witness_page_columns",
            args.iterations,
            lambda: rt.segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns(
                prepared_scene,
                ray_columns,
                partner=args.partner,
                output_capacity=output_capacity,
                witness_output_columns=witness_output_columns,
                page_limit=page_limit,
                return_metadata=True,
            ),
            sync,
        )
    finally:
        prepared_scene.close()

    metadata = page_result["metadata"]
    if int(metadata["exact_witness_count"]) != len(expected_rows):
        raise RuntimeError("streaming witness page did not preserve exact witness count")
    payload = {
        "goal": "Goal2081",
        "status": "pass",
        "git_commit": _git_commit(),
        "gpu": _gpu_name(),
        "count": args.count,
        "iterations": args.iterations,
        "partner": args.partner,
        "output_capacity": output_capacity,
        "page_limit": page_limit,
        "column_build_s": column_build_s,
        "v1_8_native_optix_rows": {
            "query_summary": _summary(v18_samples),
            "row_count": len(v18_rows),
        },
        "v2_0_partner_columns_full_python_rows": {
            "query_summary": _summary(old_samples),
            "row_count": len(old_rows),
            "ratio_vs_v1_8": statistics.median(old_samples) / statistics.median(v18_samples),
        },
        "v2_0_streaming_exact_witness_page_columns": {
            "query_summary": _summary(page_samples),
            "metadata": metadata,
            "ratio_vs_v1_8": statistics.median(page_samples) / statistics.median(v18_samples),
            "ratio_vs_old_v2_full_rows": statistics.median(page_samples) / statistics.median(old_samples),
        },
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "requires_pod_review_before_table_update": True,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

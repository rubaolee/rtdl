from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.benchmark_apps.barnes_hut import (  # noqa: E402
    rtdl_barnes_hut_benchmark_app as barnes_hut,
)
from rtdsl.numba_partner_continuation import (  # noqa: E402
    configure_numba_cuda_toolchain_environment,
)


GOAL = "Goal4458 / V3.0 M62 - Barnes-Hut current route rerank"
VERSION = "rtdl.v3_0.barnes_hut_current_route_rerank.goal4458.v1"
BODY_COUNTS = (8192, 16384, 32768)
THETA = 0.5
BUCKET_SIZE = 64
MAX_DEPTH = 32
DEFAULT_REPEAT = 31
DEFAULT_WARMUP = 3

ROUTES: tuple[dict[str, str], ...] = (
    {
        "route_id": "cpu_numba_fused",
        "mode": "fused_frontier_force_sum_bucketized_cpu_numba",
        "partner": "numba",
        "reading": "fastest measured CPU fused app route",
    },
    {
        "route_id": "numba_cuda_fused",
        "mode": "fused_frontier_force_sum_bucketized_numba_cuda",
        "partner": "numba",
        "reading": "no-C++ Python-source fused GPU partner app route",
    },
    {
        "route_id": "optix_numba_prepared_frontier",
        "mode": "prepared_aggregate_frontier_weighted_vector_optix",
        "partner": "numba",
        "reading": "RTDL/OptiX RT-core aggregate-frontier device-column evidence route",
    },
    {
        "route_id": "optix_cupy_prepared_frontier",
        "mode": "prepared_aggregate_frontier_weighted_vector_optix",
        "partner": "cupy",
        "reading": "same prepared RTDL/OptiX route with CuPy comparison partner",
    },
)


def _parse_body_counts(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("--body-counts must include at least one positive value")
    if any(value <= 0 for value in values):
        raise ValueError("--body-counts values must be positive")
    return values


def _median(values: tuple[float, ...] | list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _best_time(payload: dict[str, Any]) -> float:
    phases = payload.get("run_phases", {})
    medians = payload.get("medians", {})
    mode = str(payload.get("mode"))
    if mode == "fused_frontier_force_sum_bucketized_numba_cuda":
        kernel = phases.get("kernel_event_median_sec")
        if kernel is not None:
            return float(kernel)
        return float(phases["partner_wall_median_sec"])
    if mode == "fused_frontier_force_sum_bucketized_cpu_numba":
        return float(phases["vector_run_median_sec"])
    if mode == "prepared_aggregate_frontier_weighted_vector_optix":
        return float(medians["hot_seconds_native_plus_partner"])
    raise ValueError(f"unsupported mode for timing extraction: {mode}")


def _row_from_payload(route: dict[str, str], body_count: int, payload: dict[str, Any]) -> dict[str, Any]:
    vector_summary = payload["vector_sum_summary"]
    medians = payload.get("medians", {})
    phases = payload.get("run_phases", {})
    hot_seconds = _best_time(payload)
    repeat_seconds = tuple(float(value) for value in vector_summary.get("repeat_seconds", ()))
    hot_repeats = payload.get("hot_repeats", ())
    if not repeat_seconds and hot_repeats:
        repeat_seconds = tuple(float(row["hot_seconds_native_plus_partner"]) for row in hot_repeats)
    aggregate_count = int(vector_summary["aggregate_contribution_row_count"])
    exact_count = int(vector_summary["exact_contribution_row_count"])
    contribution_count = int(
        vector_summary.get(
            "contribution_row_count",
            vector_summary.get("frontier_row_count", aggregate_count + exact_count),
        )
    )
    return {
        "route_id": route["route_id"],
        "mode": payload["mode"],
        "partner": route["partner"],
        "reading": route["reading"],
        "body_count": body_count,
        "theta": float(payload["theta"]),
        "bucket_size": int(payload["bucket_size"]),
        "max_depth": int(payload["max_depth"]),
        "hot_median_seconds": hot_seconds,
        "hot_time_kind": (
            "cuda_event_kernel"
            if payload["mode"] == "fused_frontier_force_sum_bucketized_numba_cuda"
            else "wall_median_native_plus_partner"
        ),
        "call_wall_median_seconds": phases.get("call_wall_median_sec") or medians.get("wall_seconds"),
        "partner_wall_median_seconds": phases.get("partner_wall_median_sec") or medians.get("partner_seconds"),
        "frontier_traversal_median_seconds": medians.get("frontier_traversal_seconds"),
        "contribution_row_count": contribution_count,
        "aggregate_contribution_row_count": aggregate_count,
        "exact_contribution_row_count": exact_count,
        "checksum_force_x": float(vector_summary["checksum_force_x"]),
        "checksum_force_y": float(vector_summary["checksum_force_y"]),
        "repeat_seconds_median": _median(repeat_seconds),
        "repeat_count": int(vector_summary.get("repeat", len(hot_repeats) or len(repeat_seconds))),
        "warmup": int(vector_summary.get("warmup", 0)),
        "frontier_rows_materialized_on_host": bool(
            vector_summary.get(
                "frontier_rows_materialized_on_host",
                vector_summary.get("frontier_columns_materialized_on_host", False),
            )
        ),
        "contribution_rows_materialized_on_host": bool(
            vector_summary.get("contribution_rows_materialized_on_host", False)
        ),
        "rt_cores_used": bool(payload["claim_flags"].get("rt_cores_used", False)),
        "rt_core_accelerated_metadata": bool(payload["benchmark_metadata"]["rt_core_accelerated"]),
        "rt_core_speedup_claim_authorized": bool(
            payload["claim_flags"].get("rt_core_speedup_claim_authorized", False)
        ),
        "public_speedup_claim_authorized": bool(
            payload["claim_flags"].get("public_speedup_claim_authorized", False)
        ),
        "validation": payload["validation"],
    }


def _comparison_for_body(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_route = {row["route_id"]: row for row in rows}
    cpu = float(by_route["cpu_numba_fused"]["hot_median_seconds"])
    cuda = float(by_route["numba_cuda_fused"]["hot_median_seconds"])
    optix_numba = float(by_route["optix_numba_prepared_frontier"]["hot_median_seconds"])
    optix_cupy = float(by_route["optix_cupy_prepared_frontier"]["hot_median_seconds"])
    fastest = min(rows, key=lambda row: float(row["hot_median_seconds"]))
    return {
        "body_count": int(fastest["body_count"]),
        "fastest_route_id": fastest["route_id"],
        "cpu_numba_seconds": cpu,
        "numba_cuda_seconds": cuda,
        "optix_numba_seconds": optix_numba,
        "optix_cupy_seconds": optix_cupy,
        "numba_cuda_over_cpu_numba": cuda / cpu,
        "optix_numba_over_cpu_numba": optix_numba / cpu,
        "optix_numba_over_numba_cuda": optix_numba / cuda,
        "optix_cupy_over_optix_numba": optix_cupy / optix_numba,
    }


def planned_payload(body_counts: tuple[int, ...], repeat: int, warmup: int) -> dict[str, Any]:
    return {
        "goal": 4458,
        "milestone": "V3.0 M62",
        "version": VERSION,
        "dry_run": True,
        "body_counts": body_counts,
        "theta": THETA,
        "bucket_size": BUCKET_SIZE,
        "max_depth": MAX_DEPTH,
        "repeat": repeat,
        "warmup": warmup,
        "routes": ROUTES,
        "claim_boundary": (
            "Reranks current Barnes-Hut app routes under one logical force-summary contract. "
            "The prepared OptiX rows are RT-core evidence rows; the fused CPU/Numba and "
            "Numba CUDA rows are partner-fused rows. This does not authorize a Barnes-Hut "
            "RT-core speedup claim or automatic partner selection."
        ),
    }


def run_rerank(body_counts: tuple[int, ...], repeat: int, warmup: int) -> dict[str, Any]:
    configure_numba_cuda_toolchain_environment()
    rows: list[dict[str, Any]] = []
    raw_payloads: list[dict[str, Any]] = []
    for body_count in body_counts:
        for route in ROUTES:
            payload = barnes_hut.run_benchmark(
                route["mode"],
                body_count=body_count,
                theta=THETA,
                bucket_size=BUCKET_SIZE,
                max_depth=MAX_DEPTH,
                partner=route["partner"],
                skip_validation=True,
                query_repeat=repeat,
                warmup=warmup,
                force_output_mode="force_summary",
            )
            raw_payloads.append(payload)
            rows.append(_row_from_payload(route, body_count, payload))

    comparisons = [
        _comparison_for_body([row for row in rows if int(row["body_count"]) == body_count])
        for body_count in body_counts
    ]
    return {
        "goal": 4458,
        "milestone": "V3.0 M62",
        "version": VERSION,
        "dry_run": False,
        "body_counts": body_counts,
        "theta": THETA,
        "bucket_size": BUCKET_SIZE,
        "max_depth": MAX_DEPTH,
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "comparisons": comparisons,
        "raw_payloads": raw_payloads,
        "claim_flags": {
            "automatic_partner_selection_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "interpretation": (
            "The current Barnes-Hut performance lever is fused traversal plus force "
            "accumulation, not aggregate-frontier row emission. The RTDL/OptiX route "
            "remains useful RT-core device-column evidence, but it is not the current "
            "fastest force-summary route."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=GOAL)
    parser.add_argument("--body-counts", default=",".join(str(value) for value in BODY_COUNTS))
    parser.add_argument("--repeat", type=int, default=DEFAULT_REPEAT)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    body_counts = _parse_body_counts(args.body_counts)
    if args.repeat < 1:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")

    payload = (
        planned_payload(body_counts, args.repeat, args.warmup)
        if args.dry_run
        else run_rerank(body_counts, args.repeat, args.warmup)
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

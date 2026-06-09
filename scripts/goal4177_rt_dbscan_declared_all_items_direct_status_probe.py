from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import time
from typing import Any

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
    RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
    RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json"
)


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _gpu_summary() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            timeout=15,
        ).strip()
    except Exception as exc:  # pragma: no cover - depends on pod hardware.
        return f"unavailable: {exc}"


def _run_route(
    *,
    label: str,
    mode: str,
    dataset: str,
    point_count: int,
    partition_cell_factor: float,
    repeat: int,
    warmup: int,
    seed: int,
) -> dict[str, Any]:
    print(
        "GOAL4177_ROUTE_START",
        json.dumps(
            {
                "label": label,
                "mode": mode,
                "dataset": dataset,
                "point_count": int(point_count),
                "partition_cell_factor": float(partition_cell_factor),
                "repeat": int(repeat),
                "warmup": int(warmup),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    wall_start = time.perf_counter()
    payload = run_rt_dbscan_benchmark(
        mode=mode,
        dataset=dataset,
        point_count=point_count,
        radius=None,
        min_neighbors=None,
        seed=seed,
        partner="cupy",
        include_rows=False,
        validate=False,
        partition_cell_factor=partition_cell_factor,
        direct_status_convergence_mode="until_stable",
        repeat=repeat,
        warmup=warmup,
    )
    wall_sec = time.perf_counter() - wall_start
    metadata = dict(payload["metadata"])
    threshold_metadata = metadata.get("threshold_metadata")
    row = {
        "label": label,
        "mode": mode,
        "elapsed_sec": float(payload["elapsed_sec"]),
        "wall_sec": float(wall_sec),
        "signature": payload["signature"],
        "matches_reference": payload.get("matches_reference"),
        "path": metadata.get("path"),
        "partner": metadata.get("partner"),
        "native_engine_summary_contract": metadata.get("native_engine_summary_contract"),
        "native_execution_path": metadata.get("native_execution_path"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "rt_count_threshold_executed": bool(metadata.get("rt_count_threshold_executed", False)),
        "predicate_flags_source": metadata.get("predicate_flags_source"),
        "predicate_columns_materialized": metadata.get("predicate_columns_materialized"),
        "uses_generic_all_items_direct_status_signature": bool(
            metadata.get("uses_generic_all_items_direct_status_signature", False)
        ),
        "materializes_neighbor_summaries": bool(metadata.get("materializes_neighbor_summaries", False)),
        "materializes_neighbor_rows": bool(metadata.get("materializes_neighbor_rows", False)),
        "materializes_python_rows": bool(metadata.get("materializes_python_rows", False)),
        "all_predicate_fast_path_observed": bool(metadata.get("all_predicate_fast_path_observed", False)),
        "mixed_predicate_fail_closed": bool(metadata.get("mixed_predicate_fail_closed", False)),
        "release_authorized": bool(metadata.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(metadata.get("public_speedup_claim_authorized", False)),
        "rt_core_speedup_claim_authorized": bool(metadata.get("rt_core_speedup_claim_authorized", False)),
        "whole_app_speedup_claim_authorized": bool(metadata.get("whole_app_speedup_claim_authorized", False)),
        "true_zero_copy_claim_authorized": bool(metadata.get("true_zero_copy_claim_authorized", False)),
        "metadata": metadata,
    }
    if isinstance(threshold_metadata, dict):
        row["threshold_metadata_summary"] = {
            "path": threshold_metadata.get("path"),
            "rt_count_threshold_executed": threshold_metadata.get("rt_count_threshold_executed"),
            "predicate_columns_materialized": threshold_metadata.get("predicate_columns_materialized"),
            "uses_generic_all_items_direct_status_signature": threshold_metadata.get(
                "uses_generic_all_items_direct_status_signature"
            ),
        }
    print(
        "GOAL4177_ROUTE_DONE",
        json.dumps(
            {
                "label": label,
                "elapsed_sec": row["elapsed_sec"],
                "wall_sec": row["wall_sec"],
                "signature": row["signature"],
                "rt_count_threshold_executed": row["rt_count_threshold_executed"],
                "predicate_columns_materialized": row["predicate_columns_materialized"],
                "uses_generic_all_items_direct_status_signature": row[
                    "uses_generic_all_items_direct_status_signature"
                ],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return row


def run(
    *,
    output: pathlib.Path,
    dataset: str,
    point_count: int,
    warmup_point_count: int,
    partition_cell_factor: float,
    repeat: int,
    warmup: int,
    seed: int,
) -> dict[str, Any]:
    print("GOAL4177_PROBE_START", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), flush=True)
    warmup_row = _run_route(
        label="warmup_declared_all_items_direct_status",
        mode=RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
        dataset=dataset,
        point_count=warmup_point_count,
        partition_cell_factor=partition_cell_factor,
        repeat=1,
        warmup=0,
        seed=seed,
    )
    rows = [
        _run_route(
            label="current_grouped_stream_numba",
            mode=RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
            dataset=dataset,
            point_count=point_count,
            partition_cell_factor=partition_cell_factor,
            repeat=repeat,
            warmup=warmup,
            seed=seed,
        ),
        _run_route(
            label="measured_alltrue_predicate_direct_status",
            mode=RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
            dataset=dataset,
            point_count=point_count,
            partition_cell_factor=partition_cell_factor,
            repeat=repeat,
            warmup=warmup,
            seed=seed,
        ),
        _run_route(
            label="declared_all_items_direct_status",
            mode=RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
            dataset=dataset,
            point_count=point_count,
            partition_cell_factor=partition_cell_factor,
            repeat=repeat,
            warmup=warmup,
            seed=seed,
        ),
    ]
    reference = rows[0]["signature"]
    current_elapsed = float(rows[0]["elapsed_sec"])
    declared_elapsed = float(rows[-1]["elapsed_sec"])
    for row in rows:
        row["same_signature_as_current"] = row["signature"] == reference
        row["speedup_vs_current_elapsed"] = current_elapsed / max(float(row["elapsed_sec"]), 1.0e-12)
    payload = {
        "goal": "Goal4177",
        "schema": "rtdl.goal4177.rt_dbscan_declared_all_items_direct_status_probe.v1",
        "purpose": (
            "Warmed large-scale RT-DBSCAN timing probe after Goal4176 refactored the "
            "caller-declared all-predicate route onto the generic all-items direct-status primitive."
        ),
        "source_commit": _source_commit(),
        "gpu": _gpu_summary(),
        "dataset": dataset,
        "point_count": int(point_count),
        "warmup_point_count": int(warmup_point_count),
        "partition_cell_factor": float(partition_cell_factor),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "seed": int(seed),
        "declared_speedup_vs_current_elapsed": current_elapsed / max(declared_elapsed, 1.0e-12),
        "declared_route_uses_generic_all_items_direct_status_signature": bool(
            rows[-1]["uses_generic_all_items_direct_status_signature"]
        ),
        "declared_route_materializes_predicate_columns": bool(rows[-1]["predicate_columns_materialized"]),
        "declared_route_executes_rt_count_threshold": bool(rows[-1]["rt_count_threshold_executed"]),
        "claim_boundary": (
            "Internal large-scale route evidence only. It does not authorize release, paper "
            "reproduction, public speedup wording, broad RT-core wording, hidden dispatch, "
            "automatic partner selection, native ABI additions, true-zero-copy wording, or "
            "mixed-predicate RT-DBSCAN promotion."
        ),
        "release_authorized": False,
        "paper_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
        "warmup_row": warmup_row,
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print("GOAL4177_PROBE_DONE", json.dumps({"output": str(output), "rows": len(rows)}, sort_keys=True), flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dataset", default="road3d")
    parser.add_argument("--point-count", type=int, default=2_097_152)
    parser.add_argument("--warmup-point-count", type=int, default=4096)
    parser.add_argument("--partition-cell-factor", type=float, default=0.25)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260519)
    args = parser.parse_args()
    payload = run(
        output=args.output,
        dataset=args.dataset,
        point_count=args.point_count,
        warmup_point_count=args.warmup_point_count,
        partition_cell_factor=args.partition_cell_factor,
        repeat=args.repeat,
        warmup=args.warmup,
        seed=args.seed,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import subprocess
import sys
import time


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    DEFAULT_DATASET_CONFIG,
    RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA,
    _build_grouped_stream_timing_breakdown,
    _cluster_signature_from_partner_columns,
    _densify_cluster_labels,
    _rows_from_partner_columns,
    cluster_signature,
    fixed_radius_pairs_and_neighbor_counts_3d,
    make_rt_dbscan_points,
    run_rt_dbscan_benchmark,
    simulate_fixed_radius_blocked_grouped_component_continuation_3d,
)


TAIL_HOST_TIMING_FIELDS = (
    "adapter_run_sec",
    "rows_materialization_sec",
    "densify_cluster_labels_sec",
    "signature_sec",
    "column_signature_sec",
)
TAIL_DERIVED_TIMING_FIELDS = (
    "unattributed_elapsed_sec",
    "grouped_native_sec",
    "count_native_current_run_sec",
    "known_native_current_run_sec",
    "adapter_non_native_estimated_sec",
)


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _median_present_timing_fields(
    rows: list[dict[str, object]],
    section: str,
    fields: tuple[str, ...],
) -> dict[str, float]:
    medians: dict[str, float] = {}
    for field in fields:
        values = [
            float(row["timing_breakdown"][section][field])
            for row in rows
            if field in row["timing_breakdown"][section]
        ]
        if values:
            medians[field] = statistics.median(values)
    return medians


def _run_grouped_stream_repeats(
    *,
    point_count: int,
    repeat_count: int,
    signature_mode: str,
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    if signature_mode not in {"row", "column"}:
        raise ValueError("signature_mode must be row or column")
    dataset = "clustered3d"
    config = DEFAULT_DATASET_CONFIG[dataset]
    radius = float(config["radius"])
    min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    prepared = rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        points,
        radius=radius,
        partner="cupy",
        grouped_union_query_block_size=grouped_union_query_block_size,
        grouped_union_same_root_culling=grouped_union_same_root_culling,
        grouped_union_direct_side_effect=grouped_union_direct_side_effect,
    )
    prepare_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signatures: list[str] = []
    with prepared:
        for repeat in range(1, repeat_count + 1):
            start = time.perf_counter()
            adapter_start = time.perf_counter()
            result = rt.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=min_neighbors,
                return_metadata=True,
            )
            adapter_run_sec = time.perf_counter() - adapter_start
            timing_sec = {"adapter_run_sec": adapter_run_sec}
            if signature_mode == "row":
                rows_start = time.perf_counter()
                raw_rows = _rows_from_partner_columns(result["columns"], partner="cupy")
                timing_sec["rows_materialization_sec"] = time.perf_counter() - rows_start
                densify_start = time.perf_counter()
                component_rows = _densify_cluster_labels(raw_rows)
                timing_sec["densify_cluster_labels_sec"] = time.perf_counter() - densify_start
                signature_start = time.perf_counter()
                signature = cluster_signature(component_rows)
                timing_sec["signature_sec"] = time.perf_counter() - signature_start
            else:
                signature_start = time.perf_counter()
                signature = _cluster_signature_from_partner_columns(result["columns"], partner="cupy")
                timing_sec["column_signature_sec"] = time.perf_counter() - signature_start
            elapsed = time.perf_counter() - start
            metadata = result["metadata"]
            native = metadata.get("native_grouped_stream_metadata", {})
            count_native = metadata.get("count_metadata", {}).get("native_metadata", {})
            timing_breakdown = _build_grouped_stream_timing_breakdown(
                timing_sec,
                metadata,
                elapsed_sec=elapsed,
            )
            rows.append(
                {
                    "repeat": repeat,
                    "elapsed_sec": elapsed,
                    "timing_breakdown": timing_breakdown,
                    "signature": signature,
                    "core_flag_cache_reused": metadata.get("core_flag_cache_reused"),
                    "count_threshold": metadata.get("core_flag_threshold"),
                    "count_native_elapsed_sec": count_native.get("native_elapsed_sec"),
                    "neighbor_count_policy": metadata.get("neighbor_count_policy"),
                    "grouped_native_elapsed_sec": native.get("native_elapsed_sec"),
                    "grouped_native_execution_path": native.get("native_execution_path"),
                    "grouped_native_symbol": native.get("native_symbol"),
                    "grouped_predicate_mode": native.get("predicate_mode"),
                    "grouped_query_source": native.get("query_source"),
                    "grouped_transfer_mode": native.get("transfer_mode"),
                    "grouped_query_block_size": native.get("query_block_size"),
                    "grouped_query_block_count": native.get("query_block_count"),
                    "grouped_query_blocked": native.get("grouped_union_query_blocked"),
                    "grouped_same_root_culling_enabled": native.get("grouped_union_same_root_culling_enabled"),
                    "grouped_same_root_culling_policy": native.get("grouped_union_same_root_culling_policy"),
                    "grouped_direct_side_effect_enabled": native.get("grouped_union_direct_side_effect_enabled"),
                    "grouped_direct_side_effect_policy": native.get("grouped_union_direct_side_effect_policy"),
                }
            )
            signatures.append(json.dumps(signature, sort_keys=True))

    tail = rows[1:] if len(rows) > 1 else rows
    tail_timing_breakdown_median_sec = {
        "schema": RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA,
        "host_observed": _median_present_timing_fields(tail, "host_observed_sec", TAIL_HOST_TIMING_FIELDS),
        "derived": _median_present_timing_fields(tail, "derived_sec", TAIL_DERIVED_TIMING_FIELDS),
    }
    return {
        "dataset": dataset,
        "point_count": point_count,
        "signature_mode": signature_mode,
        "grouped_union_query_block_size": grouped_union_query_block_size,
        "grouped_union_same_root_culling": grouped_union_same_root_culling,
        "grouped_union_direct_side_effect": grouped_union_direct_side_effect,
        "radius": radius,
        "min_neighbors": min_neighbors,
        "prepare_sec": prepare_sec,
        "repeat_rows": rows,
        "tail_median_sec": statistics.median(row["elapsed_sec"] for row in tail),
        "tail_mean_sec": statistics.mean(row["elapsed_sec"] for row in tail),
        "grouped_native_tail_median_sec": statistics.median(
            row["grouped_native_elapsed_sec"] for row in tail
        ),
        "grouped_native_tail_mean_sec": statistics.mean(
            row["grouped_native_elapsed_sec"] for row in tail
        ),
        "tail_timing_breakdown_median_sec": tail_timing_breakdown_median_sec,
        "signatures_match": len(set(signatures)) == 1,
    }


def _simulator_sample() -> dict[str, object]:
    points = make_rt_dbscan_points("clustered3d", point_count=96, seed=20260520)
    _, counts = fixed_radius_pairs_and_neighbor_counts_3d(points, radius=0.055)
    flags = tuple(count >= 12 for count in counts)
    _, metadata = simulate_fixed_radius_blocked_grouped_component_continuation_3d(
        points,
        radius=0.055,
        predicate_flags=flags,
        neighbor_counts=counts,
        segment_target_hits=64,
    )
    return metadata


def _nvcc_version_line() -> str | None:
    output = _check_output(["nvcc", "--version"])
    if not output:
        return None
    lines = output.splitlines()
    return lines[-1] if lines else None


def run_baseline(
    *,
    output_dir: pathlib.Path,
    point_counts: tuple[int, ...],
    repeat_count: int,
    signature_mode: str = "row",
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for point_count in point_counts:
        summary = _run_grouped_stream_repeats(
            point_count=point_count,
            repeat_count=repeat_count,
            signature_mode=signature_mode,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        )
        summaries.append(summary)
        suffix = "" if signature_mode == "row" else f"_{signature_mode}_signature"
        if grouped_union_query_block_size is not None:
            suffix += f"_blocked_q{grouped_union_query_block_size}"
        if not grouped_union_same_root_culling:
            suffix += "_same_root_off"
        if grouped_union_direct_side_effect:
            suffix += "_direct_side_effect"
        (output_dir / f"clustered3d_{point_count}_grouped_stream{suffix}.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    tiny_smoke = run_rt_dbscan_benchmark(
        mode="optix_rt_core_grouped_stream_cupy_components_3d",
        dataset="tiny",
        point_count=None,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=True,
        grouped_union_same_root_culling=grouped_union_same_root_culling,
        grouped_union_direct_side_effect=grouped_union_direct_side_effect,
    )
    summary = {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_tree_is_git_checkout": (ROOT / ".git").exists(),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cuda_nvcc": _nvcc_version_line(),
        "signature_mode": signature_mode,
        "grouped_union_query_block_size": grouped_union_query_block_size,
        "grouped_union_same_root_culling": grouped_union_same_root_culling,
        "grouped_union_direct_side_effect": grouped_union_direct_side_effect,
        "summaries": summaries,
        "tiny_smoke_matches_reference": tiny_smoke.get("matches_reference"),
        "simulator_metadata_sample": _simulator_sample(),
        "claim_boundary": {
            "native_goal2467_implementation": False,
            "native_goal2472_query_range_candidate": grouped_union_query_block_size is not None,
            "goal2467_performance_claim_authorized": False,
            "goal2472_performance_claim_authorized": False,
            "goal2465_compatible_baseline_only": True,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Goal2467 grouped-stream pod baseline.")
    parser.add_argument(
        "--output-dir",
        default="docs/reports/goal2467_grouped_stream_baseline_pod",
    )
    parser.add_argument("--point-count", action="append", type=int, dest="point_counts")
    parser.add_argument("--repeat-count", type=int, default=5)
    parser.add_argument("--signature-mode", choices=("row", "column"), default="row")
    parser.add_argument("--grouped-union-query-block-size", type=int, default=None)
    parser.add_argument("--disable-grouped-union-same-root-culling", action="store_true")
    parser.add_argument("--enable-grouped-union-direct-side-effect", action="store_true")
    args = parser.parse_args(argv)

    point_counts = tuple(args.point_counts) if args.point_counts else (32768, 65536)
    if args.repeat_count < 1:
        raise ValueError("repeat-count must be positive")
    summary = run_baseline(
        output_dir=pathlib.Path(args.output_dir),
        point_counts=point_counts,
        repeat_count=args.repeat_count,
        signature_mode=args.signature_mode,
        grouped_union_query_block_size=args.grouped_union_query_block_size,
        grouped_union_same_root_culling=not args.disable_grouped_union_same_root_culling,
        grouped_union_direct_side_effect=args.enable_grouped_union_direct_side_effect,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    DEFAULT_DATASET_CONFIG,
    _densify_cluster_labels,
    _rows_from_partner_columns,
    cluster_signature,
    make_rt_dbscan_points,
    run_rt_dbscan_benchmark,
)


PREPARED_CUPY_GRID_MODE = "partner_cupy_prepared_grid_components_3d"
PREPARED_CUPY_ADJACENCY_MODE = "partner_cupy_prepared_adjacency_components_3d"
PREPARED_GRID_MODE = "optix_rt_core_flags_cupy_prepared_grid_components_3d"
PREPARED_OPTIX_ADJACENCY_MODE = "optix_rt_core_adjacency_cupy_components_3d"
PREPARED_OPTIX_CHUNKED_ADJACENCY_MODE = "optix_rt_core_chunked_adjacency_cupy_components_3d"

DEFAULT_MODES = (
    "partner_cupy_grid_components_3d",
    PREPARED_CUPY_GRID_MODE,
    PREPARED_CUPY_ADJACENCY_MODE,
    "optix_core_flags_cupy_grid_components_3d",
    "optix_rt_core_flags_cupy_grid_components_3d",
    PREPARED_GRID_MODE,
    PREPARED_OPTIX_ADJACENCY_MODE,
    PREPARED_OPTIX_CHUNKED_ADJACENCY_MODE,
    "optix_rt_core_flags_cupy_microcell_graph_components_3d",
)


def _run_prepared_cupy_grid_repeat_rows(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
) -> tuple[list[dict[str, object]], object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_radius = float(config["radius"])
    resolved_min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
    prepared_grid = rt.prepare_radius_graph_components_3d_cupy_grid_partner_columns(
        point_columns,
        radius=resolved_radius,
        partner="cupy",
    )
    prepared_grid_build_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signature = None
    for repeat_index in range(repeat_count):
        outer_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_prepared_grid_partner_columns(
            prepared_grid,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        component_rows = _densify_cluster_labels(
            _rows_from_partner_columns(result["columns"], partner="cupy")
        )
        current_signature = cluster_signature(component_rows)
        if signature is None:
            signature = current_signature
        outer_elapsed = time.perf_counter() - outer_start
        metadata = result["metadata"]
        rows.append(
            {
                "mode": PREPARED_CUPY_GRID_MODE,
                "repeat_index": repeat_index + 1,
                "outer_elapsed_sec": outer_elapsed,
                "app_elapsed_sec": outer_elapsed,
                "optix_core_flag_sec": None,
                "optix_rt_count_threshold_sec": None,
                "cupy_component_continuation_sec": outer_elapsed,
                "prepared_grid_build_sec": prepared_grid_build_sec,
                "prepared_grid_reused": metadata.get("prepared_grid_reused"),
                "prepared_run_count": metadata.get("prepared_run_count"),
                "prepared_composite_reused": None,
                "prepared_composite_run_count": None,
                "prepared_optix_scene_reused": None,
                "cell_graph_fast_path_active": None,
                "cell_graph_granularity": "prepared_radius_grid",
                "fallback_reason": None,
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "signature": current_signature,
            }
        )
    return rows, signature


def _run_prepared_cupy_adjacency_repeat_rows(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
) -> tuple[list[dict[str, object]], object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_radius = float(config["radius"])
    resolved_min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
    prepared_adjacency = rt.prepare_radius_graph_adjacency_3d_cupy_partner_columns(
        point_columns,
        radius=resolved_radius,
        partner="cupy",
    )
    prepared_adjacency_build_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signature = None
    for repeat_index in range(repeat_count):
        outer_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_prepared_adjacency_partner_columns(
            prepared_adjacency,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        component_rows = _densify_cluster_labels(
            _rows_from_partner_columns(result["columns"], partner="cupy")
        )
        current_signature = cluster_signature(component_rows)
        if signature is None:
            signature = current_signature
        outer_elapsed = time.perf_counter() - outer_start
        metadata = result["metadata"]
        rows.append(
            {
                "mode": PREPARED_CUPY_ADJACENCY_MODE,
                "repeat_index": repeat_index + 1,
                "outer_elapsed_sec": outer_elapsed,
                "app_elapsed_sec": outer_elapsed,
                "optix_core_flag_sec": None,
                "optix_rt_count_threshold_sec": None,
                "cupy_component_continuation_sec": outer_elapsed,
                "prepared_grid_build_sec": None,
                "prepared_adjacency_build_sec": prepared_adjacency_build_sec,
                "prepared_adjacency_reused": metadata.get("edge_stream_reused"),
                "prepared_adjacency_run_count": metadata.get("prepared_adjacency_run_count"),
                "directed_edge_count": metadata.get("directed_edge_count"),
                "prepared_grid_reused": None,
                "prepared_run_count": None,
                "prepared_composite_reused": None,
                "prepared_composite_run_count": None,
                "prepared_optix_scene_reused": None,
                "cell_graph_fast_path_active": None,
                "cell_graph_granularity": "prepared_directed_adjacency_stream",
                "fallback_reason": None,
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": True,
                "signature": current_signature,
            }
        )
    return rows, signature


def _run_prepared_grid_repeat_rows(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
) -> tuple[list[dict[str, object]], object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_radius = float(config["radius"])
    resolved_min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    prepared_graph = rt.prepare_optix_cupy_radius_graph_components_3d(
        points,
        radius=resolved_radius,
        partner="cupy",
    )
    prepared_composite_build_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signature = None
    with prepared_graph:
        for repeat_index in range(repeat_count):
            outer_start = time.perf_counter()
            result = rt.radius_graph_components_3d_optix_cupy_prepared_partner_columns(
                prepared_graph,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
            component_rows = _densify_cluster_labels(
                _rows_from_partner_columns(result["columns"], partner="cupy")
            )
            current_signature = cluster_signature(component_rows)
            if signature is None:
                signature = current_signature
            outer_elapsed = time.perf_counter() - outer_start
            metadata = result["metadata"]
            rows.append(
                {
                    "mode": PREPARED_GRID_MODE,
                    "repeat_index": repeat_index + 1,
                    "outer_elapsed_sec": outer_elapsed,
                    "app_elapsed_sec": outer_elapsed,
                    "optix_core_flag_sec": None,
                    "optix_rt_count_threshold_sec": metadata.get("optix_rt_count_threshold_sec"),
                    "cupy_component_continuation_sec": metadata.get("cupy_component_continuation_sec"),
                    "prepared_grid_build_sec": prepared_composite_build_sec,
                    "prepared_composite_build_sec": prepared_composite_build_sec,
                    "prepared_grid_reused": metadata.get("prepared_grid_reused"),
                    "prepared_run_count": metadata.get("prepared_run_count"),
                    "prepared_composite_reused": metadata.get("prepared_composite_reused"),
                    "prepared_composite_run_count": metadata.get("prepared_composite_run_count"),
                    "prepared_optix_scene_reused": True,
                    "cell_graph_fast_path_active": None,
                    "cell_graph_granularity": "prepared_radius_grid",
                    "fallback_reason": None,
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "signature": current_signature,
                }
            )
    return rows, signature


def _run_prepared_optix_adjacency_repeat_rows(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
) -> tuple[list[dict[str, object]], object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_radius = float(config["radius"])
    resolved_min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    prepared_graph = rt.prepare_optix_cupy_radius_graph_adjacency_3d(
        points,
        radius=resolved_radius,
        partner="cupy",
    )
    prepared_composite_build_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signature = None
    with prepared_graph:
        for repeat_index in range(repeat_count):
            outer_start = time.perf_counter()
            result = rt.radius_graph_components_3d_optix_cupy_prepared_adjacency_partner_columns(
                prepared_graph,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
            component_rows = _densify_cluster_labels(
                _rows_from_partner_columns(result["columns"], partner="cupy")
            )
            current_signature = cluster_signature(component_rows)
            if signature is None:
                signature = current_signature
            outer_elapsed = time.perf_counter() - outer_start
            metadata = result["metadata"]
            rows.append(
                {
                    "mode": PREPARED_OPTIX_ADJACENCY_MODE,
                    "repeat_index": repeat_index + 1,
                    "outer_elapsed_sec": outer_elapsed,
                    "app_elapsed_sec": outer_elapsed,
                    "optix_core_flag_sec": None,
                    "optix_rt_count_threshold_sec": metadata.get("count_metadata", {}).get("native_metadata", {}).get("native_elapsed_sec"),
                    "cupy_component_continuation_sec": outer_elapsed,
                    "prepared_grid_build_sec": None,
                    "prepared_composite_build_sec": prepared_composite_build_sec,
                    "prepared_adjacency_build_sec": prepared_composite_build_sec,
                    "prepared_adjacency_reused": metadata.get("edge_stream_reused"),
                    "prepared_adjacency_run_count": metadata.get("prepared_adjacency_run_count"),
                    "directed_edge_count": metadata.get("directed_edge_count"),
                    "prepared_grid_reused": None,
                    "prepared_run_count": None,
                    "prepared_composite_reused": metadata.get("edge_stream_reused"),
                    "prepared_composite_run_count": metadata.get("prepared_adjacency_run_count"),
                    "prepared_optix_scene_reused": True,
                    "cell_graph_fast_path_active": None,
                    "cell_graph_granularity": "prepared_optix_directed_adjacency_stream",
                    "fallback_reason": None,
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": True,
                    "signature": current_signature,
                }
            )
    return rows, signature


def _run_prepared_optix_chunked_adjacency_repeat_rows(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
    max_directed_edges_per_chunk: int | None,
    reuse_neighbor_index_workspace: bool,
    neighbor_index_workspace_pool_size: int,
) -> tuple[list[dict[str, object]], object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_radius = float(config["radius"])
    resolved_min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    prepared_graph = rt.prepare_optix_cupy_radius_graph_chunked_adjacency_3d(
        points,
        radius=resolved_radius,
        partner="cupy",
        max_directed_edges_per_chunk=max_directed_edges_per_chunk,
        reuse_neighbor_index_workspace=reuse_neighbor_index_workspace,
        neighbor_index_workspace_pool_size=neighbor_index_workspace_pool_size,
    )
    prepared_composite_build_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    signature = None
    with prepared_graph:
        for repeat_index in range(repeat_count):
            outer_start = time.perf_counter()
            result = rt.radius_graph_components_3d_optix_cupy_prepared_chunked_adjacency_partner_columns(
                prepared_graph,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
            component_rows = _densify_cluster_labels(
                _rows_from_partner_columns(result["columns"], partner="cupy")
            )
            current_signature = cluster_signature(component_rows)
            if signature is None:
                signature = current_signature
            outer_elapsed = time.perf_counter() - outer_start
            metadata = result["metadata"]
            rows.append(
                {
                    "mode": PREPARED_OPTIX_CHUNKED_ADJACENCY_MODE,
                    "repeat_index": repeat_index + 1,
                    "outer_elapsed_sec": outer_elapsed,
                    "app_elapsed_sec": outer_elapsed,
                    "optix_core_flag_sec": None,
                    "optix_rt_count_threshold_sec": None,
                    "cupy_component_continuation_sec": outer_elapsed,
                    "prepared_grid_build_sec": None,
                    "prepared_composite_build_sec": prepared_composite_build_sec,
                    "prepared_adjacency_build_sec": prepared_composite_build_sec,
                    "prepared_adjacency_reused": metadata.get("edge_stream_reused"),
                    "prepared_adjacency_run_count": metadata.get("prepared_chunked_adjacency_run_count"),
                    "directed_edge_count": metadata.get("total_directed_edge_count"),
                    "max_chunk_directed_edge_count": metadata.get("max_chunk_directed_edge_count"),
                    "chunk_count": metadata.get("chunk_count"),
                    "max_directed_edges_per_chunk": metadata.get("max_directed_edges_per_chunk"),
                    "neighbor_index_workspace_reused": metadata.get("neighbor_index_workspace_reused"),
                    "neighbor_index_workspace_pool_size": metadata.get("neighbor_index_workspace_pool_size"),
                    "neighbor_index_workspace_size": metadata.get("neighbor_index_workspace_size"),
                    "chunk_sync_for_neighbor_index_workspace_reuse": metadata.get(
                        "chunk_sync_for_neighbor_index_workspace_reuse"
                    ),
                    "prepared_grid_reused": None,
                    "prepared_run_count": None,
                    "prepared_composite_reused": metadata.get("edge_stream_reused"),
                    "prepared_composite_run_count": metadata.get("prepared_chunked_adjacency_run_count"),
                    "prepared_optix_scene_reused": True,
                    "cell_graph_fast_path_active": None,
                    "cell_graph_granularity": "prepared_optix_chunked_directed_adjacency_stream",
                    "fallback_reason": None,
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": False,
                    "materializes_bounded_directed_adjacency_chunks": True,
                    "signature": current_signature,
                }
            )
    return rows, signature


def run_repeat_probe(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
    modes: tuple[str, ...],
    chunk_adjacency_edge_budget: int | None = None,
    reuse_chunk_neighbor_index_workspace: bool = False,
    chunk_neighbor_index_workspace_pool_size: int = 0,
) -> dict[str, object]:
    if repeat_count < 1:
        raise ValueError("repeat_count must be positive")
    rows: list[dict[str, object]] = []
    signatures: dict[str, object] = {}
    for mode in modes:
        if mode == PREPARED_CUPY_GRID_MODE:
            prepared_rows, signature = _run_prepared_cupy_grid_repeat_rows(
                dataset=dataset,
                point_count=point_count,
                repeat_count=repeat_count,
            )
            rows.extend(prepared_rows)
            signatures.setdefault(mode, signature)
            continue
        if mode == PREPARED_CUPY_ADJACENCY_MODE:
            prepared_rows, signature = _run_prepared_cupy_adjacency_repeat_rows(
                dataset=dataset,
                point_count=point_count,
                repeat_count=repeat_count,
            )
            rows.extend(prepared_rows)
            signatures.setdefault(mode, signature)
            continue
        if mode == PREPARED_GRID_MODE:
            prepared_rows, signature = _run_prepared_grid_repeat_rows(
                dataset=dataset,
                point_count=point_count,
                repeat_count=repeat_count,
            )
            rows.extend(prepared_rows)
            signatures.setdefault(mode, signature)
            continue
        if mode == PREPARED_OPTIX_ADJACENCY_MODE:
            prepared_rows, signature = _run_prepared_optix_adjacency_repeat_rows(
                dataset=dataset,
                point_count=point_count,
                repeat_count=repeat_count,
            )
            rows.extend(prepared_rows)
            signatures.setdefault(mode, signature)
            continue
        if mode == PREPARED_OPTIX_CHUNKED_ADJACENCY_MODE:
            prepared_rows, signature = _run_prepared_optix_chunked_adjacency_repeat_rows(
                dataset=dataset,
                point_count=point_count,
                repeat_count=repeat_count,
                max_directed_edges_per_chunk=chunk_adjacency_edge_budget,
                reuse_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
                neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
            )
            rows.extend(prepared_rows)
            signatures.setdefault(mode, signature)
            continue
        for repeat_index in range(repeat_count):
            outer_start = time.perf_counter()
            result = run_rt_dbscan_benchmark(
                mode=mode,
                dataset=dataset,
                point_count=point_count,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=False,
                validate=False,
            )
            outer_elapsed = time.perf_counter() - outer_start
            signatures.setdefault(mode, result["signature"])
            metadata = result.get("metadata", {})
            rows.append(
                {
                    "mode": mode,
                    "repeat_index": repeat_index + 1,
                    "outer_elapsed_sec": outer_elapsed,
                    "app_elapsed_sec": result["elapsed_sec"],
                    "optix_core_flag_sec": metadata.get("optix_core_flag_sec"),
                    "optix_rt_count_threshold_sec": metadata.get("optix_rt_count_threshold_sec"),
                    "cupy_component_continuation_sec": metadata.get("cupy_component_continuation_sec"),
                    "prepared_grid_build_sec": metadata.get("prepared_grid_build_sec"),
                    "prepared_grid_reused": metadata.get("prepared_grid_reused"),
                    "prepared_run_count": metadata.get("prepared_run_count"),
                    "prepared_optix_scene_reused": metadata.get("prepared_optix_scene_reused"),
                    "cell_graph_fast_path_active": metadata.get("cell_graph_fast_path_active"),
                    "cell_graph_granularity": metadata.get("cell_graph_granularity"),
                    "fallback_reason": metadata.get("fallback_reason"),
                    "rt_core_accelerated": result["claim_boundary"]["rt_core_accelerated"],
                    "materializes_neighbor_rows": metadata.get("materializes_neighbor_rows"),
                    "signature": result["signature"],
                }
            )
    return {
        "app": "rt_dbscan_repeat_probe",
        "dataset": dataset,
        "point_count": point_count,
        "repeat_count": repeat_count,
        "modes": list(modes),
        "rows": rows,
        "signatures_match": len({json.dumps(value, sort_keys=True) for value in signatures.values()}) == 1,
        "claim_boundary": {
            "paper_dataset_reproduction": False,
            "paper_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "steady_state_probe_only": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repeat probe for RT-DBSCAN bridge warm/steady-state behavior.")
    parser.add_argument("--dataset", default="clustered3d", choices=("clustered3d", "road3d", "ngsim_dense"))
    parser.add_argument("--point-count", type=int, default=4096)
    parser.add_argument("--repeat-count", type=int, default=4)
    parser.add_argument("--mode", action="append", choices=DEFAULT_MODES, dest="modes")
    parser.add_argument("--chunk-adjacency-edge-budget", type=int, default=None)
    parser.add_argument("--reuse-chunk-neighbor-index-workspace", action="store_true")
    parser.add_argument("--chunk-neighbor-index-workspace-pool-size", type=int, default=0)
    args = parser.parse_args(argv)
    modes = tuple(args.modes) if args.modes else DEFAULT_MODES
    print(
        json.dumps(
            run_repeat_probe(
                dataset=args.dataset,
                point_count=args.point_count,
                repeat_count=args.repeat_count,
                modes=modes,
                chunk_adjacency_edge_budget=args.chunk_adjacency_edge_budget,
                reuse_chunk_neighbor_index_workspace=args.reuse_chunk_neighbor_index_workspace,
                chunk_neighbor_index_workspace_pool_size=args.chunk_neighbor_index_workspace_pool_size,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

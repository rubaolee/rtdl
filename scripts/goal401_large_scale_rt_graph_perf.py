from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, "src")

import rtdsl as rt
from rtdsl.graph_perf import measure_bfs_perf
from rtdsl.graph_perf import measure_triangle_perf
from rtdsl.graph_perf import tune_bfs_perf
from rtdsl.graph_perf import tune_triangle_perf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to a SNAP edge-list archive or text file.")
    parser.add_argument("--dataset-name", default="custom_graph", help="Dataset name recorded in the summary.")
    parser.add_argument("--workload", choices=("bfs", "triangle_count"), required=True)
    parser.add_argument("--max-edges", type=int, required=True, help="Bounded edge cap for the loaded graph slice.")
    parser.add_argument("--frontier-size", type=int, default=1024, help="Frontier batch size for large BFS step timing.")
    parser.add_argument("--seed-count", type=int, default=4096, help="Canonical seed-edge batch size for large triangle timing.")
    parser.add_argument("--source-id", type=int, default=0, help="Preferred source vertex for BFS frontier seeding.")
    parser.add_argument("--repeats", type=int, default=3, help="Median timing repeat count.")
    parser.add_argument("--postgresql-dsn", required=True, help="PostgreSQL DSN used for the indexed external baseline.")
    parser.add_argument("--target-backend", choices=("embree", "optix", "vulkan"), default=None, help="Optional backend whose execution time should be tuned toward the target window.")
    parser.add_argument("--target-seconds", type=float, default=None, help="Optional backend execution target in seconds.")
    parser.add_argument("--target-min-factor", type=float, default=0.5, help="Lower acceptable ratio for the target-duration window.")
    parser.add_argument("--target-max-factor", type=float, default=1.5, help="Upper acceptable ratio for the target-duration window.")
    parser.add_argument("--max-frontier-size", type=int, default=None, help="Optional cap while scaling BFS frontier batch size.")
    parser.add_argument("--max-seed-count", type=int, default=None, help="Optional cap while scaling triangle seed batch size.")
    parser.add_argument("--execution-iterations", type=int, default=1, help="Repeat the prepared RT step and PostgreSQL query this many times per timed sample.")
    parser.add_argument("--postgresql-query-iterations", type=int, default=1, help="Repeat the PostgreSQL query this many times per timed sample.")
    parser.add_argument("--max-execution-iterations", type=int, default=1024, help="Upper cap for execution-iteration scaling in target-duration mode.")
    parser.add_argument("--max-rounds", type=int, default=8, help="Maximum tuning rounds when target-duration mode is enabled.")
    args = parser.parse_args()

    if (args.target_backend is None) != (args.target_seconds is None):
        parser.error("--target-backend and --target-seconds must be provided together")
    if args.target_min_factor <= 0 or args.target_max_factor <= 0:
        parser.error("target window factors must be positive")
    if args.target_min_factor > args.target_max_factor:
        parser.error("--target-min-factor must be <= --target-max-factor")
    if args.execution_iterations <= 0 or args.postgresql_query_iterations <= 0 or args.max_execution_iterations <= 0:
        parser.error("iteration counts must be positive")

    dataset_path = Path(args.dataset)
    if args.workload == "bfs":
        graph = rt.load_snap_edge_list_graph(dataset_path, directed=True, max_edges=args.max_edges)
        if args.target_backend is not None:
            summary = tune_bfs_perf(
                graph,
                frontier_size=args.frontier_size,
                source_id=args.source_id,
                repeats=args.repeats,
                postgresql_dsn=args.postgresql_dsn,
                target_backend=args.target_backend,
                target_seconds=args.target_seconds,
                min_factor=args.target_min_factor,
                max_factor=args.target_max_factor,
                max_frontier_size=args.max_frontier_size,
                max_execution_iterations=args.max_execution_iterations,
                max_rounds=args.max_rounds,
            )
        else:
            summary = measure_bfs_perf(
                graph,
                frontier_size=args.frontier_size,
                source_id=args.source_id,
                repeats=args.repeats,
                postgresql_dsn=args.postgresql_dsn,
                execution_iterations=args.execution_iterations,
                postgresql_query_iterations=args.postgresql_query_iterations,
            )
        summary["max_edges_loaded"] = args.max_edges
    else:
        graph = rt.load_snap_simple_undirected_graph(dataset_path, max_edges=args.max_edges)
        if args.target_backend is not None:
            summary = tune_triangle_perf(
                graph,
                seed_count=args.seed_count,
                repeats=args.repeats,
                postgresql_dsn=args.postgresql_dsn,
                target_backend=args.target_backend,
                target_seconds=args.target_seconds,
                min_factor=args.target_min_factor,
                max_factor=args.target_max_factor,
                max_seed_count=args.max_seed_count,
                max_execution_iterations=args.max_execution_iterations,
                max_rounds=args.max_rounds,
            )
        else:
            summary = measure_triangle_perf(
                graph,
                seed_count=args.seed_count,
                repeats=args.repeats,
                postgresql_dsn=args.postgresql_dsn,
                execution_iterations=args.execution_iterations,
                postgresql_query_iterations=args.postgresql_query_iterations,
            )
        summary["max_canonical_edges_loaded"] = args.max_edges
        summary["graph_transform"] = "simple_undirected"

    summary["dataset"] = args.dataset_name
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

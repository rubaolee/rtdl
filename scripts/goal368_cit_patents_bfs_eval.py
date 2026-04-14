from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, "src")

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="build/graph_datasets/cit-Patents.txt.gz",
        help="Path to the bounded cit-Patents edge-list archive.",
    )
    parser.add_argument(
        "--max-edges",
        type=int,
        default=500_000,
        help="Bound the number of loaded directed edges for the first cit-Patents BFS slice.",
    )
    parser.add_argument(
        "--source-id",
        type=int,
        default=0,
        help="Source vertex for the bounded BFS run.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Median-timing repeat count.",
    )
    parser.add_argument(
        "--postgresql-dsn",
        default=None,
        help="Optional PostgreSQL DSN for the bounded external baseline.",
    )
    args = parser.parse_args()

    spec = rt.graph_dataset_spec("graphalytics_cit_patents")
    graph = rt.load_snap_edge_list_graph(
        Path(args.dataset),
        directed=spec.directed,
        max_edges=args.max_edges,
        expected_vertex_count=spec.vertex_count_hint,
    )
    summary = rt.bfs_baseline_evaluation(
        graph,
        source_id=args.source_id,
        repeats=args.repeats,
        postgresql_dsn=args.postgresql_dsn,
    )
    summary["dataset"] = spec.name
    summary["max_edges_loaded"] = args.max_edges
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

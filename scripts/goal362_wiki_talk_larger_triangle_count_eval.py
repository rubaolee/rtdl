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
        default="build/graph_datasets/wiki-Talk.txt.gz",
        help="Path to SNAP wiki-Talk edge-list archive.",
    )
    parser.add_argument(
        "--max-edges",
        type=int,
        default=150_000,
        help="Bound the number of canonical undirected edges loaded for the larger real-data triangle-count slice.",
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

    graph = rt.load_snap_simple_undirected_graph(
        Path(args.dataset),
        max_edges=args.max_edges,
    )
    summary = rt.triangle_count_baseline_evaluation(
        graph,
        repeats=args.repeats,
        postgresql_dsn=args.postgresql_dsn,
    )
    summary["dataset"] = "snap_wiki_talk"
    summary["goal"] = "goal362"
    summary["graph_transform"] = "simple_undirected"
    summary["max_canonical_edges_loaded"] = args.max_edges
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

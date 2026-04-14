from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, "src")

import rtdsl as rt


def main() -> int:
    repeats = int(os.environ.get("RTDL_GRAPH_REPEATS", "3"))
    postgresql_dsn = os.environ.get("RTDL_POSTGRESQL_DSN")

    # Keep the PostgreSQL external baseline in a genuinely bounded regime.
    bfs_graph = rt.binary_tree_graph(127)
    triangle_graph = rt.clique_graph(24)

    summary = {
        "bfs": rt.bfs_baseline_evaluation(
            bfs_graph,
            source_id=0,
            repeats=repeats,
            postgresql_dsn=postgresql_dsn,
        ),
        "triangle_count": rt.triangle_count_baseline_evaluation(
            triangle_graph,
            repeats=repeats,
            postgresql_dsn=postgresql_dsn,
        ),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

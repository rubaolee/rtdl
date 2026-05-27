#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    write_binary_edges,
)


def k4_clique_edges(clique_count: int) -> tuple[tuple[int, int], ...]:
    if clique_count <= 0:
        raise ValueError("clique_count must be positive")
    edges: list[tuple[int, int]] = []
    for index in range(clique_count):
        base = index * 4
        edges.extend(
            (
                (base + 0, base + 1),
                (base + 0, base + 2),
                (base + 0, base + 3),
                (base + 1, base + 2),
                (base + 1, base + 3),
                (base + 2, base + 3),
            )
        )
    return tuple(edges)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate RT-Graph-style K4 clique binary edge fixtures.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cliques", type=int, required=True)
    args = parser.parse_args(argv)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    edges = k4_clique_edges(args.cliques)
    write_binary_edges(args.output, edges)
    print(
        f"wrote {len(edges)} edges for {args.cliques} K4 cliques to {args.output}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

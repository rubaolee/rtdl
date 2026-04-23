from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


def make_case(copies: int = 1) -> dict[str, object]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    row_offsets = [0]
    column_indices: list[int] = []
    frontier: list[rt.FrontierVertex] = []
    visited: list[int] = []
    for copy_index in range(copies):
        base = copy_index * 4
        adjacency = ((base + 1, base + 2), (base + 2, base + 3), (base + 3,), ())
        frontier.extend(
            (
                rt.FrontierVertex(vertex_id=base + 0, level=0),
                rt.FrontierVertex(vertex_id=base + 1, level=0),
            )
        )
        visited.extend((base + 0, base + 1))
        for neighbors in adjacency:
            column_indices.extend(neighbors)
            row_offsets.append(len(column_indices))
    return {
        "frontier": tuple(frontier),
        "graph": rt.csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(column_indices)),
        "visited": tuple(visited),
    }


def _summarize(rows) -> dict[str, object]:
    row_list = list(rows)
    return {
        "discovered_edge_count": len(row_list),
        "discovered_vertex_count": len({int(row["dst_vertex"]) for row in row_list}),
        "max_level": max((int(row["level"]) for row in row_list), default=0),
    }


def run_backend(backend: str, copies: int = 1, output_mode: str = "rows") -> dict[str, object]:
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    case = make_case(copies)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(bfs_expand_kernel, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(bfs_expand_kernel, **case)
    elif backend == "embree":
        rows = rt.run_embree(bfs_expand_kernel, **case)
    elif backend == "optix":
        rows = rt.run_optix(bfs_expand_kernel, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(bfs_expand_kernel, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    return {
        "app": "graph_bfs",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "graph_vertex_count": 4 * copies,
        "graph_edge_count": 5 * copies,
        "frontier_size": len(case["frontier"]),
        "visited_size": len(case["visited"]),
        "rows": rows if output_mode == "rows" else [],
        "summary": _summarize(rows),
        "optix_performance": {
            "class": "host_indexed_fallback",
            "note": (
                "OptiX BFS currently uses a host-indexed CSR expansion correctness path; "
                "this is not an RTX graph acceleration claim."
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release-facing RTDL graph BFS one-step example.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic graph fixture this many times.")
    parser.add_argument("--output-mode", default="rows", choices=("rows", "summary"))
    args = parser.parse_args(argv)
    print(json.dumps(run_backend(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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


def make_case() -> dict[str, object]:
    return {
        "frontier": (
            rt.FrontierVertex(vertex_id=0, level=0),
            rt.FrontierVertex(vertex_id=1, level=0),
        ),
        "graph": rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 5),
            column_indices=(1, 2, 2, 3, 3),
        ),
        "visited": (0, 1),
    }


def run_backend(backend: str) -> dict[str, object]:
    case = make_case()
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
        "graph_vertex_count": 4,
        "graph_edge_count": 5,
        "frontier": [{"vertex_id": 0, "level": 0}, {"vertex_id": 1, "level": 0}],
        "visited": [0, 1],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release-facing RTDL graph BFS one-step example.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_backend(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

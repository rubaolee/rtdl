from __future__ import annotations

import argparse
import json
import os
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
    return rt.summarize_bfs_rows(rows)


def _enforce_rt_core_requirement(backend: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    raise RuntimeError(
        "graph_bfs OptiX native graph-ray mode is not NVIDIA RT-core traversal "
        "claim-safe until the RTX cloud gate passes"
    )


def run_backend(
    backend: str,
    copies: int = 1,
    output_mode: str = "rows",
    *,
    require_rt_core: bool = False,
    optix_graph_mode: str = "auto",
) -> dict[str, object]:
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    if optix_graph_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError(f"unsupported optix_graph_mode: {optix_graph_mode}")
    _enforce_rt_core_requirement(backend, require_rt_core)
    case = make_case(copies)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(bfs_expand_kernel, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(bfs_expand_kernel, **case)
    elif backend == "embree":
        rows = rt.run_embree(bfs_expand_kernel, **case)
    elif backend == "optix":
        previous = os.environ.get("RTDL_OPTIX_GRAPH_MODE")
        if optix_graph_mode != "auto":
            os.environ["RTDL_OPTIX_GRAPH_MODE"] = "native" if optix_graph_mode == "native" else "host_indexed"
        try:
            rows = rt.run_optix(bfs_expand_kernel, **case)
        finally:
            if optix_graph_mode != "auto":
                if previous is None:
                    os.environ.pop("RTDL_OPTIX_GRAPH_MODE", None)
                else:
                    os.environ["RTDL_OPTIX_GRAPH_MODE"] = previous
    elif backend == "vulkan":
        rows = rt.run_vulkan(bfs_expand_kernel, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    return {
        "app": "graph_bfs",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "optix_graph_mode": optix_graph_mode if backend == "optix" else "not_applicable",
        "graph_vertex_count": 4 * copies,
        "graph_edge_count": 5 * copies,
        "frontier_size": len(case["frontier"]),
        "visited_size": len(case["visited"]),
        "row_count": len(rows),
        "rows": rows if output_mode == "rows" else [],
        "summary": _summarize(rows),
        "native_continuation_active": output_mode == "summary",
        "native_continuation_backend": "oracle_cpp" if output_mode == "summary" else None,
        "ray_tracing_accelerated": backend == "embree",
        "ray_tracing_note": (
            "Embree uses ray traversal over graph-edge primitives for frontier "
            "candidate generation; CPU-side visited/frontier bookkeeping remains "
            "outside the RT traversal."
            if backend == "embree"
            else "This backend is not currently classified as the graph BFS ray-tracing path."
        ),
        "rt_core_accelerated": False,
        "optix_performance": {
            "class": "host_indexed_fallback",
            "note": (
                "OptiX BFS currently uses a host-indexed CSR expansion correctness path; "
                "native graph-ray mode is available behind RTDL_OPTIX_GRAPH_MODE=native "
                "but is not an RTX graph acceleration claim until cloud-gated."
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
    parser.add_argument("--optix-graph-mode", default="auto", choices=("auto", "host_indexed", "native"))
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_backend(
                args.backend,
                copies=args.copies,
                output_mode=args.output_mode,
                require_rt_core=args.require_rt_core,
                optix_graph_mode=args.optix_graph_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

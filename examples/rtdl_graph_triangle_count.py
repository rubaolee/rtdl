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
def triangle_probe_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


def make_case() -> dict[str, object]:
    return {
        "seeds": ((0, 1), (1, 2), (0, 2)),
        "graph": rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        ),
    }


def run_backend(backend: str) -> dict[str, object]:
    case = make_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(triangle_probe_kernel, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(triangle_probe_kernel, **case)
    elif backend == "embree":
        rows = rt.run_embree(triangle_probe_kernel, **case)
    elif backend == "optix":
        rows = rt.run_optix(triangle_probe_kernel, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(triangle_probe_kernel, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    return {
        "app": "graph_triangle_count",
        "backend": backend,
        "graph_vertex_count": 4,
        "graph_edge_count": 6,
        "seed_edges": [{"u": 0, "v": 1}, {"u": 1, "v": 2}, {"u": 0, "v": 2}],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release-facing RTDL graph triangle-count one-step example.")
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

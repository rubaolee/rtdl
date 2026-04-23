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


def make_case(copies: int = 1) -> dict[str, object]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    row_offsets = [0]
    column_indices: list[int] = []
    seeds: list[tuple[int, int]] = []
    for copy_index in range(copies):
        base = copy_index * 4
        adjacency = ((base + 1, base + 2), (base + 0, base + 2), (base + 0, base + 1), ())
        seeds.extend(((base + 0, base + 1), (base + 1, base + 2), (base + 0, base + 2)))
        for neighbors in adjacency:
            column_indices.extend(neighbors)
            row_offsets.append(len(column_indices))
    return {
        "seeds": tuple(seeds),
        "graph": rt.csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(column_indices)),
    }


def _summarize(rows) -> dict[str, object]:
    row_list = list(rows)
    vertices = {int(row[name]) for row in row_list for name in ("u", "v", "w")}
    return {
        "triangle_count": len(row_list),
        "touched_vertex_count": len(vertices),
    }


def run_backend(backend: str, copies: int = 1, output_mode: str = "rows") -> dict[str, object]:
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    case = make_case(copies)
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
        "copies": copies,
        "output_mode": output_mode,
        "graph_vertex_count": 4 * copies,
        "graph_edge_count": 6 * copies,
        "seed_count": len(case["seeds"]),
        "rows": rows if output_mode == "rows" else [],
        "summary": _summarize(rows),
        "optix_performance": {
            "class": "host_indexed_fallback",
            "note": (
                "OptiX triangle-count currently uses a host-indexed CSR probe correctness path; "
                "this is not an RTX graph acceleration claim."
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release-facing RTDL graph triangle-count one-step example.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic triangle fixture this many times.")
    parser.add_argument("--output-mode", default="rows", choices=("rows", "summary"))
    args = parser.parse_args(argv)
    print(json.dumps(run_backend(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
